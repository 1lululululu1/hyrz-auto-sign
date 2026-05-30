# 游戏自动签到 — 多账号 GitHub Actions 配置说明

## 概述

脚本内置组装活动接口请求，实现多账号定时签到、访问任务、领取任务和活跃度奖励领取。账号数据通过 JSON 格式存储在 GitHub Secrets 中，工作流每日自动执行。

## 文件说明

| 文件 | 路径 | 用途 |
|------|------|------|
| 账号 JSON 示例 | `accounts.json.example` | 多账号数据格式模板 |
| 签到脚本 | `game_sign.py` | 读取 JSON 循环签到、访问、领取和活跃度奖励 |
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
| `partition` | 区服分区，用于领取任务奖励 |
| `roleId` | 角色 ID，用于领取任务奖励 |

## JSON 格式

```json
{
  "1050194": {
    "openid": "xxx",
    "acctype": "qc",
    "appid": "xxx",
    "access_token": "xxx",
    "partition": "xxx",
    "roleId": "xxx"
  },
  "1985123": {
    "openid": "yyy",
    "acctype": "qc",
    "appid": "yyy",
    "access_token": "yyy",
    "partition": "yyy",
    "roleId": "yyy"
  }
}
```

每个 key 为账号 ID（用于通知显示），value 为账号 Cookie 和角色相关字段。

## 脚本逻辑

1. 从环境变量 `GAME_ACCOUNTS` 读取 JSON 字符串
2. 解析为账号对象（key 为账号 ID）
3. 每个账号先获取当前活跃度，若 `actIntegral > 100`，直接记录今日已经签到完成并跳过后续接口
4. 未跳过的账号组装 Cookie，执行签到 POST 请求
5. 解析 `modRet.iRet` 字段判断成功（`"0"`）/已签到（`"100012"`）/失败
6. 签到后执行内置的访问任务请求，每个请求之间随机等待 1-2 秒
7. 访问任务全部执行完后，继续执行内置的领取任务请求，领取请求之间不等待
8. 领取任务全部执行完后，继续执行内置的活跃度奖励领取请求，活跃度请求之间不等待
9. 控制台输出完整执行结果，飞书通知只保留签到结果和活跃度奖励结果
10. 若设置了 `FEISHU_WEBHOOK` 环境变量，自动发送飞书群机器人通知
11. 有账号失败或附加任务请求失败时以非零退出码结束

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
