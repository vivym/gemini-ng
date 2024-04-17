import typing

from pydantic import Field

from .base import BaseModel
from .harm import HarmCategory, HarmBlockThreshold
from .part import TextPart, FilePart


class ChatMessage(BaseModel):
    role: typing.Literal["model", "user"] = Field(
        ..., description="Role of the author of the parts."
    )
    parts: list[TextPart | FilePart] = Field(
        ..., description="Parts of the chat message."
    )


class ChatHistory(BaseModel):
    messages: list[ChatMessage] = Field(
        ..., description="History of chat messages."
    )


class GenerationRequestParts(BaseModel):
    parts: list[TextPart | FilePart] = Field(
        ..., description="Parts of the request."
    )


class GenerationConfig(BaseModel):
    stop_sequences: list[str] | None = Field(
        None,
        alias="stopSequences",
        description="The set of character sequences (up to 5) that will stop output generation.",
    )

    candidate_count: int | None = Field(
        None,
        alias="candidateCount",
        description=(
            "Number of generated responses to return. This value must be between [1, 8], inclusive. "
            "If unset, this will default to 1."
        ),
    )

    max_output_tokens: int | None = Field(
        None,
        alias="maxOutputTokens",
        description=(
            "The maximum number of tokens to generate. The default value varies by model, see the "
            "Model.output_token_limit attribute of the Model returned from the `get_model` function."
        ),
    )

    temperature: float | None = Field(
        None,
        description=(
            "Controls randomness in generation. Lower values make the model more deterministic. "
            "High values make the model more creative."
        ),
    )

    top_p: float | None = Field(
        None,
        alias="topP",
        description="The maximum cumulative probability of tokens to consider when sampling.",
    )

    top_k: int | None = Field(
        None,
        alias="topK",
        description="The maximum number of tokens to consider when sampling.",
    )


class SafetySetting(BaseModel):
    category: HarmCategory | None = Field(
        None, description="The category of harmful content to block."
    )

    threshold: HarmBlockThreshold | None = Field(
        None, description="The threshold of harmful content to block."
    )


class GenerationRequest(BaseModel):
    contents: list[GenerationRequestParts | ChatMessage] | dict = Field(
        ..., description="Contents of the request."
    )

    generation_config: GenerationConfig | dict | None = Field(
        None, alias="generationConfig", description="Generation configuration."
    )

    safety_settings: list[SafetySetting | dict] | None = Field(
        None, alias="safetySettings", description="Safety settings."
    )
