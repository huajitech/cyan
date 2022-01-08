import asyncio
from cyan.model.channel import TextChannel

from cyan.bot import Bot, Ticket


async def main():
    api = "https://sandbox.api.sgroup.qq.com/"
    app_id = input("请输入 APP ID: ")
    token = input("请输入 Token: ")

    async with Bot(api, Ticket(app_id, token)) as bot:
        current_user = await bot.get_current_user()
        print(
            "Current User Info:\n "
            f"ID: {current_user.identifier}, Name: {current_user.name}, "
            f"Bot: {current_user.bot}"
        )

        guilds = await bot.get_guilds()
        print(
            "Guilds:\n" + "\n".join([
                f" ID: {guild.identifier}, Name: {guild.name},"
                f" Capacity: {guild.capacity}, Description: {guild.description}"
                for guild in guilds
            ])
        )

        if guilds:
            guild = guilds[0]

            roles = await guild.get_roles()
            print(f"Guild {guild.name} Roles:\n" + "\n".join([
                f" ID: {role.identifier}, Name: {role.name},"
                f" Color: {role.color}, Capacity: {role.capacity}"
                for role in roles
            ]))

            members = await guild.get_members()
            print(f"Guild {guild.name} Members:\n" + "\n".join([
                f" ID: {member.as_user().identifier}, Name: {member.as_user().name},"
                f" Nickname: {member.nickname},"
                f" Roles: {[role.name for role in (await member.get_roles())]},"
                f" Joined Time: {member.joined_time}"
                for member in members
            ]))

            channel_groups = await guild.get_channel_groups()
            print(f"Guild {guild.name} Channel Groups:\n" + "\n".join([
                f" ID: {group.identifier}, Name: {group.name},"
                f" Owner: {getattr(await group.get_owner(), 'nickname', None)}"
                for group in channel_groups
            ]))

            channels = await guild.get_channels()
            print(f"Guild {guild.name} Channels:\n" + "\n".join([
                f" ID: {channel.identifier}, Name: {channel.name},"
                f" Type: {channel.__class__.__name__}, " + (
                    f" SubType: {channel.text_channel_type},"
                    if isinstance(channel, TextChannel) else ""
                ) + f" Parent: {(await channel.get_parent()).name},"
                f" Owner: {getattr(await channel.get_owner(), 'nickname', None)}"
                for channel in channels
            ]))

asyncio.run(main())
