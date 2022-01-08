import asyncio
from cyan.color import ARGB

from cyan.model.channel import TextChannel
from cyan.bot import Bot, Ticket


async def main():
    api = "https://sandbox.api.sgroup.qq.com/"
    app_id = input("请输入 APP ID：")
    token = input("请输入 Token：")

    async with Bot(api, Ticket(app_id, token)) as bot:
        current_user = await bot.get_current_user()
        print(
            "当前用户信息：\n "
            f"ID: {current_user.identifier}，名称：{current_user.name}，"
            f"是否为机器人：{current_user.bot}"
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
                f"在 {guild.name} 创建频道结果：\n"
                f" ID：{role.identifier}，名称：{role.name}，"
                f"颜色：{role.color}，是否单独展示：{role.shown}"
            )

            await role.set_name("Cyan yyds!")
            await role.set_color(ARGB(0xFF, 0x00, 0xCD, 0xCD))
            await role.show()

            print(
                f"修改角色 {role.identifier} 结果：\n"
                f" ID：{role.identifier}，名称：{role.name}，"
                f"颜色：{role.color}，是否单独展示：{role.shown}"
            )

            roles = await guild.get_roles()
            print(f"Guild {guild.name} Roles：\n" + "\n".join([
                f" ID：{role.identifier}，名称：{role.name}，"
                f"颜色：{role.color}，容量：{role.capacity}，"
                f"是否单独展示：{role.shown}"
                for role in roles
            ]))

            members = await guild.get_members()
            print(f"Guild {guild.name} Members：\n" + "\n".join([
                f" ID：{member.as_user().identifier}，名称：{member.as_user().name}，"
                f"昵称：{member.nickname}，"
                f"身份组：{[role.name for role in (await member.get_roles())]}，"
                f"加入时间：{member.joined_time}"
                for member in members
            ]))

            channel_groups = await guild.get_channel_groups()
            print(f"Guild {guild.name} Channel Groups：\n" + "\n".join([
                f" ID：{group.identifier}，名称：{group.name}，"
                f"创建者：{getattr(await group.get_owner(), 'nickname', None)}"
                for group in channel_groups
            ]))

            channels = await guild.get_channels()
            print(f"Guild {guild.name} Channels：\n" + "\n".join([
                f" ID：{channel.identifier}，名称：{channel.name}，"
                f"类型：{channel.__class__.__name__}，" + (
                    f"文字频道类型：{channel.text_channel_type}，"
                    if isinstance(channel, TextChannel) else ""
                ) + f"附属子频道组：{(await channel.get_parent()).name}，"
                f"创建者：{getattr(await channel.get_owner(), 'nickname', None)}"
                for channel in channels
            ]))

            await role.discard()

asyncio.run(main())
