# -*- coding: utf-8 -*-
{
    "name": "LLM Service",
    "version": "19.0.1.0.0",
    "category": "AI",
    "summary": "Unified LLM API wrapper for Odoo (OpenAI-compatible)",
    "description": """
LLM Service
===========
Odoo 内统一的大模型 API 封装，对应《动手学大模型》Ch2 的工程化落地。

功能：
- 配置化（ir.config_parameter）：API Key / base_url / 模型 / 温度 / 超时
- 零第三方依赖：标准库 urllib 调用 OpenAI 兼容协议
- 唯一的 LLM 入口：llm.service（业务模块统一走这里，不散落 API 调用）
- 错误处理：401 / 429 限流 / 网络失败 / 返回结构异常 → 用户可读错误

配置项（系统参数）：
- llm_service.api_key            API Key（智谱 / DeepSeek / 豆包 等 OpenAI 兼容服务）
- llm_service.base_url           接口地址，默认 https://open.bigmodel.cn/api/paas/v4
- llm_service.default_model      默认模型，默认 glm-4.7-flash
- llm_service.models            备用模型列表（逗号分隔），主模型过载自动切换
- llm_service.default_temperature 默认温度，默认 0.7
- llm_service.timeout            请求超时（秒），默认 30
- llm_service.retries            429/5xx 重试次数（指数退避），默认 3
    """,
    "author": "odoo-ai-journey contributors",
    "website": "https://github.com/fengyuGbt/odoo-ai-journey",
    "license": "MIT",
    "depends": ["base"],
    "data": [],
    "installable": True,
    "application": False,
}
