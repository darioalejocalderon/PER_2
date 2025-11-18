"""
Music Cipher System

Uses musical properties (notes, intervals, rhythms) as encryption keys.
"""

from music21 import converter, note, interval, chord
from typing import List, Dict, Tuple
import hashlib


class MusicCipher:
    """
    Cipher system that uses music as an encryption key.
    """

    def __init__(self):
        self.key_sequence = []
        self.key_hash = None

    def load_key(self, musicxml_file: str) -> Dict[str, any]:
        """
        Load a MusicXML file and generate a cipher key from it.

        Args:
            musicxml_file: Path to MusicXML key file

        Returns:
            Dictionary with key statistics
        """
        score = converter.parse(musicxml_file)

        # Extract notes
        notes_list = []
        for element in score.flatten().notesAndRests:
            if isinstance(element, note.Note):
                notes_list.append(element)
            elif isinstance(element, chord.Chord):
                # Use the root note of chords
                notes_list.append(element.root())

        if len(notes_list) == 0:
            raise ValueError("No notes found in key file!")

        # Generate key sequence from musical properties
        self.key_sequence = []

        for i, n in enumerate(notes_list):
            # Use multiple properties to generate key bytes
            key_byte = 0

            # Pitch (MIDI number mod 256)
            key_byte ^= n.pitch.midi % 256

            # Octave
            key_byte ^= (n.pitch.octave * 17) % 256

            # Duration (quarter length * 16, mod 256)
            key_byte ^= int(n.quarterLength * 16) % 256

            # Interval from previous note (if exists)
            if i > 0:
                interv = interval.Interval(notes_list[i-1], n)
                key_byte ^= (abs(interv.semitones) * 7) % 256

            self.key_sequence.append(key_byte)

        # Create a hash of the key for verification
        key_bytes = bytes(self.key_sequence)
        self.key_hash = hashlib.sha256(key_bytes).hexdigest()

        stats = {
            'key_length': len(self.key_sequence),
            'key_hash': self.key_hash[:16],  # First 16 chars
            'unique_values': len(set(self.key_sequence)),
            'notes_processed': len(notes_list)
        }

        return stats

    def encrypt_message(self, message: str, musicxml_key: str = None) -> Tuple[bytes, str]:
        """
        Encrypt a message using the musical key.

        Args:
            message: Plaintext message
            musicxml_key: Optional path to key file (if not already loaded)

        Returns:
            Tuple of (encrypted bytes, key hash)
        """
        # Load key if provided
        if musicxml_key:
            self.load_key(musicxml_key)

        if not self.key_sequence:
            raise ValueError("No key loaded! Load a key file first.")

        # Convert message to bytes
        msg_bytes = message.encode('utf-8')

        # XOR encryption using key sequence (stream cipher)
        encrypted = []
        key_len = len(self.key_sequence)

        for i, byte in enumerate(msg_bytes):
            # Use key bytes in a repeating pattern
            key_byte = self.key_sequence[i % key_len]

            # Additional mixing: use previous encrypted byte if available
            if i > 0:
                key_byte ^= encrypted[i - 1]

            encrypted_byte = byte ^ key_byte
            encrypted.append(encrypted_byte)

        return bytes(encrypted), self.key_hash

    def decrypt_message(self, encrypted: bytes, musicxml_key: str = None) -> str:
        """
        Decrypt a message using the musical key.

        Args:
            encrypted: Encrypted bytes
            musicxml_key: Optional path to key file (if not already loaded)

        Returns:
            Decrypted plaintext message
        """
        # Load key if provided
        if musicxml_key:
            self.load_key(musicxml_key)

        if not self.key_sequence:
            raise ValueError("No key loaded! Load a key file first.")

        # XOR decryption (same as encryption for XOR cipher)
        decrypted = []
        key_len = len(self.key_sequence)

        for i, byte in enumerate(encrypted):
            # Use same key sequence
            key_byte = self.key_sequence[i % key_len]

            # Additional mixing: use previous encrypted byte
            if i > 0:
                key_byte ^= encrypted[i - 1]

            decrypted_byte = byte ^ key_byte
            decrypted.append(decrypted_byte)

        return bytes(decrypted).decode('utf-8')

    def encrypt_to_hex(self, message: str, musicxml_key: str = None) -> str:
        """
        Encrypt message and return as hex string.

        Args:
            message: Plaintext message
            musicxml_key: Optional path to key file

        Returns:
            Hex-encoded encrypted message
        """
        encrypted, _ = self.encrypt_message(message, musicxml_key)
        return encrypted.hex()

    def decrypt_from_hex(self, hex_string: str, musicxml_key: str = None) -> str:
        """
        Decrypt from hex string.

        Args:
            hex_string: Hex-encoded encrypted message
            musicxml_key: Optional path to key file

        Returns:
            Decrypted plaintext message
        """
        encrypted = bytes.fromhex(hex_string)
        return self.decrypt_message(encrypted, musicxml_key)

    def analyze_key_strength(self) -> Dict[str, any]:
        """
        Analyze the cryptographic strength of the loaded key.

        Returns:
            Dictionary with strength metrics
        """
        if not self.key_sequence:
            raise ValueError("No key loaded!")

        # Calculate entropy
        from collections import Counter
        freq = Counter(self.key_sequence)
        total = len(self.key_sequence)

        import math
        entropy = 0
        for count in freq.values():
            p = count / total
            entropy -= p * math.log2(p)

        # Calculate statistics
        analysis = {
            'key_length': len(self.key_sequence),
            'unique_bytes': len(set(self.key_sequence)),
            'entropy': entropy,
            'max_entropy': 8.0,  # Maximum for byte values
            'entropy_percentage': (entropy / 8.0) * 100,
            'byte_distribution': dict(freq.most_common(10)),
            'min_value': min(self.key_sequence),
            'max_value': max(self.key_sequence),
            'average_value': sum(self.key_sequence) / len(self.key_sequence)
        }

        # Strength assessment
        if entropy > 7.0:
            analysis['strength'] = 'Excellent'
        elif entropy > 6.0:
            analysis['strength'] = 'Good'
        elif entropy > 5.0:
            analysis['strength'] = 'Fair'
        else:
            analysis['strength'] = 'Weak'

        return analysis

    def generate_substitution_cipher(self) -> Dict[str, str]:
        """
        Generate a substitution cipher from the musical key.

        Returns:
            Dictionary mapping characters to encrypted characters
        """
        if not self.key_sequence:
            raise ValueError("No key loaded!")

        import string

        # Create alphabet
        alphabet = string.ascii_lowercase + string.ascii_uppercase + string.digits + ' .,!?'

        # Generate substitution based on key
        substitution = {}
        key_sum = sum(self.key_sequence)

        for i, char in enumerate(alphabet):
            # Use key to determine substitution
            offset = self.key_sequence[i % len(self.key_sequence)]
            offset += (key_sum >> (i % 8)) & 0xFF
            new_index = (i + offset) % len(alphabet)
            substitution[char] = alphabet[new_index]

        return substitution

    def encrypt_substitution(self, message: str, musicxml_key: str = None) -> str:
        """
        Encrypt using substitution cipher derived from music.

        Args:
            message: Plaintext message
            musicxml_key: Optional path to key file

        Returns:
            Encrypted message
        """
        if musicxml_key:
            self.load_key(musicxml_key)

        substitution = self.generate_substitution_cipher()

        encrypted = []
        for char in message:
            encrypted.append(substitution.get(char, char))

        return ''.join(encrypted)

    def decrypt_substitution(self, encrypted: str, musicxml_key: str = None) -> str:
        """
        Decrypt substitution cipher.

        Args:
            encrypted: Encrypted message
            musicxml_key: Optional path to key file

        Returns:
            Decrypted message
        """
        if musicxml_key:
            self.load_key(musicxml_key)

        substitution = self.generate_substitution_cipher()

        # Reverse the substitution
        reverse_sub = {v: k for k, v in substitution.items()}

        decrypted = []
        for char in encrypted:
            decrypted.append(reverse_sub.get(char, char))

        return ''.join(decrypted)
