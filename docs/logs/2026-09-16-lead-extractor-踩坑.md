# lead_extractor 踩坑日志（2026-09-16）

> 第 4 波：L2 结构化抽取「询盘 → 商机」模块开发中踩到的真实坑。
> 与第 1、2 波一样，坑和代码一样有价值。

## 1. Odoo 19 的 CRM 主菜单 external id 变了

**现象**：安装模块报 `ParseError: <menuitem parent="crm.menu_crm_root">` 找不到父菜单。

**原因**：Odoo 19 里 CRM 主菜单 external id 已从 `crm.menu_crm_root` 改为 `crm.crm_menu_root`。
老教程/记忆里的 id 会直接让安装失败。

**解决**：odoo shell 查真实 id——
```python
env["ir.model.data"].search([("model", "=", "ir.ui.menu"), ("res_id", "=", m.id)])
# → TOP MENU: crm.crm_menu_root -> CRM
```
教训：**引用第三方模块的 external id 前先查库**，跨大版本别信记忆。

## 2. Odoo 模型方法只读，`_patch_method` 也不存在

**现象**：测试里 `llm.chat = fake` 报 `attribute 'chat' is read-only`；
换 `llm._patch_method("chat", fake)` 报 `has no attribute '_patch_method'`。

**原因**：Odoo Model 的方法通过特殊机制暴露，直接赋值被拒；
Odoo 19 已移除 `_patch_method`（或本环境不可用）。

**解决**：类级 monkeypatch（第 2 波 `test_product_desc_mock.py` 已验证的方式）：
```python
import odoo.addons.llm_service.models.llm_service as ls_module
_orig = ls_module.LLMService.chat
ls_module.LLMService.chat = fake_chat
try:
    ...
finally:
    ls_module.LLMService.chat = _orig
```

## 3. 测试脚本自己漏 import（不是模块的锅）

**现象**：`except UserError` 报 `NameError: name 'UserError' is not defined`。

**原因**：测试脚本没 `from odoo.exceptions import UserError`。业务代码抛错逻辑完全正确
（UserError 信息把 schema 错误和模型原始输出都展示出来了），是测试脚本的问题。

## 4. 复用边界实测确认（好消息）

- `llm.service.chat(prompt, system=...)` 原生支持 system + user 两段，
  L2 提示词模板 `build_prompt()` 返回 `(system, user)` 即可零改动接入；
- 自纠正需要"追加坏输出再问一次"的多轮 messages → 走底层 `llm.service._call_llm(messages)`，
  鉴权/重试/降级全部继承——封装一行没改。
