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
[
  {
    "openid": "xxx",
    "acctype": "qc",
    "appid": "xxx",
    "access_token": "xxx"
  },
  {
    "openid": "yyy",
    "acctype": "qc",
    "appid": "yyy",
    "access_token": "yyy"
  }
]
```

每个数组元素代表一个账号，只需 Cookie 中的四个字段。

## 脚本逻辑

1. 从环境变量 `GAME_ACCOUNTS` 读取 JSON 字符串
2. 解析为账号列表
3. 对每个账号组装 Cookie，执行 POST 请求
4. 打印每个账号的签到结果（成功/失败）

## GitHub Secrets 配置

1. 打开 GitHub 仓库 → **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**
3. **Name**: `GAME_ACCOUNTS`
4. **Secret**: 填入上方 JSON 格式的完整账号数据

## 工作流触发器

| 类型 | 触发条件 |
|------|----------|
| 定时 | 每天 UTC 1:00（北京时间 9:00） |
| 手动 | GitHub Actions 页面点击 `Run workflow` |
