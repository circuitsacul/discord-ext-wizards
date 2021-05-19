from typing import Callable, Awaitable

import discord


class SpecialTypeClass:
    pass


MISSING = SpecialTypeClass()
ACTION = Callable[[discord.Message], Awaitable[None]]
