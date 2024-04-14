# Next-generation Gemini API Client

```python
from gemini_ng import GeminiClient

client = GeminiClient() # api key from environment variable `GEMINI_API_KEY`

with client.start_chat(model="models/gemini-1.5-pro-latest") as chat:
    image = client.upload_image("path/to/image.jpg")

    rsp = chat.send_message([image, "Can you describe this image?"])

    print(rsp)
```
