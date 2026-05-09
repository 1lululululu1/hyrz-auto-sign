# 游戏自动签到 — 多账号 GitHub Actions 配置说明

## 概述

基于 `curl.txt` 中的请求信息，实现多账号定时签到。账号数据通过 JSON 格式存储在 GitHub Secrets 中，工作流每日自动执行。

## 文件说明

| 文件 | 路径 | 用途 |
|------|------|------|
| 账号 JSON 示例 | `accounts.json.example` | 多账号数据格式模板 |
| 签到脚本 | `game_sign.py` | 读取 JSON 循环签到 |
| 工作流配置 | `.github/workflows/game-sign.yml` | GitHub Actions 定时任务 |

## 请求结构

### 接口
```
POST https://x8m8.ams.game.qq.com/ams/ame/amesvr?ameVersion=0.3&sServiceType=hyrz&iActivityId=576370&game=hyrz&eas_url=http%3A%2F%2Fwechatmini.qq.com%2Fhyrz%2Fwxc47b57c32a7fe64b%2Fpages%2Fwelfaresite%2Fwelfaresite%2F&e_code=0
```

### 固定 Header

| 字段 | 值 |
|------|-----|
| `xweb_xhr` | `1` |
| `X-WECHAT-HOSTSIGN` | 固定写死 |

### 固定 Form 数据

| 字段 | 值 |
|------|-----|
| `iActivityId` | `576370` |
| `iFlowId` | `1083576` |
| `sOpenid` | `""` |
| `openId` | `""` |
| `g_tk` | `1842395457` |

### 每个账号不同的字段（Cookie 中）

| 字段 | 说明 |
|------|------|
| `openid` | 用户标识 |
| `acctype` | 账号类型（固定 `qc`） |
| `appid` | 应用 ID |
| `access_token` | 访问令牌 |

## JSON 格式

```json
{
  "1050194": {
    "openid": "xxx",
    "acctype": "qc",
    "appid": "xxx",
    "access_token": "xxx"
  },
  "1985123": {
    "openid": "yyy",
    "acctype": "qc",
    "appid": "yyy",
    "access_token": "yyy"
  }
}
```

每个 key 为账号 ID（用于通知显示），value 为 Cookie 中的四个字段。

## 脚本逻辑

1. 从环境变量 `GAME_ACCOUNTS` 读取 JSON 字符串
2. 解析为账号列表
3. 对每个账号组装 Cookie，执行 POST 请求
4. 解析响应 `iRet` 字段判断成功/失败
5. 将签到结果写入 `sign_result.txt` 文件
6. 若设置了 `FEISHU_WEBHOOK` 环境变量，自动发送飞书群机器人通知
7. 有账号失败时以非零退出码结束

## GitHub Secrets 配置

需要在 GitHub Secrets 中配置以下两个变量：

### GAME_ACCOUNTS

1. 打开 GitHub 仓库 → **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. **Name**: `GAME_ACCOUNTS`
4. **Secret**: 填入 JSON 格式的完整账号数据

### FEISHU_WEBHOOK（可选）

1. 在飞书群组中添加自定义机器人，获取 Webhook 地址
2. 同样在 **Actions secrets** 中新增
3. **Name**: `FEISHU_WEBHOOK`
4. **Secret**: 飞书机器人 Webhook URL（如 `https://open.feishu.cn/open-apis/bot/v2/hook/xxx`）

## 飞书通知效果

签到完成后，飞书群机器人会发送如下格式的通知：

```
🎮 游戏签到通知

✅ 账号1 (openid_abc...) 签到成功
✅ 账号2 (openid_def...) 签到成功
❌ 账号3 (openid_ghi...) 请求异常: ...

签到完成: 成功 2 / 失败 1 / 总计 3
```

## 工作流触发器

| 类型 | 触发条件 |
|------|----------|
| 定时 | 每天 UTC 1:00（北京时间 9:00） |
| 手动 | GitHub Actions 页面点击 `Run workflow` |
