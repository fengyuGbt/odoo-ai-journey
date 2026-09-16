# -*- coding: utf-8 -*-
"""L2 · 解析校验层（纯函数，可脱离 Odoo 单测）。

职责：把模型返回的文本变成「可信的」结构化 dict。
对应课程知识点：LLM 输出不可信，进库前必须验货 —— 解析 + schema 校验。

清洗（去 markdown 围栏）→ json.loads（失败抛 ValueError）→ schema 校验
（必填字段 / 类型 / 空值规则）。任何一步失败由调用方走兜底（自纠正 / 降级 / 人工）。
"""
import json

REQUIRED = {"product", "quantity", "budget", "deadline", "customer"}


def clean_output(text):
    """去掉模型常见的 markdown 围栏（```json ... ```）与首尾空白。"""
    cleaned = (text or "").strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
    return cleaned


def parse_and_validate(text):
    """解析并校验模型输出，返回 {product, quantity, budget, deadline, customer}。

    失败统一抛 ValueError，由调用方决定兜底策略（绝不静默放行）。
    """
    try:
        data = json.loads(clean_output(text))
    except (TypeError, ValueError) as exc:
        raise ValueError("输出不是合法 JSON：%s" % exc)

    if not isinstance(data, dict):
        raise ValueError("输出必须是 JSON 对象，得到 %s" % type(data).__name__)

    missing = REQUIRED - set(data)
    if missing:
        raise ValueError("缺少字段: %s" % sorted(missing))

    if not isinstance(data["product"], str) or not data["product"].strip():
        raise ValueError("product 必须是非空字符串")
    if not isinstance(data["quantity"], int) or data["quantity"] <= 0:
        raise ValueError("quantity 必须是正整数")
    if data["budget"] is not None and not isinstance(data["budget"], (int, float)):
        raise ValueError("budget 必须是数字或 null")
    if data["deadline"] is not None and not isinstance(data["deadline"], str):
        raise ValueError("deadline 必须是 YYYY-MM-DD 字符串或 null")
    if data["customer"] is not None and not isinstance(data["customer"], str):
        raise ValueError("customer 必须是字符串或 null")

    return {
        "product": data["product"].strip(),
        "quantity": int(data["quantity"]),
        "budget": float(data["budget"]) if data["budget"] is not None else None,
        "deadline": data["deadline"],
        "customer": (data["customer"] or "").strip() or None,
    }
