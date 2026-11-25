"""Provider `local`: a model served on this machine through a chat-completions API.

It serves a role pinned with `provider: local` (D3, which reads the original text).
The model id of the role is the name the local server knows the model by, for example
`gpt-oss:20b` under Ollama. The request is one JSON POST with the standard library to
`http://localhost:11434/v1/chat/completions`, the address Ollama listens on.

Another address is read from the environment variable `OMISSIS_LOCAL_URL`. It must be
on this machine (`localhost`, `127.0.0.1` or `[::1]`): what this provider sends is a
text that is not pseudonymised yet, and it never sends it anywhere else. No key is
read and none is sent.

`params` of the request go into the body as they are. A reply that is empty, or cut at
the token limit, is an error and is therefore never cached, as for `groq`. A server
that does not answer, or that does not hold the model, is a `ConfigError`: the model
is missing on this machine, and a detector must stop rather than return no spans.
There is no second attempt: a local server that fails does not recover by waiting.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import TYPE_CHECKING

from omissis.config import ConfigError, ModelSpec

if TYPE_CHECKING:
    from omissis.backends import LLMRequest

URL_VARIABLE = "OMISSIS_LOCAL_URL"
DEFAULT_URL = "http://localhost:11434/v1/chat/completions"
# A local model may load for a minute and then write slowly.
TIMEOUT_SECONDS = 600
_THIS_MACHINE = frozenset({"localhost", "127.0.0.1", "::1"})


def _url() -> str:
    url = os.environ.get(URL_VARIABLE, DEFAULT_URL)
    parts = urllib.parse.urlsplit(url)
    if parts.scheme not in ("http", "https") or parts.hostname not in _THIS_MACHINE:
        raise ConfigError(
            f"{URL_VARIABLE} must be an http address on this machine (localhost, 127.0.0.1 "
            "or [::1]): the provider `local` never sends a text anywhere else"
        )
    return url


def _opener() -> urllib.request.OpenerDirector:
    """An opener that never uses a proxy: `urlopen` would honour `http_proxy`, and the
    text that this provider sends, not pseudonymised yet, would leave this machine."""
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def local_provider(model: ModelSpec, request: LLMRequest) -> str:
    """Send `request` to the model `model.id` of the local server and return its reply."""
    from omissis.backends import TruncatedReplyError  # defined before this module is imported

    url = _url()
    messages = [{"role": "user", "content": request.prompt}]
    if request.system:
        messages.insert(0, {"role": "system", "content": request.system})
    # The pinned model and the prompt come last: no parameter can take their place.
    body = {**request.params, "model": model.id, "messages": messages}
    http_request = urllib.request.Request(
        url,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json", "User-Agent": "omissis"},
        method="POST",
    )
    # The errors below carry a status or a type, never the content: it could quote the text.
    try:
        with _opener().open(http_request, timeout=TIMEOUT_SECONDS) as response:
            reply = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise ConfigError(
                f"the local model server does not hold {model.id}: pull it first "
                f"(for example `ollama pull {model.id}`)"
            ) from None
        raise RuntimeError(f"local model server answered HTTP {exc.code}") from None
    except OSError as exc:
        raise ConfigError(
            f"no model server answers on this machine ({type(exc).__name__}): start it "
            "first (for example `ollama serve`)"
        ) from None
    except ValueError:
        raise RuntimeError("local model server sent a reply that cannot be read") from None

    try:
        choice = reply["choices"][0]
        text, finish = choice["message"]["content"], choice.get("finish_reason")
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("local model reply has no choices[0].message.content") from exc
    if finish == "length":
        raise TruncatedReplyError(f"reply of {model.id} was cut at the token limit; not cached")
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError(f"reply of {model.id} is empty; not cached")
    return text
