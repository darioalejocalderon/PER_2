# Music Steganography - Detailed User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Basic Concepts](#basic-concepts)
4. [Tutorial: Your First Hidden Message](#tutorial)
5. [Advanced Usage](#advanced-usage)
6. [Technique Reference](#technique-reference)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Introduction

Music steganography is the practice of hiding information within sheet music. This system uses MusicXML files (a standard format for digital sheet music) to conceal text messages using various musical notations that don't affect the actual notes being played.

### Why Use Music Steganography?

- **Covert Communication**: Send messages hidden in plain sight
- **Educational**: Learn about information theory and cryptography
- **Creative**: Combine art (music) with technology (cryptography)
- **Fun**: Challenge friends to find hidden messages in compositions

### What Makes This System Unique?

- **Multiple Techniques**: Uses 4 different encoding methods
- **Musical Cipher**: Can use music itself as an encryption key
- **Integrity Checking**: Built-in message validation
- **Visual Tools**: See the differences between original and encoded music

## Installation

### Step 1: Install Python

Ensure you have Python 3.7 or later:

```bash
python --version
# Should show Python 3.7.x or higher
```

### Step 2: Install Dependencies

```bash
# Navigate to the project directory
cd PER_2

# Install required packages
pip install -r requirements.txt
```

### Step 3: Generate Example Files

```bash
python examples/generate_examples.py
```

This creates four example MusicXML files:
- `simple_melody.musicxml` - 16 notes, ~5 character capacity
- `twinkle_twinkle.musicxml` - 42 notes, ~15 character capacity
- `longer_piece.musicxml` - 96 notes, ~40 character capacity
- `jazz_key.musicxml` - Complex piece for cipher keys

### Step 4: Verify Installation

```bash
python -m music_steg.cli analyze -i examples/twinkle_twinkle.musicxml
```

You should see file analysis output with capacity information.

## Basic Concepts

### How Steganography Works

The system hides data by modifying musical elements that don't change the pitches or rhythm:

1. **Dynamic Markings** (pp, p, mf, f, ff)
   - Normal use: Indicates volume
   - Steganographic use: Each marking represents 3 bits (8 possible values)

2. **Stem Directions** (up/down)
   - Normal use: Visual clarity in sheet music
   - Steganographic use: Each direction represents 1 bit

3. **Articulations** (staccato, accent, tenuto)
   - Normal use: How to play the note
   - Steganographic use: Each type represents 2 bits

4. **Ornaments** (trill, mordent, turn)
   - Normal use: Note embellishments
   - Steganographic use: Each type represents 2 bits

### Message Encoding Structure

Every encoded message has this structure:

```
[16-bit length] + [64-bit hash] + [message bits]
                 ↓
         80 bits overhead
```

- **Length**: Tells decoder how many characters to extract
- **Hash**: SHA-256 checksum for validation
- **Message**: Your actual secret message

### Capacity Calculation

Using default techniques (dynamics + stem = 4 bits/note):

```
Available bits = (Number of notes × 4) - 80
Max characters = Available bits ÷ 8
```

Example: 50 notes
- Total bits: 50 × 4 = 200 bits
- After overhead: 200 - 80 = 120 bits
- Character capacity: 120 ÷ 8 = 15 characters

## Tutorial

### Tutorial 1: Hide and Reveal a Message

**Step 1: Check capacity**

```bash
python -m music_steg.cli analyze -i examples/twinkle_twinkle.musicxml
```

Output shows:
```
Maximum message: 15 characters
```

**Step 2: Encode a message**

```bash
python -m music_steg.cli encode \
  -i examples/twinkle_twinkle.musicxml \
  -m "Hello World!" \
  -o my_encoded.musicxml
```

Output:
```
✅ Encoding successful!
  Bits encoded: 176
  Notes used: 44/42
  Techniques: dynamics, stem
```

**Step 3: Decode the message**

```bash
python -m music_steg.cli decode \
  -i my_encoded.musicxml \
  --auto-detect
```

Output:
```
✅ Decoding successful! [✓ Valid]
  Message: Hello World!
```

**Success!** You've hidden and recovered your first message.

### Tutorial 2: Using Musical Cipher

**Step 1: Encrypt with music**

```bash
python -m music_steg.cli cipher \
  -k examples/jazz_key.musicxml \
  -m "Secret meeting at noon" \
  --mode encrypt \
  -o encrypted.txt
```

Output shows encrypted hex string:
```
Encrypted (hex): 3a7f2e1b9c4d...
```

**Step 2: Decrypt**

```bash
python -m music_steg.cli cipher \
  -k examples/jazz_key.musicxml \
  -m "3a7f2e1b9c4d..." \
  --mode decrypt
```

Output:
```
Decrypted: Secret meeting at noon
```

**Step 3: Analyze key strength**

```bash
python -m music_steg.cli cipher \
  -k examples/jazz_key.musicxml \
  -m "dummy" \
  --mode analyze-key \
  --analyze
```

Shows entropy and strength rating.

### Tutorial 3: Combined Security

For maximum security, combine cipher + steganography:

**Step 1: Encrypt with musical cipher**

```bash
python -m music_steg.cli cipher \
  -k examples/jazz_key.musicxml \
  -m "Top secret!" \
  --mode encrypt \
  -o encrypted.txt
```

**Step 2: Read the encrypted hex**

```bash
cat encrypted.txt
# Output: a1b2c3d4e5f6...
```

**Step 3: Hide encrypted message in music**

```bash
python -m music_steg.cli encode \
  -i examples/longer_piece.musicxml \
  -m "a1b2c3d4e5f6..." \
  -o double_protected.musicxml
```

**Step 4: To retrieve**

```bash
# First, extract from music
python -m music_steg.cli decode \
  -i double_protected.musicxml \
  --auto-detect \
  -o extracted.txt

# Then, decrypt with cipher
python -m music_steg.cli cipher \
  -k examples/jazz_key.musicxml \
  -m "$(cat extracted.txt)" \
  --mode decrypt
```

Now you have two layers of protection!

## Advanced Usage

### Custom Technique Combinations

Experiment with different techniques:

```bash
# Use all techniques (maximum capacity)
python -m music_steg.cli encode \
  -i examples/longer_piece.musicxml \
  -m "Maximum capacity message here!" \
  -o max_capacity.musicxml \
  -t dynamics,stem,articulation,ornament

# Dynamics only (most natural looking)
python -m music_steg.cli encode \
  -i examples/longer_piece.musicxml \
  -m "Natural" \
  -o natural.musicxml \
  -t dynamics

# Stem only (minimal visual impact)
python -m music_steg.cli encode \
  -i examples/longer_piece.musicxml \
  -m "Hidden" \
  -o minimal.musicxml \
  -t stem
```

### Batch Processing

Process multiple files programmatically:

```python
from music_steg import MusicEncoder

encoder = MusicEncoder()

messages = [
    "Message one",
    "Message two",
    "Message three"
]

for i, msg in enumerate(messages):
    encoder.encode_message(
        "examples/longer_piece.musicxml",
        msg,
        f"output_{i}.musicxml",
        techniques=['dynamics', 'stem']
    )
    print(f"Encoded message {i+1}")
```

### Try All Decoding Methods

If you're not sure which techniques were used:

```bash
python -m music_steg.cli decode \
  -i unknown_encoding.musicxml \
  --try-all
```

This tries all possible technique combinations and shows the most likely results.

### Programmatic Analysis

```python
from music_steg import MusicDecoder, MusicEncoder

encoder = MusicEncoder()
decoder = MusicDecoder()

# Analyze file
capacity = encoder.estimate_capacity("music.musicxml")
analysis = decoder.analyze_file("music.musicxml")

print(f"Capacity: {capacity['max_message_chars']} chars")
print(f"Detected techniques: {analysis['detected_techniques']}")
print(f"Dynamic distribution: {analysis['dynamics_distribution']}")
```

## Technique Reference

### Dynamic Markings (3 bits/note)

| Marking | Binary | Description |
|---------|--------|-------------|
| pp      | 000    | Very soft |
| p       | 001    | Soft |
| mp      | 010    | Moderately soft |
| mf      | 011    | Moderately loud |
| f       | 100    | Loud |
| ff      | 101    | Very loud |
| fff     | 110    | Extremely loud |
| ppp     | 111    | Extremely soft |

**Pros:**
- High capacity (3 bits)
- Musically meaningful
- Common in sheet music

**Cons:**
- Visible to musicians
- May affect interpretation

### Stem Directions (1 bit/note)

| Direction | Binary | Use Case |
|-----------|--------|----------|
| Down      | 0      | Lower voice/hand |
| Up        | 1      | Upper voice/hand |

**Pros:**
- Very subtle
- Often flexible in single-voice music
- Low visual impact

**Cons:**
- Low capacity (1 bit)
- Some positions have conventions

### Articulations (2 bits/note)

| Type       | Binary | Symbol |
|------------|--------|--------|
| None       | 00     | -      |
| Staccato   | 01     | •      |
| Accent     | 10     | >      |
| Tenuto     | 11     | —      |

**Pros:**
- Moderate capacity (2 bits)
- Common markings
- Clear symbols

**Cons:**
- Affects playing style
- May conflict with musical intent

### Ornaments (2 bits/note)

| Type     | Binary | Symbol |
|----------|--------|--------|
| None     | 00     | -      |
| Trill    | 01     | tr     |
| Mordent  | 10     | ♯      |
| Turn     | 11     | ∞      |

**Pros:**
- Moderate capacity (2 bits)
- Adds musical interest

**Cons:**
- Less common than dynamics
- Obvious additions

## Best Practices

### Choosing a Carrier File

Good carrier files:
- ✅ Have many notes (50+)
- ✅ Already use some dynamics
- ✅ Single voice/instrument
- ✅ Not too famous (less scrutiny)

Poor carrier files:
- ❌ Very few notes (<20)
- ❌ Completely bare (no markings)
- ❌ Multiple complex voices
- ❌ Well-known pieces

### Message Guidelines

**Do:**
- Keep messages short (use available capacity)
- Include only essential information
- Use abbreviations if needed
- Test encode/decode before sharing

**Don't:**
- Exceed capacity (will error)
- Use special Unicode characters (may not encode correctly)
- Reuse the same carrier repeatedly
- Send without testing

### Security Tips

1. **Combine Techniques**
   - Use cipher + steganography
   - Don't rely on steganography alone

2. **Key Management**
   - Keep cipher key files secret
   - Use different keys for different purposes
   - Use complex pieces (jazz, chromatic) as keys

3. **Operational Security**
   - Don't share carrier files publicly before encoding
   - Use different carrier files for each message
   - Verify messages before sending

4. **Plausible Deniability**
   - Choose musically appropriate markings
   - Don't over-encode (leave some notes unmarked)
   - Use realistic dynamic progressions

## Troubleshooting

### Problem: "Message too long" Error

**Cause**: Message exceeds file capacity

**Solution**:
```bash
# Check capacity first
python -m music_steg.cli analyze -i yourfile.musicxml

# Use a longer piece OR
# Use more techniques:
python -m music_steg.cli encode ... -t dynamics,stem,articulation
```

### Problem: Decoded Message is Garbage

**Possible causes**:
1. Wrong techniques used
2. File was modified
3. Encoding error

**Solutions**:
```bash
# Try auto-detect
python -m music_steg.cli decode -i file.musicxml --auto-detect

# Try all combinations
python -m music_steg.cli decode -i file.musicxml --try-all
```

### Problem: Invalid Checksum Warning

**Cause**: Message extracted but hash doesn't match

**Possible reasons**:
- File was edited after encoding
- Wrong technique combination
- Partial corruption

**What to do**:
- Try `--try-all` to find better match
- Re-encode from original if available
- Message may still be readable, but verify carefully

### Problem: Can't Open MusicXML File

**Cause**: Invalid or corrupted XML

**Solutions**:
```bash
# Check file is valid XML
xmllint --noout yourfile.musicxml

# Regenerate if it's an example file
python examples/generate_examples.py
```

### Problem: "No notes found" Error

**Cause**: File has no note elements (only rests or metadata)

**Solution**:
- Use a file with actual notes
- Check file in music notation software
- Regenerate example files

### Problem: Module Not Found

**Cause**: Dependencies not installed or wrong Python path

**Solutions**:
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Run as module
python -m music_steg.cli ...

# Check Python version
python --version  # Should be 3.7+
```

## Performance Tips

### For Large Files

When working with large MusicXML files:

```python
# Process in parts if needed
from music_steg import MusicEncoder

encoder = MusicEncoder()

# Check capacity before encoding
capacity = encoder.estimate_capacity("large_file.musicxml")
if capacity['max_message_chars'] < len(message):
    print("Split message or use larger file")
```

### Optimize Technique Selection

Different techniques have different performance:

- **Fastest**: dynamics, stem (simple attribute changes)
- **Slower**: articulation, ornament (new elements)

For best performance with large files:
```bash
python -m music_steg.cli encode ... -t dynamics,stem
```

## Visualization

Create visual comparisons:

```bash
# Compare before/after
python -m music_steg.visualize \
  --compare original.musicxml encoded.musicxml \
  -o comparison.png

# Show capacity of multiple files
python -m music_steg.visualize \
  --capacity examples/*.musicxml \
  -o capacity_chart.png

# Compare different techniques
python -m music_steg.visualize \
  --techniques examples/twinkle_twinkle.musicxml "Test" \
  -o technique_comparison.png
```

## Next Steps

Now that you understand the system:

1. **Experiment**: Try different messages and techniques
2. **Create Music**: Make your own MusicXML files for encoding
3. **Explore Code**: Read the source to understand implementation
4. **Extend**: Add new encoding techniques
5. **Share**: (Carefully!) Send hidden messages to friends

## Additional Resources

- **MusicXML Format**: https://www.w3.org/2021/06/musicxml40/
- **music21 Documentation**: http://web.mit.edu/music21/
- **Steganography Theory**: Research papers on digital steganography
- **Cryptography Basics**: Learn about ciphers and encryption

---

**Happy hiding!** 🎵🔐
