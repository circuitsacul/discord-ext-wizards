from typing import Awaitable, Callable

import discord


class SpecialTypeClass:
    pass


MISSING = SpecialTypeClass()
ACTION = Callable[[discord.Message], Awaitable[None]]
