REM
REM Copyright (C) 2018 Branko Majic
REM
REM This file is part of Gimmecert documentation.
REM
REM This work is licensed under the Creative Commons Attribution-ShareAlike 3.0
REM Unported License. To view a copy of this license, visit
REM http://creativecommons.org/licenses/by-sa/3.0/ or send a letter to Creative
REM Commons, 444 Castro Street, Suite 900, Mountain View, California, 94041, USA.
REM


@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=.
set BUILDDIR=_build
set SPHINXPROJ=Gimmecert
set SPHINXOPTS=-W

if "%1" == "" goto help

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.http://sphinx-doc.org/
	exit /b 1
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%

:end
popd
