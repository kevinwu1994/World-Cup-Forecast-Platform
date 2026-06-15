@echo off
cd /d "%~dp0"

set PYTHONPATH=%CD%

python scripts/main_run_worldcup_pipeline.py

pause