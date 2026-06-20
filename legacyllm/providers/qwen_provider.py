from dashscope import Generation
from dotenv import load_dotenv
import os

load_dotenv()


def _build_params(model, messages, max_tokens, temperature, system, tools, kwargs):
    final_messages = []

    if system:
        final_messages.append({"role": "system", "content": system})

    final_messages.extend(messages)

    params = {
        "model": model,
        "messages": final_messages,
        "result_format": "message",
    }

    if max_tokens is not None:
        params["max_tokens"] = max_tokens
    if temperature is not None:
        params["temperature"] = temperature
    if tools:
        params["tools"] = tools

    params.update(kwargs)
    return params


def _usage(response):
    usage = getattr(response, "usage", None)
    if not usage:
        return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

    input_tokens = getattr(usage, "input_tokens", 0)
    output_tokens = getattr(usage, "output_tokens", 0)
    total_tokens = getattr(usage, "total_tokens", input_tokens + output_tokens)

    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
    }


def _extract_text(response):
    choices = getattr(response.output, "choices", [])
    if not choices:
        return ""

    message = choices[0].message
    if isinstance(message, dict):
        return message.get("content", "")

    return getattr(message, "content", "")


def chat(model, messages, max_tokens=1024, temperature=None, system=None, stream=False, tools=None, **kwargs):
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise RuntimeError("[legacyllm] Qwen: no API key found. Set DASHSCOPE_API_KEY environment variable.")

    params = _build_params(model, messages, max_tokens, temperature, system, tools, kwargs)
    params["stream"] = stream

    if stream:
        params["incremental_output"] = True

    try:
        response = Generation.call(api_key=api_key, **params)

        if stream:
            def stream_gen():
                for chunk in response:
                    if chunk.status_code != 200:
                        raise RuntimeError(f"[legacyllm] Qwen: API error — {chunk.message}")

                    text = _extract_text(chunk)
                    if text:
                        yield text

            return stream_gen()

        if response.status_code != 200:
            error_msg = getattr(response, "message", "Unknown error")
            raise RuntimeError(f"[legacyllm] Qwen: API error — {error_msg}")

        return _extract_text(response), _usage(response)

    except Exception as e:
        error_str = str(e)

        if "401" in error_str or "Unauthorized" in error_str:
            raise RuntimeError("[legacyllm] Qwen: invalid API key. Check your DASHSCOPE_API_KEY.")
        if "404" in error_str or "Not Found" in error_str:
            raise RuntimeError(f"[legacyllm] Qwen: model '{model}' not found. Call legacyllm.params('qwen') for help.")
        if "429" in error_str or "Rate" in error_str:
            raise RuntimeError("[legacyllm] Qwen: rate limit hit. Slow down requests or upgrade your plan.")
        if "connection" in error_str.lower():
            raise RuntimeError("[legacyllm] Qwen: connection failed. Check your internet connection.")

        raise RuntimeError(f"[legacyllm] Qwen: error — {error_str}")


async def async_chat(model, messages, max_tokens=1024, temperature=None, system=None, stream=False, tools=None, **kwargs):
    return chat(model, messages, max_tokens, temperature, system, stream, tools, **kwargs)