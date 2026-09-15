#!/bin/bash
cd /home/erp/odoo-19.0
/home/erp/odoo-19.0/venv/bin/python odoo-bin shell -d dev_llm -c /home/erp/dev_llm.conf --no-http < /home/erp/list_modules.py
