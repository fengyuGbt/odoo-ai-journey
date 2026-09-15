# 查 product.template.common.form 的 external id
data = env["ir.model.data"].search([("model", "=", "ir.ui.view"), ("res_id", "=", 437)])
print("EXT_IDS:")
for d in data:
    print(" -", d.module, ".", d.name)
