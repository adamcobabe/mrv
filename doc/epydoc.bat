@echo off

REM set the environment
REM for now we first try to use normal python and if we can't find it
REM we go for mayapy instead

set PYTHONPATH=../..;../ext/pyparsing;../ext/pydot;../ext/networkx;%PYTHONPATH%
IF "%1" =="" GOTO DEFAULT
IF /I mayapy == %1 GOTO MAYAPY
GOTO HELP

:DEFAULT
	set PY="default python"
	echo.
	echo Generate docs using python in your PATH ...
	python -V
	IF ERRORLEVEL 1 GOTO MAYAPY
	echo.
	python epydoc.py -q -q -o html --config=epydoc.cfg --inheritance grouped
	IF ERRORLEVEL 1 GOTO EPYERROR
	GOTO END
	
:MAYAPY
	set PY=mayapy
	echo.
	echo Generating docs using mayapy in your PATH
	mayapy -V
	IF ERRORLEVEL 1 GOTO NOPYTHON
	echo.
	mayapy epydoc.py -q -q -o html --config=epydoc.cfg --inheritance grouped
	IF ERRORLEVEL 1 GOTO EPYERROR
	GOTO END
	
:NOPYTHON
	echo.
	echo ERROR: no python installation could be found,
	echo        please add the python installation directory to PATH environment variable
	GOTO END

:EPYERROR
	echo.
	echo ERROR: epydoc may not be installed on %PY%
	IF %PY%=="default python" echo        use "epydoc.bat mayapy" if epydoc is installed on mayapy 
	GOTO END
	
:HELP
	echo Automatically creates html documentation of mayarv to .\html subfolder.
	echo If .\html does not exists it will be created.
	echo.
	echo usage: epydoc.bat [mayapy]
	echo.
	echo By default epydoc.bat uses the python executable in your PATH, and reverts to 
	echo "mayapy" on failure. 
	echo In case epydoc package is installed just on mayapy the use of "mayapy" can be
	echo forced by executing "epydoc.bat mayapy"
	echo.
:END