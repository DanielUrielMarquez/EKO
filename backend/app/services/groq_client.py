from groq import Groq

from app.core.config import settings


SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Sos EKO, un asistente personal inteligente. "
        "Respondé en español de manera natural, clara y útil. "
        "Tu objetivo es ayudar al usuario."
    ),
}


SUMMARY_SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Sos el sistema de memoria de EKO. Tu tarea es actualizar "
        "un resumen de memoria a partir de un resumen anterior y "
        "mensajes nuevos.\n\n"
        "Escribí el resultado en español, de forma clara, compacta "
        "y organizada.\n\n"
        "Priorizá conservar:\n"
        "- Información importante sobre el usuario.\n"
        "- Preferencias y formas de trabajo.\n"
        "- Proyectos, objetivos y avances.\n"
        "- Decisiones técnicas y acuerdos.\n"
        "- Conocimientos, dificultades y tareas pendientes.\n\n"
        "No inventes información ni deduzcas hechos que no estén "
        "expresados claramente.\n"
        "Diferenciá lo que afirma el usuario de las sugerencias "
        "del asistente. No conviertas una sugerencia en un hecho.\n"
        "Eliminá repeticiones y datos circunstanciales sin valor "
        "para futuras conversaciones.\n"
        "Actualizá el resumen anterior incorporando los mensajes "
        "nuevos, sin perder información importante que siga vigente.\n"
        "Devolvé únicamente el resumen actualizado, sin introducciones."
    ),
}


def get_groq_client() -> Groq:
    api_key = settings.GROQ_API_KEY

    if api_key is None or not api_key.get_secret_value().strip():
        raise RuntimeError("La API Key de Groq no está configurada.")

    return Groq(
        api_key=api_key.get_secret_value(),
    )


def generate_response(
    messages: list[dict[str, str]],
) -> str:
    client = get_groq_client()

    completion = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            SYSTEM_PROMPT,
            *messages,
        ],
        max_completion_tokens=500,
    )

    response = completion.choices[0].message.content

    if not response:
        raise RuntimeError("Groq devolvió una respuesta vacía.")

    return response.strip()


def generate_summary(
    existing_summary: str | None,
    new_messages: list[dict[str, str]],
) -> str:
    if not new_messages:
        raise ValueError("No hay mensajes nuevos para resumir.")

    previous_summary = existing_summary or "Todavía no existe un resumen."

    formatted_messages = "\n\n".join(
        f"{item['role'].upper()}: {item['content']}"
        for item in new_messages
    )

    client = get_groq_client()

    completion = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[
            SUMMARY_SYSTEM_PROMPT,
            {
                "role": "user",
                "content": (
                    f"RESUMEN ANTERIOR:\n{previous_summary}\n\n"
                    f"MENSAJES NUEVOS:\n{formatted_messages}"
                ),
            },
        ],
        max_completion_tokens=800,
    )

    summary = completion.choices[0].message.content

    if not summary or not summary.strip():
        raise RuntimeError("Groq devolvió un resumen vacío.")

    return summary.strip()
