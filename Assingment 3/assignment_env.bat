@echo off
set "JAVA_HOME=C:\Program Files\Microsoft\jdk-11.0.30.7-hotspot"
set "CONDA_ROOT=C:\Users\hamza\miniconda3"
set "ENV_PREFIX=C:\Users\hamza\miniconda3\envs\svv-a3-py36"
set "SPIN_HOME=C:\Users\hamza\tools\spin"
set "MSYS2_UCRT64=C:\msys64\ucrt64\bin"
set "MSYS2_USR=C:\msys64\usr\bin"
set "GIT_CMD=C:\Program Files\Git\cmd"

set "PATH=%ENV_PREFIX%;%ENV_PREFIX%\Scripts;%ENV_PREFIX%\Library\bin;%JAVA_HOME%\bin;%SPIN_HOME%;%MSYS2_UCRT64%;%MSYS2_USR%;%GIT_CMD%;%CONDA_ROOT%;%CONDA_ROOT%\Scripts;%CONDA_ROOT%\Library\bin;%PATH%"
set "CONDA_DEFAULT_ENV=svv-a3-py36"
set "CONDA_PREFIX=%ENV_PREFIX%"

echo Assignment environment loaded.
echo Java:
java -version
echo.
echo Conda:
conda --version
echo.
echo Spin:
spin -V
