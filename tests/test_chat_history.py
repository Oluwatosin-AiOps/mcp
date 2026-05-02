"""Gradio → OpenAI history flattening."""

from app.chat_history import gradio_history_to_openai_messages


def test_empty_history():
    assert gradio_history_to_openai_messages(None) == []
    assert gradio_history_to_openai_messages([]) == []


def test_string_content():
    hist = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "Hi there"},
    ]
    assert gradio_history_to_openai_messages(hist) == [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "Hi there"},
    ]


def test_normalized_text_parts():
    hist = [
        {
            "role": "user",
            "content": [{"type": "text", "text": "  SKU COM-0024  "}],
        },
        {
            "role": "assistant",
            "content": [{"type": "text", "text": "Proceed?"}],
        },
    ]
    assert gradio_history_to_openai_messages(hist) == [
        {"role": "user", "content": "SKU COM-0024"},
        {"role": "assistant", "content": "Proceed?"},
    ]


def test_skips_system_and_empty():
    hist = [
        {"role": "system", "content": "nope"},
        {"role": "user", "content": ""},
        {"role": "user", "content": "real"},
    ]
    assert gradio_history_to_openai_messages(hist) == [{"role": "user", "content": "real"}]
