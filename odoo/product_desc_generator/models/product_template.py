# -*- coding: utf-8 -*-
"""product.template 继承：AI 生成描述按钮的入口方法。"""

from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    def action_generate_desc(self):
        """按钮入口：拼 few-shot 提示词 → 调 llm.service → 弹窗让用户确认。

        数据流（模式1 + 模式2 组合）：
        读库（self 是当前产品记录）→ 生成（llm.service.chat）→
        人审（TransientModel 弹窗）→ 确认后写库（wizard.action_write_desc）
        """
        self.ensure_one()
        prompt = self._build_desc_prompt()
        text = self.env["llm.service"].chat(prompt, temperature=0.7)
        wizard = self.env["product.desc.wizard"].create(
            {"product_id": self.id, "generated_text": text}
        )
        return {
            "name": "AI 生成产品描述",
            "type": "ir.actions.act_window",
            "res_model": "product.desc.wizard",
            "res_id": wizard.id,
            "view_mode": "form",
            "target": "new",
            "context": dict(self.env.context),
        }

    def _build_desc_prompt(self):
        """拼 few-shot 提示词：用产品名称 + 属性，示例来自 Ch2 少样本测试。"""
        attrs = ", ".join(self.attribute_line_ids.mapped("value_ids.name")) or "无特殊属性"
        return (
            "你是电商文案专家。根据产品信息生成不超过 80 字的中文销售描述。\n"
            "示例1：\n"
            "产品：可乐 330ml\n"
            "描述：经典碳酸饮料，330ml 易拉罐装，冰镇后口感更佳，聚会畅饮首选。\n"
            "示例2：\n"
            "产品：汉堡\n"
            "描述：现做牛肉汉堡，松软面包配多汁肉饼，分量足，出餐快，工作日午餐优选。\n"
            "现在生成：\n"
            "产品：%s（%s）\n"
            "描述：" % (self.name, attrs)
        )
