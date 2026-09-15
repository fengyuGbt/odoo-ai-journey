#!/bin/bash
# 运行 llm_service 冒烟测试（odoo shell 非交互模式，使用 dev 专用配置）
# 前置：/home/erp/.zhipu_key 存在；dev_llm 库已初始化并安装 llm_service
cd /home/erp/odoo-19.0
/home/erp/odoo-19.0/venv/bin/python odoo-bin shell -d dev_llm -c /home/erp/dev_llm.conf --no-http < /home/erp/test_llm_service.py
