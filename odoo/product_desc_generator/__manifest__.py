# -*- coding: utf-8 -*-
{
    "name": "Product Desc Generator",
    "version": "19.0.1.0.0",
    "category": "AI",
    "summary": "AI 生成产品销售描述（llm.service + 人审确认）",
    "description": """
Product Desc Generator
======================
对应《动手学大模型》Ch2 少样本概念的 Odoo 落地：产品表单加"AI 生成描述"按钮，
调用 llm.service 生成描述，弹窗确认/微调后写入 description_sale 字段。

链路（模式1 + 模式2 组合）：
- 读库：从 product.template 取产品名称 + 属性
- 生成：拼 few-shot 提示词（示例来自 Ch2 测试），调 llm.service.chat()
- 人审：弹窗展示生成结果，可修改
- 写库：确认后写入 description_sale

已知限制（v0.1）：
- 生成是同步调用，高峰期可能等待数秒（异步化留待 queue_job 方案）
- few-shot 示例暂硬编码在代码，后续抽成数据库模板（ir.model.data）
""",
    "author": "odoo-ai-journey contributors",
    "website": "https://github.com/fengyuGbt/odoo-ai-journey",
    "license": "LGPL-3",
    "depends": ["product", "llm_service"],
    "data": [
        "security/ir.model.access.csv",
        "views/product_template_views.xml",
        "views/product_desc_wizard_views.xml",
    ],
    "installable": True,
    "application": False,
}
