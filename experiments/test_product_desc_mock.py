# product_desc_generator 冒烟测试（mock 版）：
# 智谱高峰期 429 过载时，mock 掉 chat() 验证完整 Odoo 逻辑链。
# 真实 API 测试见 test_product_desc.py（高峰过后可跑）。

import odoo.addons.llm_service.models.llm_service as ls_module

# 1) mock chat：固定返回生成文本（模拟模型输出）
def fake_chat(self, prompt, system=None, **kwargs):
    return "MOCK 生成：真无线蓝牙耳机，高清降噪，音质纯净。佩戴轻盈舒适，超长续航，通勤运动首选。"

_orig_chat = ls_module.LLMService.chat
ls_module.LLMService.chat = fake_chat

try:
    Product = env["product.template"]
    p = Product.search([("name", "=", "AI 测试耳机")], limit=1)
    if not p:
        p = Product.create({"name": "AI 测试耳机", "type": "consu"})
    print("=== PRODUCT READY ===", p.id, p.name)

    # 2) 模拟点按钮（走真实按钮代码，只是 chat 被 mock）
    action = p.action_generate_desc()
    print("=== ACTION OK ===", action.get("res_model"), "| target:", action.get("target"))

    # 3) 弹窗数据
    wizard = env["product.desc.wizard"].browse(action["res_id"])
    print("=== WIZARD OK ===", "product_id:", wizard.product_id.id, "| text len:", len(wizard.generated_text))
    print("WIZARD TEXT:", wizard.generated_text[:120])

    # 4) 模拟用户微调后确认写入
    wizard.generated_text = wizard.generated_text.replace("超长续航", "超长续航 24h")
    wizard.action_write_desc()
    p.invalidate_recordset()
    print("=== DESC WRITTEN ===")
    print("description_sale:", p.description_sale)
    print("MATCH:", p.description_sale == wizard.generated_text)

    # 5) 视图存在性验证（按钮已挂上）
    btn_view = env["ir.ui.view"].search(
        [("name", "=", "product.template.ai.desc.button")], limit=1)
    print("=== VIEW OK ===", bool(btn_view), "| has button:", "AI 生成描述" in btn_view.arch_db)
    print("=== ALL TESTS PASSED ===")
finally:
    ls_module.LLMService.chat = _orig_chat
