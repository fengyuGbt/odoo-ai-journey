# -*- coding: utf-8 -*-
"""lead_extractor 全链路测试（mock LLM，避免免费 API 高峰 429）。

覆盖四条路径：
1. 正常抽取：chat 返回合格 JSON → 预览字段回填 → 创建商机
2. 自纠正：chat 返回残缺 JSON → _call_llm 二次调用返回合格 JSON
3. 二次失败：chat + _call_llm 都坏 → UserError（不静默）
4. 纯函数：解析清洗（markdown 围栏）与 schema 校验

mock 方式：类级 monkeypatch（同第 2 波 test_product_desc_mock.py），finally 恢复。
"""
import odoo.addons.llm_service.models.llm_service as ls_module
from odoo.exceptions import UserError

RAW = "你好，我们想采购一批无线鼠标，大概 300 个，预算 1 万左右，下月中旬前能交货吗？"

GOOD = '{"product": "无线鼠标", "quantity": 300, "budget": 10000.0, "deadline": "2026-10-15", "customer": null}'
BAD = '{"product": "无线鼠标"'  # 残缺 JSON

_orig_chat = ls_module.LLMService.chat
_orig_call = ls_module.LLMService._call_llm

try:
    # ---------- 1. 正常抽取 → 创建商机 ----------
    def fake_good_chat(self, prompt, system=None, **kwargs):
        return GOOD

    ls_module.LLMService.chat = fake_good_chat

    wiz = env["lead.extractor.wizard"].create({"raw_text": RAW})
    res = wiz.action_extract()
    assert res["res_model"] == "lead.extractor.wizard", "抽取后应留在向导"
    print("EXTRACT OK: %s ×%s ¥%s 交期=%s 客户=%s" % (
        wiz.product, wiz.quantity, wiz.budget, wiz.deadline, wiz.customer))
    assert wiz.product == "无线鼠标"
    assert wiz.quantity == 300
    assert abs(wiz.budget - 10000.0) < 0.01
    assert str(wiz.deadline) == "2026-10-15"
    assert wiz.extracted

    res2 = wiz.action_create_lead()
    assert res2["res_model"] == "crm.lead"
    lead = env["crm.lead"].browse(res2["res_id"])
    assert lead.exists(), "商机应已创建"
    assert "无线鼠标" in lead.name and "300" in lead.name
    assert abs(lead.expected_revenue - 10000.0) < 0.01
    print("CREATE LEAD OK: id=%s name=%s revenue=%s" % (
        lead.id, lead.name, lead.expected_revenue))

    # ---------- 2. 自纠正路径 ----------
    def fake_bad_chat(self, prompt, system=None, **kwargs):
        return BAD

    def fake_good_call(self, messages, **kwargs):
        return GOOD

    ls_module.LLMService.chat = fake_bad_chat
    ls_module.LLMService._call_llm = fake_good_call

    wiz2 = env["lead.extractor.wizard"].create({"raw_text": RAW})
    wiz2.action_extract()
    assert wiz2.product == "无线鼠标", "自纠正后应成功"
    print("SELF-CORRECT OK: product=%s" % wiz2.product)

    # ---------- 3. 二次失败 → UserError（不静默） ----------
    def fake_bad_call(self, messages, **kwargs):
        return '{"product": 123}'  # 类型错误且缺字段

    ls_module.LLMService._call_llm = fake_bad_call

    wiz3 = env["lead.extractor.wizard"].create({"raw_text": RAW})
    try:
        wiz3.action_extract()
        raise SystemExit("FAIL: 应抛 UserError 而未抛")
    except UserError as e:
        print("USERERROR OK: %s" % str(e)[:80])

    # ---------- 4. 纯函数：解析清洗 + schema 校验 ----------
    from odoo.addons.lead_extractor.models import lead_parser
    from odoo.addons.lead_extractor.models import lead_prompt

    with_fence = '```json\n{"product": "测试", "quantity": 1, "budget": null, "deadline": null, "customer": null}\n```'
    parsed = lead_parser.parse_and_validate(with_fence)
    assert parsed["product"] == "测试" and parsed["quantity"] == 1
    print("PARSER OK: 围栏清洗 + 校验通过")

    missing = '{"product": "x", "quantity": 1}'
    try:
        lead_parser.parse_and_validate(missing)
        raise SystemExit("FAIL: 缺字段应抛 ValueError")
    except ValueError as e:
        print("PARSER REJECT OK: %s" % str(e))

    system, user = lead_prompt.build_prompt(RAW)
    assert "无线鼠标" in user and "示例输入" in user and "真实输入" in user
    assert "product" in system
    print("PROMPT OK: system=%d字 user=%d字" % (len(system), len(user)))

    print("=== ALL TESTS PASSED ===")
finally:
    ls_module.LLMService.chat = _orig_chat
    ls_module.LLMService._call_llm = _orig_call
