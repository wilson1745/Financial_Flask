# 宣告使用 /bin/bash
#!/bin/bash

echo "=== 將目前執行 process 的 PID 依照數字大小排序，取出前 10 名 === "

# ps 為列出 process 相關資訊，透過 | pipe 管線傳遞資料。awk 可以根據 pattern 進行資料處理（這邊印出第一欄 PID）而 sort 是進行排序，其排序時，預設都是把資料當作字串來排序，若想讓資料根據實際數值的大小來排序，可以加上 -n 參數。-r 則是由大到小排序，預設是由小到大
ps | awk '{print $1}' | sort -rn | head -10