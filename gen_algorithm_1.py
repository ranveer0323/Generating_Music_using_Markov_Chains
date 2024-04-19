import random
from collections import defaultdict
import os
import music21 as m21


def preprocess_midi_files(folder_path):
    all_note_pairs = []

    # Iterate through all files and subdirectories
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".mid"):  # Check if file is a MIDI file
                midi_file = os.path.join(root, file)
                midi = m21.converter.parse(midi_file)

                # Extract notes from MIDI file
                notes = []
                for element in midi.flat.notes:
                    if isinstance(element, m21.note.Note):
                        notes.append(element.pitch.midi)
                    elif isinstance(element, m21.chord.Chord):
                        for pitch in element.pitches:
                            notes.append(pitch.midi)

                # Create pairs of consecutive notes
                note_pairs = [(notes[i], notes[i + 1])
                              for i in range(len(notes) - 1)]

                # Add pairs to the list of all note pairs
                all_note_pairs.extend(note_pairs)

    return all_note_pairs


# Folder path where MIDI files are stored
folder_path = r"F:\University\Sem 2\Model Thinking\Beethoven stuff\MIDI Files\new2"

# Preprocess MIDI files to get note pairs
note_pairs = preprocess_midi_files(folder_path)

# Print the first 10 note pairs as an example
print(note_pairs[:10])


def calculate_transition_matrix(note_pairs):
    # Initialize a dictionary to store counts of each note pair
    transition_counts = defaultdict(lambda: defaultdict(int))

    # Count occurrences of each note pair
    for current_note, next_note in note_pairs:
        transition_counts[current_note][next_note] += 1

    # Initialize the transition matrix
    transition_matrix = {}

    # Normalize the counts to get probabilities
    for current_note, next_notes in transition_counts.items():
        total_transitions = sum(next_notes.values())
        probabilities = {
            next_note: count / total_transitions for next_note, count in next_notes.items()}
        transition_matrix[current_note] = probabilities

    return transition_matrix


# Calculate transition probabilities for note pairs
transition_matrix = calculate_transition_matrix(note_pairs)

# Print the transition matrix for an example
for current_note, next_notes in transition_matrix.items():
    print(
        f"Current Note: {current_note}, Next Notes Probabilities: {next_notes}")


def generate_new_music(transition_matrix, num_notes, start_note=None):
    if start_note is None:
        # If no start note is provided, choose a random start note from the transition matrix keys
        start_note = random.choice(list(transition_matrix.keys()))

    new_music = [start_note]
    current_note = start_note

    for _ in range(num_notes - 1):
        # If the current note is not in the transition matrix, choose a random next note
        if current_note not in transition_matrix:
            next_note = random.choice(list(transition_matrix.keys()))
        else:
            # Use the transition probabilities to choose the next note
            next_note_probabilities = transition_matrix[current_note]
            next_note = random.choices(list(next_note_probabilities.keys()),
                                       weights=list(next_note_probabilities.values()))[0]

        new_music.append(next_note)
        current_note = next_note

    return new_music


# Generate new music with 50 notes
new_music = generate_new_music(transition_matrix, num_notes=100)

# Print the generated new music
print("Generated New Music:")
print(new_music)


def convert_to_midi(note_sequence, output_file="generated_music.mid"):
    # Create a Stream object to store the notes
    stream = m21.stream.Stream()

    # Add each note to the Stream as a Note object
    for note_number in note_sequence:
        note_obj = m21.note.Note(note_number)
        stream.append(note_obj)

    # Write the Stream to a MIDI file
    stream.write("midi", fp=output_file)
    print(f"Generated music saved to '{output_file}'")


# Convert generated music to MIDI and save as a file
convert_to_midi(new_music, output_file="generated_music.mid")
