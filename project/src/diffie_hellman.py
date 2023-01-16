# Projekt - System niezawodnego strumieniowania danych po UDP
# Autorzy: Mateusz Brzozowski, Bartłomiej Krawczyk, Jakub Marcowski, Aleksandra Sypuła
# Data ukończenia: 16.01.2023

import random
from math import gcd
from typing import Tuple

from Crypto.Util import number


def get_data() -> Tuple[int, int, int, int]:
    prime_number = get_prime_number()
    primitive_root = get_primitive_root(prime_number)
    private_key = generate_private_key()
    public_key: int = calculate_public_key(
        primitive_root, private_key, prime_number
    )
    return prime_number, primitive_root, private_key, public_key


def get_prime_number() -> int:
    prime_number = number.getPrime(64)
    print(f"Diffie-Hellman: Liczba pierwsza: {prime_number}")
    return prime_number


def generate_private_key() -> int:
    private_key = number.getRandomInteger(64)
    print(f"Diffie-Hellman: Klucz prywatny: {private_key}")
    return private_key


def calculate_public_key(
    primitive_root: int, private_key: int, prime_number: int
) -> int:
    public_key = modular_pow(primitive_root, private_key, prime_number)
    print(f"Diffie-Hellman: Klucz publiczny: {public_key}")
    return public_key


def modular_pow(base: int, exponent: int, modulus: int) -> int:
    if modulus == 1:
        return 0
    result = 1
    base %= modulus
    while exponent > 0:
        if exponent % 2 == 1:
            result = (result * base) % modulus
        exponent >>= 1
        base = (base * base) % modulus
    return result


def get_primitive_root(prime_number: int) -> int:
    max_primitive_root = min([prime_number, 2**32])
    while True:
        i = random.randint(1, max_primitive_root)
        if gcd(i, prime_number - 1) == 1:
            print(f"Diffie-Hellman: Pierwiastek pierwotny: {i}")
            return i


def get_session_key(
    public_key: int, private_key: int, prime_number: int
) -> int:
    session_key = modular_pow(public_key, private_key, prime_number)
    print(f"Diffie-Hellman: Ustalony klucz sesyjny: {session_key}")
    return session_key


def encrypt(message: bytes, session_key: int) -> bytes:
    return bytes(
        (message[i] ^ ((session_key >> (i % 24)) % 256)) % 256
        for i in range(len(message))
    )


def decrypt(message: bytes, session_key: int) -> bytes:
    return bytes(
        (message[i] ^ ((session_key >> (i % 24)) % 256)) % 256
        for i in range(len(message))
    )
