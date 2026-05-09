import json
import os
import urllib.request
import sys

URL = "https://x8m8.ams.game.qq.com/ams/ame/amesvr?ameVersion=0.3&sServiceType=hyrz&iActivityId=576370&game=hyrz&eas_url=http%3A%2F%2Fwechatmini.qq.com%2Fhyrz%2Fwxc47b57c32a7fe64b%2Fpages%2Fwelfaresite%2Fwelfaresite%2F&e_code=0"

X_WECHAT_HOSTSIGN = '{"noncestr":"a23fc53959e97d0fe6859dded6e29633","timestamp":1778303419,"signature":"355ecdbd141e3a0fb60f814d703acdcf8c96414b"}'

FORM_FIELDS = {
    "iActivityId": "576370",
    "iFlowId": "1083576",
    "sOpenid": "",
    "openId": "",
    "g_tk": "1842395457",
}


def main():
    accounts_json = os.environ.get("GAME_ACCOUNTS")
    if not accounts_json:
        print("❌ 环境变量 GAME_ACCOUNTS 未设置")
        sys.exit(1)

    try:
        accounts = json.loads(accounts_json)
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析失败: {e}")
        sys.exit(1)

    if not isinstance(accounts, list):
        print("❌ JSON 格式错误，应为数组")
        sys.exit(1)

    success_count = 0
    fail_count = 0

    for idx, account in enumerate(accounts, start=1):
        openid = account.get("openid", "")
        acctype = account.get("acctype", "qc")
        appid = account.get("appid", "")
        access_token = account.get("access_token", "")

        cookie = f"openid={openid};acctype={acctype};appid={appid};access_token={access_token}"

        form_data = urllib.parse.urlencode(FORM_FIELDS).encode("utf-8")

        req = urllib.request.Request(URL, data=form_data, method="POST")
        req.add_header("xweb_xhr", "1")
        req.add_header("X-WECHAT-HOSTSIGN", X_WECHAT_HOSTSIGN)
        req.add_header("Cookie", cookie)

        print(f"\n===== 账号 {idx} (openid: {openid[:8]}...) =====")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8")
                print(f"状态码: {resp.status}")
                print(f"响应: {body[:500]}")
                success_count += 1
        except Exception as e:
            print(f"❌ 请求失败: {e}")
            fail_count += 1

    print(f"\n===== 执行完毕 =====")
    print(f"成功: {success_count}, 失败: {fail_count}, 总计: {len(accounts)}")


if __name__ == "__main__":
    main()