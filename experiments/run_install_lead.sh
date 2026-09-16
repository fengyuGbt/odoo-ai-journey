#!/bin/bash
# Install crm + lead_extractor into dev_llm
cd /home/erp/odoo-19.0
cp /home/erp/odoo-ai-journey/experiments/test_lead_extractor.py /home/erp/test_lead_extractor.py
cp /home/erp/odoo-ai-journey/experiments/run_lead_test.sh /home/erp/run_lead_test.sh
./venv/bin/python ./odoo-bin -c /home/erp/dev_llm.conf -d dev_llm -i crm,lead_extractor --stop-after-init --logfile /home/erp/install_lead_extractor.log
echo "INSTALL_EXIT=$?"
tail -5 /home/erp/install_lead_extractor.log
