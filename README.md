# Odoo AI Journey

> Hands-on notes and an open-source project for learning Large Language Models (LLMs) **through the lens of Odoo ERP development**.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**English** | [中文](README.zh-CN.md)

---

## Why this project

Most LLM tutorials (such as SJTU's [*Dive into LLMs*](https://github.com/Lordog/dive-into-llms)) focus on **model fundamentals and training**. But most developers (including the author) are actually **integrating LLMs into business systems** — like the open-source ERP, Odoo.

The bridge between the two — RAG, function calling, eval sets, async inference, permissions & security — is exactly what the course doesn't cover but production development needs every day.

This project learns both at once:

1. **Course as warp**: chapter-by-chapter notes for *Dive into LLMs*
2. **Odoo as weft**: each chapter mapped to a real Odoo business scenario
3. **Engineering toolkit**: fills the gaps the course misses — RAG / function calling / eval

**Author background**: a developer systematically learning Python & AI/LLM, building AI Agent features on Odoo.

## Status (Wave 1 & Wave 2 shipped)

| Wave | Deliverable | Status |
|---|---|---|
| 1 | `llm_service` — production-grade LLM API wrapper for Odoo (config-driven via `ir.config_parameter`, zero third-party deps, 429/5xx retry + model fallback) | ✅ Tested live |
| 2 | `product_desc_generator` — "AI Generate Description" button on product form (few-shot prompt → wizard preview/edit → write `description_sale`) | 🚧 Logic chain tested (mocked), live API pending off-peak retest |

Every wave ships with real **pitfall logs** in `docs/logs/` — the failures are as valuable as the code.

## Repository layout

```
.
├── README.md                 # Project intro (this file, English)
├── README.zh-CN.md           # 中文版项目介绍
├── LICENSE                   # MIT License
├── docs/                     # All knowledge notes (Markdown)
│   ├── 00-roadmap.md         # Learning roadmap + priority matrix
│   ├── 01-ch2-prompt-and-cot.md        # Ch2 Prompting & CoT ★★★★★ (completed)
│   ├── 02-ch1-finetune-and-deploy.md   # Ch1 Fine-tuning & deployment
│   ├── 03-ch8-multimodal.md            # Ch8 Multimodal models
│   ├── 04-ch6-jailbreak.md             # Ch6 Jailbreak attacks
│   ├── 05-ch10-agent-safety-eval.md    # Ch10 Agent safety & eval ★★★★★
│   ├── 06-ch4-reasoning.md             # Ch4 Math reasoning
│   ├── 07-ch9-gui-agent.md             # Ch9 GUI agents
│   ├── 08-ch3-knowledge-editing.md     # Ch3 Knowledge editing
│   ├── 09-ch5-ch7-watermark-stego.md   # Ch5 Watermarking · Ch7 Steganography
│   ├── 10-ch11-rlhf.md                 # Ch11 RLHF alignment
│   ├── 11-engineering-toolkit.md       # RAG / function calling / eval
│   ├── 12-publishing-workflow.md       # Wave-by-wave publishing workflow
│   └── logs/                 # Real pitfall logs (rate-limit, Odoo 19 API diffs, ...)
├── odoo/                     # Odoo experiment modules
│   ├── README.md
│   ├── llm_service/          # Wave 1: LLM API wrapper (llm.service)
│   └── product_desc_generator/  # Wave 2: AI product description button
└── experiments/              # Verification scripts (key check, smoke tests, probes)
```

## Quick start

**Prerequisites**: Odoo 19 source environment (the module targets Odoo 19 APIs), Python 3.

1. Put the modules on your addons path:
   ```ini
   # in your odoo.conf
   addons_path = ...,/path/to/odoo-ai-journey/odoo
   ```
2. Install the modules on a dev database:
   ```bash
   odoo-bin -d <dev_db> -i llm_service,product_desc_generator --stop-after-init
   ```
3. Configure your LLM API key via system parameters (no hardcoding):
   - `llm_service.api_key` — your key (Zhipu BigModel / DeepSeek / any OpenAI-compatible service)
   - `llm_service.base_url` — default `https://open.bigmodel.cn/api/paas/v4`
   - `llm_service.default_model` — default `glm-4.7-flash`
   - `llm_service.models` — comma-separated fallback models (auto-switch on 429)
   - `llm_service.retries` / `llm_service.timeout` — retry count / timeout
4. Smoke test from the odoo shell:
   ```bash
   odoo-bin shell -d <dev_db> --no-http < experiments/test_llm_service.py
   ```

> Free-tier APIs (e.g. Zhipu GLM) can hit sustained 429s during peak hours — the `llm_service` wrapper retries with exponential backoff and falls back to a secondary model. See `docs/logs/2026-09-15-llm-service-限流重试.md`.

## Learning path (recommended order)

| Stage | Content | Notes |
|---|---|---|
| 1 · Usable today | Ch2 Prompting & CoT → product description generator | `docs/01-*.md` |
| 2 · Engineering | RAG + function calling + eval (not in the course) | `docs/11-engineering-toolkit.md` |
| 3 · ERP essentials | Ch8 multimodal document parsing · Ch1 text classification · Ch6 jailbreak safety | `docs/03/02/04-*.md` |
| 4 · Agent to prod | Ch10 agent evaluation · build a risk eval set | `docs/05-*.md` |
| 5 · Understand trade-offs | Ch4 reasoning · Ch9 GUI agents · Ch3 knowledge editing | `docs/06/07/08-*.md` |
| 6 · Broader view | Ch5 watermarking · Ch7 steganography · Ch11 RLHF | `docs/09/10-*.md` |

Priority overview: [`docs/00-roadmap.md`](docs/00-roadmap.md).

## Roadmap

- [x] Knowledge framework + 11-chapter × Odoo mapping
- [x] Ch2 + Odoo module: `llm_service` wrapper (live-tested)
- [x] Ch2 + Odoo module: `product_desc_generator` button (logic tested, live API pending retest)
- [ ] Engineering toolkit demo: natural-language customer order lookup (RAG + function calling + eval)
- [ ] Multimodal document parsing pipeline (invoices / contracts / customs forms)
- [ ] Agent safety eval set & permission whitelist
- [ ] Publish chapters: English → dev.to, Chinese → Zhihu

## License

[MIT License](LICENSE)
