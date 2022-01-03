import asyncio

from cyan import Session, Ticket


async def main():
    api = "https://sandbox.api.sgroup.qq.com/"
    app_id = input("请输入 APP ID: ")
    token = input("请输入 Token: ")

    async with Session(api, Ticket(app_id, token)) as session:
        current_user = await session.get_current_user()
        print(
            "Current User Info:\n "
            f"ID: {current_user.identifier}, Name: {current_user.name}, "
            f"Bot: {current_user.bot}"
        )

        guilds = await session.get_guilds()
        print(
            "Guilds:\n" + "\n".join([
                f" ID: {guild.identifier}, Name: {guild.name},"
                f" Capacity: {guild.capacity}, Description: {guild.description}"
                for guild in guilds
            ])
        )

        if guilds:
            guild = guilds[0]
            members = await guild.get_members()
            print(f"Guild {guild} Members:\n" + "\n".join([
                f" ID: {member.as_user().identifier}, Nickname: {member.nickname},"
                f" Roles: {member.roles}, Joined Time: {member.joined_time}"
                for member in members
            ]))

            channels = await guild.get_channels()
            print("Channels:\n" + "\n".join(
                [
                    f" ID: {channel.identifier}, Name: {channel.name},"
                    f" Type: {channel.channel_type}, SubType: {channel.channel_subtype},"
                    f" Parent: {(await channel.get_parent()).name}"
                    for channel in channels
                ]
            ))

asyncio.run(main())
