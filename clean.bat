@echo off

echo Limpando arquivos desnecessarios para Git...
echo.

echo [1/4] Removendo __pycache__...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
del /s /q *.pyo 2>nul

echo [2/4] Removendo dados extraidos...
if exist extractor\output rmdir /s /q extractor\output
if exist extractor\checkpoints rmdir /s /q extractor\checkpoints
if exist extractor\logs rmdir /s /q extractor\logs

echo [3/4] Removendo .env (mantendo .env.example)...
if exist .env del /q .env

echo [4/4] Removendo desafio.txt...
if exist desafio.txt del /q desafio.txt

echo.
echo Limpeza concluida!
echo.
echo Arquivos prontos para commit no Git.
echo.
echo Proximos passos:
echo   1. git init
echo   2. git add .
echo   3. git commit -m "Initial commit: SNCR Data Pipeline"
echo   4. git remote add origin seu-repositorio
echo   5. git push -u origin main
