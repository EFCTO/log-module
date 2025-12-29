# log-module
디스코드 봇 파이썬 로깅 모듈

# 사용방법
각 모듈을 `register(bot)` 호출 에제
```python
import discord
from discord.ext import commands

import member_update
import message_delete
import message_update
import user_update

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True  # 내용 로그가 필요하면

bot = commands.Bot(command_prefix="!", intents=intents)

# 이벤트 리스너 등록
member_update.register(bot)
message_delete.register(bot)
message_update.register(bot)
user_update.register(bot)

bot.run("YOUR_TOKEN")
```

MANAGEMENT_LOG_CHANNEL_ID 환경변수 호출
