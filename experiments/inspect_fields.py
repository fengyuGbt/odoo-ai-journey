# 探查 product.template 的属性相关字段
fields = env["product.template"]._fields
for name, f in fields.items():
    if "attribute" in name or "attr" in name:
        print(name, "|", f.type, "|", f.comodel_name or "")
