# Odoo AI Journey

> 以 **Odoo 工程为背景**，系统学习大模型（LLM）的实战笔记与开源项目。
> Learning Large Language Models hands-on, **through the lens of Odoo ERP development**.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[English](README.md) | **中文**

## 为什么有这个项目

很多 LLM 教程（如上海交大《动手学大模型》）讲的是**模型原理与训练**，
而大多数开发者（包括作者）实际在做的是**把 LLM 集成进业务系统**——比如开源 ERP（Odoo）。

两者之间的桥——RAG、function calling、eval 测试集、异步推理、权限与安全——
恰恰是课程没讲、但生产开发天天要用的。

这个项目把两者合起来学：

1. 逐章整理《动手学大模型》的知识点（课程为经）
2. 每章映射到一个 **Odoo 真实业务场景**（Odoo 为纬）
3. 补充课程缺失的 **LLM 工程三件套**：RAG / function calling / eval

**作者背景**：正在系统学习 Python 与 AI/LLM 的开发者，在开源 ERP（Odoo）上做 AI Agent 开发。

## 当前进度（第 1–4 波已发布）

| 波次 | 交付 | 状态 |
|---|---|---|
| 1 | `llm_service` — Odoo 内生产级 LLM API 封装（配置化、零第三方依赖、429/5xx 重试 + 模型降级） | ✅ 真实调用已跑通 |
| 2 | `product_desc_generator` — 产品表单"AI 生成描述"按钮（few-shot → 弹窗确认/微调 → 写入 description_sale） | ✅ 真实 API 补测通过 |
| 3 | 双语 README — 本文件（中文） + `README.md`（英文） | ✅ 已发布 |
| 4 | `lead_extractor` — L2 结构化抽取：自由文本询盘 → 产品/数量/预算/交期/客户 → 弹窗预览 → 创建 `crm.lead`（few-shot 提示词 + 严格解析 + 自纠正） | ✅ mock + 真实 API 均通过 |

每一波都配套 `docs/logs/` 里的**真实踩坑日志**——踩过的坑和代码一样有价值。

## 目录结构

```
.
├── README.md                 # 项目介绍（英文版）
├── README.zh-CN.md           # 项目介绍（本文件，中文版）
├── LICENSE                   # MIT License
├── docs/                     # 全部知识笔记（Markdown）
│   ├── 00-roadmap.md         # 学习路线图 + 优先级矩阵
│   ├── 01-ch2-prompt-and-cot.md        # Ch2 提示学习与思维链 ★★★★★（已完成）
│   ├── 02-ch1-finetune-and-deploy.md   # Ch1 微调与部署
│   ├── 03-ch8-multimodal.md            # Ch8 多模态模型
│   ├── 04-ch6-jailbreak.md             # Ch6 越狱攻击
│   ├── 05-ch10-agent-safety-eval.md    # Ch10 智能体安全评估 ★★★★★
│   ├── 06-ch4-reasoning.md             # Ch4 数学推理
│   ├── 07-ch9-gui-agent.md             # Ch9 GUI 智能体
│   ├── 08-ch3-knowledge-editing.md     # Ch3 知识编辑
│   ├── 09-ch5-ch7-watermark-stego.md   # Ch5 水印 · Ch7 隐写
│   ├── 10-ch11-rlhf.md                 # Ch11 RLHF 对齐
│   ├── 11-engineering-toolkit.md       # 工程三件套：RAG / function calling / eval
│   ├── 12-publishing-workflow.md       # 逐章发布工作流（一章节一章节往上走）
│   └── 13-l2-structured-extraction.md  # L2 结构化抽取笔记 ✅
│   └── logs/                 # 真实踩坑日志（限流重试、Odoo 19 API 差异等）
├── odoo/                     # Odoo 实验模块
│   ├── README.md
│   ├── llm_service/          # 第 1 波：LLM API 统一封装（llm.service）
│   ├── product_desc_generator/  # 第 2 波：产品描述 AI 生成按钮
│   └── lead_extractor/       # 第 4 波：询盘 → 商机（L2 结构化抽取）
└── experiments/              # 验证脚本（Key 检测、冒烟测试、结构探查）
```

## 快速开始

**前置**：Odoo 19 源码环境（模块针对 Odoo 19 API），Python 3。

1. 把模块加入 addons 路径：
   ```ini
   # 你的 odoo.conf
   addons_path = ...,/path/to/odoo-ai-journey/odoo
   ```
2. 在开发库安装模块：
   ```bash
   odoo-bin -d <dev_db> -i llm_service,product_desc_generator,lead_extractor --stop-after-init
   ```
   > `lead_extractor` 依赖 `crm` 模块（会自动安装）。
3. 通过系统参数配置 API Key（不硬编码）：
   - `llm_service.api_key` — 你的 Key（智谱 BigModel / DeepSeek / 任意 OpenAI 兼容服务）
   - `llm_service.base_url` — 默认 `https://open.bigmodel.cn/api/paas/v4`
   - `llm_service.default_model` — 默认 `glm-4.7-flash`
   - `llm_service.models` — 备用模型列表（逗号分隔，429 时自动切换）
   - `llm_service.retries` / `llm_service.timeout` — 重试次数 / 超时
4. odoo shell 冒烟测试：
   ```bash
   odoo-bin shell -d <dev_db> --no-http < experiments/test_llm_service.py
   ```

> 免费 API（如智谱 GLM）高峰期可能持续 429——`llm_service` 内置指数退避重试 + 备用模型降级。详见 `docs/logs/2026-09-15-llm-service-限流重试.md`。

## 学习路径（建议顺序）

| 阶段 | 内容 | 对应笔记 |
|---|---|---|
| 1 · 立刻能用 | Ch2 提示学习与思维链 → 产品描述生成（已完成） | `docs/01-*.md` |
| 2 · 补齐工程 | RAG + function calling + eval（课程没讲） | `docs/11-engineering-toolkit.md` |
| 3 · ERP 刚需 | Ch8 多模态单据识别 · Ch1 文本分类 · Ch6 越狱安全 | `docs/03/02/04-*.md` |
| 4 · agent 上线 | Ch10 智能体评估 · 建风险测试集 | `docs/05-*.md` |
| 5 · 理解取舍 | Ch4 推理 · Ch9 GUI agent · Ch3 知识编辑 | `docs/06/07/08-*.md` |
| 6 · 扩展认知 | Ch5 水印 · Ch7 隐写 · Ch11 RLHF | `docs/09/10-*.md` |

优先级总览见 [`docs/00-roadmap.md`](docs/00-roadmap.md)。

## 路线图（Roadmap）

- [x] 知识框架与 11 章 × Odoo 映射整理
- [x] Ch2 + Odoo 模块：`llm_service` 封装（真实调用已跑通）
- [x] Ch2 + Odoo 模块：`product_desc_generator` 按钮（真实 API 补测通过）
- [x] L2 + Odoo 模块：`lead_extractor` 询盘 → 商机（真实 API 通过）
- [ ] 工程三件套 demo：自然语言查客户订单（RAG + function calling + eval）
- [ ] 多模态单据识别流水线（发票 / 合同 / 报关单）
- [ ] agent 安全测试集与权限白名单
- [ ] 拆文章发布：英文 → dev.to，中文 → 知乎

## 许可

[MIT License](LICENSE)
