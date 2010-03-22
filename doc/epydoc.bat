@echo off

REM set the environment
REM for now we first try to use normal python and if we can't find it
REM we go for mayapy instead

set PY=python
set PYTHONPATH=../..;../ext/pyparsing;../ext/pydot;../ext/networkx;%PYTHONPATH%

IF "%1" =="" GOTO GETPYTHON
IF /I mayapy == %1 set PY=mayapy&& GOTO GETPYTHON
GOTO HELP

:GETPYTHON
	echo.
	echo Generate docs using %PY% in your PATH ...
	%PY% -V
	IF ERRORLEVEL 1 ( IF %PY%==mayapy (GOTO NOPYTHON) ELSE (set PY=mayapy&& GOTO GETPYTHON) )
	
:DOJOB
	echo.
	%PY% epydoc.py -q -q -o html --config=epydoc.cfg --inheritance grouped
	IF ERRORLEVEL 1 GOTO EPYERROR
	GOTO END
	
:NOPYTHON
	echo.
	echo ERROR: no python installation could be found,
	echo        please add the python installation directory to PATH environment variable
	GOTO END

:EPYERROR
	echo.
	echo ERROR: epydoc may not be installed on %PY:python=default python%
	IF %PY%==python echo        use "epydoc.bat mayapy" if epydoc is installed on mayapy 
	GOTO END
	
:HELP
	echo Automatically creates html project documentation to .\html subfolder.
	echo If .\html does not exist it will be created.
	echo.
	echo usage: epydoc.bat [mayapy]
	echo.
	echo By default epydoc.bat uses the python executable in your PATH, and reverts to 
	echo "mayapy" on failure. 
	echo In case epydoc package is installed just on mayapy the use of "mayapy" can be
	echo forced by executing "epydoc.bat mayapy"
	echo.
:END