# -*- coding: utf-8 -*-
"""LLM Service — Odoo 内统一的大模型 API 封装。

对应《动手学大模型》Ch2「调用大模型 API」的工程化落地。

设计要点：
- 零第三方依赖：标准库 urllib 调 OpenAI 兼容协议，任何 Odoo 环境可直装
- 配置全部走 ir.config_parameter（系统参数），不硬编码，部署改配置即可
- 所有业务模块的 LLM 调用都走本服务（llm.service 是唯一入口），便于换模型/统计/审计

配置项（系统参数，技术菜单或代码设置）：
- llm_service.api_key            API Key（智谱 / DeepSeek / 豆包 等 OpenAI 兼容服务）
- llm_service.base_url           接口地址，默认 https://open.bigmodel.cn/api/paas/v4
- llm_service.default_model      默认模型，默认 glm-4.7-flash
- llm_service.default_temperature 默认温度，默认 0.7
- llm_service.timeout            请求超时（秒），默认 60
"""

import json
import logging
import time
import urllib.error
import urllib.request

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class LLMService(models.AbstractModel):
    _name = "llm.service"
    _description = "LLM API Service"

    # ------------------------------------------------------------------
    # 配置读取
    # ------------------------------------------------------------------
    @api.model
    def _get_param(self, key, default=None):
        return self.env["ir.config_parameter"].get_param(key, default)

    @api.model
    def _get_api_key(self):
        key = self._get_param("llm_service.api_key")
        if not key:
            raise UserError(
                _("未配置 LLM API Key：请在系统参数中设置 llm_service.api_key")
            )
        return key

    @api.model
    def _get_base_url(self):
        return self._get_param(
            "llm_service.base_url", "https://open.bigmodel.cn/api/paas/v4"
        )

    @api.model
    def _get_default_model(self):
        return self._get_param("llm_service.default_model", "glm-4.7-flash")

    @api.model
    def _get_default_temperature(self):
        return float(self._get_param("llm_service.default_temperature", "0.7"))

    # ------------------------------------------------------------------
    # 核心调用（OpenAI 兼容 chat/completions）
    # ------------------------------------------------------------------
    @api.model
    def _call_llm(self, messages, model=None, temperature=None, timeout=None):
        """调用 OpenAI 兼容 chat/completions，返回模型文本。

        :param messages: 消息列表
            [{"role": "system"|"user"|"assistant", "content": "..."}, ...]
        :param model: 模型名；None 时取配置 llm_service.default_model
        :param temperature: 采样温度；None 时取配置
        :param timeout: 超时秒数；None 时取配置
        :return: 模型回复的文本（str）

        自动处理免费 API 的服务端过载（429/5xx）：
        - 按模型列表依次尝试（主模型过载自动切备用模型）
        - 每个模型最多重试 llm_service.retries 次（指数退避 2s/4s/8s）
        """
        model = model or self._get_default_model()
        configured_models = self._get_param("llm_service.models", "")
        models = [model]
        for m in configured_models.split(","):
            m = m.strip()
            if m and m not in models:
                models.append(m)
        retries = max(1, int(self._get_param("llm_service.retries", "3")))
        if temperature is None:
            temperature = self._get_default_temperature()
        if timeout is None:
            timeout = int(self._get_param("llm_service.timeout", "30"))

        last_error = None
        for m in models:
            for attempt in range(retries):
                try:
                    return self._post_chat(m, messages, temperature, timeout)
                except urllib.error.HTTPError as e:
                    detail = e.read().decode("utf-8", errors="replace")[:500]
                    last_error = (e.code, detail)
                    if e.code in (429, 500, 502, 503):
                        _logger.warning(
                            "LLM API %s 返回 %s（%s），第 %s 次重试",
                            m, e.code, detail[:120], attempt + 1,
                        )
                        if attempt < retries - 1:
                            time.sleep(min(2 ** attempt, 10))
                        continue
                    # 非可重试错误（401/400/403 等）：直接转用户可读错误
                    raise self._http_error_to_user(e.code, detail)
                except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                    # 网络失败 / 读取超时：服务端过载时常见，按可重试处理
                    last_error = ("net", str(e)[:200])
                    _logger.warning(
                        "LLM API %s 网络/超时错误：%s，第 %s 次重试",
                        m, e, attempt + 1,
                    )
                    if attempt < retries - 1:
                        time.sleep(min(2 ** attempt, 10))
                    continue
        raise UserError(
            _("LLM API 限流或服务过载（最后错误 %s）：%s，请稍后重试")
            % (last_error[0], last_error[1][:200])
        )

    @api.model
    def _post_chat(self, model, messages, temperature, timeout):
        """发送一次 chat/completions 请求，返回模型回复文本。"""
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": False,
        }
        headers = {
            "Authorization": "Bearer %s" % self._get_api_key(),
            "Content-Type": "application/json",
        }
        url = self._get_base_url().rstrip("/") + "/chat/completions"

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        try:
            return body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            _logger.error("LLM API 返回结构异常: %s", str(body)[:500])
            raise UserError(_("LLM API 返回结构异常，请查看服务端日志"))

    @api.model
    def _http_error_to_user(self, code, detail):
        """HTTP 错误转用户可读的 UserError。"""
        if code == 401:
            return UserError(
                _("LLM API Key 无效或未授权（401），请检查 llm_service.api_key")
            )
        if code == 429:
            return UserError(
                _("LLM API 限流（429）：请求过频或免费额度受限，请稍后重试")
            )
        return UserError(_("LLM API 错误 %s：%s") % (code, detail))

    # ------------------------------------------------------------------
    # 便利方法
    # ------------------------------------------------------------------
    @api.model
    def chat(self, prompt, system=None, **kwargs):
        """单轮对话：给定 user 内容（可选 system 提示），返回模型文本。

        示例：
            self.env["llm.service"].chat(
                "为这款产品写一段电商描述",
                system="你是电商文案专家，输出不超过 100 字",
                temperature=0.7,
            )
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return self._call_llm(messages, **kwargs)
