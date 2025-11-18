#!/usr/bin/env python3
"""
Generate example MusicXML files for testing the steganography system.
"""

from music21 import stream, note, metadata, tempo, key, meter


def create_simple_melody():
    """Create a simple C major melody."""
    s = stream.Score()

    # Add metadata
    s.metadata = metadata.Metadata()
    s.metadata.title = "Simple Melody"
    s.metadata.composer = "Music Steg Example"

    # Create part
    part = stream.Part()

    # Add tempo and key
    part.append(tempo.MetronomeMark(number=120))
    part.append(key.Key('C'))
    part.append(meter.TimeSignature('4/4'))

    # Simple C major scale melody
    notes_data = [
        ('C4', 1.0), ('D4', 1.0), ('E4', 1.0), ('F4', 1.0),
        ('G4', 1.0), ('A4', 1.0), ('B4', 1.0), ('C5', 2.0),
        ('B4', 1.0), ('A4', 1.0), ('G4', 1.0), ('F4', 1.0),
        ('E4', 1.0), ('D4', 1.0), ('C4', 2.0), ('C4', 2.0)
    ]

    for pitch, duration in notes_data:
        n = note.Note(pitch)
        n.quarterLength = duration
        part.append(n)

    s.append(part)
    return s


def create_longer_piece():
    """Create a longer piece with more capacity."""
    s = stream.Score()

    s.metadata = metadata.Metadata()
    s.metadata.title = "Longer Example Piece"
    s.metadata.composer = "Music Steg Example"

    part = stream.Part()
    part.append(tempo.MetronomeMark(number=100))
    part.append(key.Key('G'))
    part.append(meter.TimeSignature('4/4'))

    # Create a longer melody (repeated patterns)
    patterns = [
        # Pattern 1: ascending
        [('G4', 0.5), ('A4', 0.5), ('B4', 0.5), ('C5', 0.5),
         ('D5', 1.0), ('C5', 1.0), ('B4', 1.0), ('A4', 1.0)],

        # Pattern 2: descending
        [('G5', 0.5), ('F5', 0.5), ('E5', 0.5), ('D5', 0.5),
         ('C5', 1.0), ('B4', 1.0), ('A4', 1.0), ('G4', 1.0)],

        # Pattern 3: arpeggios
        [('G4', 0.5), ('B4', 0.5), ('D5', 0.5), ('G5', 0.5),
         ('D5', 0.5), ('B4', 0.5), ('G4', 1.0), ('G4', 1.0)],

        # Pattern 4: scalar
        [('C5', 0.5), ('D5', 0.5), ('E5', 0.5), ('F5', 0.5),
         ('G5', 0.5), ('A5', 0.5), ('B5', 0.5), ('C6', 0.5)]
    ]

    # Repeat patterns 3 times for capacity
    for _ in range(3):
        for pattern in patterns:
            for pitch, duration in pattern:
                n = note.Note(pitch)
                n.quarterLength = duration
                part.append(n)

    s.append(part)
    return s


def create_twinkle_twinkle():
    """Create 'Twinkle Twinkle Little Star'."""
    s = stream.Score()

    s.metadata = metadata.Metadata()
    s.metadata.title = "Twinkle Twinkle Little Star"
    s.metadata.composer = "Traditional"

    part = stream.Part()
    part.append(tempo.MetronomeMark(number=90))
    part.append(key.Key('C'))
    part.append(meter.TimeSignature('4/4'))

    # Twinkle Twinkle melody
    melody = [
        ('C4', 1.0), ('C4', 1.0), ('G4', 1.0), ('G4', 1.0),
        ('A4', 1.0), ('A4', 1.0), ('G4', 2.0),
        ('F4', 1.0), ('F4', 1.0), ('E4', 1.0), ('E4', 1.0),
        ('D4', 1.0), ('D4', 1.0), ('C4', 2.0),

        ('G4', 1.0), ('G4', 1.0), ('F4', 1.0), ('F4', 1.0),
        ('E4', 1.0), ('E4', 1.0), ('D4', 2.0),
        ('G4', 1.0), ('G4', 1.0), ('F4', 1.0), ('F4', 1.0),
        ('E4', 1.0), ('E4', 1.0), ('D4', 2.0),

        ('C4', 1.0), ('C4', 1.0), ('G4', 1.0), ('G4', 1.0),
        ('A4', 1.0), ('A4', 1.0), ('G4', 2.0),
        ('F4', 1.0), ('F4', 1.0), ('E4', 1.0), ('E4', 1.0),
        ('D4', 1.0), ('D4', 1.0), ('C4', 2.0)
    ]

    for pitch, duration in melody:
        n = note.Note(pitch)
        n.quarterLength = duration
        part.append(n)

    s.append(part)
    return s


def create_jazz_progression():
    """Create a jazz-style progression for cipher key."""
    s = stream.Score()

    s.metadata = metadata.Metadata()
    s.metadata.title = "Jazz Progression (Cipher Key)"
    s.metadata.composer = "Music Steg Example"

    part = stream.Part()
    part.append(tempo.MetronomeMark(number=120))
    part.append(key.Key('F'))
    part.append(meter.TimeSignature('4/4'))

    # More complex jazz-influenced melody for better cipher entropy
    melody = [
        ('F4', 0.5), ('A4', 0.5), ('C5', 0.5), ('E5', 0.5),
        ('D5', 0.75), ('Bb4', 0.25), ('G4', 1.0), ('F4', 1.0),

        ('G4', 0.5), ('B4', 0.5), ('D5', 0.5), ('F5', 0.5),
        ('E5', 0.75), ('C5', 0.25), ('A4', 1.0), ('G4', 1.0),

        ('A4', 0.5), ('C5', 0.5), ('E5', 0.5), ('G5', 0.5),
        ('F5', 0.75), ('D5', 0.25), ('B4', 1.0), ('A4', 1.0),

        ('Bb4', 0.5), ('D5', 0.5), ('F5', 0.5), ('A5', 0.5),
        ('G5', 0.75), ('E5', 0.25), ('C5', 1.0), ('Bb4', 1.0),

        # Add chromatic movement for entropy
        ('F4', 0.25), ('F#4', 0.25), ('G4', 0.25), ('Ab4', 0.25),
        ('A4', 0.25), ('Bb4', 0.25), ('B4', 0.25), ('C5', 0.25),
        ('C#5', 0.25), ('D5', 0.25), ('Eb5', 0.25), ('E5', 0.25),
        ('F5', 2.0)
    ]

    for pitch, duration in melody:
        n = note.Note(pitch)
        n.quarterLength = duration
        part.append(n)

    s.append(part)
    return s


def main():
    """Generate all example files."""
    print("🎵 Generating example MusicXML files...")

    examples = [
        ("simple_melody.musicxml", create_simple_melody()),
        ("longer_piece.musicxml", create_longer_piece()),
        ("twinkle_twinkle.musicxml", create_twinkle_twinkle()),
        ("jazz_key.musicxml", create_jazz_progression())
    ]

    for filename, score in examples:
        filepath = f"examples/{filename}"
        score.write('musicxml', fp=filepath)
        print(f"  ✓ Created {filename}")

        # Count notes
        notes = list(score.flatten().notes)
        print(f"    - {len(notes)} notes")

    print("\n✅ All example files created!")


if __name__ == '__main__':
    main()
