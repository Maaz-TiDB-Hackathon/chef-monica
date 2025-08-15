from langchain.tools import BaseTool
from typing import ClassVar
import streamlit as st

class ImageDisplayTool(BaseTool):
    name: ClassVar[str] = "display_image"
    description: ClassVar[str] = "Displays an image in the chat UI given an image URL."

    def _run(self, image_url: str) -> str:
        # Return HTML img tag that Streamlit can render
        display_image(image_url=image_url, role='assistant')

    async def _arun(self, image_url: str) -> str:
        return self._run(image_url)
