echo activate pipenv
cd C:\Users\wilso\.virtualenvs\
call activate Financial_Flask-OYIMoW_R

echo execute python
cd C:\Users\wilso\PycharmProjects\Financial_Flask\calculations\resources\

:: Line notify sends image
call python -c "import line_notify;line_notify.sendImg('Start.png', 'Start')"
echo over line_notify

:: Line notify sends image
call python -c "import line_notify;line_notify.sendImg('Complete.png', 'Complete')"
echo over line_notify

:: exit
:: 用來暫停批次檔的執行
::pause
