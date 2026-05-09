import json
import os
import urllib.request
import urllib.parse
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

RESULT_FILE = "sign_result.txt"


def send_feishu_notification(webhook_url, content):
    payload = json.dumps({
        "msg_type": "text",
        "content": {"text": content}
    }).encode("utf-8")

    req = urllib.request.Request(webhook_url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        return f"发送飞书通知失败: {e}"


def parse_result(body):
    """解析响应，返回 (status_type, message, gifts)"""
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return "error", "响应非 JSON", ""

    mod_ret = data.get("modRet", {})

    # modRet.iRet 区分不同状态
    ret_code = mod_ret.get("iRet")
    ret_msg = mod_ret.get("sMsg", "")

    # 提取奖励信息
    jdata = mod_ret.get("jData", {})
    gift_list = jdata.get("gift_list", {})
    gifts = gift_list.get("sPackageName", "")

    if ret_code == 0:
        return "success", ret_msg, gifts
    elif ret_code == 100012:
        return "already", ret_msg, ""
    else:
        return "fail", ret_msg or f"未知错误 (code={ret_code})", ""


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

    result_lines = []
    success_count = 0
    already_count = 0
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

        label = f"账号{idx} ({openid[:8]}...)"
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8")
                status, ret_msg, gifts = parse_result(body)

                if status == "success":
                    # 奖励简写：只取前两项
                    gift_items = [g.strip() for g in gifts.split(",") if g.strip()]
                    gift_short = "、".join(gift_items[:3])
                    if len(gift_items) > 3:
                        gift_short += f"等{len(gift_items)}项"
                    msg = f"✅ {label} 签到成功 🎁{gift_short}" if gift_short else f"✅ {label} 签到成功"
                    success_count += 1
                elif status == "already":
                    msg = f"⏭️ {label} 今日已签到"
                    already_count += 1
                else:
                    msg = f"❌ {label} 失败: {ret_msg}"
                    fail_count += 1

                print(msg)
                result_lines.append(msg)
        except Exception as e:
            msg = f"❌ {label} 请求异常: {e}"
            print(msg)
            result_lines.append(msg)
            fail_count += 1

    total = len(accounts)
    summary_parts = []
    if success_count:
        summary_parts.append(f"✅ 新增 {success_count}")
    if already_count:
        summary_parts.append(f"⏭️ 已签 {already_count}")
    if fail_count:
        summary_parts.append(f"❌ 失败 {fail_count}")
    summary_parts.append(f"总计 {total}")

    summary = f"签到完成: {' / '.join(summary_parts)}"
    print(f"\n{summary}")

    full_message = "\n".join(result_lines) + f"\n\n{summary}"
    with open(RESULT_FILE, "w", encoding="utf-8") as f:
        f.write(full_message)

    feishu_webhook = os.environ.get("FEISHU_WEBHOOK")
    if feishu_webhook:
        notify_msg = f"🎮 游戏签到\n\n" + full_message
        resp = send_feishu_notification(feishu_webhook, notify_msg)
        print(f"飞书通知结果: {resp}")

    if fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
