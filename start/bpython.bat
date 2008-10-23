
REM set the python path to find out package
REM we do not have maya support in the moment
REM adjust PYTHONPATH to look for maya includes
set mayapy=%MAYA_LOCATION%\Python\lib\site-packages
set mayapydll=%MAYA_LOCATION%\Python\DLLs
set mayadll=%MAYA_LOCATION%\bin

set basedir=%~dp0
set pyrepobase=%basedir%\..\py

set PYTHONPATH=%pyrepobase%;%mayapy%;%PYTHONPATH%
set PATH=%mayapydll%;%mayadll%;%PATH%

REM execute the tool 
REM python %*
"%MAYA_LOCATION%\bin\mayapy.exe" %*


:end