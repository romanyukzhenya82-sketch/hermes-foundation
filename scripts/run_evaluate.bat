@echo off
cd /d C:\Users\DJlinnuJ\hermes_foundation
set LOG=logs\evaluate_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log
C:\Python314\python.exe evaluate_signals.py --lookback 7 >> %LOG% 2>&1
