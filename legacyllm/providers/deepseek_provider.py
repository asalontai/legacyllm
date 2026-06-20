from openai import OpenAI, AsyncOpenAI
from openai import AuthenticationError, RateLimitError, NotFoundError, APIConnectionError, BadRequestError
from dotenv import load_dotenv
import os

load_dotenv()

_client = None
_async_client = None


def client():
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )
    return _client


def async_client():
    global _async_client
    if _async_client is None:
        _async_client = AsyncOpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com",
        )
    return _async_client


def _build_params(model, messages, max_tokens, temperature, system, tools, kwargs):
    final_messages = []

    if system:
        final_messages.append({"role": "system", "content": system})

    final_messages.extend(messages)

    params = {
        "model": model,
        "messages": final_messages,
        "max_tokens": max_tokens,
    }

    if temperature is not None:
        params["temperature"] = temperature
    if tools:
        params["tools"] = tools

    params.update(kwargs)
    return params


def _usage(response):
    usage = response.usage
    return {
        "input_tokens": usage.prompt_tokens,
        "output_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
    }


def chat(model, messages, max_tokens=1024, temperature=None, system=None, stream=False, tools=None, **kwargs):
    params = _build_params(model, messages, max_tokens, temperature, system, tools, kwargs)

    try:
        if stream:
            def stream_gen():
                response = client().chat.completions.create(**params, stream=True)
                for chunk in response:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content
            return stream_gen()

        response = client().chat.completions.create(**params)
        return response.choices[0].message.content, _usage(response)

    except AuthenticationError:
        raise RuntimeError("[legacyllm] DeepSeek: invalid API key. Check your DEEPSEEK_API_KEY.")
    except RateLimitError:
        raise RuntimeError("[legacyllm] DeepSeek: rate limit hit. Slow down requests or upgrade your plan.")
    except NotFoundError:
        raise RuntimeError(f"[legacyllm] DeepSeek: model '{model}' not found. Call legacyllm.params('deepseek') for help.")
    except APIConnectionError:
        raise RuntimeError("[legacyllm] DeepSeek: connection failed. Check your internet connection.")
    except BadRequestError as e:
        raise RuntimeError(f"[legacyllm] DeepSeek: bad request — {e}")


async def async_chat(model, messages, max_tokens=1024, temperature=None, system=None, stream=False, tools=None, **kwargs):
    params = _build_params(model, messages, max_tokens, temperature, system, tools, kwargs)

    try:
        if stream:
            async def stream_gen():
                response = await async_client().chat.completions.create(**params, stream=True)
                async for chunk in response:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content
            return stream_gen()

        response = await async_client().chat.completions.create(**params)
        return response.choices[0].message.content, _usage(response)

    except AuthenticationError:
        raise RuntimeError("[legacyllm] DeepSeek: invalid API key. Check your DEEPSEEK_API_KEY.")
    except RateLimitError:
        raise RuntimeError("[legacyllm] DeepSeek: rate limit hit. Slow down requests or upgrade your plan.")
    except NotFoundError:
        raise RuntimeError(f"[legacyllm] DeepSeek: model '{model}' not found. Call legacyllm.params('deepseek') for help.")
    except APIConnectionError:
        raise RuntimeError("[legacyllm] DeepSeek: connection failed. Check your internet connection.")
    except BadRequestError as e:
        raise RuntimeError(f"[legacyllm] DeepSeek: bad request — {e}")