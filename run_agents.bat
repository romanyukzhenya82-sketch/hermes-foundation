@echo off
cd /d C:\Users\DJlinnuJ\hermes_foundation
set LOG=logs\agents_%date:~-4,4%%date:~-10,2%%date:~-7,2%.log
C:\Python314\python.exe directional_binance_agents.py >> %LOG% 2>&1
