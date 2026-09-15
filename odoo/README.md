# Odoo 实验模块（规划中）

> 这里是知识笔记对应的 **Odoo 实验模块** 存放处。每个模块对应一条学习路线上的里程碑任务。
> 目前为规划状态，代码随学习进度逐步补充。

## 模块规划

| 模块名 | 对应笔记 | 功能 | 状态 |
|---|---|---|---|
| `llm_service` | Ch2 / 工程三件套 | LLM API 统一封装（Key 管理、chat、重试降级） | 🚧 第一版已跑通（2026-09-15） |
| `product_desc_generator` | Ch2 | 产品描述自动生成按钮（`product.template`） | ⬜ 规划 |
| `order_agent` | 工程三件套 | 自然语言查客户订单（RAG + function calling + eval） | ⬜ 规划 |
| `doc_ocr` | Ch8 | 发票/合同识别流水线（附件 → 视觉 API → 预填） | ⬜ 规划 |
| `message_classifier` | Ch1 | 邮件/工单自动分类（异步 + 降级） | ⬜ 规划 |
| `agent_eval` | Ch10 / Ch6 | 风险测试集 + 回归执行 + 越狱用例 | ⬜ 规划 |

## 每个模块的标准结构

```
<module_name>/
├── __manifest__.py          # 模块声明（依赖、数据文件）
├── models/
│   ├── __init__.py
│   └── *.py                 # 模型与业务逻辑
├── data/
│   └── *.xml                # 种子数据（prompt 模板、测试用例、权限）
├── security/
│   ├── ir.model.access.csv  # 模型权限
│   └── record_rules.xml     # 行级权限（LLM 调用的兜底）
├── views/
│   ├── *.xml                # 界面（按钮、看板、对话框）
│   └── *.py 或 *.js         # 前端逻辑（如有）
└── tests/
    └── test_*.py            # Odoo 自带测试（配合 eval 测试集）
```

## 环境要求（参考）

| 组件 | 建议 |
|---|---|
| Odoo | 社区版 17+（`pip install odoo` 或 Docker） |
| 数据库 | PostgreSQL 14+（RAG 用 pgvector 扩展） |
| Python | 3.10+ |
| LLM API | 任意 OpenAI 兼容接口（豆包 / OpenAI / DeepSeek…） |

## 通用设计约定

1. **`llm.service` 是唯一入口**：所有模块调 LLM 都走它，不直接散落 API 调用
2. **权限最小化**：LLM 相关调用走受限用户 + record rules 兜底（见 Ch6 笔记）
3. **异步优先**：耗时调用走 `queue_job`，不阻塞界面（见 Ch1 笔记）
4. **可评估**：每个功能配 eval 测试集（见 Ch10 笔记）
5. **留痕**：AI 自动生成/修改的数据记录来源字段（见 Ch5 笔记）

> 说明：模块代码会随学习进度逐个实现并提交。实现顺序建议：
> `llm_service` → `product_desc_generator` → `order_agent` → 其余。
