from typing import Callable, Awaitable, Any, Optional, TYPE_CHECKING, Union

import discord

if TYPE_CHECKING:
    from discord.ext.wizards.wizard import Wizard


class SpecialTypeClass:
    pass


MISSING = SpecialTypeClass()


class Step:
    def __init__(
        self,
        index: int,
        action: Callable[["Step", discord.Message], Awaitable[Any]],
        name: str,
        call_internally: bool,
        description: Union[Callable[["Step"], str], str],
    ):
        self.index = index
        self.action = action
        self.name = name
        self.description = description
        self.call_internally = call_internally
        self.result = MISSING

    async def do_step(self, wizard: "Wizard") -> Any:
        try:
            return await self._do_step(wizard)
        except Exception as e:
            return await wizard.on_step_error(self, e)

    async def _do_step(self, wizard: "Wizard") -> Any:
        if isinstance(self.description, str):
            desc = self.description
        else:
            desc = self.description(wizard, self)
        await wizard.send(desc)
        message = await wizard._ctx.bot.wait_for(
            "message", check=wizard._check_message
        )
        wizard._to_cleanup.append(message.id)
        if message.content in wizard._actions:
            action = wizard._actions[message.content]
            try:
                return await action(message)
            except Exception as e:
                return await wizard.on_action_error(action, e)
        return await self.action(wizard, self, message)


def step(
    description: Union[str, Callable[[Step], str]],
    name: Optional[str] = None,
    call_internally: bool = True,
    position: int = None,
):
    def predicate(
        action: Callable[["Step", discord.Message], Awaitable[Any]]
    ) -> Step:
        return Step(
            position if position is not None else -1,
            action,
            name or action.__name__,
            call_internally,
            description,
        )
    return predicate
