<div align="center">

# 🤖 astrbot_plugin_chehui

**AstrBot 消息撤回插件**  
撤回机器人自己发送的群聊消息，也可撤回指定群成员的消息（需管理权限）

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![AstrBot](https://img.shields.io/badge/AstrBot->=4.16-green.svg)](https://github.com/Soulter/AstrBot)
[![OneBot v11](https://img.shields.io/badge/OneBot-v11-black)](https://onebot.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

## 📖 简介

群聊消息撤回工具，支持两种模式：
- **撤回机器人自己的消息**：清理发言痕迹
- **撤回指定群成员的消息**（需机器人有管理权限）

命令简短，即开即用。

## 📥 安装

- **插件市场**：AstrBot 管理面板搜索 `astrbot_plugin_chehui` 安装。
- **手动**：将本仓库放入 `data/plugins/` 目录，重启/重载插件。

## ⚙️ 前置要求

- AstrBot ≥ 4.16，aiocqhttp 适配器。
- OneBot 客户端需开启 `get_group_msg_history` API（NapCat 在配置中设置 `true`，其他客户端通常默认开启）。
- 撤回他人消息需要机器人拥有管理员权限（否则会提示“权限不足”）。

## 🚀 使用

在群内发送命令，数量可选，默认 10 条，上限 200 条。

| 命令 | 说明 |
|------|------|
| `撤回` | 撤回机器人最近 10 条自己的消息 |
| `chehui` | 同上 |
| `撤回 5` | 撤回机器人最近 5 条自己的消息 |
| `撤回 @群成员` | 撤回该成员最近 10 条消息（需管理权限） |
| `撤回 @群成员 5` | 撤回该成员最近 5 条消息 |

执行成功时回复结果，例如：`已从 10 条消息中撤回 8 条`  
对他人撤回时若权限不足会回复：`权限不足，无法撤回该成员消息`

## ❓ 常见问题

**Q: 提示“获取消息历史失败”**  
A: 检查 OneBot 客户端是否开启了 `get_group_msg_history` 接口。

**Q: 有些消息撤回失败**  
A: 可能已超过撤回时限（一般 2 分钟）、已被删除或触发风控，间隔使用可缓解。

**Q: 为什么提示“权限不足”？**  
A: 撤回他人消息需要机器人是群管理员，否则无权操作。

**Q: 支持私聊吗？**  
A: 不支持，仅群聊环境可用。

## 👤 作者

- Jinhong270
- 仓库：https://github.com/Jinhong270/astrbot_plugin_chehui
- 反馈：Issues 页面

---

<p align="center">觉得有用的话，点个 ⭐ Star 吧</p>
