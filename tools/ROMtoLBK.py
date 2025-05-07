import os
import tkinter as tk
from tkinter import filedialog

outputDirectory = os.getcwd()+"/LBKs/"
if not os.path.exists(outputDirectory):
    os.makedirs(outputDirectory)

def promptUserToSelectFiles():
    root = tk.Tk()
    root.withdraw()
    files = filedialog.askopenfilenames()
    root.destroy()
    return files

def generateHeader(fileSize):
    header = "LBK"
    padding = 0x00000
    baseOffset = 0x01400000 #ROM base offset (always 0x01400000 for cartridge ROMs)
    romSize = fileSize #Size of ROM to be written
    lbkHeader = f"{header}{padding:05X}{baseOffset:08X}{romSize-1:07X}".encode("utf-8")
    return lbkHeader

lbkFooter = b'LBK00000FFFFFFFF00000000'

padSizes = [1 * 1024 * 1024, 2 * 1024 * 1024, 4 * 1024 * 1024, 8 * 1024 * 1024, 16 * 1024 * 1024]

def ROMtoLBK(filename):
    padAmount = 0
    fileSize = os.path.getsize(filename)
    lbkHeader = generateHeader(fileSize)

    if fileSize not in padSizes:
        targetSize = next((size for size in padSizes if fileSize < size), None)
        padAmount = targetSize - fileSize
    with open(filename, 'rb') as ROM:
        ROMData = ROM.read() #We don't want to modify the original file
    
    ROMData += b'\xFF' * padAmount
    ROMData = lbkHeader+ROMData+lbkFooter
    
    with open(outputDirectory+os.path.splitext(os.path.basename(filename))[0]+".lbk", "w+b") as LBK:
        LBK.write(ROMData)

ROMs = promptUserToSelectFiles()

for ROM in ROMs:
    ROMtoLBK(ROM)
