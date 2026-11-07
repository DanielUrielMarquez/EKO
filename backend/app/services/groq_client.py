from groq import Groq

from app.core.config import settings


def get_groq_client() -> Groq:
    api_key = settings.GROQ_API_KEY

    if api_key is None or not api_key.get_secret_value().strip():
        raise RuntimeError("La API Key de Groq no está configurada.")

    return Groq(
        api_key=api_key.get_secret_value(),
    )


def generate_response(message: str) -> str:
    client = get_groq_client()

    completion = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Sos EKO, un asistente personal inteligente. "
                    "Respondé en español de manera natural, clara y útil. "
                    "Tu objetivo es ayudar al usuario."
                ),
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        max_completion_tokens=500,
    )

    response = completion.choices[0].message.content

    if not response:
        raise RuntimeError("Groq devolvió una respuesta vacía.")

    return response.strip()