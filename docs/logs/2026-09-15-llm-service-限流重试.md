# llm_service 开发踩坑记录（2026-09-15）

> 日期：2026-09-15
> 场景：odoo-ai-journey 第 1 波 · llm_service 模块首次跑通（Odoo 19 + 智谱免费 API）
> 关联笔记：`docs/01-ch2-prompt-and-cot.md`

## 🛠 问题 1：免费 API 高峰期 429 限流

- **现象**：第一次调用 `llm.service.chat()` 返回 `HTTP 429 Too Many Requests`；裸测智谱 API 返回 `{"error":{"code":"1305","message":"该模型当前访问量过大，请您稍后再试"}}`。等待 45 秒后重试依然 429。
- **排查**：先用独立脚本裸调（不经 Odoo）排除模块问题 → 确认是智谱服务端模型过载（非 Key 问题、非账号限流、非代码问题）。晚上 9 点正是国内 API 使用高峰。
- **解决**：给 `llm.service` 加了两层机制：
  1. **指数退避重试**（`llm_service.retries`，默认 3 次，间隔 2s/4s/8s，上限 10s）
  2. **模型降级**（`llm_service.models` 逗号分隔备用模型列表，主模型 429/5xx 时自动换 `glm-4-flash`）
- **教训**：免费 API 的"免费"意味着高峰期过载是常态，**生产级 LLM 封装必须内置重试和降级**；429 响应体里的 `code` 字段（如 1305）比 HTTP 状态码更能说明原因。

## 🛠 问题 2：TimeoutError 不被 HTTPError 捕获

- **现象**：修复 429 后重试，抛 `TimeoutError: The read operation timed out`（连接建立后响应挂起 60 秒），代码直接崩。
- **排查**：栈显示 `urllib.request.urlopen` 的读取超时。Python 中 `TimeoutError` 是 `OSError` 子类，**不是** `urllib.error.URLError` 的子类，原代码只捕获 `HTTPError`/`URLError` 所以漏了。
- **解决**：异常处理改为 `except (urllib.error.URLError, TimeoutError, ConnectionError)`，网络失败/超时全部按可重试处理；默认超时从 60s 调短到 30s（服务端过载时挂起等 60s 太浪费）。
- **教训**：urllib 的异常体系有坑（超时不属于 URLError）；**网络 I/O 的异常处理要覆盖 HTTPError / URLError / TimeoutError / ConnectionError 四类**，并把超时纳入重试。

## 🛠 问题 3：scp -r 二次上传产生嵌套目录

- **现象**：第一次上传 llm_service 正常；第二次升级代码用同样的 `scp -r local/llm_service remote:llm_service_upload`，远程项目里变成了 `llm_service/llm_service/`（嵌套一层），升级安装后行为还是旧代码。
- **排查**：`ls -R` 发现嵌套。原因：scp -r 目标目录已存在时，会在目标下再建一层同名目录（`scp -r dir host:existing_dir` → `existing_dir/dir/`）；第一次目标不存在所以直接平铺。
- **解决**：把嵌套目录内容覆盖回顶层；后续上传改用**单文件 scp**（`scp local/llm_service.py host:fixed_name`）避免目录语义坑。
- **教训**：scp -r 到"已存在目录"和"不存在目录"行为不同；**重复上传同目录时先清中转目录或改用单文件传输**，并传完立刻 `ls -R` 验证结构。

## 🛠 问题 4：Ubuntu 24.04 系统 Python 被 PEP 668 保护

- **现象**：远程 WSL 里 `python3 -m pip install openai` 报 `error: externally-managed-environment`。
- **排查**：Ubuntu 24.04 的系统 Python 受 PEP 668 保护，不允许 pip 直接装包（防破坏系统环境）。
- **解决**：建独立虚拟环境 `/home/erp/venvs/llm`，用 `venv/bin/pip install openai`。Odoo 19 本身也是各带独立 venv（`odoo-19.0/venv`）。
- **教训**：Ubuntu 24.04+ 上装 Python 包**必须用 venv**（或 `--break-system-packages` 危险选项）；这也是工程最佳实践——每个项目一个虚拟环境，隔离依赖。

---

*本文件由真实开发过程整理，供社区参考。*
