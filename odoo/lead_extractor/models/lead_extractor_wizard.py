# -*- coding: utf-8 -*-
"""L2 · 业务写入层 — 询盘 → 商机（TransientModel 向导）。

交互形态（延续第 2 波产品描述的模式）：
1. 用户粘贴询盘原文 → 点「AI 抽取」
2. LLM 抽取 → 解析校验（失败自动自纠正一次）→ 回填只读预览字段
3. 用户核对/微调 → 点「创建商机」→ ORM create crm.lead（权限/审计照常）

复用边界：LLM 调用全部走 llm.service（第一次用 chat，自纠正用 _call_llm），
本层不关心 API 细节；提示词与解析是纯函数，写在独立模块便于单测。
"""
import json

from odoo import _, fields, models
from odoo.exceptions import UserError

from . import lead_parser
from . import lead_prompt


class LeadExtractorWizard(models.TransientModel):
    _name = "lead.extractor.wizard"
    _description = "AI 询盘抽取（结构化 → 商机）"

    raw_text = fields.Text(string="客户询盘文本", required=True)
    extracted = fields.Boolean(string="已抽取", default=False)

    product = fields.Char(string="产品", readonly=True)
    quantity = fields.Integer(string="数量", readonly=True)
    budget = fields.Float(string="预算（元）", readonly=True)
    deadline = fields.Date(string="期望交期", readonly=True)
    customer = fields.Char(string="客户/联系人", readonly=True)

    def action_extract(self):
        """第 1 步：LLM 抽取 → 解析校验 → 回填预览字段。"""
        self.ensure_one()
        raw = (self.raw_text or "").strip()
        if not raw:
            raise UserError(_("请先输入客户询盘文本。"))

        system, user = lead_prompt.build_prompt(raw)
        llm = self.env["llm.service"]
        try:
            text = llm.chat(user, system=system, temperature=0.0)
            data = lead_parser.parse_and_validate(text)
        except UserError:
            raise  # API 层错误（Key 无效/限流等）原样上抛
        except ValueError as exc:
            # 第一次解析失败 → 自纠正：把坏输出追加进对话再问一次
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ]
            fixed = lead_prompt.build_fix_messages(messages, text)
            try:
                text = llm._call_llm(fixed, temperature=0.0)
                data = lead_parser.parse_and_validate(text)
            except UserError:
                raise
            except ValueError as exc2:
                # 二次仍失败 → 交人工，绝不静默（展示原始输出便于排查）
                raise UserError(
                    _("AI 抽取结果无法解析：%s\n\n模型原始输出：\n%s") % (exc2, text)
                ) from exc

        self.product = data["product"]
        self.quantity = data["quantity"]
        self.budget = data["budget"] or 0.0
        self.deadline = data["deadline"] or False
        self.customer = data["customer"]
        self.extracted = True

        return {
            "type": "ir.actions.act_window",
            "res_model": self._name,
            "res_id": self.id,
            "view_mode": "form",
            "target": "new",
        }

    def action_create_lead(self):
        """第 2 步：核对预览后，把抽取结果写入 crm.lead（用户确认才落库）。"""
        self.ensure_one()
        if not self.extracted or not self.product:
            raise UserError(_("请先点击「AI 抽取」，确认抽取结果后再创建商机。"))

        vals = {
            "name": "询盘：%s ×%s" % (self.product, self.quantity or "?"),
            "expected_revenue": self.budget or 0.0,
            "description": (self.raw_text or "").strip(),
        }
        if self.deadline:
            vals["date_deadline"] = self.deadline
        if self.customer:
            partner = self.env["res.partner"].search(
                [("name", "=", self.customer)], limit=1
            )
            if partner:
                vals["partner_id"] = partner.id

        lead = self.env["crm.lead"].create(vals)

        return {
            "type": "ir.actions.act_window",
            "res_model": "crm.lead",
            "res_id": lead.id,
            "view_mode": "form",
            "target": "current",
        }
