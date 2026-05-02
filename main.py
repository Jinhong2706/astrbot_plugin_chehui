import asyncio
import re
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.core.message.components import At, Plain

@register("astrbot_plugin_chehui", "Jinhong270", "消息撤回插件", "1.0.1")
class RecallPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.config = self.get_config()
        
    def get_config(self):
        return {
            "max_recall_count": self.context.get_config().get("max_recall_count", 200),
            "recall_interval": self.context.get_config().get("recall_interval", 0.2),
            "require_admin_permission": self.context.get_config().get("require_admin_permission", True)
        }

    @filter.command("撤回")
    async def recall(self, event: AstrMessageEvent):
        async for result in self._do_recall(event):
            yield result

    @filter.command("chehui")
    async def chehui(self, event: AstrMessageEvent):
        async for result in self._do_recall(event):
            yield result

    async def _do_recall(self, event: AstrMessageEvent):
        if event.get_group_id() is None:
            yield event.plain_result("此命令仅支持群聊")
            return

        group_id = event.get_group_id()
        self_id = str(event.get_self_id())

        segments = event.get_messages()
        target_qq = None
        num = 10

        for seg in segments:
            if isinstance(seg, At) and str(seg.qq) != "all":
                target_qq = str(seg.qq)
                break

        if target_qq:
            if self.config.get("require_admin_permission", True) and not event.is_admin():
                yield event.plain_result("权限不足，仅bot管理员可撤回他人消息")
                return

        text = ""
        for seg in segments:
            if isinstance(seg, Plain):
                text += seg.text
        nums = re.findall(r"\d+", text)
        if nums:
            num = int(nums[-1])
        num = max(1, min(num, self.config["max_recall_count"]))

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
                await asyncio.sleep(self.config["recall_interval"])
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