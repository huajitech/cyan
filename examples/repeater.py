"""
复读机示例。
"""

from cyan import Session, Ticket
from cyan.event import ChannelMessageReceivedEvent
from cyan.model import ChannelMessage

session = Session(
    "https://sandbox.api.sgroup.qq.com/",
    Ticket("{app_id}", "{token}")
)


@session.on(ChannelMessageReceivedEvent)
async def message_received(data: ChannelMessage):
    await data.reply(data)

session.run()
