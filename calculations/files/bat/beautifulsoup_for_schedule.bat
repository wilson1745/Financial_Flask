echo activate pipenv
cd C:\Users\wilso\.virtualenvs\
call activate Financial_Flask-OYIMoW_R

echo execute python
cd C:\Users\wilso\PycharmProjects\Financial_Flask\calculations\resources\

::call python -m beautifulsoup_for_schedule.py
call python -m beautifulsoup_for_schedule
echo over beautifulsoup_for_schedule

call python -m line_notify
echo over line_notify

call python -m potential_stock
echo over potential_stock

call python -m industry_cal
echo over industry_cal

:: exit
:: 用來暫停批次檔的執行
::pause
