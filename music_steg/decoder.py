"""
Music Steganography Decoder

Extracts hidden messages from MusicXML files.
"""

from music21 import converter, note, dynamics, articulations, expressions
from typing import List, Dict, Tuple
from .utils import (
    decode_with_header,
    DYNAMIC_TO_BITS,
    ARTICULATION_TO_VALUE
)


class MusicDecoder:
    """
    Decoder for extracting hidden messages from MusicXML files.
    """

    def __init__(self):
        pass

    def detect_techniques(self, musicxml_file: str) -> Dict[str, bool]:
        """
        Detect which steganographic techniques are present in the file.

        Args:
            musicxml_file: Path to MusicXML file

        Returns:
            Dictionary indicating which techniques are detected
        """
        score = converter.parse(musicxml_file)
        notes_list = [n for n in score.flatten().notesAndRests if isinstance(n, note.Note)]

        detected = {
            'dynamics': False,
            'articulation': False,
            'stem': False,
            'ornament': False
        }

        # Check for dynamics
        for n in notes_list:
            if any(isinstance(e, dynamics.Dynamic) for e in n.expressions):
                detected['dynamics'] = True
                break

        # Check for articulations
        for n in notes_list:
            if len(n.articulations) > 0:
                detected['articulation'] = True
                break

        # Check for non-default stem directions
        stem_ups = sum(1 for n in notes_list if hasattr(n, 'stemDirection') and n.stemDirection == 'up')
        stem_downs = sum(1 for n in notes_list if hasattr(n, 'stemDirection') and n.stemDirection == 'down')
        if stem_ups > 0 and stem_downs > 0:
            detected['stem'] = True

        # Check for ornaments
        for n in notes_list:
            if any(isinstance(e, (expressions.Trill, expressions.Mordent, expressions.Turn))
                   for e in n.expressions):
                detected['ornament'] = True
                break

        return detected

    def decode_message(
        self,
        musicxml_file: str,
        techniques: List[str] = None,
        auto_detect: bool = True
    ) -> Dict[str, any]:
        """
        Decode a hidden message from a MusicXML file.

        Args:
            musicxml_file: Input MusicXML file path
            techniques: List of techniques to use for decoding
            auto_detect: Automatically detect techniques if True

        Returns:
            Dictionary with decoded message and statistics
        """
        # Parse the music
        score = converter.parse(musicxml_file)

        # Auto-detect techniques if requested
        if auto_detect:
            detected = self.detect_techniques(musicxml_file)
            techniques = [k for k, v in detected.items() if v]
            if not techniques:
                techniques = ['dynamics', 'stem']  # Default fallback
        elif techniques is None:
            techniques = ['dynamics', 'stem']

        # Get all notes
        notes_list = [n for n in score.flatten().notesAndRests if isinstance(n, note.Note)]

        # Extract bits using detected techniques
        extracted_bits = []

        for n in notes_list:
            # Extract from dynamics (3 bits)
            if 'dynamics' in techniques:
                dynamic_mark = None

                # Check expressions for dynamics
                for expr in n.expressions:
                    if isinstance(expr, dynamics.Dynamic):
                        dynamic_mark = expr.value
                        break

                # Also check lyrics (where we stored them during encoding)
                if not dynamic_mark and len(n.lyrics) > 0:
                    dynamic_mark = n.lyrics[0].text

                if dynamic_mark:
                    # Map dynamic to 3 bits
                    bit_value = DYNAMIC_TO_BITS.get(dynamic_mark, 0b011)  # Default to 'mf'
                    extracted_bits.append((bit_value >> 2) & 1)
                    extracted_bits.append((bit_value >> 1) & 1)
                    extracted_bits.append(bit_value & 1)

            # Extract from stem direction (1 bit)
            if 'stem' in techniques:
                if hasattr(n, 'stemDirection'):
                    stem_bit = 1 if n.stemDirection == 'up' else 0
                    extracted_bits.append(stem_bit)

            # Extract from articulation (2 bits)
            if 'articulation' in techniques:
                artic_value = 0
                if len(n.articulations) > 0:
                    artic = n.articulations[0]
                    if isinstance(artic, articulations.Staccato):
                        artic_value = 1
                    elif isinstance(artic, articulations.Accent):
                        artic_value = 2
                    elif isinstance(artic, articulations.Tenuto):
                        artic_value = 3

                extracted_bits.append((artic_value >> 1) & 1)
                extracted_bits.append(artic_value & 1)

            # Extract from ornaments (2 bits)
            if 'ornament' in techniques:
                orn_value = 0
                for expr in n.expressions:
                    if isinstance(expr, expressions.Trill):
                        orn_value = 1
                        break
                    elif isinstance(expr, expressions.Mordent):
                        orn_value = 2
                        break
                    elif isinstance(expr, expressions.Turn):
                        orn_value = 3
                        break

                extracted_bits.append((orn_value >> 1) & 1)
                extracted_bits.append(orn_value & 1)

        # Decode the message with header validation
        decoded_message, is_valid = decode_with_header(extracted_bits)

        # Calculate statistics
        stats = {
            'message': decoded_message,
            'is_valid': is_valid,
            'bits_extracted': len(extracted_bits),
            'notes_processed': len(notes_list),
            'techniques_used': techniques,
            'success': len(decoded_message) > 0
        }

        return stats

    def try_all_techniques(self, musicxml_file: str) -> List[Dict]:
        """
        Try decoding with all possible technique combinations.

        Args:
            musicxml_file: Input MusicXML file

        Returns:
            List of results from each technique combination
        """
        technique_sets = [
            ['dynamics'],
            ['stem'],
            ['dynamics', 'stem'],
            ['dynamics', 'articulation'],
            ['dynamics', 'stem', 'articulation'],
            ['dynamics', 'stem', 'articulation', 'ornament']
        ]

        results = []
        for techniques in technique_sets:
            try:
                stats = self.decode_message(
                    musicxml_file,
                    techniques=techniques,
                    auto_detect=False
                )
                stats['technique_combo'] = ' + '.join(techniques)
                results.append(stats)
            except Exception as e:
                results.append({
                    'technique_combo': ' + '.join(techniques),
                    'success': False,
                    'error': str(e)
                })

        # Sort by validity and message length
        results.sort(key=lambda x: (x.get('is_valid', False), len(x.get('message', ''))),
                    reverse=True)

        return results

    def analyze_file(self, musicxml_file: str) -> Dict[str, any]:
        """
        Perform comprehensive analysis of a MusicXML file.

        Args:
            musicxml_file: Input MusicXML file

        Returns:
            Dictionary with analysis results
        """
        score = converter.parse(musicxml_file)
        notes_list = [n for n in score.flatten().notesAndRests if isinstance(n, note.Note)]

        analysis = {
            'total_notes': len(notes_list),
            'detected_techniques': self.detect_techniques(musicxml_file),
            'dynamics_distribution': {},
            'articulation_distribution': {},
            'stem_distribution': {'up': 0, 'down': 0, 'unspecified': 0},
            'ornament_count': 0
        }

        # Analyze dynamics
        for n in notes_list:
            for expr in n.expressions:
                if isinstance(expr, dynamics.Dynamic):
                    dyn = expr.value
                    analysis['dynamics_distribution'][dyn] = \
                        analysis['dynamics_distribution'].get(dyn, 0) + 1

        # Analyze articulations
        for n in notes_list:
            for artic in n.articulations:
                artic_type = type(artic).__name__
                analysis['articulation_distribution'][artic_type] = \
                    analysis['articulation_distribution'].get(artic_type, 0) + 1

        # Analyze stems
        for n in notes_list:
            if hasattr(n, 'stemDirection') and n.stemDirection:
                analysis['stem_distribution'][n.stemDirection] += 1
            else:
                analysis['stem_distribution']['unspecified'] += 1

        # Count ornaments
        for n in notes_list:
            for expr in n.expressions:
                if isinstance(expr, (expressions.Trill, expressions.Mordent,
                                    expressions.Turn, expressions.Shake)):
                    analysis['ornament_count'] += 1

        return analysis
