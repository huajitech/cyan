import asyncio

from cyan import Session, Ticket


async def main():
    api = "https://sandbox.api.sgroup.qq.com/"
    app_id = input("请输入 APP ID: ")
    token = input("请输入 Token: ")

    session = Session(api, Ticket(app_id, token))

    current_user = await session.get_current_user()
    print(
        f"ID: {current_user.identifier}, Name: {current_user.name}, "
        f"Bot: {current_user.bot}"
    )

    await session.close()

asyncio.run(main())
