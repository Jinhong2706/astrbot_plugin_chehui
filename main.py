import asyncio
import re
import os
import json
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.message.components import At, Plain

@register("astrbot_plugin_chehui", "Jinhong270", "消息撤回插件", "1.0.3")
class RecallPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    def get_config_from_file(self):
        """从配置文件读取配置，适配Linux和Windows"""
        try:
            # 获取插件目录路径
            plugin_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 构建配置文件路径 (../../config/astrbot_plugin_chehui_config.json)
            # 插件目录: data/plugins/astrbot_plugin_chehui/
            # 配置目录: data/config/
            config_dir = os.path.join(plugin_dir, "..", "..", "config")
            config_path = os.path.join(config_dir, "astrbot_plugin_chehui_config.json")
            
            # 确保路径是绝对路径
            config_path = os.path.abspath(config_path)
            
            # 读取配置文件
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8-sig') as f:
                    config = json.load(f)
                return config
            else:
                logger.warning(f"配置文件不存在: {config_path}")
                return {}
        except Exception as e:
            logger.warning(f"读取配置文件失败: {e}")
            return {}

    @filter.command("撤回")
    async def recall(self, event: AstrMessageEvent):
        async for result in self._do_recall(event):
            yield result

    @filter.command("chehui")
    async def chehui(self, event: AstrMessageEvent):
        async for result in self._do_recall(event):
            yield result

    async def _do_recall(self, event: AstrMessageEvent):
        # 从配置文件读取配置
        file_config = self.get_config_from_file()
        
        # 优先使用文件配置，如果没有则使用context配置
        cfg = self.context.get_config()
        default_count = int(file_config.get("default_recall_count", cfg.get("default_recall_count", 10)))
        require_admin = file_config.get("require_admin_permission", cfg.get("require_admin_permission", True))
        recall_interval = float(file_config.get("recall_interval", cfg.get("recall_interval", 0.2)))

        if event.get_group_id() is None:
            yield event.plain_result("此命令仅支持群聊")
            return

        group_id = event.get_group_id()
        self_id = str(event.get_self_id())

        segments = event.get_messages()
        target_qq = None
        num = default_count  # 使用默认撤回条数

        for seg in segments:
            if isinstance(seg, At) and str(seg.qq) != "all":
                target_qq = str(seg.qq)
                break

        if target_qq:
            if require_admin and not event.is_admin():
                yield event.plain_result("权限不足，仅bot管理员可撤回他人消息")
                return

        text = ""
        for seg in segments:
            if isinstance(seg, Plain):
                text += seg.text
        nums = re.findall(r"\d+", text)
        if nums:
            num = int(nums[-1])
        
        # 移除最大限制，只确保至少撤回1条
        num = max(1, num)

        fetch_count = num * 3
        try:
            result = await event.bot.call_action(
                "get_group_msg_history",
                group_id=int(group_id),
                count=fetch_count
            )
            messages = result.get("messages", []) if isinstance(result, dict) else []
        except Exception:
            yield event.plain_result("获取消息历史失败，请确认适配器支持历史记录 API")
            return

        if not messages:
            yield event.plain_result("没有可撤回的消息")
            return

        filter_id = target_qq if target_qq else self_id
        filtered = [
            m for m in messages
            if str(m.get("sender", {}).get("user_id", "")) == filter_id
        ]
        filtered.sort(key=lambda x: x.get("time", 0), reverse=True)
        target_messages = filtered[:num]

        if not target_messages:
            who = "该用户" if target_qq else "我"
            yield event.plain_result(f"最近 {num} 条消息中没有{who}发送的内容")
            return

        success = 0
        permission_fail = 0
        for msg in target_messages:
            message_id = msg.get("message_id")
            if not message_id:
                continue
            try:
                await event.bot.delete_msg(message_id=message_id)
                success += 1
                await asyncio.sleep(recall_interval)
            except Exception as e:
                if target_qq:
                    permission_fail += 1
                    logger.warning(f"撤回他人消息失败，可能权限不足: {e}")
                else:
                    logger.warning(f"撤回自己消息失败: {e}")
                continue

        if target_qq:
            if success == 0:
                yield event.plain_result("撤回失败，请检查机器人是否具有管理员权限")
            else:
                yield event.plain_result(
                    f"已从 @{target_qq} 的 {num} 条消息中撤回 {success} 条"
                    + (f"，{permission_fail} 条因权限不足失败" if permission_fail else "")
                )
        else:
            yield event.plain_result(f"已从 {num} 条消息中撤回 {success} 条")
