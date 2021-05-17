import discord
from typing import Awaitable, Callable, List


ACTION = Callable[[discord.Message], Awaitable[None]]


def action(*names: List[str]) -> Callable[[ACTION], ACTION]:
    def predicate(function: ACTION) -> ACTION:
        function.__action_triggers__ = names
        return function
    return predicate
