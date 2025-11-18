#!/usr/bin/env python3
"""
Visual demonstration tool for music steganography.

Shows before/after comparisons of sheet music.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from music21 import converter, note
from typing import List, Tuple
import argparse


class MusicVisualizer:
    """
    Visualizer for comparing original and steganographic music.
    """

    def __init__(self):
        pass

    def extract_note_data(self, musicxml_file: str) -> List[dict]:
        """
        Extract note data for visualization.

        Args:
            musicxml_file: Path to MusicXML file

        Returns:
            List of note data dictionaries
        """
        score = converter.parse(musicxml_file)
        notes_list = [n for n in score.flatten().notesAndRests if isinstance(n, note.Note)]

        note_data = []
        for i, n in enumerate(notes_list):
            data = {
                'index': i,
                'pitch': n.pitch.midi,
                'pitch_name': n.pitch.nameWithOctave,
                'duration': n.quarterLength,
                'dynamic': None,
                'articulation': None,
                'stem': None,
                'ornament': None
            }

            # Extract dynamics
            for expr in n.expressions:
                if hasattr(expr, 'value'):
                    data['dynamic'] = expr.value
                    break

            # Check lyrics for dynamics
            if not data['dynamic'] and len(n.lyrics) > 0:
                data['dynamic'] = n.lyrics[0].text

            # Extract articulation
            if len(n.articulations) > 0:
                data['articulation'] = type(n.articulations[0]).__name__

            # Extract stem
            if hasattr(n, 'stemDirection') and n.stemDirection:
                data['stem'] = n.stemDirection

            # Extract ornaments
            for expr in n.expressions:
                expr_type = type(expr).__name__
                if expr_type in ['Trill', 'Mordent', 'Turn', 'Shake']:
                    data['ornament'] = expr_type
                    break

            note_data.append(data)

        return note_data

    def compare_files(self, original_file: str, encoded_file: str, output_file: str = None):
        """
        Create a visual comparison of original and encoded files.

        Args:
            original_file: Original MusicXML file
            encoded_file: Encoded MusicXML file
            output_file: Output image file (optional)
        """
        orig_data = self.extract_note_data(original_file)
        enc_data = self.extract_note_data(encoded_file)

        fig, axes = plt.subplots(4, 1, figsize=(14, 10))
        fig.suptitle('Music Steganography: Before/After Comparison', fontsize=16, fontweight='bold')

        # Plot 1: Pitch comparison
        ax1 = axes[0]
        indices = [d['index'] for d in orig_data]
        orig_pitches = [d['pitch'] for d in orig_data]
        enc_pitches = [d['pitch'] for d in enc_data]

        ax1.plot(indices, orig_pitches, 'o-', label='Original', alpha=0.7, linewidth=2)
        ax1.plot(indices, enc_pitches, 's--', label='Encoded', alpha=0.7, linewidth=2)
        ax1.set_ylabel('MIDI Pitch')
        ax1.set_title('Note Pitches (Should be identical)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Plot 2: Dynamics comparison
        ax2 = axes[1]
        orig_dynamics = self._encode_dynamics_for_plot(orig_data)
        enc_dynamics = self._encode_dynamics_for_plot(enc_data)

        x = range(len(orig_dynamics))
        width = 0.35
        ax2.bar([i - width/2 for i in x], orig_dynamics, width, label='Original', alpha=0.7)
        ax2.bar([i + width/2 for i in x], enc_dynamics, width, label='Encoded', alpha=0.7)
        ax2.set_ylabel('Dynamic Level')
        ax2.set_title('Dynamic Markings (Encoded data here)')
        ax2.set_xlabel('Note Index')
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis='y')

        # Plot 3: Stem directions
        ax3 = axes[2]
        orig_stems = self._encode_stems_for_plot(orig_data)
        enc_stems = self._encode_stems_for_plot(enc_data)

        ax3.scatter(x, orig_stems, marker='o', s=50, label='Original', alpha=0.7)
        ax3.scatter(x, enc_stems, marker='s', s=50, label='Encoded', alpha=0.7)
        ax3.set_ylabel('Stem Direction (0=down, 1=up)')
        ax3.set_title('Stem Directions (Encoded data here)')
        ax3.set_xlabel('Note Index')
        ax3.set_yticks([0, 1])
        ax3.set_yticklabels(['Down', 'Up'])
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        # Plot 4: Articulation comparison
        ax4 = axes[3]
        orig_artics = self._encode_articulations_for_plot(orig_data)
        enc_artics = self._encode_articulations_for_plot(enc_data)

        ax4.bar([i - width/2 for i in x], orig_artics, width, label='Original', alpha=0.7)
        ax4.bar([i + width/2 for i in x], enc_artics, width, label='Encoded', alpha=0.7)
        ax4.set_ylabel('Articulation Type')
        ax4.set_title('Articulations (Encoded data here)')
        ax4.set_xlabel('Note Index')
        ax4.legend()
        ax4.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, dpi=150, bbox_inches='tight')
            print(f"💾 Visualization saved to {output_file}")
        else:
            plt.show()

    def _encode_dynamics_for_plot(self, note_data: List[dict]) -> List[int]:
        """Convert dynamics to numeric values for plotting."""
        dynamic_map = {
            'ppp': 0, 'pp': 1, 'p': 2, 'mp': 3,
            'mf': 4, 'f': 5, 'ff': 6, 'fff': 7
        }
        return [dynamic_map.get(d['dynamic'], 0) for d in note_data]

    def _encode_stems_for_plot(self, note_data: List[dict]) -> List[int]:
        """Convert stem directions to numeric values."""
        return [1 if d['stem'] == 'up' else 0 for d in note_data]

    def _encode_articulations_for_plot(self, note_data: List[dict]) -> List[int]:
        """Convert articulations to numeric values."""
        artic_map = {
            None: 0,
            'Staccato': 1,
            'Accent': 2,
            'Tenuto': 3,
            'Staccatissimo': 4,
            'Marcato': 5
        }
        return [artic_map.get(d['articulation'], 0) for d in note_data]

    def show_capacity_chart(self, musicxml_files: List[str], output_file: str = None):
        """
        Show capacity comparison chart for multiple files.

        Args:
            musicxml_files: List of MusicXML file paths
            output_file: Output image file (optional)
        """
        from music_steg.encoder import MusicEncoder

        encoder = MusicEncoder()
        file_data = []

        for filepath in musicxml_files:
            capacity = encoder.estimate_capacity(filepath)
            file_data.append({
                'name': filepath.split('/')[-1].replace('.musicxml', ''),
                'notes': capacity['total_notes'],
                'chars': capacity['max_message_chars'],
                'bits': capacity['total_bits']
            })

        # Create chart
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle('Steganography Capacity Analysis', fontsize=14, fontweight='bold')

        names = [d['name'] for d in file_data]
        notes = [d['notes'] for d in file_data]
        chars = [d['chars'] for d in file_data]

        # Chart 1: Notes count
        ax1.barh(names, notes, color='skyblue')
        ax1.set_xlabel('Number of Notes')
        ax1.set_title('Notes Available')
        ax1.grid(True, alpha=0.3, axis='x')

        # Chart 2: Character capacity
        ax2.barh(names, chars, color='lightcoral')
        ax2.set_xlabel('Maximum Message Length (characters)')
        ax2.set_title('Message Capacity')
        ax2.grid(True, alpha=0.3, axis='x')

        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, dpi=150, bbox_inches='tight')
            print(f"💾 Capacity chart saved to {output_file}")
        else:
            plt.show()

    def create_technique_comparison(self, musicxml_file: str, message: str, output_file: str = None):
        """
        Show how different techniques encode the same message.

        Args:
            musicxml_file: Input MusicXML file
            message: Message to encode
            output_file: Output image file (optional)
        """
        from music_steg.encoder import MusicEncoder
        import tempfile
        import os

        encoder = MusicEncoder()

        # Encode with different techniques
        techniques_sets = [
            (['dynamics'], 'Dynamics Only'),
            (['stem'], 'Stem Only'),
            (['dynamics', 'stem'], 'Dynamics + Stem'),
            (['dynamics', 'articulation'], 'Dynamics + Articulation'),
        ]

        fig, axes = plt.subplots(len(techniques_sets), 1, figsize=(12, 10))
        fig.suptitle(f'Technique Comparison: "{message}"', fontsize=14, fontweight='bold')

        for idx, (techniques, label) in enumerate(techniques_sets):
            # Create temp file
            temp_file = tempfile.mktemp(suffix='.musicxml')

            try:
                stats = encoder.encode_message(musicxml_file, message, temp_file, techniques)

                # Extract data
                enc_data = self.extract_note_data(temp_file)

                # Plot encoding pattern
                ax = axes[idx]
                x = range(len(enc_data))

                # Show which notes were modified
                y_vals = []
                for d in enc_data:
                    value = 0
                    if d['dynamic']:
                        value += 1
                    if d['stem']:
                        value += 1
                    if d['articulation']:
                        value += 1
                    y_vals.append(value)

                ax.bar(x, y_vals, alpha=0.7)
                ax.set_ylabel('Modifications')
                ax.set_title(f'{label} - {stats["bits_encoded"]} bits, {stats["notes_used"]} notes')
                ax.grid(True, alpha=0.3, axis='y')

                if idx == len(techniques_sets) - 1:
                    ax.set_xlabel('Note Index')

            except Exception as e:
                print(f"Error with {label}: {e}")

            finally:
                if os.path.exists(temp_file):
                    os.remove(temp_file)

        plt.tight_layout()

        if output_file:
            plt.savefig(output_file, dpi=150, bbox_inches='tight')
            print(f"💾 Technique comparison saved to {output_file}")
        else:
            plt.show()


def main():
    """Main entry point for visualization tool."""
    parser = argparse.ArgumentParser(description='Visualize music steganography')

    parser.add_argument('--compare', nargs=2, metavar=('ORIGINAL', 'ENCODED'),
                       help='Compare original and encoded files')
    parser.add_argument('--capacity', nargs='+', metavar='FILE',
                       help='Show capacity chart for files')
    parser.add_argument('--techniques', nargs=2, metavar=('FILE', 'MESSAGE'),
                       help='Compare different techniques')
    parser.add_argument('-o', '--output', help='Output image file')

    args = parser.parse_args()

    viz = MusicVisualizer()

    if args.compare:
        viz.compare_files(args.compare[0], args.compare[1], args.output)
    elif args.capacity:
        viz.show_capacity_chart(args.capacity, args.output)
    elif args.techniques:
        viz.create_technique_comparison(args.techniques[0], args.techniques[1], args.output)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
