#!/usr/bin/env python3
"""
Music Steganography CLI Tool

Command-line interface for encoding/decoding messages in sheet music.
"""

import argparse
import sys
import json
from pathlib import Path

from .encoder import MusicEncoder
from .decoder import MusicDecoder
from .cipher import MusicCipher


def encode_command(args):
    """Handle encode command."""
    encoder = MusicEncoder()

    print(f"📝 Encoding message into {args.input}...")
    print(f"Message: '{args.message}'")
    print(f"Output: {args.output}")

    # Parse techniques
    techniques = args.techniques.split(',') if args.techniques else ['dynamics', 'stem']

    try:
        # Check capacity first
        capacity = encoder.estimate_capacity(args.input)
        print(f"\n📊 Capacity Analysis:")
        print(f"  Total notes: {capacity['total_notes']}")
        print(f"  Maximum message size: {capacity['max_message_chars']} characters")
        print(f"  Your message size: {len(args.message)} characters")

        if len(args.message) > capacity['max_message_chars']:
            print(f"\n❌ Error: Message too long!")
            return 1

        # Encode
        stats = encoder.encode_message(
            args.input,
            args.message,
            args.output,
            techniques
        )

        print(f"\n✅ Encoding successful!")
        print(f"  Bits encoded: {stats['bits_encoded']}")
        print(f"  Notes used: {stats['notes_used']}/{stats['total_notes']}")
        print(f"  Techniques: {', '.join(stats['techniques_used'])}")
        print(f"  Capacity remaining: {stats['capacity_remaining']} bits")

        if args.json:
            with open(args.json, 'w') as f:
                json.dump(stats, f, indent=2)
            print(f"\n📄 Statistics saved to {args.json}")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


def decode_command(args):
    """Handle decode command."""
    decoder = MusicDecoder()

    print(f"🔍 Decoding message from {args.input}...")

    try:
        # Detect techniques first
        if args.auto_detect:
            print("\n🔬 Auto-detecting techniques...")
            detected = decoder.detect_techniques(args.input)
            print(f"  Detected: {', '.join([k for k, v in detected.items() if v])}")

        # Parse techniques
        techniques = args.techniques.split(',') if args.techniques else None

        # Decode
        if args.try_all:
            print("\n🧪 Trying all technique combinations...")
            results = decoder.try_all_techniques(args.input)

            print(f"\n📊 Results:")
            for i, result in enumerate(results[:5], 1):  # Show top 5
                if result.get('success'):
                    validity = "✓" if result.get('is_valid') else "?"
                    print(f"\n  {i}. [{validity}] {result['technique_combo']}")
                    print(f"     Message: '{result['message'][:50]}{'...' if len(result['message']) > 50 else ''}'")
                    print(f"     Length: {len(result['message'])} chars")

            if results and results[0].get('success'):
                print(f"\n✅ Best result:")
                print(f"Message: {results[0]['message']}")

        else:
            stats = decoder.decode_message(
                args.input,
                techniques=techniques,
                auto_detect=args.auto_detect
            )

            if stats['success']:
                validity = "✓ Valid" if stats['is_valid'] else "⚠ Invalid checksum"
                print(f"\n✅ Decoding successful! [{validity}]")
                print(f"  Message: {stats['message']}")
                print(f"  Bits extracted: {stats['bits_extracted']}")
                print(f"  Techniques used: {', '.join(stats['techniques_used'])}")

                if args.output:
                    with open(args.output, 'w') as f:
                        f.write(stats['message'])
                    print(f"\n💾 Message saved to {args.output}")
            else:
                print(f"\n❌ No message found!")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def analyze_command(args):
    """Handle analyze command."""
    decoder = MusicDecoder()
    encoder = MusicEncoder()

    print(f"🔬 Analyzing {args.input}...")

    try:
        # Get capacity
        capacity = encoder.estimate_capacity(args.input)

        # Get analysis
        analysis = decoder.analyze_file(args.input)

        print(f"\n📊 File Analysis:")
        print(f"  Total notes: {analysis['total_notes']}")
        print(f"\n  Capacity:")
        print(f"    Maximum message: {capacity['max_message_chars']} characters")
        print(f"    Total bits available: {capacity['total_bits']}")

        print(f"\n  Detected techniques:")
        for tech, detected in analysis['detected_techniques'].items():
            status = "✓" if detected else "✗"
            print(f"    {status} {tech}")

        if analysis['dynamics_distribution']:
            print(f"\n  Dynamic markings:")
            for dyn, count in sorted(analysis['dynamics_distribution'].items()):
                print(f"    {dyn}: {count}")

        if analysis['articulation_distribution']:
            print(f"\n  Articulations:")
            for artic, count in sorted(analysis['articulation_distribution'].items()):
                print(f"    {artic}: {count}")

        print(f"\n  Stem directions:")
        for direction, count in analysis['stem_distribution'].items():
            print(f"    {direction}: {count}")

        if analysis['ornament_count'] > 0:
            print(f"\n  Ornaments: {analysis['ornament_count']}")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


def cipher_command(args):
    """Handle cipher command."""
    cipher = MusicCipher()

    print(f"🎵 Music Cipher Mode")

    try:
        if args.mode == 'encrypt':
            print(f"🔐 Encrypting message using key: {args.key}")

            key_stats = cipher.load_key(args.key)
            print(f"\n🔑 Key loaded:")
            print(f"  Length: {key_stats['key_length']} bytes")
            print(f"  Hash: {key_stats['key_hash']}")
            print(f"  Unique values: {key_stats['unique_values']}")

            if args.analyze:
                strength = cipher.analyze_key_strength()
                print(f"\n  Strength: {strength['strength']}")
                print(f"  Entropy: {strength['entropy']:.2f}/{strength['max_entropy']} ({strength['entropy_percentage']:.1f}%)")

            # Encrypt
            encrypted_hex = cipher.encrypt_to_hex(args.message)

            print(f"\n✅ Encryption successful!")
            print(f"  Plaintext: {args.message}")
            print(f"  Encrypted (hex): {encrypted_hex}")

            if args.output:
                with open(args.output, 'w') as f:
                    f.write(encrypted_hex)
                print(f"\n💾 Encrypted message saved to {args.output}")

        elif args.mode == 'decrypt':
            print(f"🔓 Decrypting message using key: {args.key}")

            key_stats = cipher.load_key(args.key)
            print(f"\n🔑 Key loaded:")
            print(f"  Hash: {key_stats['key_hash']}")

            # Decrypt
            decrypted = cipher.decrypt_from_hex(args.message)

            print(f"\n✅ Decryption successful!")
            print(f"  Encrypted (hex): {args.message}")
            print(f"  Decrypted: {decrypted}")

            if args.output:
                with open(args.output, 'w') as f:
                    f.write(decrypted)
                print(f"\n💾 Decrypted message saved to {args.output}")

        elif args.mode == 'analyze-key':
            print(f"🔬 Analyzing key: {args.key}")

            key_stats = cipher.load_key(args.key)
            print(f"\n🔑 Key Statistics:")
            print(f"  Length: {key_stats['key_length']} bytes")
            print(f"  Hash: {key_stats['key_hash']}")
            print(f"  Notes processed: {key_stats['notes_processed']}")

            strength = cipher.analyze_key_strength()
            print(f"\n  Cryptographic Strength: {strength['strength']}")
            print(f"  Entropy: {strength['entropy']:.2f}/{strength['max_entropy']} ({strength['entropy_percentage']:.1f}%)")
            print(f"  Unique bytes: {strength['unique_bytes']}/{strength['key_length']}")
            print(f"  Value range: [{strength['min_value']}, {strength['max_value']}]")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Music Steganography and Cryptography System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Encode a message
  python -m music_steg.cli encode -i music.musicxml -m "Secret message" -o output.musicxml

  # Decode a message
  python -m music_steg.cli decode -i encoded.musicxml --auto-detect

  # Analyze a file
  python -m music_steg.cli analyze -i music.musicxml

  # Encrypt with music cipher
  python -m music_steg.cli cipher -k key.musicxml -m "Secret" --mode encrypt

  # Decrypt with music cipher
  python -m music_steg.cli cipher -k key.musicxml -m "a1b2c3..." --mode decrypt
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Encode command
    encode_parser = subparsers.add_parser('encode', help='Encode a message in sheet music')
    encode_parser.add_argument('-i', '--input', required=True, help='Input MusicXML file')
    encode_parser.add_argument('-m', '--message', required=True, help='Message to hide')
    encode_parser.add_argument('-o', '--output', required=True, help='Output MusicXML file')
    encode_parser.add_argument('-t', '--techniques', help='Comma-separated techniques (dynamics,stem,articulation,ornament)')
    encode_parser.add_argument('-j', '--json', help='Save statistics to JSON file')

    # Decode command
    decode_parser = subparsers.add_parser('decode', help='Decode a message from sheet music')
    decode_parser.add_argument('-i', '--input', required=True, help='Input MusicXML file')
    decode_parser.add_argument('-o', '--output', help='Output text file for message')
    decode_parser.add_argument('-t', '--techniques', help='Comma-separated techniques to use')
    decode_parser.add_argument('--auto-detect', action='store_true', help='Auto-detect techniques')
    decode_parser.add_argument('--try-all', action='store_true', help='Try all technique combinations')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze a MusicXML file')
    analyze_parser.add_argument('-i', '--input', required=True, help='Input MusicXML file')

    # Cipher command
    cipher_parser = subparsers.add_parser('cipher', help='Musical cipher encryption/decryption')
    cipher_parser.add_argument('-k', '--key', required=True, help='MusicXML key file')
    cipher_parser.add_argument('-m', '--message', required=True, help='Message (plaintext or hex)')
    cipher_parser.add_argument('--mode', required=True, choices=['encrypt', 'decrypt', 'analyze-key'],
                              help='Operation mode')
    cipher_parser.add_argument('-o', '--output', help='Output file')
    cipher_parser.add_argument('--analyze', action='store_true', help='Analyze key strength')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to appropriate command
    if args.command == 'encode':
        return encode_command(args)
    elif args.command == 'decode':
        return decode_command(args)
    elif args.command == 'analyze':
        return analyze_command(args)
    elif args.command == 'cipher':
        return cipher_command(args)


if __name__ == '__main__':
    sys.exit(main())
