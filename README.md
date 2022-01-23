<div align="center">
    <img src="logo.png" width="200" alt="cyan">
</div>

## 简介

Cyan 是一个 Python QQ 机器人 SDK，基于 Python 的类型注解和异步特性。

## 特性

- 异步操作：使用 `httpx`、`websockets` 异步框架及 Python 的异步特性
- 化繁为简：简化 API 繁琐的操作，使用户容易上手
- 类型注释：SDK 100% 使用类型注解，通过 `Pyright` 的**严格**检查，用户可使用支持类型检查的 IDE 减少 Bug 出现的可能性
- 支持扩展：SDK 开放与 API 交互的函数，用户可通过提供的函数与 API 交互，实现 SDK 未实现的功能

## 示例

```py
from cyan import Session, Ticket
from cyan.event.events import ChannelMessageReceivedEvent
from cyan.model import Message

session = Session(
    "https://sandbox.api.sgroup.qq.com/",
    Ticket("{app_id}", "{token}")
)


@session.on(ChannelMessageReceivedEvent)
async def message_received(data: Message):
    await data.reply("收到消息：\n", data)

session.run()
```

[更多](example)
