"""
Music Steganography Encoder

Encodes secret messages into MusicXML files using various steganographic techniques.
"""

from music21 import converter, stream, note, dynamics, articulations, expressions
from typing import List, Dict, Tuple
import copy
from .utils import (
    encode_with_header,
    BITS_TO_DYNAMIC,
    VALUE_TO_ARTICULATION,
    VALUE_TO_ORNAMENT
)


class MusicEncoder:
    """
    Encoder for hiding messages in MusicXML files using steganography.
    """

    def __init__(self):
        self.capacity_report = {}

    def estimate_capacity(self, musicxml_file: str) -> Dict[str, int]:
        """
        Estimate the data capacity of a MusicXML file.

        Args:
            musicxml_file: Path to MusicXML file

        Returns:
            Dictionary with capacity estimates for each technique
        """
        score = converter.parse(musicxml_file)
        notes_list = list(score.flatten().notesAndRests)

        # Filter to only notes (not rests)
        actual_notes = [n for n in notes_list if isinstance(n, note.Note)]

        capacity = {
            'total_notes': len(actual_notes),
            'dynamic_bits': len(actual_notes) * 3,  # 3 bits per note (8 dynamics)
            'articulation_bits': len(actual_notes) * 2,  # ~2-3 bits per note
            'stem_bits': len(actual_notes),  # 1 bit per note
            'ornament_bits': len(actual_notes) * 2,  # ~2 bits per note
            'total_bits': 0,
            'max_message_chars': 0
        }

        # Conservative estimate: use dynamics (3 bits) + stems (1 bit) = 4 bits per note
        capacity['total_bits'] = len(actual_notes) * 4
        capacity['max_message_chars'] = (capacity['total_bits'] - 80) // 8  # Subtract header

        return capacity

    def encode_message(
        self,
        musicxml_file: str,
        message: str,
        output_file: str,
        techniques: List[str] = None
    ) -> Dict[str, any]:
        """
        Encode a message into a MusicXML file.

        Args:
            musicxml_file: Input MusicXML file path
            message: Secret message to hide
            output_file: Output MusicXML file path
            techniques: List of techniques to use ['dynamics', 'articulation', 'stem', 'ornament']
                       Default: ['dynamics', 'stem']

        Returns:
            Dictionary with encoding statistics
        """
        if techniques is None:
            techniques = ['dynamics', 'stem']

        # Parse the music
        score = converter.parse(musicxml_file)

        # Get capacity
        capacity = self.estimate_capacity(musicxml_file)

        # Encode message with header
        encoded_bits, total_bits = encode_with_header(message)

        if total_bits > capacity['total_bits']:
            raise ValueError(
                f"Message too long! Message needs {total_bits} bits, "
                f"but file only has capacity for {capacity['total_bits']} bits "
                f"({capacity['max_message_chars']} characters)."
            )

        # Get all notes from the score
        notes_list = [n for n in score.flatten().notesAndRests if isinstance(n, note.Note)]

        # Encode using selected techniques
        bit_index = 0
        notes_used = 0

        for n in notes_list:
            if bit_index >= total_bits:
                break

            # Dynamics encoding (3 bits per note)
            if 'dynamics' in techniques and bit_index + 3 <= total_bits:
                # Extract 3 bits
                dynamic_value = (encoded_bits[bit_index] << 2) | \
                               (encoded_bits[bit_index + 1] << 1) | \
                               encoded_bits[bit_index + 2]

                # Map to dynamic marking
                dynamic_mark = BITS_TO_DYNAMIC.get(dynamic_value, 'mf')

                # Remove existing dynamics
                n.expressions = [e for e in n.expressions if not isinstance(e, dynamics.Dynamic)]

                # Add new dynamic
                n.addLyric(dynamic_mark)  # Add as lyric for visibility
                if dynamic_mark == 'pp':
                    n.expressions.append(dynamics.Dynamic('pp'))
                elif dynamic_mark == 'p':
                    n.expressions.append(dynamics.Dynamic('p'))
                elif dynamic_mark == 'mp':
                    n.expressions.append(dynamics.Dynamic('mp'))
                elif dynamic_mark == 'mf':
                    n.expressions.append(dynamics.Dynamic('mf'))
                elif dynamic_mark == 'f':
                    n.expressions.append(dynamics.Dynamic('f'))
                elif dynamic_mark == 'ff':
                    n.expressions.append(dynamics.Dynamic('ff'))
                elif dynamic_mark == 'fff':
                    n.expressions.append(dynamics.Dynamic('fff'))
                elif dynamic_mark == 'ppp':
                    n.expressions.append(dynamics.Dynamic('ppp'))

                bit_index += 3

            # Stem direction encoding (1 bit per note)
            if 'stem' in techniques and bit_index < total_bits:
                stem_bit = encoded_bits[bit_index]
                n.stemDirection = 'up' if stem_bit == 1 else 'down'
                bit_index += 1

            # Articulation encoding (2-3 bits per note)
            if 'articulation' in techniques and bit_index + 2 <= total_bits:
                artic_value = (encoded_bits[bit_index] << 1) | encoded_bits[bit_index + 1]

                # Remove existing articulations
                n.articulations = []

                # Add articulation based on value
                artic_type = VALUE_TO_ARTICULATION.get(artic_value)
                if artic_type == 'staccato':
                    n.articulations.append(articulations.Staccato())
                elif artic_type == 'accent':
                    n.articulations.append(articulations.Accent())
                elif artic_type == 'tenuto':
                    n.articulations.append(articulations.Tenuto())

                bit_index += 2

            # Ornament encoding (2 bits per note)
            if 'ornament' in techniques and bit_index + 2 <= total_bits:
                orn_value = (encoded_bits[bit_index] << 1) | encoded_bits[bit_index + 1]

                # Remove existing ornaments
                n.expressions = [e for e in n.expressions
                               if not isinstance(e, (expressions.Trill, expressions.Mordent,
                                                    expressions.Turn, expressions.Shake))]

                # Add ornament based on value
                orn_type = VALUE_TO_ORNAMENT.get(orn_value)
                if orn_type == 'trill':
                    n.expressions.append(expressions.Trill())
                elif orn_type == 'mordent':
                    n.expressions.append(expressions.Mordent())
                elif orn_type == 'turn':
                    n.expressions.append(expressions.Turn())

                bit_index += 2

            notes_used += 1

        # Write output
        score.write('musicxml', fp=output_file)

        # Return statistics
        stats = {
            'message_length': len(message),
            'bits_encoded': bit_index,
            'notes_used': notes_used,
            'total_notes': len(notes_list),
            'capacity_remaining': capacity['total_bits'] - bit_index,
            'techniques_used': techniques,
            'success': True
        }

        return stats

    def batch_encode(
        self,
        musicxml_file: str,
        messages: List[str],
        output_prefix: str,
        technique_sets: List[List[str]] = None
    ) -> List[Dict]:
        """
        Encode multiple messages using different technique combinations.

        Args:
            musicxml_file: Input MusicXML file
            messages: List of messages to encode
            output_prefix: Prefix for output files
            technique_sets: List of technique combinations to try

        Returns:
            List of encoding statistics
        """
        if technique_sets is None:
            technique_sets = [
                ['dynamics', 'stem'],
                ['dynamics', 'articulation'],
                ['dynamics', 'stem', 'articulation']
            ]

        results = []
        for i, message in enumerate(messages):
            for j, techniques in enumerate(technique_sets):
                output_file = f"{output_prefix}_msg{i}_tech{j}.musicxml"
                try:
                    stats = self.encode_message(
                        musicxml_file,
                        message,
                        output_file,
                        techniques
                    )
                    stats['output_file'] = output_file
                    stats['message_index'] = i
                    stats['technique_index'] = j
                    results.append(stats)
                except Exception as e:
                    results.append({
                        'output_file': output_file,
                        'message_index': i,
                        'technique_index': j,
                        'success': False,
                        'error': str(e)
                    })

        return results
