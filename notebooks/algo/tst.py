import sys
import time
import random
from concurrent import futures

import tqdm


PROCESSES = 4
THREADS = 3


def main():
    I = 20
    for i in range(I):

        sys.stdout.write(f'\r{i}/{I}...')
        sys.stdout.flush()
        time.sleep(1)
    return 

    with futures.ProcessPoolExecutor(max_workers=PROCESSES) as executor:
        fut_to_num = {}
        for i in range(PROCESSES):
            fut = executor.submit(execute_many_threads, i)
            fut_to_num[fut] = i

        for future in futures.as_completed(fut_to_num):
            r = future.result()
            # print('{} returned {}'.format(fut_to_num[future], r))
    print('\nDone!\n')


def execute_many_threads(n_pool=0):
    with futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
        for i in range(THREADS):
            executor.submit(execute_thread, n_pool, i)
    return n_pool+1


def execute_thread(n_pool=0, n_thread=0):
    s = random.randint(1, 5)
    thread_num = n_pool*(PROCESSES-1) + n_thread

    progress = tqdm.tqdm(
        desc='#{:02d}'.format(thread_num),
        position=thread_num,
        total=10*s,
        leave=False,
    )
    # print('Executing {}: {}...'.format(thread_num, s))
    for i in range(s):
        time.sleep(1)
        progress.update(n=10)
    progress.close()
    return s


if __name__ == '__main__':
    main()
