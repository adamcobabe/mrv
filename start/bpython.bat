
REM set the python path to find out package
REM we do not have maya support in the moment
set basedir=%~dp0
set pyrepobase=%basedir%\..\py
set PYTHONPATH=%pyrepobase%;%PYTHONPATH%

REM execute the tool 
python %*


:end