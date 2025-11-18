#!/usr/bin/env python3
"""
Music Steganography System - Comprehensive Demo

This script demonstrates all features of the music steganography system.
"""

import sys
import os


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def run_command(cmd):
    """Run a command and print it."""
    print(f"$ {cmd}")
    result = os.system(cmd)
    print()
    return result


def main():
    """Run comprehensive demo."""

    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║        Music Steganography & Cryptography System Demo           ║
║                                                                  ║
║   Hide messages in sheet music using steganography and music    ║
║   based encryption. This demo showcases all system features.    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    # Section 1: File Analysis
    print_section("1. Analyzing Music Files for Capacity")

    print("Let's check how much data we can hide in different pieces:\n")

    run_command("python -m music_steg.cli analyze -i examples/simple_melody.musicxml")
    run_command("python -m music_steg.cli analyze -i examples/twinkle_twinkle.musicxml")
    run_command("python -m music_steg.cli analyze -i examples/longer_piece.musicxml")

    # Section 2: Basic Steganography
    print_section("2. Basic Steganography - Encoding Messages")

    print("Encoding a secret message into Twinkle Twinkle Little Star:\n")

    run_command('python -m music_steg.cli encode '
               '-i examples/twinkle_twinkle.musicxml '
               '-m "Meet at 5pm" '
               '-o demo_encoded1.musicxml')

    print("Now let's decode it back:\n")

    run_command('python -m music_steg.cli decode '
               '-i demo_encoded1.musicxml '
               '--try-all')

    # Section 3: Different Techniques
    print_section("3. Using Different Encoding Techniques")

    print("Let's encode the same message with different techniques:\n")

    print("Technique 1: Dynamics only\n")
    run_command('python -m music_steg.cli encode '
               '-i examples/longer_piece.musicxml '
               '-m "Technique test" '
               '-o demo_dynamics.musicxml '
               '-t dynamics')

    print("\nTechnique 2: Dynamics + Stem directions\n")
    run_command('python -m music_steg.cli encode '
               '-i examples/longer_piece.musicxml '
               '-m "Technique test" '
               '-o demo_dynamic_stem.musicxml '
               '-t dynamics,stem')

    print("\nTechnique 3: All techniques (maximum capacity)\n")
    run_command('python -m music_steg.cli encode '
               '-i examples/longer_piece.musicxml '
               '-m "Technique test" '
               '-o demo_all.musicxml '
               '-t dynamics,stem,articulation,ornament')

    # Section 4: Musical Cipher
    print_section("4. Musical Cipher - Using Music as Encryption Key")

    print("Analyzing the cipher key strength:\n")

    run_command('python -m music_steg.cli cipher '
               '-k examples/jazz_key.musicxml '
               '-m "dummy" '
               '--mode analyze-key '
               '--analyze')

    print("Encrypting a message:\n")

    result = os.popen('python -m music_steg.cli cipher '
                     '-k examples/jazz_key.musicxml '
                     '-m "Top secret information!" '
                     '--mode encrypt').read()
    print(result)

    # Extract the hex from output
    for line in result.split('\n'):
        if 'Encrypted (hex):' in line:
            encrypted_hex = line.split('Encrypted (hex):')[1].strip()
            break

    print(f"Decrypting the message:\n")

    run_command(f'python -m music_steg.cli cipher '
               f'-k examples/jazz_key.musicxml '
               f'-m "{encrypted_hex}" '
               f'--mode decrypt')

    # Section 5: Combined Security
    print_section("5. Combined Security - Cipher + Steganography")

    print("Step 1: Encrypt with musical cipher\n")

    encrypted = os.popen('python -m music_steg.cli cipher '
                        '-k examples/jazz_key.musicxml '
                        '-m "Double protected" '
                        '--mode encrypt').read()

    for line in encrypted.split('\n'):
        if 'Encrypted (hex):' in line:
            encrypted_msg = line.split('Encrypted (hex):')[1].strip()
            break

    print(encrypted)

    print("\nStep 2: Hide encrypted message in music\n")

    run_command(f'python -m music_steg.cli encode '
               f'-i examples/longer_piece.musicxml '
               f'-m "{encrypted_msg}" '
               f'-o demo_double_protected.musicxml')

    print("Step 3: Extract from music\n")

    decrypted_result = os.popen('python -m music_steg.cli decode '
                                '-i demo_double_protected.musicxml '
                                '--try-all').read()
    print(decrypted_result)

    # Extract the hex message
    for line in decrypted_result.split('\n'):
        if 'Message:' in line and 'Best result' not in line:
            extracted_hex = line.split("'")[1]
            break

    print(f"\nStep 4: Decrypt with musical key\n")

    run_command(f'python -m music_steg.cli cipher '
               f'-k examples/jazz_key.musicxml '
               f'-m "{extracted_hex}" '
               f'--mode decrypt')

    # Section 6: Summary
    print_section("Demo Complete!")

    print("""
Summary of Features Demonstrated:
─────────────────────────────────────────────────────────────────

✓ File capacity analysis
✓ Basic message encoding/decoding
✓ Multiple encoding techniques
✓ Musical cipher encryption/decryption
✓ Key strength analysis
✓ Combined security (cipher + steganography)

Files Created:
─────────────────────────────────────────────────────────────────
- demo_encoded1.musicxml         : Basic steganography example
- demo_dynamics.musicxml         : Dynamics-only encoding
- demo_dynamic_stem.musicxml     : Dynamics + stem encoding
- demo_all.musicxml              : All techniques encoding
- demo_double_protected.musicxml : Cipher + steganography

Next Steps:
─────────────────────────────────────────────────────────────────
1. Read MUSIC_STEG_README.md for detailed documentation
2. Read docs/USER_GUIDE.md for tutorials
3. Experiment with your own MusicXML files
4. Create visualizations of encoded music

Try These Commands:
─────────────────────────────────────────────────────────────────
# Create visualization comparing before/after
python -m music_steg.visualize \\
  --compare examples/twinkle_twinkle.musicxml demo_encoded1.musicxml \\
  -o comparison.png

# Show capacity chart
python -m music_steg.visualize \\
  --capacity examples/*.musicxml \\
  -o capacity.png

Thank you for exploring the Music Steganography System! 🎵🔐
    """)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
