from typing import Any, Awaitable, Callable

import discord


ACTION = Callable[[discord.Message], Awaitable[None]]
STEP = Callable[[discord.Message], Awaitable[Any]]
