Feel free to reimplement, borrow or use this documentation for your own research and tools.

# To-do
- Make a ROM splitter now that the offsets have been figured out
- Document how offsets work on the LeapPad and all related (pre-Leapster) systems
- Document the shape format used by the LeapPad (it uses these for the touch functionality) and make an automated graphics ripper for the iQuest/Turbo Twists
- Document the RIB table at offset 0x10100
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

# Q&A

Q - "How do I use the MIDI conversion script?"

A - You can't (at least, not yet. Wait for the ROM splitter to release first.)
