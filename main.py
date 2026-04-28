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
        self_id = event.get_self_id()

        msg = event.message_str.strip()
        parts = msg.split(maxsplit=1)
        num = 10
        if len(parts) >= 2:
            try:
                num = int(parts[1])
            except ValueError:
                pass
        num = max(1, min(num, 50))

        raw = event.message_obj.raw_message
        message_id = raw.get('message_id')
        current_seq = raw.get('message_seq')
        if current_seq is None and message_id:
            try:
                msg_data = await event.adapter.call_api('get_msg', message_id=message_id)
                current_seq = msg_data.get('message_seq')
            except Exception:
                yield event.plain_result("获取消息序号失败")
                return

        if current_seq is None:
            yield event.plain_result("无法获取消息序号")
            return

        fetch_count = min(num * 2, 100)
        try:
            history = await event.adapter.call_api(
                'get_group_msg_history',
                group_id=group_id,
                message_seq=current_seq - 1,
                count=fetch_count
            )
        except Exception:
            yield event.plain_result("获取历史消息失败，请确认适配器支持历史消息 API")
            return

        messages = history.get('messages', [])
        if not messages:
            yield event.plain_result("没有可撤回的消息")
            return

        bot_messages = [m for m in messages if m.get('sender', {}).get('user_id') == self_id]
        target_messages = bot_messages[:num]

        if not target_messages:
            yield event.plain_result(f"最近 {num} 条消息中没有机器人发送的内容")
            return

        success = 0
        for msg in target_messages:
            try:
                await event.adapter.call_api('delete_msg', message_id=msg['message_id'])
                success += 1
                await asyncio.sleep(0.2)
            except Exception:
                continue

        yield event.plain_result(f"已从 {num} 条消息中撤回 {success} 条")
