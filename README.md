Feel free to reimplement, borrow or use this documentation for your own research and tools.

# To-do
- Figure out how to properly split earlier ROMs (there's no asset count variable at the start of tables in ROMs from before a certain point in 2003)
- Document the shape format used by the LeapPad (it uses these for the touch functionality) and make an automated graphics ripper for the iQuest/Turbo Twists
- Figure out where code execution starts and write a disassembler for the Ax51 that the LeapPad (and all similar LeapFrog hardware) used (it isn't a regular 8051 processor! It has some extra instructions and some 16 and 32-Bit functionality.)

More documentaion on the Ax51 can be found here:

https://developer.arm.com/documentation/101655/0961/Ax51-User-s-Guide/Ax51-Introduction

# ROM version list
- 0x0193 - Turbo Twist Spelling and Fact Blaster BaseROMs
- 0x7F35 - LeapPad BaseROM (Canada)
- 0x7F49 - Little Touch LeapPad BaseROM
- 0x7F4F - LeapPad BaseROM (US, might be a revision)
- 0x7F51 - iQuest Handheld BaseROM
- 0x7F5B - My First LeapPad BaseROM (international)
- 0x7F5C - My First LeapPad, Vocabulator and Turbo Extreme BaseROMs

Potentially bad dumps with unconfirmed version numbers:
- Turbo Twist Math (the RIB is at the wrong offset or this system works entirely differently to the spelling one)
- Turbo Twist Brain Quest (the RIB is at the wrong offset or this system works differently to the other Turbo Twists)

# How do offsets in the asset tables work?
They use the start offset of the table as the base address. Add the start offset to the pointer to get the true offset in the ROM.

# LeapPad soundfont
This is the soundfont you'll want to use on LeapPad MIDIs (the instruments aren't identical to the Leapster ones):

[LeapPad.zip](https://github.com/user-attachments/files/17003961/LeapPad.zip)
