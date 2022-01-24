"""
“自闭”示例。
"""

import random
from datetime import timedelta

from cyan import Session, Ticket
from cyan.event import ChannelMessageReceivedEvent
from cyan.exception import OpenApiError
from cyan.model import Message

session = Session(
    "https://sandbox.api.sgroup.qq.com/",
    Ticket("{app_id}", "{token}")
)


@session.on(ChannelMessageReceivedEvent)
async def message_received(data: Message):
    plain_text = data.content.extract_plain_text()
    if plain_text.strip() == "我要自闭":
        member = await data.get_sender_as_member()
        duration = timedelta(minutes=random.randint(10, 60))
        try:
            await member.mute(duration)
            await data.reply("自闭成功 ( • ̀ω•́ )✧")
        except OpenApiError as ex:
            if ex.code == 502008:
                await data.reply("你权限太大了，我把握不住 ╮(╯﹏╰）╭")

session.run()
