@echo off
call venv\Scripts\activate.bat  # Aktiválás
python mainServer.py  # Python program futtatása
venv\Scripts\deactivate.bat  # Deaktiválás