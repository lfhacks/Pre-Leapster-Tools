import struct
import tkinter as tk  # Used to kill the extra tkinter window
import os
import time
import hashlib
from tkinter import filedialog

#Create a root window
root = tk.Tk()
#Hide the root window
root.withdraw()
files = filedialog.askopenfilenames()
root.destroy()  # Destroy the root window

syn_dir = os.path.join(os.getcwd(), "SYN")
if not os.path.exists(syn_dir):
    os.makedirs(syn_dir)

processed_hashes = {}

def getSYN(file, offset):
    trackEndCheck = b'\xFF'
    SYN = b''
    tracks = 0
    hits = 0
    with open(file, "rb") as rom:
        rom.seek(offset)
        for i in range(6):
            data = rom.read(2)
            SYN += data
            if data != b'\x00\x00':
                tracks += 1
        while hits != tracks:
            readForCheck = rom.read(1)
            SYN += readForCheck
            if readForCheck == trackEndCheck:
                check2 = rom.read(1)
                if check2 == b'\x00':
                    SYN = SYN + check2 #Be sure to add the extra 0 so this SYN file is complete
                    hits += 1
                else: #False alarm! Keep going
                    SYN = SYN + check2
            if rom.tell() >= os.path.getsize(file):
                break
    try:
        if SYN[0] == 0 and SYN[1] == 0xC:
            return SYN
        else: #Good offset, but the data is wrong
            print("I PARSED NON-SYN DATA!!!!!")
            return "I PARSED NON-SYN DATA!!!!!"
    except: #Bad offset, no data
        print("I PARSED NON-SYN DATA!!!!!")
        return "I PARSED NON-SYN DATA!!!!!"


def hash_data(data):
    return hashlib.md5(data).hexdigest()


def save_unique_syn(syn_data, rom_name, offset, pointer):
    if syn_data == "I PARSED NON-SYN DATA!!!!!":
        return False
    data_hash = hash_data(syn_data)
    if data_hash in processed_hashes:
        print(f"Duplicate SYN found: {data_hash} (already exists as {processed_hashes[data_hash]})")
        return False
    filename = f"SYN_{rom_name}_{data_hash[0:8]}.bin" #Each SYN is given a hash so duplicates don't get extracted
    filepath = os.path.join(syn_dir, filename)
    with open(filepath, "w+b") as syn:
        syn.write(syn_data)
    processed_hashes[data_hash] = filename
    print(f"Saved: {filename}")
    return True


def parseSYNTable(file, offset, rom_name):
    with open(file, "rb") as rom:
        rom.seek(offset - 2)
        count = struct.unpack(">H", rom.read(2))[0]
        if count > 1000: #Required for earlier LeapPad stuff because there was no SYN count variable
            count = 800
        
        print(f"Processing SYN table at {hex(offset)} with {count} entries")
        valid_entries = 0
        
        for pointer in range(count):
            address = struct.unpack(">I", rom.read(4))[0] + offset
            print(f"Processing entry {pointer} at {hex(rom.tell() - 4)}, points to {hex(address)}")
            
            SYN = getSYN(file, address)
            if SYN != "I PARSED NON-SYN DATA!!!!!":
                if save_unique_syn(SYN, rom_name, offset, pointer):
                    valid_entries += 1
            else:
                print(f"Invalid SYN data at entry {pointer}")
                break #End the table parsing nonsense
        
        print(f"Found {valid_entries} valid SYN entries in table at {hex(offset)}")


def parseRIBTable(file):
    rom_name = os.path.basename(file).split(".")[0]
    print(f"Processing ROM: {rom_name}")
    
    with open(file, "rb") as rom:
        rom.seek(0x10100) #The RIB table always starts here in a good dump
        ROMVer = struct.unpack(">H", rom.read(2))[0]
        
        RibID = rom.read(1)[0]
        Reserved1 = rom.read(1)
        CompatibleCopyright = struct.unpack(">H", rom.read(2))[0]
        CompatibleSecurity = struct.unpack(">H", rom.read(2))[0]
        
        rom.seek(0x18, 1) #Skip what we don't need here
        
        SynBaseLib = struct.unpack(">I", rom.read(4))[0] #This is the start of the SYN Index Table (BaseROM)
        SynCartApp = struct.unpack(">I", rom.read(4))[0] #This is the start of the SYN Index Table (Cartridge)
        
        rom.seek(0x24, 1) #Skip what we don't need here
        
        RomStart = struct.unpack(">I", rom.read(4))[0] #Use as the base address for the ROM
        RomEnd = struct.unpack(">I", rom.read(4))[0]
        
        print(f"ROM Version: {hex(ROMVer)}")
        print(f"ROM Start: {hex(RomStart)}")
        print(f"SynBaseLib: {hex(SynBaseLib)}")
        print(f"SynCartApp: {hex(SynCartApp)}")
        
        #BaseROMs
        if RomStart == 0:
            if SynBaseLib != 0:
                print("Processing BaseROM SYN table")
                parseSYNTable(file, SynBaseLib, rom_name)
        
        #Cartridge ROMs
        if RomStart >= 0x1400000:
            if SynCartApp != 0:
                print("Processing Cartridge ROM SYN table")
                parseSYNTable(file, SynCartApp - 0x1400000, rom_name)

print(f"SYN files will be saved to: {syn_dir}")
for file in files:
    try:
        parseRIBTable(file)
    except: #Complain about bad ROM to the user
        print("Bad ROM detected! Not going to extract SYN files, as the table is inaccessible.")

print(f"\nExtraction complete! Saved {len(processed_hashes)} unique SYN files.")
