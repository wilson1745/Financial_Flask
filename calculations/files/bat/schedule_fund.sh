# 宣告使用 /bin/bash
#!/bin/bash

echo " === Execute Lucre Funds from Financial Flask project === "

source /root/.local/share/virtualenvs/Financial_Flask-lIXclJgf/bin/activate

cd /git/Financial_Flask/calculations/resources

python lucre_funds.py

deactivate
