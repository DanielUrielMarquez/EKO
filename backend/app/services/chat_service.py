def process_message(message: str) -> str:
    normalized_message = message.strip()

    if normalized_message.lower() in [
        "hola",
        "buenas",
        "buen día",
        "buenos días",
    ]:
        return "¡Hola! Soy EKO, tu asistente personal. ¿En qué puedo ayudarte?"

    return (
        f"Recibí tu mensaje: {normalized_message}. "
        "Todavía estoy aprendiendo a procesar solicitudes más complejas."
    )