#A script that aims to accurately parse the LeapFrog AppTable ("RIB") header format (1999 LeapPad version)
import struct
import tkinter as tk #Used to kill the extra tkinter window
import os
import time
from tkinter import filedialog
root = tk.Tk()#Create a root window
root.withdraw()#Hide the root window
files = filedialog.askopenfilenames()
root.destroy()#Destroy the root window

def createTXTH(path):
    with open(path+".bin.TXTH", "w+") as txthGen:
        txthGen.write(txth)

def getGAS(file, offset): #Incomplete!
    with open(file, "rb") as rom:
        rom.seek(offset)
        GAS = rom.read(1)
    return GAS

def getLPC(file, offset): #Incomplete! Works the same as the Leapster.
    lpcEndCheck = b'\xC0'
    continueScanning = True
    with open(file, "rb") as rom:
        rom.seek(offset)
        outData = b''
        while continueScanning == True:
            data = rom.read(1)
            outData = outData+data
            if data == lpcEndCheck:
                data2 = rom.read(1)
                outData = outData+data2
                if data2 == b'\x0F':
                    continueScanning == False
                    break
                else:
                    "" #Keep going
    return outData

def getRAW(file, offset, length):
    with open(file, "rb") as rom:
        rom.seek(offset)
        RAW = rom.read(length)
    return RAW

def getSYN(file, offset):
    print(hex(offset))
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
                tracks+=1
        while hits != tracks:
            readForCheck = rom.read(1)
            SYN += readForCheck
            if readForCheck == trackEndCheck:
                SYN = SYN+rom.read(1) #Be sure to add the extra 0 so this SYN file is complete
                hits+=1
            if rom.tell() >= os.path.getsize(file):
                break
    try:
        if SYN [0] == 0 and SYN[1] == 0xC:
            return SYN
        else: #Good offset, but the data is wrong
            return "I PARSED NON-SYN DATA!!!!!"
    except: #Bad offset, no data
        return "I PARSED NON-SYN DATA!!!!!"

def parseGASTable(file, offset):
    with open(file, "rb") as rom:
        rom.seek(offset-2)
        count = struct.unpack(">H", rom.read(2))[0]
        createTXTH(paths[4])
        if count > 2000:
            print("Earlier LeapPad cartridges aren't entirely supported yet (GAS)")
            count = 0
        for pointer in range(count):
            address = struct.unpack(">I", rom.read(4))[0]+offset
            GAS = getGAS(file, address)
            with open(f"{paths[1]}GAS_{hex(offset)}_{pointer}.bin", "w+b") as gas:
                gas.write(GAS)

def parseLPCTable(file, offset):
    with open(file, "rb") as rom:
        rom.seek(offset-2)
        count = struct.unpack(">H", rom.read(2))[0]
        if count > 2000:
            print("Earlier LeapPad cartridges aren't entirely supported yet (LPC)")
            count = 0
        for pointer in range(count):
            address = struct.unpack(">I", rom.read(4))[0]+offset
            LPC = getLPC(file, address)
            with open(f"{paths[3]}LPC_{hex(offset)}_{pointer}.bin", "w+b") as lpc:
                lpc.write(LPC)

def parseRAWTable(file, offset):
    with open(file, "rb") as rom:
        rom.seek(offset-2)
        count = struct.unpack(">H", rom.read(2))[0]
        createTXTH(paths[4])
        if count > 2000:
            print("Earlier LeapPad cartridges aren't entirely supported yet (RAW)")
            count = 0
        for pointer in range(count):
            startaddress = struct.unpack(">I", rom.read(4))[0]+offset
            endaddress = struct.unpack(">I", rom.read(4))[0]+offset
            length = endaddress-startaddress
            RAW = getRAW(file, startaddress, length)
            with open(f"{paths[4]}RAW_{hex(offset)}_{pointer}.bin", "w+b") as raw:
                raw.write(RAW)
                

def parseSYNTable(file, offset):
    with open(file, "rb") as rom:
        rom.seek(offset-2)
        count = struct.unpack(">H", rom.read(2))[0]
        if count > 1000: #Required for earlier LeapPad stuff because there was no SYN count variable
            count = 800
        for pointer in range(count):
            address = struct.unpack(">I", rom.read(4))[0]+offset
            print(hex(rom.tell()))
            
            SYN = getSYN(file, address)
            if SYN != "I PARSED NON-SYN DATA!!!!!":
                with open(f"{paths[5]}SYN_{hex(offset)}_{pointer}.bin", "w+b") as syn:
                    syn.write(SYN)
            elif SYN == "I PARSED NON-SYN DATA!!!!!":
                break #End the table parsing nonsense

def parseRIBTable(file):
    with open(file, "rb") as rom:
        rom.seek(0x10100) #The RIB table always starts here in a good dump
        ROMVer = struct.unpack(">H", rom.read(2))[0]
        
        RibID = rom.read(1)[0]
        Reserved1 = rom.read(1)
        CompatibleCopyright = struct.unpack(">H", rom.read(2))[0]
        CompatibleSecurity = struct.unpack(">H", rom.read(2))[0]
        
        GasBaseLib = struct.unpack(">I", rom.read(4))[0]        #This is the start of the GAS Index Table (BaseROM)
        GasCartApp = struct.unpack(">I", rom.read(4))[0]        #This is the start of the GAS Index Table (Cartridge)
        
        LpcBaseLib = struct.unpack(">I", rom.read(4))[0]        #This is the start of the LPC Index Table (BaseROM)
        LpcCartApp = struct.unpack(">I", rom.read(4))[0]        #This is the start of the LPC Index Table (Cartridge)
        
        RawBaseLib = struct.unpack(">I", rom.read(4))[0]        #This is the start of the RAW Index Table (BaseROM)
        RawCartApp = struct.unpack(">I", rom.read(4))[0]        #This is the start of the RAW Index Table (Cartridge)
        
        SynBaseLib = struct.unpack(">I", rom.read(4))[0]        #This is the start of the SYN Index Table (BaseROM)
        SynCartApp = struct.unpack(">I", rom.read(4))[0]        #This is the start of the SYN Index Table (Cartridge)
        
        InstrumentBaseLib = struct.unpack(">I", rom.read(4))[0] #This is the start of the Instrument Index Table (BaseROM)
        InstrumentCartApp = struct.unpack(">I", rom.read(4))[0] #This is the start of the Instrument Index Table (Cartridge)
        
        ShapeBaseLib = struct.unpack(">I", rom.read(4))[0]      #This is the start of the Shape Index Table (BaseROM)
        ShapeCartApp = struct.unpack(">I", rom.read(4))[0]      #This is the start of the Shape Index Table (Cartridge)

        CodeBook = struct.unpack(">I", rom.read(4))[0]
        ModelData = struct.unpack(">I", rom.read(4))[0]
        CalData = struct.unpack(">I", rom.read(4))[0]
        PowerDown = struct.unpack(">H", rom.read(2))[0]
        LowBattery = struct.unpack(">H", rom.read(2))[0]
        Kernel = struct.unpack(">I", rom.read(4))[0]
        
        RomStart = struct.unpack(">I", rom.read(4))[0] #Use as the base address for the ROM
        RomEnd = struct.unpack(">I", rom.read(4))[0]
        LoadEnd = struct.unpack(">I", rom.read(4))[0]
        
        Storage = struct.unpack(">I", rom.read(4))[0]
        
        BootApp = struct.unpack(">I", rom.read(4))[0]
        InetApp = struct.unpack(">I", rom.read(4))[0]
        
        FontBaseLib = struct.unpack(">I", rom.read(4))[0] #Turbo Twists and iQuest likely used this because they have screens
        FontCartApp = struct.unpack(">I", rom.read(4))[0] #Turbo Twists and iQuest likely used this because they have screens
        GcsBaseLib = struct.unpack(">I", rom.read(4))[0]
        GcsBaseApp = struct.unpack(">I", rom.read(4))[0]
        
        ProductId = struct.unpack(">H", rom.read(2))[0]
        
        Reserved2 = struct.unpack(">H", rom.read(2))[0]
        
        RomId = struct.unpack(">I", rom.read(4))[0]
        
        FlashAccessTable = struct.unpack(">H", rom.read(2))[0]
        ExtendedRomInfo = struct.unpack(">H", rom.read(2))[0]
        ControlParms = struct.unpack(">H", rom.read(2))[0]
        ExtendedRibInfo = struct.unpack(">H", rom.read(2))[0]
        GasBaseApp = struct.unpack(">I", rom.read(4))[0]
        GasApp3 = struct.unpack(">I", rom.read(4))[0]
        LpcBaseApp = struct.unpack(">I", rom.read(4))[0]
        LpcApp3 = struct.unpack(">I", rom.read(4))[0]
        RawBaseApp = struct.unpack(">I", rom.read(4))[0]
        RawApp3 = struct.unpack(">I", rom.read(4))[0]
        SynBaseApp = struct.unpack(">I", rom.read(4))[0]
        SynApp3 = struct.unpack(">I", rom.read(4))[0]
        InstrBaseApp = struct.unpack(">I", rom.read(4))[0]
        InstrApp3 = struct.unpack(">I", rom.read(4))[0]
        FontBaseApp = struct.unpack(">I", rom.read(4))[0]
        FontApp3 = struct.unpack(">I", rom.read(4))[0]
        GcsBaseApp = struct.unpack(">I", rom.read(4))[0]
        GcsApp3 = struct.unpack(">I", rom.read(4))[0]

        offsetsRom = [GasCartApp, LpcCartApp, RawCartApp, SynCartApp, InstrumentCartApp, ShapeCartApp, RomStart, RomEnd]
        offsetsBase = [GasBaseLib, LpcBaseLib, RawBaseLib, SynBaseLib, InstrumentBaseLib, ShapeBaseLib, RomStart, RomEnd]
        
        stringRom = f"ROM memory range: {hex(offsetsRom[6])}-{hex(offsetsRom[7])}\nGAS: {hex(offsetsRom[0])}\nLPC: {hex(offsetsRom[1])}\nRAW: {hex(offsetsRom[2])}\nSYN: {hex(offsetsRom[3])}\nInstrument: {hex(offsetsRom[4])}\nShape: {hex(offsetsRom[5])}\n"
        stringBase = f"ROM memory range: {hex(offsetsBase[6])}-{hex(offsetsBase[7])}\nGAS: {hex(offsetsBase[0])}\nLPC: {hex(offsetsBase[1])}\nRAW: {hex(offsetsBase[2])}\nSYN: {hex(offsetsBase[3])}\nInstrument: {hex(offsetsBase[4])}\nShape: {hex(offsetsBase[5])}\n"

        #BaseROMs
        if RomStart == 0:
            RomSizeMegabytes = round(RomEnd/1048576)
            print(f"ROM size (megabytes): {RomSizeMegabytes}")
            print(stringBase)
            #GAS data (unable to be converted currently)
            if GasBaseLib != 0:
                parseGASTable(file, GasBaseLib)
            if GasBaseApp != 0xFFFFFFFF and GasBaseApp != 0:
                parseGASTable(file, GasBaseApp)
                
            #Voices, some sound effects (unable to be converted currently!)
            if LpcBaseLib != 0:
                parseLPCTable(file, LpcBaseLib)
            if LpcBaseApp != 0xFFFFFFFF and LpcBaseApp != 0:
                parseLPCTable(file, LpcBaseApp)

            #Sound effects
            if RawBaseLib != 0:
                parseRAWTable(file, RawBaseLib)
            if RawBaseApp != 0xFFFFFFFF and RawBaseApp != 0:
                parseRAWTable(file, RawBaseApp)

            #Music
            if SynBaseLib != 0:
                parseSYNTable(file, SynBaseLib)
            if SynBaseApp != 0xFFFFFFFF and SynBaseApp != 0:
                parseSYNTable(file, SynBaseApp)

        #Cartridge ROMs
        if RomStart == 0x1400000:
            RomSizeMegabytes = round((RomEnd-RomStart)/1048576)
            print(f"ROM size (megabytes): {RomSizeMegabytes}")
            #Voices, some sound effects
            if LpcCartApp != 0:
                parseLPCTable(file, LpcCartApp-0x1400000)
            if LpcApp3 != 0 and LpcApp3 < RomStart-0x1400000:
                parseLPCTable(file, LpcApp3-0x1400000)

            #Music
            if SynCartApp != 0:
                parseSYNTable(file, SynCartApp-0x1400000)
            if SynApp3 != 0 and SynApp3 < RomStart-0x1400000:
                parseSYNTable(file, SynApp3-0x1400000)

for file in files:
    ROMName = os.path.basename(file).split(".")[0]
    print(ROMName)
    romVersions = [0x015E, #LeapPad cartridge
                   0x0193, #Turbo Twist Spelling and Fact Blaster BaseROMs
                   0x7F35, #LeapPad BaseROM (Canada)
                   0x7F49, #Little Touch LeapPad BaseROM
                   0x7F4F, #LeapPad BaseROM (US, might be a revision), some cartridges (such as Cars) also use this one
                   0x7F51, #iQuest Handheld BaseROM
                   0x7F57, #Turbo Extreme cartridge
                   0x7F5A, #My Own Learning Leap cartridge
                   0x7F5B, #My First LeapPad BaseROM (international)
                   0x7F5C, #My First LeapPad, Vocabulator and Turbo Extreme BaseROMs
                   0x7F64, #Imagination Desk cartridge
                   0x7F6A, #LeapPad cartridge
                   0x7F6E, #LeapPad cartridge
                   0x7F74, #LeapPad cartridge
                   0x7F75, #LeapPad cartridge
                   0x7F8C, #Quantum Leap cartridge, LeapPad
                   ]
    paths = [os.getcwd()+f"/Split_ROMs/{ROMName}/",                  #Index = 0, root folder (title info goes here)
             os.getcwd()+f"/Split_ROMs/{ROMName}/Audio/GAS/",        #Index = 1, GAS folder
             os.getcwd()+f"/Split_ROMs/{ROMName}/Audio/Instruments/",#Index = 2, Instrument folder
             os.getcwd()+f"/Split_ROMs/{ROMName}/Audio/LPC/",        #Index = 3, LPC/LFC folder
             os.getcwd()+f"/Split_ROMs/{ROMName}/Audio/RAW/",        #Index = 4, RAW folder
             os.getcwd()+f"/Split_ROMs/{ROMName}/Audio/SYN/",        #Index = 5, SYN folder
             ]
    txth = "codec = ALAW\nsample_rate = 8000\nchannels = 1\nstart_offset = 0\nnum_samples = data_size" #For creating the TXTH used for the instruments and sound effects
    for path in paths:
        if os.path.exists(path) == False:
            os.makedirs(path)
    parseRIBTable(file)

#General notes:
#The LeapPad systems are big endian. This should partially work on all of them, including toys if those ever get dumped (but the RIB table layout will likely change based on what device the ROMs are from).
#Supported system list:
"""
LeapPad
My First LeapPad
Little Touch LeapPad
LeapPad Plus Writing
LeapPad Plus Microphone
CoCoPad (Japan exclusive, not dumped yet)
Quantum LeapPad
Imagination Desk
My Own Learning Leap
iQuest Handheld
Turbo Twist Spelling
Turbo Twist Math
Turbo Extreme"""
#If a system errors out or returns garbage data, it's either unsupported or the dump is bad. A few of the iQuest and LeapPad dumps are known to be bad.
