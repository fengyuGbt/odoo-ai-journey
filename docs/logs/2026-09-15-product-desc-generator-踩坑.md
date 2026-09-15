# product_desc_generator 开发踩坑记录（2026-09-15）

> 日期：2026-09-15
> 场景：odoo-ai-journey 第 2 波 · 产品描述按钮（模式1+2：弹窗确认后写库）
> 关联：`odoo/product_desc_generator/`、`docs/01-ch2-prompt-and-cot.md`

## 🛠 问题 1：Odoo 19 license 字段不接受 "MIT"

- **现象**：`odoo-bin -i product_desc_generator` 报 `ValueError: Wrong value for ir.module.module.license: 'MIT'`。
- **排查**：license 是 Selection 字段，Odoo 19 的选项枚举里没有 'MIT'（旧教程常写 MIT）。
- **解决**：改为 `"license": "LGPL-3"`；同时把 `llm_service` 的 manifest 一起改掉（避免下次 update_list 扫描再炸）。
- **教训**：**Odoo 版本迭代会改 manifest 枚举值**——license 用 LGPL-3 / AGPL-3 这类稳定选项，别照抄网上老教程的 MIT。

## 🛠 问题 2：Odoo 19 属性字段改名（attribute_value_ids 已移除）

- **现象**：按钮方法报 `AttributeError: 'product.template' object has no attribute 'attribute_value_ids'. Did you mean: 'attribute_line_ids'?`
- **排查**：shell 探查 `product.template._fields` 确认：Odoo 19 只有 `attribute_line_ids`（one2many→product.template.attribute.line）和 `valid_product_template_attribute_line_ids`，没有 Odoo 17/18 的 `attribute_value_ids`。
- **解决**：改为 `self.attribute_line_ids.mapped("value_ids.name")`（属性行 → 属性值 → 名称）。
- **教训**：**跨版本开发前先用 odoo shell 探查字段/视图真实结构**（`_fields`、`arch_db`），不要凭旧文档写；Odoo 19 的产品属性 API 与 17/18 差异很大。

## 🛠 问题 3：免费 API 高峰期持续 429（两次重试均过载）

- **现象**：mock 前真实调用连续两次（间隔 90s）返回 `429 / code 1305 / "该模型当前访问量过大"`，`glm-4.7-flash` 和降级的 `glm-4-flash` 都被限。
- **排查**：与第 1 波 429 同源——免费模型服务端过载，非 Key/代码问题；模块的重试+降级机制正确触发（日志可见自动切换备用模型）。
- **解决**：开发期用 **mock 测试**（monkeypatch `llm.service.chat` 返回固定文本）验证完整 Odoo 逻辑链；真实 API 补测待服务端过载缓解（用户可在低谷时段跑 `run_pdg_test.sh`）。
- **教训**：**免费 API 的 429 是常态，开发节奏要配套**：逻辑链用 mock 先验，API 联调挑低谷时段；mock 也顺便测出了"人审可修改"这类纯 Odoo 行为。

## 🛠 问题 4（复现）：PowerShell 拦截远程命令里的 `&` / `<`

- **现象**：本地 PowerShell 直接拼 `ssh ... "wsl ... bash -c '... < file'"` 报 `&` 保留字符错误；`<` 重定向经多层传递被 Windows cmd 吃掉（"系统找不到指定的路径"）。
- **解决**：遵守 remote-desktop-connector 指引——**复杂命令一律写成 .py/.sh 上传执行**（scp 到 Windows 侧 → cp 进 WSL → `bash /home/erp/xxx.sh`），odoo shell 的 stdin 重定向放在 .sh 内部完成。
- **教训**：老坑复现。ssh→cmd→wsl→bash 四层传递里，引号、`&`、`<`、`>` 都不可靠；**凡超过一行的远程逻辑，先落盘成脚本再跑**。

---

*本文件由真实开发过程整理，供社区参考。*
