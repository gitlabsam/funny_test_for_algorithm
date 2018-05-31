# -*- coding: utf-8 -*-

from random import choice
import datetime
import time


def monty_holl_test(flag):
	list = ['sheep', 'sheep', 'car']
	# 第一次选择
	first_choice = choice(list)
	list.remove(first_choice)
	# 主持人去掉一个sheep
	list.remove('sheep')
	# 第二次选择，默认不换门
	second_choice = first_choice
	# 换门
	if flag == '2':
		second_choice = choice(list)
	return second_choice == 'car'

if __name__ == '__main__':
    count = 0
    correct_count = 0
    incorrect_count = 0
    time_stamp = datetime.datetime.now()

    start = time.clock()
    total_count = input("请输入测试次数：")
    total_count = int(total_count)
    flag = input("请输入是否换门（1 不换 2 换）：")
    print("开始于%s" % time_stamp.strftime('%Y-%m-%d %H:%M:%S'))
    while(total_count > count ):
        if monty_holl_test(flag):
            correct_count += 1
        else:
            incorrect_count += 1

        count += 1

    if flag == '1':
        print('不换门获胜的概率为：%s' % (correct_count / total_count))
        print('不换门失败的概率为：%s' % (incorrect_count / total_count))
    else:
	    print('换门获胜的概率为：%s' % (correct_count / total_count))
	    print('换门失败的概率为：%s' % (incorrect_count / total_count))

    time_stamp = datetime.datetime.now()
    print("结束于%s" % time_stamp.strftime('%Y-%m-%d %H:%M:%S'))
    end = time.clock()
    print("总耗时：%.3f 秒"  % (end - start))