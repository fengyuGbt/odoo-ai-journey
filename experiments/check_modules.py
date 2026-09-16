# -*- coding: utf-8 -*-
"""Check which modules are installed in the dev database."""
from odoo import api, SUPERUSER_ID

env = api.Environment(env.cr, SUPERUSER_ID, {})
for name in ("crm", "product", "llm_service", "product_desc_generator", "lead_extractor"):
    mod = env["ir.module.module"].search([("name", "=", name)], limit=1)
    if mod:
        print(f"{name}: state={mod.state}")
    else:
        print(f"{name}: NOT FOUND")
