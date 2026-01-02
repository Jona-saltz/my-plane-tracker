@echo off
echo Checking for updates from GitHub...
git pull
echo.
echo Starting the Plane Tracker...
python plane_tracker.py
echo.
echo Script finished.
pause