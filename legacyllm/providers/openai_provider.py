from openai import OpenAI, AsyncOpenAI
from openai import AuthenticationError, RateLimitError, NotFoundError, APIConnectionError, BadRequestError
from dotenv import load_dotenv

load_dotenv()

_client = None
_async_client = None


def client():
    global _client
    if _client is None:
        _client = OpenAI()
    return _client


def async_client():
    global _async_client
    if _async_client is None:
        _async_client = AsyncOpenAI()
    return _async_client


def _build_params(model, messages, max_tokens, temperature, system, tools, kwargs):
    params = {
        "model": model,
        "input": messages,
        "max_output_tokens": max_tokens,
    }
    if system:
        params["instructions"] = system
    if temperature is not None:
        params["temperature"] = temperature
    if tools:
        params["tools"] = tools
    params.update(kwargs)
    return params


def _usage(response):
    return {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "total_tokens": response.usage.total_tokens,
    }


def chat(model, messages, max_tokens=1024, temperature=None, system=None, stream=False, tools=None, **kwargs):
    params = _build_params(model, messages, max_tokens, temperature, system, tools, kwargs)
    try:
        if stream:
            def stream_gen():
                with client().responses.stream(**params) as s:
                    for chunk in s.text_deltas:
                        yield chunk
            return stream_gen()

        response = client().responses.create(**params)
        return response.output_text, _usage(response)

    except AuthenticationError:
        raise RuntimeError("[legacyllm] OpenAI: invalid API key. Check your OPENAI_API_KEY.")
    except RateLimitError:
        raise RuntimeError("[legacyllm] OpenAI: rate limit hit. Slow down requests or upgrade your plan.")
    except NotFoundError:
        raise RuntimeError(f"[legacyllm] OpenAI: model '{model}' not found. Call legacyllm.params('openai') for help.")
    except APIConnectionError:
        raise RuntimeError("[legacyllm] OpenAI: connection failed. Check your internet connection.")
    except BadRequestError as e:
        raise RuntimeError(f"[legacyllm] OpenAI: bad request — {e}")


async def async_chat(model, messages, max_tokens=1024, temperature=None, system=None, stream=False, tools=None, **kwargs):
    params = _build_params(model, messages, max_tokens, temperature, system, tools, kwargs)
    try:
        if stream:
            async def stream_gen():
                async with async_client().responses.stream(**params) as s:
                    async for chunk in s.text_deltas:
                        yield chunk
            return stream_gen()

        response = await async_client().responses.create(**params)
        return response.output_text, _usage(response)

    except AuthenticationError:
        raise RuntimeError("[legacyllm] OpenAI: invalid API key. Check your OPENAI_API_KEY.")
    except RateLimitError:
        raise RuntimeError("[legacyllm] OpenAI: rate limit hit. Slow down requests or upgrade your plan.")
    except NotFoundError:
        raise RuntimeError(f"[legacyllm] OpenAI: model '{model}' not found. Call legacyllm.params('openai') for help.")
    except APIConnectionError:
        raise RuntimeError("[legacyllm] OpenAI: connection failed. Check your internet connection.")
    except BadRequestError as e:
        raise RuntimeError(f"[legacyllm] OpenAI: bad request — {e}")
