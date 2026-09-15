# 列出 dev_llm 已安装模块
mods = env["ir.module.module"].search([("state", "=", "installed")])
print("INSTALLED MODULES:", len(mods))
for m in mods:
    print(" -", m.name)
