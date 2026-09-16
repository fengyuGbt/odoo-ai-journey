# -*- coding: utf-8 -*-
"""Find crm-related menu external ids."""
from odoo import api, SUPERUSER_ID

env = api.Environment(env.cr, SUPERUSER_ID, {})
menus = env["ir.ui.menu"].search(
    [("name", "ilike", "crm"), ("parent_id", "=", False)]
)
for m in menus:
    xids = env["ir.model.data"].search(
        [("model", "=", "ir.ui.menu"), ("res_id", "=", m.id)]
    )
    for x in xids:
        print(f"TOP MENU: {x.module}.{x.name} -> {m.name}")

# also search any menu with 'crm' in module
menus2 = env["ir.ui.menu"].search([("name", "ilike", "商机")], limit=10)
for m in menus2:
    xids = env["ir.model.data"].search(
        [("model", "=", "ir.ui.menu"), ("res_id", "=", m.id)]
    )
    for x in xids:
        print(f"LEAD MENU: {x.module}.{x.name} -> {m.name} (parent={m.parent_id.name if m.parent_id else None})")
