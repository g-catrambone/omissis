"""Provider `groq`: the chat-completions API of GroqCloud, over plain HTTPS (task 2.4).

It serves every role pinned with `provider: groq`; the model id of the role is the
Groq model id (for example `openai/gpt-oss-120b`). No SDK is used: the request is
one JSON POST with the standard library.

The key is read from the environment variable `GROQ_API_KEY` (or `API_KEY`), never
from a file: start the command with `uv run --env-file .env ...`. Further keys
(`GROQ_API_KEY2`, `API_KEY2`, ... up to 9) are used in turn when a key hits its rate
limit.

`params` of the request go into the body as they are, except `max_tokens`, which
Groq calls `max_completion_tokens`. A reply that is empty, or cut at the token
limit, is an error and is therefore never cached. When the API answers 429 (rate
limit) or a 5xx (service briefly down) the call waits for the time the API asks, or
ten seconds, and tries again, a few times.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from typing import TYPE_CHECKING, Any

from omissis.config import ConfigError, ModelSpec

if TYPE_CHECKING:
    from omissis.backends import LLMRequest


def _truncated(message: str) -> RuntimeError:
    from omissis.backends import TruncatedReplyError  # defined before this module is imported

    return TruncatedReplyError(message)


URL = "https://api.groq.com/openai/v1/chat/completions"
# The first key, then any further key: GROQ_API_KEY2, API_KEY2, ... up to 9.
KEY_VARIABLES = ("GROQ_API_KEY", "API_KEY") + tuple(
    f"{name}{n}" for n in range(2, 10) for name in ("GROQ_API_KEY", "API_KEY")
)
TIMEOUT_SECONDS = 120
MAX_ATTEMPTS = 6  # one call plus five waits
# Rate limit, and the errors of a service that is briefly down or overloaded.
RETRY_STATUS = (429, 500, 502, 503, 504)
DEFAULT_WAIT_SECONDS = 10.0
MAX_WAIT_SECONDS = 120.0  # a longer wait is a daily limit: stop, do not sleep for hours

_next_key = 0  # index of the key to try first: a key that hit its limit is left behind


def _keys() -> list[str]:
    """Every key set in the environment, without repeats, in the order of `KEY_VARIABLES`."""
    values = [os.environ.get(name, "").strip() for name in KEY_VARIABLES]
    keys = list(dict.fromkeys(v for v in values if v))
    if not keys:
        raise ConfigError(
            f"no Groq API key: set {KEY_VARIABLES[0]} in .env and start the command with "
            "`uv run --env-file .env ...`"
        )
    return keys


def _post(body: dict[str, Any], keys: list[str]) -> dict[str, Any]:
    """POST `body` to the API and return the decoded reply.

    On a rate limit the next key is tried; when every key has been refused in a row,
    on a 5xx and when the API does not answer, the call waits and tries again,
    `MAX_ATTEMPTS` times at most.
    """
    global _next_key
    data = json.dumps(body, ensure_ascii=False).encode("utf-8")
    refused = 0  # keys refused in a row for a rate limit
    for attempt in range(1, MAX_ATTEMPTS + 1):
        while True:
            key = keys[_next_key % len(keys)]
            request = urllib.request.Request(
                URL,
                data=data,
                headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                    "User-Agent": "omissis",
                },
                method="POST",
            )
            try:
                with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                    return json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                if exc.code not in RETRY_STATUS or attempt == MAX_ATTEMPTS:
                    # The status only: the body of an error may quote the prompt.
                    raise RuntimeError(f"Groq API answered HTTP {exc.code}") from None
                try:
                    wait = float(exc.headers.get("retry-after", ""))
                except (TypeError, ValueError):
                    wait = DEFAULT_WAIT_SECONDS
                if exc.code == 429:
                    _next_key += 1
                    refused += 1
                    if refused < len(keys):
                        continue  # another key may still have room
                refused = 0
                if wait > MAX_WAIT_SECONDS:
                    raise RuntimeError(
                        f"Groq API rate limit: every key asks to wait {wait:.0f} s; "
                        "launch the command again later, the calls made are in the cache"
                    ) from None
                time.sleep(wait)
                break
            except OSError as exc:  # no answer: a timeout, a dropped connection, no network
                if attempt == MAX_ATTEMPTS:
                    raise RuntimeError(f"Groq API did not answer ({type(exc).__name__})") from None
                time.sleep(DEFAULT_WAIT_SECONDS)
                break
    raise AssertionError("unreachable")


def groq_provider(model: ModelSpec, request: LLMRequest) -> str:
    """Send `request` to the Groq model `model.id` and return the text of the reply."""
    keys = _keys()
    params = dict(request.params)
    if "max_tokens" in params:
        params["max_completion_tokens"] = params.pop("max_tokens")
    messages = [{"role": "user", "content": request.prompt}]
    if request.system:
        messages.insert(0, {"role": "system", "content": request.system})
    reply = _post({"model": model.id, "messages": messages, **params}, keys)

    try:
        choice = reply["choices"][0]
        text, finish = choice["message"]["content"], choice.get("finish_reason")
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("Groq API reply has no choices[0].message.content") from exc
    if finish == "length":
        raise _truncated(f"reply of {model.id} was cut at the token limit; not cached")
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError(f"reply of {model.id} is empty; not cached")
    return text
