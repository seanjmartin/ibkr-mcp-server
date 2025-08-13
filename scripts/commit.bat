@echo off
REM Convenient wrapper to use the Python git commit script
REM Usage: commit.bat "Your message here"
REM Usage: commit.bat (interactive)

C:\Python313\python.exe "%~dp0git-commit.py" %*
