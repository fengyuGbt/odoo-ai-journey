# odoo shell 冒烟测试：llm.service.chat() 真实调用智谱 GLM
# 用法：odoo-bin shell -d dev_llm < test_llm_service.py
# 前置：/home/erp/.zhipu_key 文件内含智谱 API Key（Key 不落对话、不进仓库）

key = open("/home/erp/.zhipu_key").read().strip()
env["ir.config_parameter"].set_param("llm_service.api_key", key)

svc = env["llm.service"]

# 1) 基础对话（system + user）
resp = svc.chat("你好，请用一句话介绍你自己。", system="你是 Odoo llm_service 的测试助手。")
print("=== CHAT OK ===")
print(resp)

# 2) 少样本示例：产品描述生成（对应 Ch2 少样本概念）
few_shot = (
    "你是电商文案专家。根据产品信息生成不超过 80 字的中文描述。\n"
    "示例1：\n产品：可乐 330ml\n描述：经典碳酸饮料，330ml 易拉罐装，冰镇后口感更佳，聚会畅饮首选。\n"
    "示例2：\n产品：汉堡\n描述：现做牛肉汉堡，松软面包配多汁肉饼，分量足，出餐快，工作日午餐优选。\n"
    "现在生成：\n产品：无线蓝牙耳机\n描述："
)
desc = svc.chat(few_shot, temperature=0.7)
print("=== FEW-SHOT DESC OK ===")
print(desc)

print("=== ALL TESTS PASSED ===")
