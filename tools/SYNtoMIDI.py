from codingTools import *
import os

#Create working and output directories
WORKING_DIR = os.path.join(os.getcwd(), "WORKING")
OUTPUT_DIR = os.path.join(os.getcwd(), "OUTPUT")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
#Create directories if they don't exist
for directory in [WORKING_DIR, OUTPUT_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

#Select multiple SYN files using dialogs.files()
synFiles = dialogs.files()

def decodeSYN(synFile, offsets, system, output_base_name):
    print(f"Decoding {len(offsets)} tracks from {system} SYN file...")
    midis = []
    
    for index, offset in enumerate(offsets):
        print(f"Processing track {index}...")
        noteIsOn = False #Track when current note is active
        storedNote = 0 #Holds note for later
        storedDuration = 0 #Holds note duration for later
        volume = 0x64 #Default volume
        
        #Create MIDI file
        midi = MidiFileHandler()
        midiFile, track = midi.create_midi_file()
        midi.add_track_name(track, f'{output_base_name} - {system} track {index}')
        midi.add_tempo_change(track, midi.bpm_to_tempo(32))
        if system == "LeapPad":
            midi.set_pitch_bend_range(track, 7)
        if system == "Leapster":
            midi.set_pitch_bend_range(track, 7)
        
        #Position at track start
        synFile.seek(offset)
        decoder = BE_BitReader(synFile)
        totalDurationSinceLastNote = 0
        #Decode track data
        while True:
            
            storedBend = 0
            data = decoder.read(8) #Read 8 bits for the command check
            if data in range(0, 0x7F): #Note
                if noteIsOn == True:
                    noteIsOn = False
                    track.append(midi.create_note_off_message(storedNote, volume, time=storedDuration))
                    bend = 0
                    track.append(midi.create_pitch_bend_message(int(bend), time=0))
                if storedNote !=  0:
                    totalDurationSinceLastNote = 0
                    track.append(midi.create_note_off_message(storedNote, volume, time=0))
                    storedNote = 0
                variableWidthBit = decoder.read(1)
                if variableWidthBit == 0: #Duration is 127 ticks or lower
                    duration = decoder.read(7)
                    if data != 0:
                        track.append(midi.create_note_on_message(data, volume))
                        noteIsOn = True
                        storedNote = data
                        storedDuration = duration
                    else:
                        track.append(midi.create_note_off_message(data, volume, time=duration))
                    
                else: #Duration is 128 ticks or higher
                    duration = decoder.read(15)
                    if data != 0:
                        track.append(midi.create_note_on_message(data, volume))
                        noteIsOn = True
                        storedNote = data
                        storedDuration = duration
                    else:
                        track.append(midi.create_note_off_message(data, volume, time=duration))
                totalDurationSinceLastNote+=duration
                        
            elif data == 0x81:
                ""#print("PitchShift Required.")
                
            elif data == 0x82:
                ""#print("PitchShift not Required.")
                
            elif data == 0x83:
                ""#print("Reserve voice")
                
            elif data == 0x84:
                ""#print("Release voice")
                
            elif data == 0x88:
                volume = decoder.read(8)
                
            elif data == 0x89: #Program change
                data = decoder.read(8)
                if data == 0xC0:
                    instrument = decoder.read(8)
                    track.append(midi.create_program_change_message(instrument))
                else:
                    track.append(midi.create_program_change_message(data))
                    
            elif data == 0x8A: #Pitch bend
                if noteIsOn == True:
                    noteIsOn = False
                    track.append(midi.create_note_off_message(0, volume, time=storedDuration))
                    storedDuration = 0
                    bend = 0
                    track.append(midi.create_pitch_bend_message(int(bend), time=0))
                if system == "LeapPad":
                    bendData = (decoder.read(8)*64) #This literally maps to the source MIDIs near-perfectly in the output but is still bad...
                    if bendData != 0x3fc0:
                        bend = bendData-8192
                    else:
                        bend = 0
                    variableWidthBit = decoder.read(1)
                    if variableWidthBit == 0:
                        duration = decoder.read(7)
                        track.append(midi.create_pitch_bend_message(int(bend), time=0))
                        track.append(midi.create_note_off_message(0, volume, time=duration))
                    else:
                        duration = decoder.read(15)
                        track.append(midi.create_pitch_bend_message(int(bend), time=0))
                        track.append(midi.create_note_off_message(0, volume, time=duration))
                if system == "Leapster":
                    bendData = (decoder.read(8)*64)
                    if bendData != 0x3fc0:
                        bend = bendData-8192
                    else:
                        bend = 0
                    variableWidthBit = decoder.read(1)
                    if variableWidthBit == 0:
                        duration = decoder.read(7)
                        track.append(midi.create_pitch_bend_message(int(bend), time=0))
                        track.append(midi.create_note_off_message(0, volume, time=duration))
                    else:
                        duration = decoder.read(15)
                        track.append(midi.create_pitch_bend_message(int(bend), time=0))
                        track.append(midi.create_note_off_message(0, volume, time=duration))
                    totalDurationSinceLastNote+=duration
                    
            elif data == 0x8E: #Set loop count and loop start position
                if noteIsOn == True:
                    noteIsOn = False
                    track.append(midi.create_note_off_message(storedNote, volume, time=storedDuration))
                    bend = 0
                    track.append(midi.create_pitch_bend_message(int(bend), time=0))
                    
                loops = decoder.read(8)
                track.append(midi.create_control_change_message(110, loops))
                
            elif data == 0x8F: #Set loop end position
                if noteIsOn == True:
                    noteIsOn = False
                    track.append(midi.create_note_off_message(storedNote, volume, time=storedDuration))
                    bend = 0
                    track.append(midi.create_pitch_bend_message(int(bend), time=0))
                    
                padding = decoder.read(8)
                track.append(midi.create_control_change_message(111, 0))
                
            elif data == 0xFF: #End of track data marker (0xFF00)
                if noteIsOn == True:
                    noteIsOn = False
                    track.append(midi.create_note_off_message(storedNote, volume, time=storedDuration))
                break
        
        #Save individual track to the WORKING directory
        track.append(midi.create_note_off_message(0, volume, time=128))
        trackFilename = f'track_{index:02d}.mid'
        trackPath = os.path.join(WORKING_DIR, trackFilename)
        midi.save_midi_file(midiFile, trackPath)
        midis.append(trackPath)

    #Combine all tracks into one MIDI file in the OUTPUT directory
    combined_filename = f'{output_base_name}.mid'
    combined_path = os.path.join(OUTPUT_DIR, combined_filename)
    midi.combine_midi_files(midis, combined_path)
    print(f"Combined all tracks into {combined_path}")
    
    return midis, combined_path

if not synFiles:
    print("No files selected. Exiting.")
else:
    #Process each selected SYN file
    for synPath in synFiles:
        try:
            #Get base filename without extension for naming output files
            input_filename = os.path.basename(synPath).split('.')[0]
            print(f"\nProcessing SYN file: {synPath}")
            
            with open(synPath, "rb") as f:
                trackOffsets = []
                headCheck = f.read(2)
                
                if headCheck != b'\x02\x00': #LeapPad SYN
                    f.seek(0)
                    trackOffsets = BE_multiunpack.ushort(f.read(12))
                    system = "LeapPad"
                else: #Leapster SYN
                    trackCount = LE_unpack.ushort(f.read(2))
                    for track in range(trackCount):
                        offset = LE_unpack.ushort(f.read(2))
                        ID = BE_unpack.ushort(f.read(2))
                        trackOffsets.append(offset)
                    system = "Leapster"
                
                #Filter out any zero offsets
                trackOffsets = [offset for offset in trackOffsets if offset > 0]
                
                print(f"Detected {system} SYN file with {len(trackOffsets)} tracks")
                
                #Decode the SYN file using the input filename as the base for output files
                trackPaths, combined_path = decodeSYN(f, trackOffsets, system, input_filename)
                
                print(f"Conversion complete for {input_filename}!")
        except:
            ""
    
    print("\nAll files processed successfully!")
