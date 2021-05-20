from setuptools import setup

from discord.ext.wizards import __version__

setup(
    name="discord-ext-wizards",
    author="Circuit",
    url="https://github.com/CircuitsBots/discord-ext-wizards",
    version=__version__,
    packages=["discord.ext.wizards"],
    license="MIT",
    description="A module for making setup wizards easily.",
    install_request=["discord.py>=1.2.5"],
    python_requires=">=3.5.3",
)
