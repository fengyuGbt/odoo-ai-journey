# L2 结构化抽取 · 从"生成文本"到"驱动业务流程"

> 课程关联：Ch2 提示工程实战延伸（结构化输出 / few-shot / 自纠正）+ 工程三件套之 function calling 前置
> Odoo 关联：`crm.lead`（商机）· `lead_extractor` 模块
> 优先级：★★★★★ 生产价值最高的一层
> 状态：✅ 已完成（第 4 波 `lead_extractor`，mock 全链路验证通过；真实 API 测试脚本就绪，待 API 稳定时段补测）

## 这一节在讲什么

L1 让 LLM **帮你写**（文本 → 文本，人读、人判断），L2 让 LLM **替系统干活**：
把非结构化输入（询盘 / 邮件 / 备注）变成机器可直接消费的**结构化数据**，直接驱动业务流程。

**三个核心知识点（L2 的工程内核）：**

1. **约束输出**：给模型 few-shot 示例 + schema 声明，把输出"框"成可解析的 JSON
   —— 这是 Ch2 提示工程（角色设定 + 少样本）的实战延伸，不是新概念
2. **严格校验**：LLM 输出不可信。必须 `json.loads` + schema 校验
   （必填字段 / 类型 / 空值规则），校验不过就重试，**绝不直接写库**
3. **失败兜底**：自纠正 → 降级模型 → 交人工确认，三层兜底。
   —— 这是"LLM 进生产系统"的第一原则，Odoo 里就是 `UserError` + wizard 确认

> 关键认知：**LLM 的输出永远是"可能出错"的草稿**。让它驱动业务流程的前提不是"让它更聪明"，
> 而是"在它出错时系统不会坏"——解析校验层就是这道保险。

## Odoo 落地场景

| 功能 | Odoo 模型 | 一句话说明 |
|---|---|---|
| 询盘 → 商机（**本次实现**） | `crm.lead` | 客户询盘文本 → 抽取产品/数量/预算/交期/客户 → 自动建商机草稿 |
| 报价单字段抽取 | `sale.order` | 从客户报价要求里抽取数量/单价/条款生成报价草稿 |
| 供应商邮件归档 | `res.partner` + `mail.thread` | 抽取出货期/价格/联系人，结构化进供应商档案 |
| 发票要素抽取 | `account.move` | 从 PDF/邮件抽发票号/金额/税号（L3 多模态的前置） |

## 工程要点（Odoo 侧）

### 三块新增 vs 一块复用

| 层 | 职责 | 形态 | 是否 Odoo 专属 |
|---|---|---|---|
| ① 提示词模板 | 输入 + 约束 → `(system, user)` 两段文本 | 纯函数，可脱离 Odoo 单测 | 否，但 schema 字段映射到 Odoo 模型 |
| ② 解析校验 | 模型文本 → 可信 dict | 纯函数，可脱离 Odoo 单测 | 否 |
| ③ 业务写入 | dict → `crm.lead` | TransientModel 向导（弹窗预览 → 确认 → ORM create） | 是 |
| 🔵 llm.service | messages → 文本（鉴权/重试/降级） | 第 1 波封装，**一行不改** | 通用 |

### llm.service 为什么能原样复用（抽象边界）

它管的是**通信协议**（怎么把消息送出去、出错怎么办），不管**业务语义**（消息里装什么）：

1. **接口契约稳定**：`chat(prompt, system=...)` / `_call_llm(messages)` 输入输出类型不变
2. **无业务状态**：AbstractModel，不存业务字段，无状态调用
3. **失败策略通用**：429 重试、模型降级、错误翻译——任何 LLM 调用都需要，与业务无关

比喻：llm.service 是**快递公司**（只管送达、坏了重送、换路线）；提示词模板是打包的人（装什么）、
解析校验是收货验货（对不对）、业务写入是摆上货架（进 Odoo）。

### 本次接法的两个细节

- 单轮抽取：`llm.chat(user, system=system, temperature=0.0)` —— `chat` 原生支持 system+user 两段，
  提示词模板零改动接入
- 自纠正（多轮对话）：`llm._call_llm(messages)` 传完整消息列表（system + user + assistant(坏输出) + user(修正指令)）
  —— 仍是同一封装入口，鉴权/重试/降级全继承

### 交互模式（延续第 2 波）

**AI 生成 = 草稿，用户确认才落库**：先弹窗预览抽取结果（可核对）→ 点"创建商机"才 `create`。
LLM 永不直接写业务数据，决定权永远在人。

## 动手任务

- [x] `lead_extractor` 模块（提示词模板 / 解析校验 / 向导 / 视图 / ACL，8 文件）
- [x] mock 全链路测试（正常抽取 / 建商机 / 自纠正 / 二次失败不静默 / 解析 / 提示词）
- [x] 真实 API 测试脚本就绪（`test_lead_extractor_real.py`，待稳定时段补跑）
- [ ] 收集模型"坏输出"样本，做结构化抽取的失败率统计（为 eval 打基础）
- [ ] 用 CRM 历史询盘替换示例样本，对比抽取准确率

## 🛠 实测记录（2026-09-16）

**环境**：Odoo 19（WSL，dev 库 `dev_llm`）；新增依赖 `crm` 模块；智谱 GLM-4.7-Flash 免费 API。

**1. mock 全链路 ✅**（`test_lead_extractor.py`，类级 monkeypatch）
```
EXTRACT OK: 无线鼠标 ×300 ¥10000.0 交期=2026-10-15
CREATE LEAD OK: id=2 name=询盘：无线鼠标 ×300 revenue=10000.0
SELF-CORRECT OK          # chat 返回残缺 JSON → 自纠正成功
USERERROR OK             # 二次失败 → UserError 展示 schema 错误 + 原始输出
PARSER OK / REJECT OK    # markdown 围栏清洗 + 缺字段拒绝
=== ALL TESTS PASSED ===
```

**2. 真实 API（第 2 波同链路已验证 ✅）**：`product_desc_generator` 真实补测通过
（生成描述 → 微调 → 写库 MATCH: True），证明 `llm.service` 真实链路可用；
`lead_extractor` 真实抽取待 API 稳定时段补跑。

**3. 踩坑记录**（详见 `docs/logs/2026-09-16-lead-extractor-踩坑.md`）：
- Odoo 19 CRM 主菜单 external id：`crm.menu_crm_root` → **`crm.crm_menu_root`**（跨版本别信记忆，先查库）
- Odoo 模型方法只读：`model.method = fake` 报 read-only；`_patch_method` 不存在
  → 用**类级 monkeypatch**（`import ...llm_service as m; m.LLMService.chat = fake`，finally 恢复）
- 测试脚本自己漏 `from odoo.exceptions import UserError` → NameError（不是模块的锅）

## 核心代码骨架

```python
# ① 提示词模板（纯函数）：system 立规矩 + user 给 few-shot 示范和真实输入
system, user = lead_prompt.build_prompt(raw_text)
# system = "你是 Odoo 销售助理…字段定义…无法确定填 null，不要编造"
# user   = "示例输入：…\n期望输出：{…}\n\n真实输入：{raw_text}"

# ② LLM 调用（复用 llm.service，一行不改）
text = llm.chat(user, system=system, temperature=0.0)

# ③ 解析校验（纯函数）：清洗 → json.loads → schema 校验
data = lead_parser.parse_and_validate(text)   # 失败 → ValueError → 自纠正

# ④ 自纠正（多轮 messages，走 _call_llm）
fixed = lead_prompt.build_fix_messages(messages, bad_output)
text = llm._call_llm(fixed, temperature=0.0)

# ⑤ 业务写入（用户确认后 ORM create，权限/审计照常）
lead = self.env["crm.lead"].create(vals)
```
