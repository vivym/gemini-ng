# Next-generation Gemini API Client

A human-friendly API client for the Gemini API, with support for text, image, and video inputs.

## Installation

```bash
pip install -U gemini-ng
```

## Usage

1. Set the `GEMINI_NG_API_KEY` environment variable with your [Google AI Studio API key](https://aistudio.google.com/app/apikey).

2. Use the client to interact with the Gemini API.

```python
from gemini_ng import GeminiClient

client = GeminiClient() # api key from environment variable `GEMINI_NG_API_KEY`

with client.start_chat(model="models/gemini-1.5-pro-latest") as chat:
    image = client.upload_image("path/to/image.jpg")
    video = client.upload_video("path/to/video.mp4", verbose=True)

    prompt = [
        video,
        image,
        "Describe the scene in the video and the image above in detail.",
    ]
    rsp = chat.send_message(prompt)

    print(rsp.candidates[0].text)
```

## License

This project is licensed under the terms of the MIT license. See the [LICENSE](LICENSE) file for details.
