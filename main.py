import asyncio
from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("astrbot_plugin_chehui", "Jinhong270", "消息撤回插件", "1.0.0")
class RecallPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

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

        msg = event.message_str.strip()
        parts = msg.split(maxsplit=1)
        num = 10
        if len(parts) >= 2:
            try:
                num = int(parts[1])
            except ValueError:
                pass
        num = max(1, min(num, 200))

        fetch_count = min(num * 3, 500)
        try:
            result = await event.bot.call_action(
                "get_group_msg_history",
                group_id=int(group_id),
                count=fetch_count
            )
            messages = result.get("messages", []) if isinstance(result, dict) else []
        except Exception:
            yield event.plain_result("获取消息历史失败，请确认适配器为aiocqhttp")
            return

        if not messages:
            yield event.plain_result("没有可撤回的消息")
            return

        bot_messages = [
            m for m in messages
            if str(m.get("sender", {}).get("user_id", "")) == self_id
        ]
        bot_messages.sort(key=lambda x: x.get("time", 0), reverse=True)
        target_messages = bot_messages[:num]

        if not target_messages:
            yield event.plain_result(f"最近 {num} 条消息中没有我发送的内容")
            return

        success = 0
        for msg in target_messages:
            message_id = msg.get("message_id")
            if not message_id:
                continue
            try:
                await event.bot.delete_msg(message_id=message_id)
                success += 1
                await asyncio.sleep(0.2)
            except Exception:
                continue

        yield event.plain_result(f"已从 {num} 条消息中撤回 {success} 条")
