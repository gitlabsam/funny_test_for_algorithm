# -*- coding: utf-8 -*-

from random import choice
import datetime
import time


"""
蒙提·霍尔悖论

蒙提霍尔悖论亦称为蒙提霍尔问题、蒙特霍问题或蒙提霍尔悖论、三门问题（Monty Hall problem）。
三门问题（Monty Hall problem），是一个源自博弈论的数学游戏问题，大致出自美国的电视游戏节目Let's Make a Deal。
问题的名字来自该节目的主持人蒙提·霍尔（Monty Hall）

游戏规则

这个游戏的玩法是：参赛者会看见三扇关闭了的门，其中一扇的后面有一辆汽车，选中后面有车的那扇门就可以赢得该汽车，
而另外两扇门后面则各藏有一只山羊。当参赛者选定了一扇门，但未去开启它的时候，节目主持人会开启剩下两扇门的其中一扇，
露出其中一只山羊。主持人其后会问参赛者要不要换另一扇仍然关上的门。问题是：换另一扇门会否增加参赛者赢得汽车的机会率？

转摘自：https://baike.baidu.com/item/蒙提·霍尔悖论/5331548?fr=aladdin
"""

def monty_hall_test(flag):
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
        if monty_hall_test(flag):
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