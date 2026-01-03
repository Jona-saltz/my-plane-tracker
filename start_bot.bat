@echo off
cd /d "%~dp0"
echo Checking for updates...
git pull
echo Starting bot...
python plane_tracker.py
:: pause removed so it closes automatically