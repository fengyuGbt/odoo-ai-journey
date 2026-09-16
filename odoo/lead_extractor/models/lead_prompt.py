# -*- coding: utf-8 -*-
"""L2 · 提示词模板（纯函数，不依赖 Odoo 环境，可脱离 Odoo 单测）。

职责：把「非结构化询盘 + 输出约束」组装成发给 LLM 的消息。
对应课程知识点：Ch2 提示工程 —— 角色设定（system）+ few-shot 示范（user）。

返回 (system, user) 两段文本，供 llm.service.chat(prompt, system=...) 使用；
复杂对话（如自纠正重试）由 build_fix_messages 构造完整 messages 列表，
走 llm.service._call_llm(messages)。
"""
import json

# 输出 schema 声明：告诉模型「只准吐这些字段」
SCHEMA = {
    "product": "str, 产品名称",
    "quantity": "int, 数量",
    "budget": "float, 预算金额（元），无法确定填 null",
    "deadline": "str, 期望交期 YYYY-MM-DD，无法确定填 null",
    "customer": "str, 客户/联系人名称，无法确定填 null",
}

# few-shot 示例：覆盖「能填」和「填 null」两种情况，教模型别编造
EXAMPLES = [
    {
        "input": "你好，我们想采购一批无线鼠标，大概要 300 个，预算 1 万左右，下个月中旬之前能交货吗？",
        "output": {
            "product": "无线鼠标",
            "quantity": 300,
            "budget": 10000.0,
            "deadline": "2026-10-15",
            "customer": None,
        },
    },
    {
        "input": "我们公司需要 50 台办公笔记本电脑，预算 25 万，越快越好，联系人是张伟。",
        "output": {
            "product": "办公笔记本电脑",
            "quantity": 50,
            "budget": 250000.0,
            "deadline": None,
            "customer": "张伟",
        },
    },
]


def _schema_text():
    return "\n".join("  - %s: %s" % (k, v) for k, v in SCHEMA.items())


def build_prompt(raw_text):
    """返回 (system, user) 两段文本。

    system 立规矩（角色 + schema + 空值规则），user 给 few-shot 示范 + 真实输入。
    """
    system = (
        "你是 Odoo 销售助理，从客户询盘中抽取结构化信息。\n"
        "只输出 JSON，不要输出任何其他文字。\n"
        "字段定义如下：\n%s\n"
        "无法确定的字段一律填 null，不要编造。" % _schema_text()
    )
    parts = []
    for ex in EXAMPLES:
        parts.append(
            "示例输入：%s\n期望输出：%s"
            % (ex["input"], json.dumps(ex["output"], ensure_ascii=False))
        )
    parts.append("真实输入：%s" % raw_text)
    return system, "\n\n".join(parts)


def build_fix_messages(messages, bad_output):
    """自纠正：把模型上次的坏输出追加进对话，要求重新输出合格 JSON。

    :param messages: 原始 messages 列表
    :param bad_output: 模型上次返回的文本（无法解析 / 不符合 schema）
    :return: 扩展后的 messages 列表（可直接传给 llm.service._call_llm）
    """
    fixed = list(messages)
    fixed.append({"role": "assistant", "content": bad_output})
    fixed.append({
        "role": "user",
        "content": "你上次的输出无法解析或不符合字段要求，请重新只输出符合字段定义的 JSON。",
    })
    return fixed
