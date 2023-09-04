@echo off
call venv\Scripts\activate.bat  # Aktiválás
python mainTest.py  # Python program futtatása
venv\Scripts\deactivate.bat  # Deaktiválás