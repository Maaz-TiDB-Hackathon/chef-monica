from langchain.tools import BaseTool
from typing import ClassVar
import streamlit as st
from utils import write_message

class TextDisplayTool(BaseTool):
    name: ClassVar[str] = "display_text"
    description: ClassVar[str] = "Displays text in the chat UI given an image URL."

    def _run(self, content: str) -> str:
        # Return HTML img tag that Streamlit can render
        write_message(role='assistant', content=content, save=True)

    async def _arun(self, image_url: str) -> str:
        return self._run(image_url)
