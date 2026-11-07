
from app.services.groq_client import generate_response


def process_message(message: str) -> str:
    normalized_message = message.strip()

    if not normalized_message:
        raise ValueError("El mensaje no puede estar vacío.")

    return generate_response(normalized_message)
