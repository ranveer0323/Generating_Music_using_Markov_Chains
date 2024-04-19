import os
import music21 as m21
import random
from collections import defaultdict


def preprocess_midi_files(folder_path):
    left_hand_notes = []
    right_hand_notes = []

    # Iterate through all files and subdirectories
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".mid"):  # Check if file is a MIDI file
                midi_file = os.path.join(root, file)
                midi = m21.converter.parse(midi_file)

                # Extract left hand and right hand notes from MIDI file
                left_notes, right_notes = extract_left_right_hand_notes(midi)

                # Add notes to the lists
                left_hand_notes.extend(left_notes)
                right_hand_notes.extend(right_notes)

    return left_hand_notes, right_hand_notes


def extract_left_right_hand_notes(midi):
    left_notes = []
    right_notes = []

    for element in midi.flat.notes:
        if isinstance(element, m21.note.Note):
            # Determine hand based on pitch range
            # Assuming middle C (C4) is around pitch 60
            if element.pitch.ps < 60:
                left_notes.append(element)
            else:
                right_notes.append(element)

    return left_notes, right_notes


def calculate_transition_matrix(notes):
    # Initialize a dictionary to store counts of each note pair
    transition_counts = defaultdict(lambda: defaultdict(int))

    # Count occurrences of each note pair
    for i in range(len(notes) - 1):
        current_note = notes[i]
        next_note = notes[i + 1]
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


def convert_and_save_new_music(new_music, output_file="generated_music.mid"):
    # Create a Stream object to store the notes
    stream = m21.stream.Stream()

    # Add each note to the Stream
    for note in new_music:
        stream.append(note)

    # Write the Stream to a MIDI file
    stream.write("midi", fp=output_file)
    print(f"Generated music saved to '{output_file}'")


# Folder path where MIDI files are stored
folder_path = "F:\\University\\Sem 2\\Model Thinking\\Beethoven stuff\\MIDI Files\\new"

# Preprocess MIDI files to get left hand and right hand notes
left_hand_notes, right_hand_notes = preprocess_midi_files(folder_path)

# Create transition matrices for left hand and right hand notes
left_hand_transition_matrix = calculate_transition_matrix(left_hand_notes)
right_hand_transition_matrix = calculate_transition_matrix(right_hand_notes)

# Generate new music with both left hand and right hand notes
new_music_with_both_hands_left = generate_new_music(
    left_hand_transition_matrix, num_notes=100)
new_music_with_both_hands_right = generate_new_music(
    right_hand_transition_matrix, num_notes=100)

# Combine left and right hand music
combined_music = new_music_with_both_hands_left + new_music_with_both_hands_right

# Convert and save the combined music
convert_and_save_new_music(combined_music, output_file="combined_music.mid")
