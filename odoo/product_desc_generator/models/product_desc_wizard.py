# -*- coding: utf-8 -*-
"""产品描述确认弹窗（TransientModel）：人审环节，确认/微调后写库。"""

from odoo import fields, models


class ProductDescWizard(models.TransientModel):
    _name = "product.desc.wizard"
    _description = "AI 生成产品描述确认"

    product_id = fields.Many2one("product.template", string="产品", readonly=True)
    generated_text = fields.Text(string="生成描述", required=True)

    def action_write_desc(self):
        """确认写入：把弹窗里（可能被用户微调过的）文本写入 description_sale。"""
        self.ensure_one()
        self.product_id.description_sale = self.generated_text
        return {"type": "ir.actions.act_window_close"}
