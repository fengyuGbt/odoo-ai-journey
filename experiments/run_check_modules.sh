#!/bin/bash
# Check installed modules in dev_llm
cd /home/erp/odoo-19.0
./venv/bin/python ./odoo-bin shell -c /home/erp/dev_llm.conf -d dev_llm --no-http < /home/erp/check_modules.py 2>&1 | grep -v "^$"
