@ECHO OFF
setlocal
set PYTHONPATH=%1
set _all=%*
call set _tail=%%_all:*%2=%%
set _tail=%2%_tail%
python %_tail%
endlocal