from unittest.mock import MagicMock, patch

import pytest

from app.services.groq_client import (
    SUMMARY_SYSTEM_PROMPT,
    generate_summary,
)


def test_generate_summary_success():
    mock_client = MagicMock()

    mock_client.chat.completions.create.return_value.choices[
        0
    ].message.content = "  El usuario está desarrollando EKO.  "

    new_messages = [
        {"role": "user", "content": "Estoy desarrollando EKO."},
        {"role": "assistant", "content": "¡Excelente proyecto!"},
    ]

    with patch(
        "app.services.groq_client.get_groq_client",
        return_value=mock_client,
    ) as mock_get_client:
        summary = generate_summary(
            existing_summary="El usuario estudia programación.",
            new_messages=new_messages,
        )

    assert summary == "El usuario está desarrollando EKO."

    mock_get_client.assert_called_once()

    mock_client.chat.completions.create.assert_called_once()

    call_arguments = (
        mock_client.chat.completions.create.call_args.kwargs
    )

    assert call_arguments["messages"][0] == SUMMARY_SYSTEM_PROMPT
    assert call_arguments["messages"][1]["role"] == "user"
    assert "El usuario estudia programación." in (
        call_arguments["messages"][1]["content"]
    )
    assert "Estoy desarrollando EKO." in (
        call_arguments["messages"][1]["content"]
    )
    assert call_arguments["max_completion_tokens"] == 800


def test_generate_summary_without_new_messages():
    with patch(
        "app.services.groq_client.get_groq_client"
    ) as mock_get_client:
        with pytest.raises(
            ValueError,
            match="No hay mensajes nuevos para resumir.",
        ):
            generate_summary(
                existing_summary=None,
                new_messages=[],
            )

    mock_get_client.assert_not_called()


def test_generate_summary_empty_response():
    mock_client = MagicMock()

    mock_client.chat.completions.create.return_value.choices[
        0
    ].message.content = "   "

    with patch(
        "app.services.groq_client.get_groq_client",
        return_value=mock_client,
    ):
        with pytest.raises(
            RuntimeError,
            match="Groq devolvió un resumen vacío.",
        ):
            generate_summary(
                existing_summary=None,
                new_messages=[
                    {"role": "user", "content": "Estoy desarrollando EKO."},
                ],
            )
