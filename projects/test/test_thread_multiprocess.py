"""
Python界有條不成文的標準：計算密集型任務適合多線程，IO密集型任務適合多線程。本篇文章來作個比較。

經常說多線程相對於多進程有優勢，因為創建一個線程比較大，但因為在 python 中有很多 GIL 把大鎖的存在，
導致執行計算密集型任務時多線程實際是單線程。因為線程之間的單一導致多線程往往比實際的線程更慢，所以python中計算密集型任務使用多進程切換，因為每個進程都有各自獨立的GIL，通常互不干擾。

而在 IO 真正密集型任務等待狀態，需要與真實環境進行交互，如讀寫文件，在網絡間通信等。在這期間 GIL 會被釋放，就可以了線程。

以上是理論，下面做一個簡單的模擬測試：大量計算用 math.sin() + math.cos() 來代替，IO 密集用 time.sleep() 來模擬。多線程和多線程，這裡一併看看有沒有頻繁的差異：

多進程： joblib.multiprocessing, multiprocessing.Pool, multiprocessing.apply_async, concurrent.futures.ProcessPoolExecutor
多線程： joblib.threading, threading.Thread, concurrent.futures.ThreadPoolExecutor
"""

import math
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from multiprocessing import Pool
from threading import Thread

from joblib import delayed, Parallel, parallel_backend


def f_IO(a):  # IO 密集型
    time.sleep(5)


def f_compute(a):  # 計算密集型
    for _ in range(int(1e7)):
        math.sin(40) + math.cos(40)
    return


def normal(sub_f):
    for i in range(6):
        sub_f(i)
    return


def joblib_process(sub_f):
    with parallel_backend("multiprocessing", n_jobs=6):
        res = Parallel()(delayed(sub_f)(j) for j in range(6))
    return


def joblib_thread(sub_f):
    with parallel_backend('threading', n_jobs=6):
        res = Parallel()(delayed(sub_f)(j) for j in range(6))
    return


def mp(sub_f):
    with Pool(processes=6) as p:
        res = p.map(sub_f, list(range(6)))
    return


def asy(sub_f):
    with Pool(processes=6) as p:
        result = []
        for j in range(6):
            a = p.apply_async(sub_f, args=(j,))
            result.append(a)
        res = [j.get() for j in result]


def thread(sub_f):
    threads = []
    for j in range(6):
        t = Thread(target=sub_f, args=(j,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()


def thread_pool(sub_f):
    with ThreadPoolExecutor(max_workers=6) as executor:
        res = [executor.submit(sub_f, j) for j in range(6)]


def process_pool(sub_f):
    with ProcessPoolExecutor(max_workers=6) as executor:
        res = executor.map(sub_f, list(range(6)))


def showtime(f, sub_f, name):
    start_time = time.time()
    f(sub_f)
    print("{} time: {:.4f}s".format(name, time.time() - start_time))


def main(sub_f):
    showtime(normal, sub_f, "normal")
    print()
    print("------ 多進程 ------")
    showtime(joblib_process, sub_f, "joblib multiprocess")
    showtime(mp, sub_f, "pool")
    showtime(asy, sub_f, "async")
    showtime(process_pool, sub_f, "process_pool")
    print()
    print("----- 多線程 -----")
    showtime(joblib_thread, sub_f, "joblib thread")
    showtime(thread, sub_f, "thread")
    showtime(thread_pool, sub_f, "thread_pool")


def query_data(num):
    print(num * num)


if __name__ == "__main__":
    print("----- 計算密集型 -----")
    sub_f = f_compute
    main(sub_f)
    print()
    print("----- IO 密集型 -----")
    sub_f = f_IO
    main(sub_f)

    # with parallel_backend(THREAD, n_jobs=-1):
    #     Parallel()(delayed(query_data)(num) for num in range(10))
