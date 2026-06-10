from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError
from dotenv import load_dotenv

load_dotenv()

_client = None


def client():
    global _client
    if _client is None:
        _client = genai.Client()
    return _client


def _convert_messages(messages: list) -> list:
    contents = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
    return contents


def _build_config(max_tokens, temperature, system, tools):
    config = types.GenerateContentConfig(max_output_tokens=max_tokens)
    if temperature is not None:
        config.temperature = temperature
    if system:
        config.system_instruction = system
    if tools:
        config.tools = tools
    return config


def _usage(response):
    return {
        "input_tokens": response.usage_metadata.prompt_token_count,
        "output_tokens": response.usage_metadata.candidates_token_count,
        "total_tokens": response.usage_metadata.total_token_count,
    }


def _handle_error(e, model):
    if isinstance(e, ClientError):
        s = str(e)
        if "API_KEY" in s or "403" in s:
            return RuntimeError("[modelguard] Google: invalid API key. Check your GEMINI_API_KEY.")
        if "404" in s:
            return RuntimeError(f"[modelguard] Google: model '{model}' not found. Call modelguard.params('google') for help.")
        if "400" in s:
            return RuntimeError(f"[modelguard] Google: bad request — {e}")
        return RuntimeError(f"[modelguard] Google: client error — {e}")
    if isinstance(e, ServerError):
        return RuntimeError(f"[modelguard] Google: server error — {e}")
    return None


def chat(model, messages, max_tokens=1024, temperature=None, system=None, stream=False, tools=None, **kwargs):
    contents = _convert_messages(messages)
    config = _build_config(max_tokens, temperature, system, tools)
    try:
        if stream:
            def stream_gen():
                for chunk in client().models.generate_content_stream(model=model, contents=contents, config=config):
                    if chunk.text:
                        yield chunk.text
            return stream_gen()

        response = client().models.generate_content(model=model, contents=contents, config=config)
        return response.text, _usage(response)

    except (ClientError, ServerError) as e:
        raise _handle_error(e, model)


async def async_chat(model, messages, max_tokens=1024, temperature=None, system=None, stream=False, tools=None, **kwargs):
    contents = _convert_messages(messages)
    config = _build_config(max_tokens, temperature, system, tools)
    try:
        if stream:
            async def stream_gen():
                async for chunk in await client().aio.models.generate_content_stream(model=model, contents=contents, config=config):
                    if chunk.text:
                        yield chunk.text
            return stream_gen()

        response = await client().aio.models.generate_content(model=model, contents=contents, config=config)
        return response.text, _usage(response)

    except (ClientError, ServerError) as e:
        raise _handle_error(e, model)
