from anthropic import Anthropic, AsyncAnthropic
from anthropic import AuthenticationError, RateLimitError, NotFoundError, APIConnectionError, BadRequestError
from dotenv import load_dotenv

load_dotenv()

_client = None
_async_client = None


def client():
    global _client
    if _client is None:
        _client = Anthropic()
    return _client


def async_client():
    global _async_client
    if _async_client is None:
        _async_client = AsyncAnthropic()
    return _async_client


def _build_params(model, messages, max_tokens, temperature, system, tools, kwargs):
    params = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }
    if temperature is not None:
        params["temperature"] = temperature
    if system:
        params["system"] = system
    if tools:
        params["tools"] = tools
    params.update(kwargs)
    return params


def _usage(response):
    return {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
    }


def chat(model, messages, max_tokens=1024, temperature=None, system=None, stream=False, tools=None, **kwargs):
    params = _build_params(model, messages, max_tokens, temperature, system, tools, kwargs)
    try:
        if stream:
            def stream_gen():
                with client().messages.stream(**params) as s:
                    for chunk in s.text_stream:
                        yield chunk
            return stream_gen()

        response = client().messages.create(**params)
        return response.content[0].text, _usage(response)

    except AuthenticationError:
        raise RuntimeError("[legacyllm] Anthropic: invalid API key. Check your ANTHROPIC_API_KEY.")
    except RateLimitError:
        raise RuntimeError("[legacyllm] Anthropic: rate limit hit. Slow down requests or upgrade your plan.")
    except NotFoundError:
        raise RuntimeError(f"[legacyllm] Anthropic: model '{model}' not found. Call legacyllm.params('anthropic') for help.")
    except APIConnectionError:
        raise RuntimeError("[legacyllm] Anthropic: connection failed. Check your internet connection.")
    except BadRequestError as e:
        raise RuntimeError(f"[legacyllm] Anthropic: bad request — {e}")


async def async_chat(model, messages, max_tokens=1024, temperature=None, system=None, stream=False, tools=None, **kwargs):
    params = _build_params(model, messages, max_tokens, temperature, system, tools, kwargs)
    try:
        if stream:
            async def stream_gen():
                async with async_client().messages.stream(**params) as s:
                    async for chunk in s.text_stream:
                        yield chunk
            return stream_gen()

        response = await async_client().messages.create(**params)
        return response.content[0].text, _usage(response)

    except AuthenticationError:
        raise RuntimeError("[legacyllm] Anthropic: invalid API key. Check your ANTHROPIC_API_KEY.")
    except RateLimitError:
        raise RuntimeError("[legacyllm] Anthropic: rate limit hit. Slow down requests or upgrade your plan.")
    except NotFoundError:
        raise RuntimeError(f"[legacyllm] Anthropic: model '{model}' not found. Call legacyllm.params('anthropic') for help.")
    except APIConnectionError:
        raise RuntimeError("[legacyllm] Anthropic: connection failed. Check your internet connection.")
    except BadRequestError as e:
        raise RuntimeError(f"[legacyllm] Anthropic: bad request — {e}")
