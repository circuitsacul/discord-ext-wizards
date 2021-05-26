# discord-ext-wizards
A module for creating setup wizards easily.

For support, please join https://discord.gg/dGAzZDaTS9.

## Instalation:
Run `pip install --upgrade discord-ext-wizards` to install.

## Example Usage
Below is an example usage of discord-ext-wizards to create an interactive embed builder.
```python
import discord
from discord.ext import wizards, commands


class EmbedBuilderWizard(wizards.Wizard):
    def __init__(self):
        self.result = {}
        super().__init__(cleanup_after=False, timeout=30.0)

    # register an action, so users can type "stop" or "cancel" to stop
    # the wizard
    @wizards.action("stop", "cancel")
    async def cancel_wizard(self, message):
        await self.send("Wizard Cancelled.")
        await self.stop(wizards.StopReason.CANCELLED)

    @wizards.step(
        "What should the embed title be?",
        position=1
    )
    async def embed_title(self, message):
        self.result["title"] = message.content

    @wizards.step(
        "What should the embed description be?",
        timeout=180.0,  # override the default timeout of 30
        position=2,
    )
    async def embed_description(self, message):
        length = len(message.content)
        if length > 2000:
            await self.send(
                f"That description is {length} chars, but the maximum is 2000."
            )
            return await self.do_step(self.embed_description)  # redo the step
        self.result["description"] = message.content

    @wizards.step(
        "Type 1 to add a field, or 2 to move on.",
        position=3,
    )
    async def embed_fields(self, message):
        self.result.setdefault("fields", [])
        if message.content == "2":
            pass  # move on to the next step
        elif message.content == "1":
            field_name = await self.do_step(self.embed_field_name)
            field_value = await self.do_step(self.embed_field_value)
            field_inline = await self.do_step(self.embed_field_inline)
            self.result["fields"].append(
                (field_name, field_value, field_inline)
            )

            # repeat the step, so users can add multiple fields
            return await self.do_step(self.embed_fields)
        else:
            await self.send("Please choose 1 or 2.")
            return await self.do_step(self.embed_fields)

    @wizards.step(
        "What should the field name be?",
        call_internally=False,
    )
    async def embed_field_name(self, message):
        return message.content

    @wizards.step(
        "What should the field description be?",
        call_internally=False,
    )
    async def embed_field_value(self, message):
        return message.content

    @wizards.step(
        "Should the field be inline?",
        call_internally=False,
    )
    async def embed_field_inline(self, message):
        if message.content.lower().startswith("y"):
            return True
        elif message.content.lower().startswith("n"):
            return False
        else:
            await self.send("Please choose yes or no.")
            return await self.do_step(self.embed_field_inline)


bot = commands.Bot("!")


@bot.command()
async def embed(ctx):
    wizard = EmbedBuilderWizard()
    await wizard.start(ctx)
    result = wizard.result

    embed = discord.Embed(
        title=result["title"],
        description=result["description"],
    )
    for name, value, inline in result["fields"]:
        embed.add_field(name=name, value=value, inline=inline)

    await ctx.send(embed=embed)


bot.run("TOKEN")
```
See here for the output of the code: https://circuit.is-from.space/kox47xokm9a.mov
