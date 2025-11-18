"""
Music Steganography and Cryptography System

A comprehensive system for hiding messages in sheet music using MusicXML format.
Supports multiple steganographic techniques and musical cipher modes.
"""

__version__ = "1.0.0"
__author__ = "Music Steg Team"

from .encoder import MusicEncoder
from .decoder import MusicDecoder
from .cipher import MusicCipher

__all__ = ['MusicEncoder', 'MusicDecoder', 'MusicCipher']
