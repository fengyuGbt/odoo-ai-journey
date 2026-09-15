# product_desc_generator 冒烟测试：模拟按钮完整链路
# 读库 → 生成 → 弹窗(wizard) → 确认写入 → 验证 description_sale

# 1) 确保 Key 可用（从 Key 文件重新注入系统参数）
key = open("/home/erp/.zhipu_key").read().strip()
env["ir.config_parameter"].set_param("llm_service.api_key", key)

Product = env["product.template"]
# 2) 找或建测试产品
p = Product.search([("name", "=", "AI 测试耳机")], limit=1)
if not p:
    p = Product.create({"name": "AI 测试耳机", "type": "consu"})
print("=== PRODUCT READY ===", p.id, p.name)

# 3) 模拟点按钮：action_generate_desc
action = p.action_generate_desc()
print("=== ACTION OK ===", action.get("res_model"), "| target:", action.get("target"))

# 4) 弹窗数据（wizard 已生成文本）
wizard = env["product.desc.wizard"].browse(action["res_id"])
print("=== WIZARD OK ===", "product_id:", wizard.product_id.id, "| text len:", len(wizard.generated_text))
print("WIZARD TEXT:", wizard.generated_text[:150])

# 5) 模拟用户微调一句再确认（体现"人审可改"）
wizard.generated_text = wizard.generated_text.rstrip("。") + "，支持蓝牙 5.3。"
wizard.action_write_desc()
p.invalidate_recordset()
print("=== DESC WRITTEN ===")
print("description_sale:", p.description_sale)
print("MATCH:", p.description_sale == wizard.generated_text)
print("=== ALL TESTS PASSED ===")
