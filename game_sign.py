import json
import os
import random
import urllib.request
import urllib.parse
import sys
import time

URL = "https://x8m8.ams.game.qq.com/ams/ame/amesvr?ameVersion=0.3&sServiceType=hyrz&iActivityId=576370&game=hyrz&eas_url=http%3A%2F%2Fwechatmini.qq.com%2Fhyrz%2Fwxc47b57c32a7fe64b%2Fpages%2Fwelfaresite%2Fwelfaresite%2F&e_code=0"

X_WECHAT_HOSTSIGN = '{"noncestr":"a23fc53959e97d0fe6859dded6e29633","timestamp":1778303419,"signature":"355ecdbd141e3a0fb60f814d703acdcf8c96414b"}'

FORM_FIELDS = {
    "iActivityId": "576370",
    "iFlowId": "1083576",
    "sOpenid": "",
    "openId": "",
    "g_tk": "1842395457",
}

EXTRA_SUCCESS_CODES = {"0", "2250", "4050", "4300"}

ULINK_TASK_DONE_URL = "https://ulinkact.game.qq.com/app/7335/1824be56cbeb29e7/index.php?route=Index/taskDone&iActId=8265&sAppId=ULINK-AKKJ-784060&game=hyrz&eas_url={eas_url}&e_code=0"
ULINK_TASK_LOTTERY_URL = "https://ulinkact.game.qq.com/app/7335/1824be56cbeb29e7/index.php?route=Index/taskLotteryNow&iActId=8265&sAppId=ULINK-AKKJ-784060&game=hyrz&eas_url=http%3A%2F%2Fwechatmini.qq.com%2Fhyrz%2Fwxc47b57c32a7fe64b%2Fpages%2Fwelfaresite%2Fwelfaresite%2F&e_code=0"
ULINK_ACTIVITY_URL = "https://ulinkact.game.qq.com/app/7335/1824be56cbeb29e7/index.php?route=Welfare/getTodayActGiftNow&iActId=8265&sAppId=ULINK-AKKJ-784060&game=hyrz&eas_url=http%3A%2F%2Fwechatmini.qq.com%2Fhyrz%2Fwxc47b57c32a7fe64b%2Fpages%2Fwelfaresite%2Fwelfaresite%2F&e_code=0"
ULINK_ACTIVITY_INFO_URL = "https://ulinkact.game.qq.com/app/7335/1824be56cbeb29e7/index.php?route=Welfare/getTodayActInfo&iActId=8265&sAppId=ULINK-AKKJ-784060&game=hyrz&eas_url=http%3A%2F%2Fwechatmini.qq.com%2Fhyrz%2Fwxc47b57c32a7fe64b%2Fpages%2Fwelfaresite%2Fwelfaresite%2F&e_code=0"

ACCESS_TASKS = [
    {
        "name": "忍者站",
        "eas_url": "http%3A%2F%2Fwechatmini.qq.com%2Fhyrz%2Fwxc47b57c32a7fe64b%2Fpages%2Fmain%2Fmain%2F",
        "index": "ninja",
    },
    {
        "name": "查看卷轴成绩",
        "eas_url": "http%3A%2F%2Fwechatmini.qq.com%2Fhyrz%2Fwxc47b57c32a7fe64b%2Fpages%2Fscroll%2Fscroll%2F",
        "index": "scrollRecord",
    },
    {
        "name": "查看壁纸站",
        "eas_url": "http%3A%2F%2Fwechatmini.qq.com%2Fhyrz%2Fwxc47b57c32a7fe64b%2Fsubpackages%2Fpages%2Fwallpaper%2Fwallpaper%2F",
        "index": "wallpaper",
    },
    {
        "name": "查看金币助手",
        "eas_url": "http%3A%2F%2Fwechatmini.qq.com%2Fhyrz%2Fwxc47b57c32a7fe64b%2Fpages%2Fouter%2Fouter%2F",
        "index": "goldHelper",
    },
    {
        "name": "访问活动日历",
        "eas_url": "http%3A%2F%2Fwechatmini.qq.com%2Fhyrz%2Fwxc47b57c32a7fe64b%2Factivitypackages%2Fpages%2Fcalendar%2Fcalendar%2F",
        "index": "actCalendar",
    },
    {
        "name": "进入村口",
        "eas_url": "http%3A%2F%2Fwechatmini.qq.com%2Fhyrz%2Fwxc47b57c32a7fe64b%2Fpages%2Fsquare%2Fsquare%2F",
        "index": "dynamicArticle",
    },
]

RECEIVE_TASKS = [
    {
        "name": "今日签到",
        "index": "sign",
    },
    {
        "name": "卷轴战机",
        "index": "scrollRecord",
    },
    {
        "name": "壁纸站",
        "index": "wallpaper",
    },
    {
        "name": "忍者站",
        "index": "ninja",
    },
    {
        "name": "村口",
        "index": "dynamicArticle",
    },
    {
        "name": "活动日历",
        "index": "actCalendar",
    },
    {
        "name": "金币助手",
        "index": "goldHelper",
    },
]

ACTIVITY_TASKS = [
    {
        "name": "60活跃度",
        "url": ULINK_ACTIVITY_URL,
        "index": "1",
    },
    {
        "name": "100活跃度",
        "url": ULINK_ACTIVITY_URL,
        "index": "2",
    },
    {
        "name": "40活跃度",
        "url": ULINK_ACTIVITY_URL,
        "index": "0",
    },
]


def build_cookie(account):
    openid = account.get("openid", "")
    acctype = account.get("acctype", "qc")
    appid = account.get("appid", "")
    access_token = account.get("access_token", "")
    return f"openid={openid};acctype={acctype};appid={appid};access_token={access_token}"


def build_role_form_fields(account, index=None):
    partition = account.get("partition")
    role_id = account.get("roleId")
    if partition in (None, ""):
        raise ValueError("账号缺少 partition")
    if role_id in (None, ""):
        raise ValueError("账号缺少 roleId")

    form_fields = {
        "area": "2",
        "platId": "0",
        "partition": str(partition),
        "roleId": str(role_id),
        "iActId": "8265",
        "sAppId": "ULINK-AKKJ-784060",
        "g_tk": "1842395457",
    }
    if index is not None:
        form_fields = {"index": index, **form_fields}
    return form_fields


def parse_response(body):
    if not body:
        return {"code": "", "msg": "", "jdata": None, "summary": "无响应内容"}

    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return {"code": "", "msg": "", "jdata": None, "summary": body[:120]}

    if not isinstance(data, dict):
        summary = str(data)[:120]
        return {"code": "", "msg": "", "jdata": None, "summary": summary}

    mod_ret = data.get("modRet")
    if isinstance(mod_ret, dict):
        code = mod_ret.get("iRet", "")
        msg = mod_ret.get("sMsg") or mod_ret.get("msg") or ""
        jdata = mod_ret.get("jData")
    else:
        code = data.get("iRet", data.get("ret", data.get("code", "")))
        msg = data.get("sMsg") or data.get("msg") or data.get("message") or ""
        jdata = data.get("jData")

    parts = []
    if code != "":
        parts.append(f"code={code}")
    if msg:
        parts.append(str(msg))
    summary = "，".join(parts) if parts else body[:120]
    return {"code": str(code) if code != "" else "", "msg": msg, "jdata": jdata, "summary": summary}


def summarize_response(body):
    return parse_response(body)["summary"]


def extract_reward_text(value):
    if value in (None, "", [], {}):
        return ""

    if isinstance(value, dict):
        award_list = value.get("awardList")
        if isinstance(award_list, list):
            rewards = [extract_reward_text(item) for item in award_list]
            rewards = [reward for reward in rewards if reward]
            return "、".join(rewards)

        gift_list = value.get("gift_list")
        if isinstance(gift_list, dict):
            gift_name = gift_list.get("sPackageName")
            if gift_name:
                return str(gift_name)

        for key in ("sPackageName", "packageName", "awardName", "name", "sItemName"):
            if value.get(key):
                return str(value[key])

        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))

    if isinstance(value, list):
        rewards = [extract_reward_text(item) for item in value]
        rewards = [reward for reward in rewards if reward]
        return "、".join(rewards)

    return str(value)


def format_activity_detail(account_line, task_name, response_info):
    code = response_info["code"]
    msg = response_info["msg"]
    reward = extract_reward_text(response_info["jdata"])

    if code == "0":
        return f"✅ {account_line} 活跃度/{task_name}: {reward}" if reward else f"✅ {account_line} 活跃度/{task_name}: {msg or '领取成功'}"
    if code == "4050":
        return f"⏭️ {account_line} 活跃度/{task_name}: {msg or '今日已领取该奖励'}"
    if is_extra_success(response_info):
        return f"✅ {account_line} 活跃度/{task_name}: {msg or response_info['summary']}"
    return f"❌ {account_line} 活跃度/{task_name}: {response_info['summary']}"


def is_extra_success(response_info):
    code = response_info["code"]
    return not code or code in EXTRA_SUCCESS_CODES


def build_extra_request(task, account, receive=False):
    if receive:
        url = task.get("url", ULINK_TASK_LOTTERY_URL)
        form_fields = build_role_form_fields(account, index=task["index"])
    else:
        url = ULINK_TASK_DONE_URL.format(eas_url=task["eas_url"])
        form_fields = {
            "index": task["index"],
            "iActId": "8265",
            "sAppId": "ULINK-AKKJ-784060",
            "g_tk": "1842395457",
        }

    data = urllib.parse.urlencode(form_fields).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("xweb_xhr", "1")
    req.add_header("X-WECHAT-HOSTSIGN", X_WECHAT_HOSTSIGN)
    req.add_header("Cookie", build_cookie(account))
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    return req


def build_activity_info_request(account):
    data = urllib.parse.urlencode(build_role_form_fields(account)).encode("utf-8")
    req = urllib.request.Request(ULINK_ACTIVITY_INFO_URL, data=data, method="POST")
    req.add_header("xweb_xhr", "1")
    req.add_header("X-WECHAT-HOSTSIGN", X_WECHAT_HOSTSIGN)
    req.add_header("Cookie", build_cookie(account))
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    return req


def get_current_activity(account):
    req = build_activity_info_request(account)
    with urllib.request.urlopen(req, timeout=30) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        body = resp.read().decode(charset, errors="replace")

    response_info = parse_response(body)
    if not is_extra_success(response_info):
        raise ValueError(response_info["summary"])

    jdata = response_info["jData"]
    if not isinstance(jdata, dict):
        raise ValueError("获取当前活跃度响应缺少 jData")

    act_integral = int(jdata.get("actIntegral", 0))
    ico_integral = jdata.get("icoIntegral", "")
    integral_task_list = jdata.get("integralTaskList", [])
    done_points = 0
    if isinstance(integral_task_list, list):
        for task in integral_task_list:
            if not isinstance(task, dict):
                continue
            if int(task.get("curDone") or 0) >= int(task.get("target") or 0):
                done_points += int(task.get("pointNum") or 0)

    return {
        "actIntegral": act_integral,
        "icoIntegral": ico_integral,
        "donePoints": done_points,
    }


def send_extra_task(task, account, receive=False):
    req = build_extra_request(task, account, receive=receive)

    with urllib.request.urlopen(req, timeout=30) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        body = resp.read().decode(charset, errors="replace")
    return parse_response(body)


def run_extra_tasks(
    tasks,
    account,
    account_line,
    stage_name,
    result_lines,
    receive=False,
    sleep_between=False,
    keep_success_log=True,
    show_reward=False,
):
    task_fail_count = 0
    for index, task in enumerate(tasks):
        try:
            response_info = send_extra_task(task, account, receive=receive)
            response_summary = response_info["summary"]
            if is_extra_success(response_info):
                reward = extract_reward_text(response_info["jdata"]) if show_reward else ""
                gift_text = f" 🎁{reward}" if reward else ""
                detail = f"✅ {account_line} {stage_name}/{task['name']}: {response_summary}{gift_text}"
            else:
                detail = f"❌ {account_line} {stage_name}/{task['name']}: {response_summary}"
                task_fail_count += 1
        except Exception as e:
            detail = f"❌ {account_line} {stage_name}/{task['name']}: {e}"
            task_fail_count += 1

        print(detail)
        if keep_success_log:
            result_lines.append(detail)

        if sleep_between and index < len(tasks) - 1:
            delay = random.uniform(1, 2)
            print(f"⏱️ {account_line} 等待 {delay:.2f}s 后继续{stage_name}")
            time.sleep(delay)

    return task_fail_count


def run_activity_tasks(tasks, account, account_line, result_lines):
    task_fail_count = 0
    rewards = []
    already_count = 0

    for task in tasks:
        try:
            response_info = send_extra_task(task, account, receive=True)
            detail = format_activity_detail(account_line, task["name"], response_info)

            if is_extra_success(response_info):
                reward = extract_reward_text(response_info["jData"])
                if reward:
                    rewards.extend([item for item in reward.split("、") if item])
                if response_info["code"] == "4050":
                    already_count += 1
            else:
                task_fail_count += 1
        except Exception as e:
            detail = f"❌ {account_line} 活跃度/{task['name']}: {e}"
            task_fail_count += 1

        print(detail)

    if rewards:
        deduped_rewards = list(dict.fromkeys(rewards))
        result_lines.append(f"✅ {account_line} 活跃度奖励 🎁{'、'.join(deduped_rewards)}")
    elif already_count == len(tasks):
        result_lines.append(f"⏭️ {account_line} 活跃度奖励今日已领取")
    elif task_fail_count:
        result_lines.append(f"❌ {account_line} 活跃度奖励领取异常")

    return task_fail_count


def send_feishu_notification(webhook_url, content):
    """发送飞书机器人通知"""
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

    if not isinstance(accounts, dict):
        print("❌ JSON 格式错误，应为对象")
        sys.exit(1)

    result_lines = []
    success_count = 0
    already_count = 0
    fail_count = 0
    task_fail_count = 0

    for idx, (aid, account) in enumerate(accounts.items(), start=1):
        cookie = build_cookie(account)
        line = f"账号{idx} ({aid})"

        try:
            activity_info = get_current_activity(account)
            act_integral = activity_info["actIntegral"]
            ico_integral = activity_info["icoIntegral"]
            done_points = activity_info["donePoints"]
            print(f"ℹ️ {line} 当前活跃度 actIntegral={act_integral}, icoIntegral={ico_integral}, 已完成任务积分合计={done_points}")
            if act_integral >= 100:
                detail = f"⏭️ {line} 今日已经签到完成（当前活跃度 {act_integral}）"
                print(detail)
                result_lines.append(detail)
                already_count += 1
                continue
        except Exception as e:
            detail = f"❌ {line} 获取当前活跃度异常: {e}"
            print(detail)
            task_fail_count += 1

        form_data = urllib.parse.urlencode(FORM_FIELDS).encode("utf-8")

        req = urllib.request.Request(URL, data=form_data, method="POST")
        req.add_header("xweb_xhr", "1")
        req.add_header("X-WECHAT-HOSTSIGN", X_WECHAT_HOSTSIGN)
        req.add_header("Cookie", cookie)

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                body = resp.read().decode("utf-8")
                data = json.loads(body)
                mod_ret = data.get("modRet", {})

                # iRet 可能是 int 0 或 str "100012"，统一转 str 比较
                ret_code = str(mod_ret.get("iRet", ""))
                ret_msg = mod_ret.get("sMsg", "")

                if ret_code == "0":
                    # 签到成功，提取奖励
                    jdata = mod_ret.get("jData", {})
                    gift_list = jdata.get("gift_list", {})
                    gifts = gift_list.get("sPackageName", "")
                    gift_items = [g.strip() for g in gifts.split(",") if g.strip()]
                    gift_short = "、".join(gift_items[:3])
                    if len(gift_items) > 3:
                        gift_short += f"等{len(gift_items)}项"

                    detail = f"✅ {line} 签到成功 🎁{gift_short}" if gift_short else f"✅ {line} 签到成功"
                    success_count += 1
                elif ret_code == "100012":
                    detail = f"⏭️ {line} 今日已签到"
                    already_count += 1
                else:
                    detail = f"❌ {line} 失败: {ret_msg}"
                    fail_count += 1

                print(detail)
                result_lines.append(detail)
        except Exception as e:
            detail = f"❌ {line} 请求异常: {e}"
            print(detail)
            result_lines.append(detail)
            fail_count += 1

        task_fail_count += run_extra_tasks(
            ACCESS_TASKS,
            account,
            line,
            "访问",
            result_lines,
            receive=False,
            sleep_between=True,
            keep_success_log=False,
        )
        task_fail_count += run_extra_tasks(
            RECEIVE_TASKS,
            account,
            line,
            "领取",
            result_lines,
            receive=True,
            sleep_between=False,
            keep_success_log=False,
        )
        task_fail_count += run_activity_tasks(ACTIVITY_TASKS, account, line, result_lines)

    total = len(accounts)
    summary_parts = []
    if success_count:
        summary_parts.append(f"✅ 签到成功 {success_count}")
    if already_count:
        summary_parts.append(f"⏭️ 今日已签 {already_count}")
    if fail_count:
        summary_parts.append(f"❌ 签到失败 {fail_count}")
    if task_fail_count:
        summary_parts.append(f"❌ 附加任务失败 {task_fail_count}")
    summary_parts.append(f"总计 {total}")

    summary = " / ".join(summary_parts)
    print(f"\n{summary}")

    # 飞书通知：区分不同场景
    feishu_webhook = os.environ.get("FEISHU_WEBHOOK")
    if feishu_webhook:
        notify_detail = "\n".join(result_lines) if result_lines else "无账号执行记录"
        notify_msg = f"🎮 游戏签到\n\n{notify_detail}\n\n{summary}"
        resp = send_feishu_notification(feishu_webhook, notify_msg)
        print(f"飞书通知结果: {resp}")

    # 如果有失败，退出码非零
    if fail_count > 0 or task_fail_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
