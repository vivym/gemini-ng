import hashlib
import os
import tempfile

import requests
import googleapiclient.discovery as g_discovery
from tqdm import tqdm

from .chat import ChatSession
from .schemas import (
    ChatMessage,
    ChatHistory,
    GenerationConfig,
    GenerationRequest,
    GenerationRequestParts,
    GenerationResponse,
    SafetySettings,
    TextPart,
    ImagePart,
    FilePart,
    VideoPart,
    UploadFile,
    UploadedFile,
)
from .utils.cache import get_cache_instance
from .utils.error import handle_http_exception
from .utils.video import extract_video_frames


class GeminiClient:
    def __init__(
        self,
        api_key: str | None = None,
        version: str = "v1beta",
    ):
        api_key = api_key or os.getenv("GEMINI_NG_API_KEY")

        if api_key is None:
            raise ValueError("Gemini API (`GEMINI_NG_API_KEY`) key must be provided")

        self.api_key = api_key

        rsp = requests.get(
            "https://generativelanguage.googleapis.com/$discovery/rest",
            params={"version": version, "key": api_key},
        )
        rsp.raise_for_status()

        self.genai_service = g_discovery.build_from_document(
            rsp.content, developerKey=api_key
        )

    @staticmethod
    def normalize_prompt(prompt: list | str) -> list:
        parts = []

        if isinstance(prompt, str):
            prompt = [prompt]

        for i, part in enumerate(prompt):
            if isinstance(part, str):
                parts.append(TextPart(text=part if i == 0 else "\n" + part))
            elif isinstance(part, (TextPart, FilePart, ImagePart)):
                parts.append(part)
            elif isinstance(part, VideoPart):
                parts.extend(part.content_parts())
            else:
                raise ValueError(f"Invalid prompt part type: {type(part)} ({part})")

        return parts

    @handle_http_exception
    def get_token_count(self, model: str, prompt: GenerationRequest | list) -> int:
        if isinstance(prompt, GenerationRequest):
            request = prompt
        else:
            parts = self.normalize_prompt(prompt)
            request = GenerationRequest(contents=[GenerationRequestParts(parts=parts)])

        rsp = (
            self.genai_service
                .models()
                .getTokenCount(
                    model=model,
                    body=request.model_dump(by_alias=True, exclude_none=True),
                )
                .execute()
        )

        return rsp["totalTokens"]

    @handle_http_exception
    def generate(
        self,
        model: str,
        prompt: GenerationRequest | ChatHistory | list | str,
        generation_config: GenerationConfig | dict | None = None,
        safety_settings: SafetySettings | dict | None = None,
    ) -> GenerationResponse:
        generation_request = self._prepare_generation_request(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings,
        )

        rsp = (
            self.genai_service
                .models()
                .generateContent(
                    model=model,
                    body=generation_request.model_dump(by_alias=True, exclude_none=True),
                )
                .execute()
        )

        return GenerationResponse.model_validate(rsp)

    def start_chat(
        self,
        model: str,
        history: list[ChatMessage] | ChatHistory | None = None,
        generation_config: GenerationConfig | dict | None = None,
        safety_settings: SafetySettings | dict | None = None,
    ) -> ChatSession:
        if isinstance(history, ChatHistory):
            history = history.messages

        return ChatSession(
            self,
            model,
            history=history,
            generation_config=generation_config,
            safety_settings=safety_settings,
        )

    def _prepare_generation_request(
        self,
        prompt: GenerationRequest | ChatHistory | list | str,
        generation_config: GenerationConfig | dict | None = None,
        safety_settings: SafetySettings | dict | None = None,
    ) -> GenerationRequest:
        if isinstance(prompt, GenerationRequest):
            request = prompt
        elif isinstance(prompt, ChatHistory):
            request = GenerationRequest(contents=prompt.messages)
        else:
            parts = self.normalize_prompt(prompt)
            request = GenerationRequest(
                contents=[GenerationRequestParts(parts=parts)]
            )

        if generation_config is not None:
            if not isinstance(generation_config, GenerationConfig):
                generation_config = GenerationConfig.model_validate(generation_config)
            request.generation_config = generation_config

        if safety_settings is not None:
            if not isinstance(safety_settings, SafetySettings):
                safety_settings = SafetySettings.model_validate(safety_settings)
            request.safety_settings = safety_settings

        return request

    def upload_image(self, image_path: str) -> ImagePart:
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        uploaded_file = self._upload_file(
            UploadFile.from_path(
                image_path,
                body={"file": {"displayName": os.path.basename(image_path)}},
            )
        )

        return uploaded_file.to_file_part()

    def upload_video(self, video_path: str, verbose: bool = False) -> VideoPart:
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        if os.path.isdir(video_path):
            frame_paths = os.listdir(video_path)
            frame_paths = filter(
                lambda x: x.lower().endswith((".jpg", ".jpeg", ".png")), frame_paths
            )
            frame_paths = sorted(
                frame_paths, key=lambda x: int(os.path.splitext(x)[0])
            )

            image_parts = [
                self.upload_image(os.path.join(video_path, frame_path))
                for frame_path in tqdm(
                    frame_paths, disable=not verbose, desc="Uploading video frames"
                )
            ]
        else:
            with tempfile.TemporaryDirectory() as temp_dir:
                frame_paths = extract_video_frames(
                    video_path, save_dir=temp_dir, sample_fps=1
                )

                image_parts = [
                    self.upload_image(frame_path)
                    for frame_path in tqdm(
                        frame_paths, disable=not verbose, desc="Uploading video frames"
                    )
                ]

        return VideoPart(
            time_spans=[
                TextPart(text=f"{i // 60:02d}:{i % 60:02d}")
                for i in range(len(image_parts))
            ],
            frames=image_parts,
        )

    @handle_http_exception
    def _upload_file(self, file: UploadFile) -> UploadedFile:
        m = hashlib.sha256()
        with open(file.file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                m.update(chunk)

        sha256_hash = m.hexdigest()
        cache_key = f"{self.api_key}_file_{sha256_hash}"

        cache = get_cache_instance()
        cached_obj = cache.get(cache_key)
        if cached_obj:
            return UploadedFile.model_validate(cached_obj)

        rsp = (
            self.genai_service.media()
            .upload(
                media_body=file.file_path,
                media_mime_type=file.mime_type,
                body=file.body,
            )
            .execute()
        )

        uploaded_file = UploadedFile.model_validate(rsp["file"])

        cache.set(cache_key, uploaded_file.model_dump(by_alias=True, exclude_none=True))

        return uploaded_file

    def _upload_files(self, *files: list[UploadFile]) -> list[UploadedFile]:
        return [self._upload_file(file) for file in files]
