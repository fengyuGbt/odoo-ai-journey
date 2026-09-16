#!/bin/bash
# lead_extractor 全链路测试（mock LLM）
cd /home/erp/odoo-19.0
./venv/bin/python ./odoo-bin shell -c /home/erp/dev_llm.conf -d dev_llm --no-http < /home/erp/test_lead_extractor.py 2>&1 | grep -v "^$"
