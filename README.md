# Odoo AI Journey

> 以 **Odoo 工程为背景**，系统学习大模型（LLM）的实战笔记与开源项目。
> Learning Large Language Models hands-on, **through the lens of Odoo ERP development**.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

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

## 学习路径（建议顺序）

| 阶段 | 内容 | 对应笔记 |
|---|---|---|
| 1 · 立刻能用 | Ch2 提示学习与思维链 → 做 Odoo 产品描述生成 | `docs/01-*.md` |
| 2 · 补齐工程 | RAG + function calling + eval（课程没讲） | `docs/11-engineering-toolkit.md` |
| 3 · ERP 刚需 | Ch8 多模态单据识别 · Ch1 文本分类 · Ch6 越狱安全 | `docs/03/02/04-*.md` |
| 4 · agent 上线 | Ch10 智能体评估 · 建风险测试集 | `docs/05-*.md` |
| 5 · 理解取舍 | Ch4 推理 · Ch9 GUI agent · Ch3 知识编辑 | `docs/06/07/08-*.md` |
| 6 · 扩展认知 | Ch5 水印 · Ch7 隐写 · Ch11 RLHF | `docs/09/10-*.md` |

优先级总览见 [`docs/00-roadmap.md`](docs/00-roadmap.md)。

## 目录结构

```
.
├── README.md                 # 项目介绍（本文件）
├── LICENSE                   # MIT License
├── docs/                     # 全部知识笔记（Markdown）
│   ├── 00-roadmap.md         # 学习路线图 + 优先级矩阵
│   ├── 01-ch2-prompt-and-cot.md        # Ch2 提示学习与思维链 ★★★★★
│   ├── 02-ch1-finetune-and-deploy.md   # Ch1 微调与部署
│   ├── 03-ch8-multimodal.md            # Ch8 多模态模型
│   ├── 04-ch6-jailbreak.md             # Ch6 越狱攻击
│   ├── 05-ch10-agent-safety-eval.md    # Ch10 智能体安全评估 ★★★★★
│   ├── 06-ch4-reasoning.md             # Ch4 数学推理
│   ├── 07-ch9-gui-agent.md             # Ch9 GUI 智能体
│   ├── 08-ch3-knowledge-editing.md     # Ch3 知识编辑
│   ├── 09-ch5-ch7-watermark-stego.md   # Ch5 水印 · Ch7 隐写
│   ├── 10-ch11-rlhf.md                 # Ch11 RLHF 对齐
│   └── 11-engineering-toolkit.md       # 工程三件套：RAG / function calling / eval
│   └── 12-publishing-workflow.md       # 逐章发布工作流（一章节一章节往上走）
└── odoo/                     # Odoo 实验模块（规划与代码，逐步补充）
    └── README.md
```

## 如何学习（给读者）

- 按 `docs/00-roadmap.md` 的顺序读，每章笔记结构统一：
  **这一章在讲什么 → Odoo 落地场景 → 工程要点 → 动手任务**
- 笔记里的「动手任务」都设计成可在 Odoo 社区版上完成的小功能
- 建议配合 [上海交大《动手学大模型》](https://github.com/Lordog/dive-into-llms) 原课程阅读

## 路线图（Roadmap）

- [x] 知识框架与 11 章 × Odoo 映射整理
- [ ] Ch2 + Odoo 产品描述生成模块（`llm.service` 封装）
- [ ] 工程三件套 demo：自然语言查客户订单（RAG + function calling + eval）
- [ ] 多模态单据识别流水线（发票 / 合同 / 报关单）
- [ ] agent 安全测试集与权限白名单
- [ ] 拆文章发布：英文 → dev.to，中文 → 知乎

## 许可

[MIT License](LICENSE)
