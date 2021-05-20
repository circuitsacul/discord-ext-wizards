import traceback
from typing import Any, Dict, List, Optional

from discord.ext.commands import Context

import discord
from discord.ext.wizards.constants import ACTION
from discord.ext.wizards.step import Step
from discord.ext.wizards.stopreason import StopReason


class Wizard:
    def __init__(self, cleanup_after: bool = True, timeout: float = 180.0):
        self._ctx: Optional[Context] = None
        self._running = True
        self._steps: List["Step"] = []
        self._actions: Dict[str, "ACTION"] = {}
        self._to_cleanup: List[int] = []

        self.timeout = timeout
        self.cleanup_after = cleanup_after
        self.stop_reason: Optional[StopReason] = None

        for attr_name in dir(self):
            attr = self.__getattribute__(attr_name)
            if isinstance(attr, Step):
                self._steps.append(attr)
            else:
                try:
                    names = attr.__action_triggers__
                except AttributeError:
                    pass
                else:
                    for n in names:
                        self._actions[n] = attr

        self._steps.sort(key=lambda s: s.index)

    async def start(self, ctx: Context) -> Dict[str, Any]:
        self._ctx = ctx
        await self._internal_loop()
        if self.cleanup_after:
            await self.cleanup()

    async def stop(self, reason: Optional[StopReason] = None):
        self.stop_reason = reason
        self._running = False

    async def cleanup(self):
        def check(m: discord.Message) -> bool:
            return m.id in self._to_cleanup

        try:
            await self._ctx.channel.purge(limit=200, check=check)
        except discord.Forbidden:
            for mid in self._to_cleanup:
                mobj = self._ctx.channel.get_partial_message(mid)
                try:
                    await mobj.delete()
                except (discord.NotFound, discord.Forbidden):
                    pass

    async def send(self, *args, **kwargs) -> discord.Message:
        m = await self._ctx.send(*args, **kwargs)
        self._to_cleanup.append(m.id)
        return m

    async def do_step(self, step: "Step") -> Any:
        return await step.do_step(self)

    async def on_step_error(self, step: "Step", err: Exception):
        traceback.print_exception(err.__class__, err, err.__traceback__)
        await self.stop(StopReason.ERROR)

    async def on_action_error(self, action: "ACTION", err: Exception):
        traceback.print_exception(err.__class__, err, err.__traceback__)
        await self.stop(StopReason.ERROR)

    async def _internal_loop(self):
        current_step = 0
        while self._running and current_step < len(self._steps):
            step = self._steps[current_step]
            current_step += 1
            if not step.call_internally:
                continue

            await step.do_step(self)
        self._running = False

    def _check_message(self, message: discord.Message) -> bool:
        return message.author.id == self._ctx.author.id
