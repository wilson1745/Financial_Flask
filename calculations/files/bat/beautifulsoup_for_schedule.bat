echo activate pipenv
cd C:\Users\wilso\.virtualenvs\
call activate Financial_Calculations-yGs826X0

echo execute python
cd C:\Users\wilso\PycharmProjects\Financial_Calculations\projects\

::call python -m beautifulsoup_for_schedule.py
call python -m beautifulsoup_for_schedule
echo over beautifulsoup_for_schedule

call python -m line_notify
echo over line_notify

call python -m potential_stock
echo over potential_stock

:: exit
:: 用來暫停批次檔的執行
:: pause
