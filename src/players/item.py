from abc import abstractmethod
from discord.ext.commands.context import Context
from typing import List
from io import BytesIO


class Item:

    def __init__(self, text: str, context: Context) -> None:
        self.text = text
        self.context = context
    

    @abstractmethod
    def description(self) -> str:
        raise NotImplementedError
    

    @abstractmethod
    def process(self, object) -> BytesIO:
        raise NotImplementedError