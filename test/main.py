import asyncio

from cyan.color import ARGB
from cyan.event.events import (
    ChannelCreatedEvent,
    ChannelDeletedEvent,
    ChannelUpdatedEvent,
    GuildCreatedEvent,
    GuildDeletedEvent,
    GuildUpdatedEvent,
    MemberJoinedEvent,
    MemberUpdatedEvent,
    MemberLeftEvent,
    ChannelMessageReceivedEvent
)
from cyan.model import AppChannel, TextChannel, Channel, Guild, Member
from cyan import Bot, Ticket
from cyan.model.message import Message
from cyan.model.message.elements import PlainText
from cyan.model.message.elements.content import ChannelLink, Mention


api = "https://sandbox.api.sgroup.qq.com/"
app_id = input("请输入 APP ID：")
token = input("请输入 Token：")

bot = Bot(api, Ticket(app_id, token))
event_source = bot.get_event_source()


async def main():
    async with bot:
        await event_source.connect()

        current_user = await bot.get_current_user()
        print(
            "当前用户信息：\n "
            f"ID: {current_user.identifier}，名称：{current_user.name}，"
            f"是否为机器人：{current_user.is_bot}"
        )

        guilds = await bot.get_guilds()
        print(
            "频道：\n" + "\n".join([
                f" ID：{guild.identifier}，名称：{guild.name}，"
                f"容量：{guild.capacity}，描述：{guild.description}"
                for guild in guilds
            ])
        )

        if guilds:
            guild = guilds[0]

            role = await guild.create_role("Foo.Bar", ARGB(0xFF, 0xFF, 0xEE, 0x11), False)

            print(
                f"在 {guild.name} 创建身份组结果：\n"
                f" ID：{role.identifier}，名称：{role.name}，"
                f"颜色：{role.color}，是否单独展示：{role.shown}"
            )

            await role.set_name("Cyan yyds!")
            await role.set_color(ARGB(0xFF, 0x00, 0xCD, 0xCD))
            await role.show()

            print(
                f"修改身份组 {role.identifier} 结果：\n"
                f" ID：{role.identifier}，名称：{role.name}，"
                f"颜色：{role.color}，是否单独展示：{role.shown}"
            )

            roles = await guild.get_roles()
            print(f"频道 {guild.name} 身份组：\n" + "\n".join([
                f" ID：{role.identifier}，名称：{role.name}，"
                f"颜色：{role.color}，容量：{role.capacity}，"
                f"是否单独展示：{role.shown}"
                for role in roles
            ]))

            members = await guild.get_members()
            print(f"频道 {guild.name} 成员：\n" + "\n".join([
                f" ID：{member.as_user().identifier}，名称：{member.as_user().name}，"
                f"昵称：{member.name}，"
                f"身份组：{[role.name for role in (await member.get_roles())]}，"
                f"加入时间：{member.joined_time}"
                for member in members
            ]))

            channel_groups = await guild.get_channel_groups()
            print(f"频道 {guild.name} 子频道组：\n" + "\n".join([
                f" ID：{group.identifier}，名称：{group.name}，"
                f"创建者：{getattr(await group.get_owner(), 'nickname', None)}"
                for group in channel_groups
            ]))

            channels = await guild.get_channels()
            print(f"频道 {guild.name} 子频道：\n" + "\n".join([
                f" ID：{channel.identifier}，名称：{channel.name}，"
                f"类型：{channel.__class__.__name__}，" + (
                    f"文字频道类型：{channel.text_channel_type}，"
                    if isinstance(channel, TextChannel) else ""
                ) + f"附属子频道组：{(await channel.get_parent()).name}，"
                f"创建者：{getattr(await channel.get_owner(), 'nickname', None)}"
                for channel in channels
            ]))

            if channels:
                for channel in channels:
                    if not isinstance(channel, AppChannel):
                        continue
                    schedules = await channel.get_schedules()
                    if not schedules:
                        continue
                    print(f"子频道 {channel.name} 日程：\n" + "\n".join([
                        f" ID：{schedule.identifier}，名称：{schedule.name}，"
                        f"描述：{schedule.description}，开始时间：{schedule.start_time}，"
                        f"结束时间：{schedule.end_time}，"
                        f"创建者：{schedule.creator.as_user().name}，"
                        f"跳转子频道：{getattr(await schedule.get_destination(), 'name', None)}，"
                        f"提醒类型：{schedule.remind_type}"
                        for schedule in schedules
                    ]))
                    break

            await role.discard()

        await event_source.wait_until_stopped()


@event_source.listen(ChannelCreatedEvent)
async def channel_created(data: Channel):
    print(f"子频道 {data.name} 已创建。")


@event_source.listen(ChannelDeletedEvent)
async def channel_deleted(data: Channel):
    print(f"子频道 {data.name} 被删除。")


@event_source.listen(ChannelUpdatedEvent)
async def channel_updated(data: Channel):
    print(f"子频道 {data.name} 资料更新。")


@event_source.listen(GuildCreatedEvent)
async def guild_created(data: Guild):
    print(f"频道 {data.name} 已创建。")


@event_source.listen(GuildDeletedEvent)
async def guild_deleted(data: Guild):
    print(f"频道 {data.name} 被删除。")


@event_source.listen(GuildUpdatedEvent)
async def guild_updated(data: Guild):
    print(f"频道 {data.name} 资料更新。")


@event_source.listen(MemberJoinedEvent)
async def member_joined(data: Member):
    print(f"用户 {data.as_user().name} 加入频道 {data.guild.name}。")


@event_source.listen(MemberLeftEvent)
async def member_left(data: Member):
    print(f"用户 {data.as_user().name} 离开频道 {data.guild.name}。")


@event_source.listen(MemberUpdatedEvent)
async def member_updated(data: Member):
    print(f"用户 {data.as_user().name} 在频道 {data.guild.name} 更新资料。")


@event_source.listen(ChannelMessageReceivedEvent)
async def channel_message_received(data: Message):
    print(
        f"用户 {data.sender.name} 在频道 {(await data.get_guild()).name} 发送消息：\n"
        f"    {''.join(map(str, data.content))}"
    )
    raw_content = data.content
    await data.reply(
        PlainText(
            "我收到了子频道 "
        ) + ChannelLink(
            await data.get_channel()
        ) + PlainText(
            " 用户 "
        ) + Mention(
            data.sender
        ) + PlainText(
            " 的信息，让我来复读一下：\n"
        ) + raw_content
    )


asyncio.run(main())
