import os
import json

import pytest

from llms.groq_llm import GroqLLM


class DummyResp:
    def __init__(self, status_code=200, data=None, text=""):
        self.status_code = status_code
        self._data = data or {"text": "hello"}
        self.text = text or json.dumps(self._data)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

    def json(self):
        return self._data


def test_generate_monkeypatch(monkeypatch):
    called = {}

    def fake_post(url, json, headers, timeout):
        called['url'] = url
        called['json'] = json
        called['headers'] = headers
        return DummyResp()

    monkeypatch.setattr("requests.post", fake_post)

    os.environ['GROQ_API_KEY'] = "test-key"
    os.environ['GROQ_MODEL'] = "test-model"
    llm = GroqLLM()
    out = llm.generate("hello world")
    assert out == "hello"
    assert called['json']['prompt'] == "hello world"
