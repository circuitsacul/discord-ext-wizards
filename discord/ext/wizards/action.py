from typing import Callable, List

from discord.ext.wizards.constants import ACTION


def action(*names: List[str]) -> Callable[[ACTION], ACTION]:
    def predicate(function: ACTION) -> ACTION:
        function.__action_triggers__ = names
        return function

    return predicate
