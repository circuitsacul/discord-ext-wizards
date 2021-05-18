from typing import Any, Dict, List, Optional

import discord
from discord.ext.commands import Context
from discord.ext.wizards.step import MISSING, Step
from discord.ext.wizards.action import ACTION


class Wizard:
    def __init__(self, cleanup_after: bool = True):
        self._ctx: Optional[Context] = None
        self._running = True
        self._steps: List[Step] = []
        self._actions: Dict[str, ACTION] = {}
        self._to_cleanup: List[int] = []

        self.cleanup_after = cleanup_after
        self.cancelled: bool = False

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
        return self.result

    async def stop(self, cancelled: bool = False):
        self.cancelled = cancelled
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

    @property
    def result(self) -> Dict[str, Any]:
        dct: Dict[str, Any] = {}
        for step in self._steps:
            if step.result is not MISSING:
                dct[step.name] = step.result
        return dct

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
