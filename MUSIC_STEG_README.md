# Music Steganography and Cryptography System

A comprehensive Python-based system for hiding secret messages in sheet music using MusicXML format. This tool combines multiple steganographic techniques with musical cipher encryption to provide flexible options for covert communication through music.

## Features

### 1. Steganography (Hide Messages in Music)

Hide text messages within sheet music using multiple techniques:
- **Dynamic Markings**: Encode 3 bits per note using volume markings (pp, p, mp, mf, f, ff, fff, ppp)
- **Stem Directions**: Encode 1 bit per note using stem up/down
- **Articulation Marks**: Encode 2 bits per note using staccato, accent, tenuto
- **Ornaments**: Encode 2 bits per note using trills, mordents, turns

### 2. Musical Cipher Encryption

Use a piece of music as an encryption key:
- Extracts note pitches, intervals, and durations to generate cipher keys
- XOR stream cipher with musical mixing
- Substitution cipher generation
- Key strength analysis with entropy calculation

### 3. Visualization & Analysis

- Before/after comparison charts
- Capacity estimation
- Technique comparison visualizations
- Detailed file analysis

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Generate example files
python examples/generate_examples.py
```

### Requirements
- Python 3.7+
- music21 >= 9.1.0
- lxml >= 4.9.0
- matplotlib >= 3.7.0
- Pillow >= 10.0.0

## Quick Start

### Encoding a Message

```bash
# Basic encoding using dynamics and stem directions
python -m music_steg.cli encode \
  -i examples/twinkle_twinkle.musicxml \
  -m "Secret message here" \
  -o output_encoded.musicxml

# Use specific techniques
python -m music_steg.cli encode \
  -i examples/longer_piece.musicxml \
  -m "Top secret!" \
  -o output.musicxml \
  -t dynamics,stem,articulation
```

### Decoding a Message

```bash
# Auto-detect techniques and decode
python -m music_steg.cli decode \
  -i output_encoded.musicxml \
  --auto-detect

# Try all technique combinations
python -m music_steg.cli decode \
  -i output_encoded.musicxml \
  --try-all

# Save decoded message to file
python -m music_steg.cli decode \
  -i output_encoded.musicxml \
  --auto-detect \
  -o decoded_message.txt
```

### Analyzing Capacity

```bash
# Check how much data can be hidden
python -m music_steg.cli analyze \
  -i examples/longer_piece.musicxml
```

### Musical Cipher Mode

```bash
# Encrypt a message using music as a key
python -m music_steg.cli cipher \
  -k examples/jazz_key.musicxml \
  -m "Secret message" \
  --mode encrypt \
  -o encrypted.txt

# Decrypt
python -m music_steg.cli cipher \
  -k examples/jazz_key.musicxml \
  -m "a1b2c3d4..." \
  --mode decrypt

# Analyze key strength
python -m music_steg.cli cipher \
  -k examples/jazz_key.musicxml \
  -m "dummy" \
  --mode analyze-key \
  --analyze
```

## Usage Examples

### Example 1: Basic Steganography

```python
from music_steg import MusicEncoder, MusicDecoder

# Initialize
encoder = MusicEncoder()
decoder = MusicDecoder()

# Check capacity
capacity = encoder.estimate_capacity("input.musicxml")
print(f"Can hide up to {capacity['max_message_chars']} characters")

# Encode
stats = encoder.encode_message(
    "input.musicxml",
    "This is a secret message!",
    "output.musicxml",
    techniques=['dynamics', 'stem']
)
print(f"Encoded {stats['bits_encoded']} bits in {stats['notes_used']} notes")

# Decode
result = decoder.decode_message("output.musicxml", auto_detect=True)
print(f"Decoded message: {result['message']}")
print(f"Valid checksum: {result['is_valid']}")
```

### Example 2: Musical Cipher

```python
from music_steg import MusicCipher

cipher = MusicCipher()

# Load musical key
key_stats = cipher.load_key("key.musicxml")
print(f"Key loaded: {key_stats['key_length']} bytes")

# Encrypt
encrypted, key_hash = cipher.encrypt_message("Secret message")
print(f"Encrypted: {encrypted.hex()}")

# Decrypt
decrypted = cipher.decrypt_message(encrypted)
print(f"Decrypted: {decrypted}")

# Analyze key strength
strength = cipher.analyze_key_strength()
print(f"Key strength: {strength['strength']}")
print(f"Entropy: {strength['entropy']:.2f} bits")
```

### Example 3: Visualization

```python
from music_steg.visualize import MusicVisualizer

viz = MusicVisualizer()

# Compare original and encoded files
viz.compare_files(
    "original.musicxml",
    "encoded.musicxml",
    "comparison.png"
)

# Show capacity chart
viz.show_capacity_chart(
    ["file1.musicxml", "file2.musicxml", "file3.musicxml"],
    "capacity_chart.png"
)

# Compare techniques
viz.create_technique_comparison(
    "input.musicxml",
    "Test message",
    "techniques.png"
)
```

## How It Works

### Steganographic Encoding

The system encodes messages in multiple layers:

1. **Message Preparation**
   - Convert message to bits
   - Add length header (16 bits)
   - Add SHA-256 hash for integrity (64 bits)
   - Total overhead: 80 bits

2. **Encoding Process**
   - Parse MusicXML file to extract notes
   - Map message bits to musical elements:
     - Dynamics: 8 levels = 3 bits per note
     - Stems: 2 directions = 1 bit per note
     - Articulations: 4 types = 2 bits per note
     - Ornaments: 4 types = 2 bits per note

3. **Output**
   - Modified MusicXML file
   - Music remains playable
   - Changes appear natural to musicians

### Musical Cipher

The cipher system works by:

1. **Key Generation**
   - Extract notes from MusicXML
   - Combine MIDI pitch, octave, duration
   - Calculate intervals between consecutive notes
   - XOR properties to create key bytes

2. **Encryption**
   - Stream cipher using XOR
   - Key bytes repeat cyclically
   - Previous ciphertext byte mixed into key
   - Provides diffusion across message

3. **Security**
   - Entropy analysis measures key randomness
   - Longer, more complex pieces = stronger keys
   - Jazz/chromatic music provides better entropy

## Capacity Estimates

Typical capacity using dynamics + stem encoding (4 bits/note):

| Piece Type | Notes | Characters | Example |
|------------|-------|------------|---------|
| Simple melody | 16 | ~5 | "Hello" |
| Short song | 42 | ~15 | "Top secret msg!" |
| Full piece | 96 | ~40 | Full sentences |
| Long composition | 200+ | 90+ | Paragraphs |

*Note: 80 bits reserved for header (length + hash)*

## Security Considerations

### Steganography
- **Strength**: Security through obscurity
- **Detection**: Statistical analysis of dynamic/articulation patterns could reveal hidden data
- **Best Practices**:
  - Use music with natural dynamic variation
  - Don't reuse the same carrier file
  - Combine with encryption before encoding

### Musical Cipher
- **Strength**: Depends on key entropy and length
- **Recommendations**:
  - Use complex, chromatic pieces as keys
  - Longer pieces (50+ notes) provide better security
  - Key should be at least as long as message
  - Don't share key file publicly

### Combined Approach
For maximum security:
1. Encrypt message with musical cipher
2. Encode encrypted message in different music piece
3. Results in encryption + steganography layers

## File Structure

```
music_steg/
├── __init__.py          # Package initialization
├── encoder.py           # Steganographic encoder
├── decoder.py           # Steganographic decoder
├── cipher.py            # Musical cipher system
├── utils.py             # Utility functions
├── cli.py               # Command-line interface
└── visualize.py         # Visualization tools

examples/
├── generate_examples.py # Generate test files
├── simple_melody.musicxml
├── longer_piece.musicxml
├── twinkle_twinkle.musicxml
└── jazz_key.musicxml

docs/
└── USER_GUIDE.md        # Detailed user guide
```

## Command-Line Reference

### Encode Command
```bash
python -m music_steg.cli encode -i INPUT -m MESSAGE -o OUTPUT [-t TECHNIQUES] [-j JSON_OUTPUT]
```

**Options:**
- `-i, --input`: Input MusicXML file (required)
- `-m, --message`: Message to hide (required)
- `-o, --output`: Output MusicXML file (required)
- `-t, --techniques`: Comma-separated list (default: dynamics,stem)
- `-j, --json`: Save statistics to JSON file

**Techniques:**
- `dynamics`: Dynamic markings (pp, p, mp, mf, f, ff)
- `stem`: Stem directions (up/down)
- `articulation`: Articulation marks (staccato, accent, tenuto)
- `ornament`: Ornaments (trill, mordent, turn)

### Decode Command
```bash
python -m music_steg.cli decode -i INPUT [-o OUTPUT] [-t TECHNIQUES] [--auto-detect] [--try-all]
```

**Options:**
- `-i, --input`: Input MusicXML file (required)
- `-o, --output`: Output text file for message
- `-t, --techniques`: Specific techniques to use
- `--auto-detect`: Automatically detect techniques
- `--try-all`: Try all technique combinations

### Analyze Command
```bash
python -m music_steg.cli analyze -i INPUT
```

Shows detailed file analysis including capacity and detected techniques.

### Cipher Command
```bash
python -m music_steg.cli cipher -k KEY -m MESSAGE --mode MODE [-o OUTPUT] [--analyze]
```

**Modes:**
- `encrypt`: Encrypt message with musical key
- `decrypt`: Decrypt hex message
- `analyze-key`: Analyze key strength

## Visualization Tools

### Compare Files
```bash
python -m music_steg.visualize --compare original.musicxml encoded.musicxml -o comparison.png
```

### Show Capacity
```bash
python -m music_steg.visualize --capacity file1.musicxml file2.musicxml -o capacity.png
```

### Compare Techniques
```bash
python -m music_steg.visualize --techniques input.musicxml "Message" -o techniques.png
```

## Testing

Run the test suite:

```bash
# Basic functionality test
python -m music_steg.cli analyze -i examples/twinkle_twinkle.musicxml

# Encode/decode roundtrip test
python -m music_steg.cli encode -i examples/longer_piece.musicxml -m "Test message" -o test_encoded.musicxml
python -m music_steg.cli decode -i test_encoded.musicxml --auto-detect

# Cipher test
python -m music_steg.cli cipher -k examples/jazz_key.musicxml -m "Secret" --mode encrypt -o encrypted.txt
```

## Limitations

1. **Capacity**: Limited by number of notes in the piece
2. **Detection**: Unusual patterns may be detectable by analysis
3. **Music Quality**: Heavy encoding may affect musical naturalness
4. **Format**: Requires MusicXML format (not MIDI or audio)
5. **Playback**: Some notation software may not preserve all markings

## Future Enhancements

Potential improvements:
- Support for MIDI file format
- Audio-based steganography (hiding in WAV/MP3)
- Machine learning for natural-looking encoding
- Multi-voice/polyphonic encoding
- Error correction codes
- Compression before encoding

## Contributing

This is a demonstration project. Potential areas for contribution:
- Additional encoding techniques
- Better visualization options
- Support for more music formats
- Improved error handling
- Performance optimization

## License

For Private Use Only

## Acknowledgments

- Built with [music21](http://web.mit.edu/music21/) library
- Inspired by classical steganography techniques
- MusicXML format by MakeMusic

## Support

For issues or questions:
1. Check the documentation in `docs/`
2. Review example files in `examples/`
3. Examine the source code for implementation details

---

**Note**: This tool is for educational and research purposes. Always ensure you have the right to modify and distribute any sheet music files you use.
