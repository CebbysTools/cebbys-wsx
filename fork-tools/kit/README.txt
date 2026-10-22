NHL 27 on Windows through AnyPS5 - setup kit
============================================

This kit has no game files. You need your own decrypted dump of NHL 27 (PPSA34063).

Needs: Windows 10/11 x64, a Vulkan GPU (tested: NVIDIA RTX 4070), Python 3 (python.org).

Setup (once):
  powershell -ExecutionPolicy Bypass -File setup.ps1 -Dump "D:\path\to\NHL 27"

  setup.ps1 unwraps eboot.bin and the game's modules, converts them with relinker.exe,
  places the converted *.guest.prx files next to the originals in your dump, and makes
  windows\ with eboot.exe, a link to libs\ and a link (app0) to your dump.

Optional, saves about 160 GB of disk: add -Compress to the setup command. It uses Windows' own
NTFS LZX compression on Data\ (transparent to the game; undo with compact /u /s /exe in Data\).

Play:
  windows\Run NHL 27.cmd

What to expect (build in BUILD.txt):
  - First start compiles about 26k shaders (~5 min, cache in windows\shader_cache).
  - About 1-2 FPS. Match load about 10 minutes.
  - Title screen: X through sign-in and licence screens.
  - Team select: Triangle (CPU vs CPU) then X, or pick a side and X.
  - Each intermission and the end-of-game summary wait for X.
  - Tested: a 2-hour CPU vs CPU run without crash or GPU reset.

Source and patches: https://github.com/CebbysTools/cebbys-wsx (branch nhl27, PR #9).
AnyPS5 is GPL-2.0-only: https://github.com/boykopovar/AnyPS5
