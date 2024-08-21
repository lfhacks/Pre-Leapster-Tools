import struct
import tkinter as tk
from tkinter import filedialog
import mido
import os

root = tk.Tk()
root.withdraw()
files = filedialog.askopenfilenames()
root.destroy()
currentTrack = 0

#Function to add MIDI messages to the track
def add_midi_message(message_type, channel, data1, data2, delta_time):
    if message_type == 'program_change':
        track.append(mido.Message('program_change', program=data1, channel=channel, time=delta_time))
    elif message_type == 'control_change':
        track.append(mido.Message('control_change', channel=channel, control=data1, value=data2, time=0))
    elif message_type == 'note_on':
        track.append(mido.Message('note_on', note=data1, velocity=data2, channel=channel, time=delta_time))
    elif message_type == 'note_off':
        track.append(mido.Message('note_off', note=data1, velocity=0, channel=channel, time=delta_time))
    elif message_type == 'pitch_wheel':
        track.append(mido.Message('pitchwheel', channel=channel, pitch=data1, time=delta_time))
    
        
for file_path in files:
    mid = mido.MidiFile(type=1)
    with open(file_path, "rb") as syn:
        track_count = 6
        print(track_count)
        currentSynTrack = 0
        
        for synTrack in range(track_count):
            lastDuration = -1 #Store the last note duration here
            lastNote = -1     #Store the last note here
            tracks = 0            
            trackoffset = struct.unpack(">H",syn.read(2))[0]
            if trackoffset != 0:
                print(hex(trackoffset))
                lastTrack = syn.tell()
                track = mido.MidiTrack()
                mid.tracks.append(track)
                track.append(mido.MetaMessage('set_tempo', tempo=1900000))
                syn.seek(trackoffset)
                currentSynTrack += 1
                current_bend = 8192
                hasLoop = False
                hasLoopEnd = False
                if currentSynTrack == 9: #The bothersome "percussion" channel must be stopped. It has ruined countless lives and - oh, wait. I can just skip it.
                    currentSynTrack += 1
                while True:
                    data = syn.read(1)
                    if len(data) == 0:
                        break
                    if data[0] == 0x81: #PitchShift required.
                        add_midi_message('control_change', currentSynTrack, 108, 0, 0)
                    if data[0] == 0x82: #PitchShift not required.
                        add_midi_message('control_change', currentSynTrack, 106, 0, 0)
                    if data[0] == 0x83: #Reserve voice
                        add_midi_message('control_change', currentSynTrack, 107, 0, 0)
                    if data[0] == 0x84: #Release voice
                        add_midi_message('control_change', currentSynTrack, 109, 0, 0)
                
                    
                    if data[0] == 0x88: #Set volume
                        volume = syn.read(1)[0]
                    
                    if data[0] == 0x89: #Program change
                        instrument = syn.read(1)[0]
                        if instrument < 0x80:
                            add_midi_message('program_change', currentSynTrack, instrument, None, 0)
                        else: #This SYN gets instruments from the cartridge instead (prefix 0xC0)
                            instrument = syn.read(1)[0]
                            add_midi_message('program_change', currentSynTrack, instrument, None, 0)

                    if data[0] == 0x8A: #Pitch bend
                        bend = struct.unpack("<B", syn.read(1))[0]
                        duration = syn.read(1)[0]
                        if duration == 0x80:
                            duration -= 0x80
                            duration_2 = syn.read(1)[0]
                            duration += duration_2
                        elif duration >= 0x81 and duration < 0xFF:
                            duration -= 0x80
                            if duration <= 0xF:
                                main = str(hex(duration))[2:3]
                            else:
                                main = str(hex(duration))[2:4]
                            duration_2 = str(hex(syn.read(1)[0]))[2:4]
                            
                            if len(duration_2) == 2:
                                duration = int(str("0x"+main+duration_2), 16)
                            else:
                                duration = int(str("0x"+main+"0"+duration_2), 16)
                        current_bend = -4096 + int(bend*32)
                        #print(current_bend)
                        #input()
                        if current_bend > 8192 or current_bend < -8192:
                            print(current_bend)
                            current_bend =0
                        add_midi_message('pitch_wheel', currentSynTrack, current_bend, 127, duration)


                    if data[0] == 0x8E: #Start of loop
                        loopCount = syn.read(1)[0]
                        hasLoop = True #Loop points are now added after the previous note ends to ensure that they're timed right
                        
                    if data[0] == 0x8F: #End of loop
                        zero = syn.read(1)[0]
                        hasLoopEnd = True #Loop points are now added after the previous note ends to ensure that they're timed right
                        
                    if data[0] in range(0x00, 0x7F):
                        note = data[0]
                        duration = syn.read(1)[0]
                        current_bend = 0 #Reset the pitch bend for every note (mainly because figuring out how they work is still a work in progress)
                        if duration >= 0x80 and duration < 0xFF:
                            duration -= 0x80
                            if duration <= 0xF:
                                main = str(hex(duration))[2:3]
                            else:
                                main = str(hex(duration))[2:4]
                            duration_2 = str(hex(syn.read(1)[0]))[2:4]
                            
                            if len(duration_2) == 2:
                                duration = int(str("0x"+main+duration_2), 16)
                            else:
                                duration = int(str("0x"+main+"0"+duration_2), 16)
                        if lastDuration != -1:
                            add_midi_message('note_off', currentSynTrack, lastNote, volume, lastDuration) #Now end the note
                            if hasLoop == True:
                                add_midi_message('control_change', currentSynTrack, 110, loopCount, 0)
                                hasLoop = False
                        if note >= 1:
                            add_midi_message('note_on', currentSynTrack, note, volume, 0) #Start the note
                        
                        
                        lastDuration = duration
                        lastNote = note

                    if data[0] == 0xFF: #End of sequence
                        add_midi_message('note_off', currentSynTrack, lastNote, 127, lastDuration)
                        if hasLoopEnd == True:
                            add_midi_message('control_change', currentSynTrack, 111, zero, 0)
                            hasLoopEnd = False
                        break
            
##                    except:
##                        if syn.tell() == os.path.getsize(file_path):
##                            print("Oops!")
##                            break
                syn.seek(lastTrack)
        add_midi_message('note_off', currentSynTrack, 0, 127, 100) #Add a delay to ensure that shorter, non-looping stuff doesn't get cut off early
        base, ext = os.path.splitext(file_path)
        output_path = f"{base}_converted.mid"
        mid.save(output_path)
        print(f"Conversion complete! MIDI file saved as {output_path}")
