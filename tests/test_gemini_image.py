"""gemini_image: error mapping and retries of _call, response parsing, redaction. All through a fake urlopen."""

import base64
import io
import json
import urllib.error
import urllib.request

import pytest

import gemini_image


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def http_error(code: int, detail: str = '{"error": "x"}') -> urllib.error.HTTPError:
    return urllib.error.HTTPError("https://example.invalid/", code, "status", {}, io.BytesIO(detail.encode("utf-8")))


@pytest.fixture
def api(monkeypatch):
    """A fake urlopen that answers from a queue of payloads (dict) or exceptions, recording every request."""
    monkeypatch.setattr(gemini_image, "api_key", lambda: "not-a-real-key")
    queue, requests = [], []

    def urlopen(request, timeout=None):
        requests.append((request, timeout))
        item = queue.pop(0)
        if isinstance(item, BaseException):
            raise item
        return FakeResponse(item)

    monkeypatch.setattr(urllib.request, "urlopen", urlopen)
    return queue, requests


def test_call_sends_the_key_in_a_header_and_parses_json(api):
    queue, requests = api
    queue.append({"models": [{"name": "models/x"}]})
    assert gemini_image._call("GET", "models?pageSize=200", timeout=60) == {"models": [{"name": "models/x"}]}
    request, timeout = requests[0]
    assert request.full_url == f"{gemini_image.API_ROOT}/models?pageSize=200" and request.get_method() == "GET"
    assert request.get_header("X-goog-api-key") == "not-a-real-key" and timeout == 60
    assert request.data is None
    queue.append({"ok": True})
    gemini_image._call("POST", "interactions", {"model": "m"})
    assert json.loads(requests[1][0].data) == {"model": "m"}


def test_402_is_a_billing_error(api):
    queue, requests = api
    queue.append(http_error(402))
    with pytest.raises(gemini_image.BillingError) as err:
        gemini_image._call("POST", "interactions", {})
    assert err.value.status == 402 and str(err.value) == gemini_image.BILLING_HELP
    assert isinstance(err.value, gemini_image.GeminiError)


def test_402_is_not_retried_by_generate_image(api):
    queue, requests = api
    queue.append(http_error(402))
    with pytest.raises(gemini_image.BillingError):
        gemini_image.generate_image("m", [], retries=2)
    assert len(requests) == 1


@pytest.mark.parametrize("code", [429, 500, 502, 503, 504])
def test_retryable_statuses_retry_up_to_the_limit(api, code):
    queue, requests = api
    queue.extend([http_error(code)] * 3)
    with pytest.raises(gemini_image.GeminiError) as err:
        gemini_image.generate_image("m", [], retries=2)
    assert err.value.status == code and f"HTTP {code} for POST interactions" in str(err.value)
    assert len(requests) == 3  # the first call and two retries


def test_a_retry_can_succeed(api):
    queue, requests = api
    png = b"\x89PNG fake"
    queue.extend([http_error(503), {"output_image": {"data": base64.b64encode(png).decode(), "mime_type": "image/png"}}])
    result = gemini_image.generate_image("m", [], retries=1)
    assert result["image_bytes"] == png and result["attempts"] == 2 and result["image_source"] == "output_image"
    assert len(requests) == 2


def test_network_errors_are_retried(api):
    queue, requests = api
    queue.extend([urllib.error.URLError("dns failed"), ConnectionResetError("reset"), TimeoutError()])
    with pytest.raises(gemini_image.GeminiError) as err:
        gemini_image.generate_text("m", [], retries=2)
    assert err.value.status == gemini_image.NETWORK and "Network error" in str(err.value)
    assert len(requests) == 3


def test_400_is_not_retried(api):
    queue, requests = api
    queue.append(http_error(400, '{"error": {"message": "bad request"}}'))
    with pytest.raises(gemini_image.GeminiError) as err:
        gemini_image.generate_image("m", [], retries=2)
    assert err.value.status == 400 and "bad request" in str(err.value)
    assert len(requests) == 1


def test_generate_text_reads_model_output_steps(api):
    queue, requests = api
    queue.append({"steps": [{"type": "thinking", "content": [{"type": "text", "text": "hmm"}]},
                            {"type": "model_output", "content": [{"type": "text", "text": "{\"pass\": true}"}]}],
                  "usage": {"total_input_tokens": 10}})
    result = gemini_image.generate_text("m", [gemini_image.text_part("q")])
    assert result["text"] == '{"pass": true}' and result["response"]["usage"] == {"total_input_tokens": 10}
    body = json.loads(requests[0][0].data)
    assert body == {"model": "m", "input": [{"type": "text", "text": "q"}]} and requests[0][1] == 180
    queue.append({"steps": []})
    with pytest.raises(gemini_image.GeminiError, match="No text in response"):
        gemini_image.generate_text("m", [])


def test_generate_image_request_body_and_fallback_fields(api):
    queue, requests = api
    png = b"\x89PNG fake"
    data = base64.b64encode(png).decode()
    queue.append({"steps": [{"type": "model_output", "content": [{"type": "image", "data": data, "mime_type": "image/jpeg"}]}]})
    result = gemini_image.generate_image("m", [gemini_image.text_part("draw")], aspect_ratio="1:1", image_size="1K", thinking_level="low")
    assert result["mime_type"] == "image/jpeg" and result["image_source"] == "steps.model_output"
    body = json.loads(requests[0][0].data)
    assert body["response_format"] == {"type": "image", "aspect_ratio": "1:1", "image_size": "1K"}
    assert body["generation_config"] == {"thinking_level": "low"}
    assert body["input"] == [{"type": "text", "text": "draw"}]
    queue.append({"candidates": [{"content": {"parts": [{"inlineData": {"data": data, "mimeType": "image/png"}}]}}]})
    assert gemini_image.generate_image("m", [])["image_source"] == "candidates"
    queue.append({"steps": [{"type": "model_output", "content": [{"type": "text", "text": "I cannot draw that"}]}]})
    with pytest.raises(gemini_image.GeminiError, match="No image in response"):
        gemini_image.generate_image("m", [])


def test_parts_and_redact():
    assert gemini_image.text_part("hi") == {"type": "text", "text": "hi"}
    part = gemini_image.image_part(b"abc", "image/jpeg")
    assert part == {"type": "image", "mime_type": "image/jpeg", "data": base64.b64encode(b"abc").decode()}
    long = "x" * (gemini_image.LONG_STRING + 1)
    short = "x" * gemini_image.LONG_STRING
    node = {"a": [long, short, {"b": long}], "c": 3, "d": None}
    assert gemini_image.redact(node) == {"a": [f"<{len(long)} chars omitted>", short, {"b": f"<{len(long)} chars omitted>"}], "c": 3, "d": None}
    assert gemini_image.redact(node) is not node


def test_api_key_errors_without_a_key(monkeypatch):
    monkeypatch.setattr(gemini_image, "read_key", lambda names: None)
    with pytest.raises(gemini_image.GeminiError, match="No Gemini API key found"):
        gemini_image.api_key()
    monkeypatch.setattr(gemini_image, "read_key", lambda names: "k")
    assert gemini_image.api_key() == "k"


def test_list_models_follows_pages(api):
    queue, requests = api
    queue.extend([{"models": [{"name": "models/a"}], "nextPageToken": "t2"}, {"models": [{"name": "models/b"}]}])
    assert [m["name"] for m in gemini_image.list_models()] == ["models/a", "models/b"]
    assert requests[1][0].full_url.endswith("&pageToken=t2")


def test_check_command(monkeypatch, capsys):
    monkeypatch.setattr(gemini_image, "list_models", lambda: [{"name": "models/gemini-nano-banana-2.1", "displayName": "NB"},
                                                             {"name": "models/text-only"}])
    assert gemini_image.main(["check"]) == 0
    out = capsys.readouterr().out
    assert "Key OK. 2 models visible" in out and "models/gemini-nano-banana-2.1  (NB)" in out and "text-only" not in out
    assert gemini_image.main([]) == 2
    def fail():
        raise gemini_image.GeminiError("HTTP 400 for GET models: API key not valid", 400)
    monkeypatch.setattr(gemini_image, "list_models", fail)
    assert gemini_image.main(["check"]) == 1
    assert "FAILED: HTTP 400" in capsys.readouterr().out
