import os
import secrets
import string
import bcrypt
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# ---------------------------------------------------------
# Autenticación (Contraseña Maestra)
# ---------------------------------------------------------

def hash_master_password(password: str) -> bytes:
    """Genera un hash bcrypt seguro para la contraseña maestra."""
    salt = bcrypt.gensalt(rounds=14)
    return bcrypt.hashpw(password.encode('utf-8'), salt)

def verify_master_password(password: str, hashed: bytes) -> bool:
    """Verifica la contraseña maestra contra el hash almacenado."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

def generate_salt() -> bytes:
    """Genera un salt aleatorio para la derivación de claves."""
    return os.urandom(16)

def derive_key(password: str, salt: bytes) -> bytes:
    """
    Deriva una clave AES-256 (32 bytes) a partir de la contraseña maestra y un salt,
    usando PBKDF2HMAC con SHA256 y 600,000 iteraciones (Estándar recomendado actual).
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=600000,
        backend=default_backend()
    )
    return kdf.derive(password.encode('utf-8'))

# ---------------------------------------------------------
# Cifrado de Datos (AES-256-GCM)
# ---------------------------------------------------------

def encrypt_data(key: bytes, plaintext: str) -> bytes:
    """Cifra un texto plano usando AES-256 en modo GCM (Autenticado)."""
    if not plaintext:
        return b""
    iv = os.urandom(12)  # Vector de inicialización de 96 bits recomendado para GCM
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(plaintext.encode('utf-8')) + encryptor.finalize()
    # Guardamos IV + Tag de autenticación (16 bytes) + Texto cifrado
    return iv + encryptor.tag + ciphertext

def decrypt_data(key: bytes, encrypted_data: bytes) -> str:
    """Descifra un texto cifrado con AES-256-GCM."""
    if not encrypted_data:
        return ""
    try:
        iv = encrypted_data[:12]
        tag = encrypted_data[12:28]
        ciphertext = encrypted_data[28:]
        
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        return plaintext.decode('utf-8')
    except Exception as e:
        # Falla si la clave es incorrecta o los datos fueron manipulados
        return ""

# ---------------------------------------------------------
# Utilidades de Contraseñas
# ---------------------------------------------------------

def generate_secure_password(length=16, use_upper=True, use_lower=True, use_numbers=True, use_symbols=True) -> str:
    """Genera una contraseña criptográficamente segura."""
    characters = ""
    if use_upper: characters += string.ascii_uppercase
    if use_lower: characters += string.ascii_lowercase
    if use_numbers: characters += string.digits
    if use_symbols: characters += "!@#$%^&*()-_=+[]{}|;:,.<>?"
    
    if not characters:
        characters = string.ascii_letters + string.digits
        
    return ''.join(secrets.choice(characters) for _ in range(length))

def check_password_strength(password: str) -> str:
    """Evalúa la fortaleza de la contraseña."""
    if len(password) < 8:
        return "Débil"
    
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in string.punctuation for c in password)
    
    score = sum([has_upper, has_lower, has_digit, has_symbol])
    
    if len(password) >= 12 and score >= 4:
        return "Fuerte"
    elif len(password) >= 8 and score >= 3:
        return "Media"
    else:
        return "Débil"