from typing import TYPE_CHECKING

from .schemas import (
    ChatMessage, ChatHistory, GenerationConfig, GenerationResponse, SafetySettings
)


if TYPE_CHECKING:
    from .client import GeminiClient


class ChatSession:
    def __init__(
        self,
        client: "GeminiClient",
        model: str,
        history: list[ChatMessage] | None = None,
        generation_config: GenerationConfig | dict | None = None,
        safety_settings: SafetySettings | dict | None = None,
    ):
        self.client = client
        self.model = model
        self.history = history or []
        self.generation_config = generation_config
        self.safety_settings = safety_settings

    def send_message(
        self,
        message: list | str,
        generation_config: GenerationConfig | dict | None = None,
        safety_settings: SafetySettings | dict | None = None,
    ) -> GenerationResponse:
        parts = self.client.normalize_prompt(message)
        self.history.append(ChatMessage(role="user", parts=parts))

        rsp = self.client.generate(
            self.model,
            ChatHistory(messages=self.history),
            generation_config=generation_config or self.generation_config,
            safety_settings=safety_settings or self.safety_settings,
        )
        if len(rsp.candidates) > 0 and rsp.candidates[0].content is not None:
            rsp_parts = rsp.candidates[0].content.parts
            self.history.append(ChatMessage(role="model", parts=rsp_parts))

        return rsp

    def clear(self):
        self.history = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.clear()
