#!/usr/bin/env python
# -*- coding: utf-8 -*-

import queue
import threading
import time

"""
通过阻塞队列实现生产者-消费者模式
"""

DEFAULT_QUEUE_SIZE = 100

q = queue.Queue(DEFAULT_QUEUE_SIZE)


def producer():
    ele = 0
    while True:
        print('+++putting element to queue:%d' % ele)
        # put a element with BLOCK model
        q.put(ele, True)
        print('+++succeed put element to queue:%d' % ele)
        time.sleep(1)
        ele = ele + 1


def consumer():
    while True:
        print('---getting element from queue,queue size:%d'% q.qsize())
        # get the first element with BLOCK model
        ele = q.get(True)
        print('---succeed get element from queue:%d' % ele)
        time.sleep(2)


def main():
    # init two consumer Thread and one producer Thread
    t1 = threading.Thread(target=consumer)
    t2 = threading.Thread(target=producer)
    t3 = threading.Thread(target=consumer)
    t1.start()
    t2.start()
    t3.start()


# when run py, this method will be called
if __name__ == '__main__':
    main()
