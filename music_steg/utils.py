"""
Utility functions for music steganography system
"""

import hashlib
from typing import List, Tuple


def text_to_bits(text: str) -> List[int]:
    """
    Convert text to a list of bits.

    Args:
        text: Input text string

    Returns:
        List of bits (0s and 1s)
    """
    bits = []
    for char in text:
        byte_val = ord(char)
        for i in range(8):
            bits.append((byte_val >> (7 - i)) & 1)
    return bits


def bits_to_text(bits: List[int]) -> str:
    """
    Convert a list of bits back to text.

    Args:
        bits: List of bits (0s and 1s)

    Returns:
        Decoded text string
    """
    chars = []
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            byte_val = 0
            for j in range(8):
                byte_val = (byte_val << 1) | bits[i + j]
            if byte_val > 0:  # Skip null bytes
                chars.append(chr(byte_val))
    return ''.join(chars)


def text_to_ternary(text: str) -> List[int]:
    """
    Convert text to base-3 (ternary) representation for 3-state encoding.

    Args:
        text: Input text string

    Returns:
        List of ternary digits (0, 1, 2)
    """
    ternary = []
    for char in text:
        byte_val = ord(char)
        # Convert to ternary (need 6 ternary digits for 8 bits: 3^6 = 729 > 256)
        ternary_digits = []
        for _ in range(6):
            ternary_digits.append(byte_val % 3)
            byte_val //= 3
        ternary.extend(reversed(ternary_digits))
    return ternary


def ternary_to_text(ternary: List[int]) -> str:
    """
    Convert ternary representation back to text.

    Args:
        ternary: List of ternary digits (0, 1, 2)

    Returns:
        Decoded text string
    """
    chars = []
    for i in range(0, len(ternary), 6):
        if i + 6 <= len(ternary):
            byte_val = 0
            for j in range(6):
                byte_val = byte_val * 3 + ternary[i + j]
            if byte_val > 0 and byte_val < 256:
                chars.append(chr(byte_val))
    return ''.join(chars)


def add_error_correction(bits: List[int]) -> List[int]:
    """
    Add simple parity-based error correction to bit stream.

    Args:
        bits: Original bit list

    Returns:
        Bits with error correction
    """
    # Add parity bit every 7 bits
    corrected = []
    for i in range(0, len(bits), 7):
        chunk = bits[i:i+7]
        parity = sum(chunk) % 2
        corrected.extend(chunk)
        corrected.append(parity)
    return corrected


def remove_error_correction(bits: List[int]) -> Tuple[List[int], int]:
    """
    Remove error correction and check for errors.

    Args:
        bits: Bits with error correction

    Returns:
        Tuple of (original bits, error count)
    """
    original = []
    errors = 0
    for i in range(0, len(bits), 8):
        if i + 8 <= len(bits):
            chunk = bits[i:i+7]
            parity = bits[i+7]
            expected_parity = sum(chunk) % 2
            if expected_parity != parity:
                errors += 1
            original.extend(chunk)
    return original, errors


def create_message_hash(message: str) -> str:
    """
    Create a hash of the message for integrity checking.

    Args:
        message: Input message

    Returns:
        Hex hash string
    """
    return hashlib.sha256(message.encode()).hexdigest()[:8]


def encode_with_header(message: str) -> Tuple[List[int], int]:
    """
    Encode message with length header and hash for integrity.

    Args:
        message: Message to encode

    Returns:
        Tuple of (encoded bits, total length)
    """
    # Create header: [length (16 bits)] [hash (32 bits)] [message bits]
    msg_hash = create_message_hash(message)
    msg_bits = text_to_bits(message)
    hash_bits = text_to_bits(msg_hash)

    # Encode length as 16-bit integer
    length = len(message)
    length_bits = []
    for i in range(16):
        length_bits.append((length >> (15 - i)) & 1)

    # Combine all parts
    full_message = length_bits + hash_bits + msg_bits
    return full_message, len(full_message)


def decode_with_header(bits: List[int]) -> Tuple[str, bool]:
    """
    Decode message with header validation.

    Args:
        bits: Encoded bit stream

    Returns:
        Tuple of (decoded message, is_valid)
    """
    if len(bits) < 48:  # Minimum: 16 (length) + 32 (hash)
        return "", False

    # Extract length
    length = 0
    for i in range(16):
        length = (length << 1) | bits[i]

    # Extract hash
    hash_bits = bits[16:80]
    stored_hash = bits_to_text(hash_bits)

    # Extract message
    msg_bits = bits[80:80 + (length * 8)]
    message = bits_to_text(msg_bits)

    # Validate
    computed_hash = create_message_hash(message)
    is_valid = (stored_hash == computed_hash)

    return message, is_valid


# Encoding mappings for different techniques

DYNAMIC_TO_BITS = {
    'pp': 0b000,
    'p': 0b001,
    'mp': 0b010,
    'mf': 0b011,
    'f': 0b100,
    'ff': 0b101,
    'fff': 0b110,
    'ppp': 0b111
}

BITS_TO_DYNAMIC = {v: k for k, v in DYNAMIC_TO_BITS.items()}

ARTICULATION_TO_VALUE = {
    None: 0,
    'staccato': 1,
    'accent': 2,
    'tenuto': 3,
    'staccatissimo': 4,
    'marcato': 5
}

VALUE_TO_ARTICULATION = {v: k for k, v in ARTICULATION_TO_VALUE.items()}

ORNAMENT_TO_VALUE = {
    None: 0,
    'trill': 1,
    'mordent': 2,
    'turn': 3,
    'shake': 4
}

VALUE_TO_ORNAMENT = {v: k for k, v in ORNAMENT_TO_VALUE.items()}
