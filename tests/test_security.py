from app.core.security import hash_password, verify_password


def test_hash_password():
    password = "prueba-temporal"

    hashed = hash_password(password)

    assert hashed != password
    assert hashed.startswith("$argon2")


def test_verify_correct_password():
    password = "prueba-temporal"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_incorrect_password():
    hashed = hash_password("prueba-temporal")

    assert verify_password("otra-clave", hashed) is False


def test_hash_password_generates_different_hashes():
    password = "prueba-temporal"

    hash_one = hash_password(password)
    hash_two = hash_password(password)

    assert hash_one != hash_two
    assert verify_password(password, hash_one) is True
    assert verify_password(password, hash_two) is True