# 宣告使用 /bin/bash
#!/bin/bash

echo " === Execute Line Notify from Financial Flask project === "

source /root/.local/share/virtualenvs/Financial_Flask-lIXclJgf/bin/activate

cd /git/Financial_Flask/calculations/tests

python test_line_notify.py

deactivate
