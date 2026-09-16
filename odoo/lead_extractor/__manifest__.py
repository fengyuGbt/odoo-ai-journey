{
    "name": "Lead Extractor (AI)",
    "version": "0.1.0",
    "category": "Sales/CRM",
    "summary": "Extract structured lead data from customer inquiry text via LLM",
    "description": """
L2 · 结构化抽取 — 询盘 → 商机

把客户询盘/邮件原文交给 LLM，抽取 {product, quantity, budget, deadline, customer}
结构化字段，预览确认后创建 Odoo 商机（crm.lead）。

新增三块（对应 L2 知识点）：
- 提示词模板（models/lead_prompt.py）：system 立规矩 + few-shot 示范
- 解析校验（models/lead_parser.py）：json.loads + schema 校验，失败自纠正
- 业务写入（models/lead_extractor_wizard.py）：映射到 crm.lead，弹窗确认后落库

复用：llm.service（第 1 波封装）原样复用，一行不改。
    """,
    "depends": ["base", "crm", "llm_service"],
    "data": [
        "security/ir.model.access.csv",
        "views/lead_extractor_views.xml",
    ],
    "license": "LGPL-3",
    "installable": True,
    "application": False,
    "auto_install": False,
}
