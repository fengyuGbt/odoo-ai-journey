# 工程前史 · odoo-ai-agent 踩坑精华（2026-09-15）

> 本文件整理自作者此前开发的 **odoo-ai-agent** 项目（Odoo「AI 操作层」外部服务）的实战记录，脱敏后收录为 odoo-ai-journey 的工程前史。
> 价值：这些坑是"在 Odoo 上做自动化/AI 开发"的真实学费，llm_service 模块开发时先看本文件可避开大部分。
> 说明：文中 `<user>`、`<repo>` 等为脱敏占位；密码、密钥、内网地址一律不收录。

---

## 背景：odoo-ai-agent 是什么

- 定位：给 Odoo 加「AI 操作层」——**外部独立 Python 服务**，通过 odoorpc（Odoo XML-RPC 封装）操作 Odoo，**不是**把 AI 嵌进 Odoo 模块。
- 核心理念：**AI 跑流程、人做判断**。每个写操作（增/改/删/流程按钮）都停在「权限门」前进入 PENDING，等人明确批准才执行；动作前先用 OCA tier 审批规则（base_tier_validation）预检；每个动作写入 append-only JSONL 审计日志。
- 交付：8 个流程 Agent（销售/采购/需求/收货/付款/生产/出货/物流）+ 1 个经营监控 Agent；WSL 源码开发 + Docker Compose 交付双轨制。
- 与 odoo-ai-journey 的关系：odoo-ai-agent 缺的正是 **LLM 决策内核**（当时全部是确定性规则脚本）。本项目的课程学习路线（Ch2 提示工程 → llm.service → 评估）就是补这块的路径。前史踩坑直接适用于本项目。

---

## 一、架构决策记录（为什么这么设计）

| 决策 | 理由 | 对 odoo-ai-journey 的启示 |
|---|---|---|
| AI 操作层外置（odoorpc API）而非模块内嵌 | 与 Odoo 解耦：升级 Odoo 不影响 AI 层；AI 故障不拖垮 ERP；不依赖具体版本 | llm.service 做**模块内**能力，两种架构可共存：业务内 AI（本模块）vs 流程 Agent（外部服务） |
| 权限门：所有写操作必须人批准 | AI 输出不可信，流程关键步骤必须有人的判断兜底 | 这正是课程 Ch6"LLM 不可信需兜底"思想的工程实现，可作课程×工程的招牌案例 |
| tier 预检（OCA base_tier_validation） | 复用 Odoo 生态现成审批规则，不重复造轮子 | 集成优先 OCA 生态，模块能挂 OCA 就挂 |
| 审计 JSONL append-only | 全动作留痕，可追溯、可复盘 | LLM 调用日志也应 append-only，记录 prompt/输出/耗时/成本 |
| 双轨制：WSL 源码开发 + Docker 交付 | 开发快、交付标准化 | 本项目沿用：WSL 开发验证，发布到 GitHub 供他人 Docker 部署 |

---

## 二、Odoo 19 API 差异（最重要的避坑清单）

> 开发 llm_service 模块（Odoo 19）前必读。以下是 Odoo 19 与旧版/Odoo 16-17 的差异：

1. **odoorpc 0.10.1 类名大写**：`from odoorpc import ODOO`（不是 `odoo`）。
2. **create 返回 int id**：`Model.create()` 直接返回记录 id（int），不是 recordset。
3. **Model.browse() 触发 NewId 问题**：跨进程 browse 的 recordset 可能触发 NewId 异常；权限门调用改用 `execute_kw` 传 `ids` 列表，避免 browse 后回调。
4. **res.users.groups_id → group_ids**：字段名变了（groups_id 已废弃）。
5. **res.groups.users → all_user_ids**：反向关联字段名变化。
6. **manifest 版本号格式**：模块 `__manifest__.py` 的 version 字段应为 `19.0.*`。
7. **搜索视图 `<group expand>` 删除**：Odoo 19 中该属性移除，搜索结果视图写法需调整。
8. **picking 取消用 action_cancel**（不是 button_cancel）；入库/发货确认用 **button_validate**。
9. **生产单（MO）action_confirm 在未装工单模块时直接进入 done**：流程断言要考虑这个差异。
10. **账单过账前必须有 invoice_date**：否则报错。
11. **付款单过账后状态为 in_process**（不是 posted）。
12. **已 done 的 picking 不能 unlink**：留痕优先，清理演示数据用专门脚本（cleanup_demo 系列）。

**教训**：Odoo 每大版本 API 都在变，写代码前先查目标版本的官方迁移说明；测试断言不要依赖"旧版行为"。

---

## 三、WSL 运维坑（远程开发环境）

1. **ssh 会话结束后 WSL 被空闲关闭**（~60s）：PG 崩溃恢复会被打断。`.wslconfig` 的 `vmIdleTimeout` 在 Win10 无效 → 用 Windows 计划任务 KeepWSLAlive 保活。
2. **普通 nohup 启动 Odoo 挂在 ssh 会话上会被杀**：必须 `setsid` 脱离会话 + `</dev/null` + `disown`，否则 ssh 一关进程就死。
3. **--dev=xml 热重载用错 python 会崩溃**：启动脚本里去掉 `--dev=xml`，或确保用 venv 的 python。
4. **shell 多层传递坑**：ssh → Windows cmd → WSL → bash 层层转义，`bash -lc`、管道、`pipefail`、PowerShell 吃 `&&` 和引号都会出问题。**复杂命令写 .sh 文件上传后执行**，不要现场拼长命令。
5. **PEP 668（Ubuntu 24.04）**：系统 Python 直接 `pip install` 被拒，必须用 venv。llm_service 实验环境用 `/home/<user>/venvs/llm` 这类独立 venv。

---

## 四、网络与发布坑（GitHub 链路）

1. **github.com:443 直连被阻断，但 api.github.com 通**：git push 走不通时，可用纯 urllib 调 Git Data REST API 推送（读 gh CLI 的 oauth token）。这是网络受限环境的变通方案，正式环境用正常 git push。
2. **镜像站差异**：gh-proxy.com 可克隆不可 push；部分镜像完全不通。克隆失败换镜像，别硬试。
3. **SSH key 缺 scope**：GitHub SSH key 缺 admin:public_key 等 scope 时部分操作走不通 → 优先 HTTPS + token。
4. **发布平台新人限制**：HN 新账号受 /showlim 限制（需养号攒 karma）；Reddit 新号发帖被自动筛选器移除且不能申诉；r/Odoo 版规禁 promotion 和 AI generated content。**首发选 Odoo 官方论坛 / OCA Discord / t.me 群**（新号可发、即时）。

---

## 五、Docker 交付坑

1. **ssh 直接启动 GUI / docker pull 会被 job object 杀**（Windows 用户态 Docker Desktop）：必须用 schtasks 在桌面会话跑，否则进程被回收。
2. **scp 拍平同名覆盖**：`scp addons/README.md` 曾覆盖根 `README.md`。同名文件传输要确认目标路径，或用不同文件名。
3. compose 交付时 Web 端口与源码开发端口错开（如 8069 / 8070），避免本地冲突。

---

## 六、对 odoo-ai-journey 的启示（怎么用这份前史）

1. **llm_service 模块开发时对照 §二**：Odoo 19 API 差异直接适用，省去踩坑时间。
2. **权限门 = 课程 Ch6 的工程化落地**：写进 Ch6 笔记时引用此设计，"AI 提建议、人做判断"是最好的安全故事。
3. **日志规范**：LLM 调用日志设计为 append-only，记录 prompt / 输出 / 耗时 / 用量——审计思想从第一天做起。
4. **远程开发链路**：本地整理 → 打包上传远程台式机 → WSL 内操作（git/venv/脚本）→ 发布。链路细节见本文件 §三、§四。
5. **发布渠道预研**：本项目后续推广（dev.to / 知乎）不受 HN/Reddit 新号限制影响，但开源社区的"养号期"经验仍适用。

---

*本文件所有凭据、密码、内网地址均已脱敏。原文完整版见作者本地交接文档，不进入公开仓库。*
