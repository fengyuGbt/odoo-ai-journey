# -*- coding: utf-8 -*-
"""验证智谱 GLM API Key 可用性（OpenAI 兼容协议）

用法:
    pip install openai
    python check_glm.py              # 默认从环境变量 ZHIPU_API_KEY 读取
    python check_glm.py sk-xxxx      # 或直接传 Key

输出: 模型返回的一句话自我介绍 = Key 可用。
若所有免费模型都报错，检查：Key 是否有效、是否已完成实名认证。
"""
import sys


def main():
    api_key = sys.argv[1] if len(sys.argv) > 1 else None
    if not api_key:
        import os
        api_key = os.environ.get("ZHIPU_API_KEY", "")
    if not api_key:
        sys.exit("错误：未提供 API Key。用法：python check_glm.py sk-xxxx")

    from openai import OpenAI
    client = OpenAI(api_key=api_key, base_url="https://open.bigmodel.cn/api/paas/v4")

    # 免费模型按新到旧依次尝试（新账号用 glm-4.7-flash；老账号可能只有 glm-4-flash）
    models = ["glm-4.7-flash", "glm-4-flash"]
    for model in models:
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role": "user",
                           "content": "你好，请用一句话介绍你自己，并说明你的免费模型身份。"}],
            )
            print(f"[OK] 模型 {model} 调用成功，返回：")
            print(resp.choices[0].message.content)
            return
        except Exception as e:
            print(f"[跳过] 模型 {model} 不可用：{type(e).__name__}: {e}")
    sys.exit("所有免费模型均不可用，请检查 Key / 实名认证 / 模型名")


if __name__ == "__main__":
    main()
