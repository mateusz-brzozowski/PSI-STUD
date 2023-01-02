from typing import List
import random


def get_data():
    prime_number = get_random_prime_number(1000, 10000)
    primitive_root = get_primitive_root(
        prime_number)
    private_key = get_random_number(100, 1000)
    public_key = (primitive_root ** private_key) % prime_number
    return prime_number, primitive_root, private_key, public_key


def get_random_prime_number(min_prime_number: int, max_prime_number: int) -> int:
    primes = [i for i in range(
        min_prime_number, max_prime_number) if is_prime(i)]
    return random.choice(primes)


def is_prime(number: int) -> bool:
    if number < 2:
        return False
    if number == 2:
        return True
    if number % 2 == 0:
        return False
    for i in range(3, int(number**0.5)+1, 2):
        if number % i == 0:
            return False
    return True


def get_primitive_root(prime_number: int) -> int:
    factors = get_prime_factors(prime_number-1)
    primitive_roots = []
    for i in range(2, prime_number):
        for factor in factors:
            if i**((prime_number-1)//factor) % prime_number == 1:
                break
        else:
            primitive_roots.append(i)
    return random.choice(primitive_roots)


def get_prime_factors(number: int) -> List[int]:
    factors = []
    while number % 2 == 0:
        factors.append(2)
        number /= 2
    for i in range(3, int(number**0.5)+1, 2):
        while number % i == 0:
            factors.append(i)
            number /= i
    if number > 2:
        factors.append(number)
    return factors


def get_random_number(min_number: int, max_number: int) -> int:
    return random.randint(min_number, max_number)


def get_session_key(public_key: int, private_key: int, prime_number: int) -> int:
    return (public_key ** private_key) % prime_number


def encrypt(message: str, session_key: int) -> str:
    encrypted_message = ""
    for c in message:
        encrypted_message += chr(ord(c)+session_key)
    return encrypted_message


def decrypt(message: str, session_key: int) -> str:
    decrypted_message = ""
    for c in message:
        decrypted_message += chr(ord(c)-session_key)
    return decrypted_message
