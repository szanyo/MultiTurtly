@echo off
call venv\Scripts\activate.bat  # Aktiválás
python mainClient.py  # Python program futtatása
venv\Scripts\deactivate.bat  # Deaktiválás