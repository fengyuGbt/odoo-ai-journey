# 裸测智谱 API：打印完整响应体，诊断 429 原因
import json
import urllib.error
import urllib.request

key = open("/home/erp/.zhipu_key").read().strip()
url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
payload = {
    "model": "glm-4.7-flash",
    "messages": [{"role": "user", "content": "hi"}],
    "temperature": 0.7,
}
req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Authorization": "Bearer %s" % key, "Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        print("HTTP 200 OK")
        print(resp.read().decode("utf-8")[:1000])
except urllib.error.HTTPError as e:
    print("HTTP", e.code)
    print("--- response body ---")
    print(e.read().decode("utf-8", errors="replace")[:1500])
except Exception as e:
    print("ERR", type(e).__name__, e)
