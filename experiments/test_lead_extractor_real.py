# -*- coding: utf-8 -*-
"""lead_extractor 真实 API 冒烟测试（不 mock，走智谱真实调用）。"""
# 注入 Key（从 Key 文件重新注入系统参数，同第 2 波真实测试做法）
key = open("/home/erp/.zhipu_key").read().strip()
env["ir.config_parameter"].set_param("llm_service.api_key", key)

RAW = "你好，我们想采购一批无线鼠标，大概 300 个，预算 1 万左右，下月中旬前能交货吗？"

wiz = env["lead.extractor.wizard"].create({"raw_text": RAW})
wiz.action_extract()
print("REAL EXTRACT OK: 产品=%s 数量=%s 预算=%s 交期=%s 客户=%s" % (
    wiz.product, wiz.quantity, wiz.budget, wiz.deadline, wiz.customer))
if not wiz.extracted or not wiz.product:
    raise SystemExit("FAIL: 抽取未成功")

res = wiz.action_create_lead()
lead = env["crm.lead"].browse(res["res_id"])
assert lead.exists(), "商机应已创建"
print("REAL LEAD OK: id=%s name=%s revenue=%s" % (
    lead.id, lead.name, lead.expected_revenue))
print("=== REAL TEST PASSED ===")
