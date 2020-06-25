from midiutil import MIDIFile
import pygame
import json

# One track, defaults to format 1 (tempo track automatically created)
MyMIDI = MIDIFile(1, deinterleave=True)
DEGREES = [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71]
CONFIDENCE_THRESHOLD = .500
PITCH_THRESHOLD = .800
SECTION_CONFIDENCE_THRESHOLD = .500
MAX_MIDI_VOLUME = 127
TEMPO = 0

# init method or constructor
def __init__(self, name):
    self.name = name
    self.tempo = 0


def convert_seconds_to_quarter(time_in_sec, bpm):
    quarter_per_second = (60/bpm)
    time_in_quarter = time_in_sec * quarter_per_second
    return time_in_quarter


def calculate_measure_length(tempo, time_signature):
    beat_length = 60/tempo
    measure_length = beat_length * time_signature
    return beat_length, measure_length


def read_analysis_json(filename):
    # Opening JSON file
    with open(filename, 'r') as openfile:
        # Reading from json file
        analysis = json.load(openfile)

    # print(json.dumps(analysis, indent=4))
    return analysis


def create_sections(sections):
    track = 0

    for section in sections:
        if section['confidence'] > SECTION_CONFIDENCE_THRESHOLD:
            start = section['start']
            tempo = int(round(section['tempo']))

            # Add Tempo to track
            MyMIDI.addTempo(track, start, tempo)

    return None


def convert_segments(tempo, section_dict, segments):
    for segment in segments:
        confidence = segment['confidence']

        if confidence >= CONFIDENCE_THRESHOLD:
            pitches = segment['pitches']

            for i in range(len(pitches)):
                # Add note to MidiFile if pitch value is above defined threshold value
                pitch = pitches[i]

                if pitch >= PITCH_THRESHOLD:
                    duration = segment['duration']
                    start = segment['start']

                    # Calculate volume by setting pitch vector value * the max volume
                    volume = int(round(pitch * MAX_MIDI_VOLUME))

                    # Add note to MIDI FILE
                    MyMIDI.addNote(0, 0, pitch=DEGREES[i], time=start, duration=duration, volume=volume)


def create_midi_file(json_file):
    # Read JSON analysis file
    analysis = read_analysis_json("./TestSongAnalysis/"+json_file)

    track = analysis['track']
    # Get Time Signature of track
    time_signature = track['time_signature']

    # Get Tempo of track
    track_tempo = int(round(track['tempo']))

    calculate_measure_length(tempo=track_tempo, time_signature=time_signature)
    # Create Section dictionary,
    # To outline Tempo & Time Signature for specific time intervals
    sections = analysis['sections']
    section_dict = create_sections(sections)

    # Get Sections
    segments = analysis['segments']
    convert_segments(tempo=track_tempo, section_dict=section_dict, segments=segments)

    filename = "./MidiFiles/" + "{}.mid".format(json_file[:-5])
    with open(filename, "wb") as output_file:
        MyMIDI.writeFile(output_file)


def play_midi_file(midi_file):
    clock = pygame.time.Clock()
    try:
        pygame.mixer.music.load(midi_file)
        print
        "Music file %s loaded!" % midi_file
    except pygame.error:
        print
        "File %s not found! (%s)" % (midi_file, pygame.get_error())
        return
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        # check if playback has finished
        clock.tick(30)


if __name__ == '__main__':
    # pick a midi music file you have ...
    # (if not in working folder use full path)
    create_midi_file('2VjXGuPVVxyhMgER3Uz2Fe.json')
    midi_file = './MidiFiles/2VjXGuPVVxyhMgER3Uz2Fe.mid'

    freq = 44100    # audio CD quality
    bitsize = -16   # unsigned 16 bit
    channels = 2    # 1 is mono, 2 is stereo
    buffer = 1024    # number of samples
    pygame.mixer.init(freq, bitsize, channels, buffer)

    # optional volume 0 to 1.0
    pygame.mixer.music.set_volume(0.8)
    try:
        play_midi_file(midi_file)
    except KeyboardInterrupt:
        # if user hits Ctrl/C then exit
        # (works only in console mode)
        pygame.mixer.music.fadeout(1000)
        pygame.mixer.music.stop()
        raise SystemExit