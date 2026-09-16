#!/bin/bash
cd /home/erp/odoo-19.0
./venv/bin/python ./odoo-bin shell -c /home/erp/dev_llm.conf -d dev_llm --no-http < /home/erp/find_crm_menu.py 2>&1 | grep "MENU" 
