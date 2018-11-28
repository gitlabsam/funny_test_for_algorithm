#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import re

"""
获取和解析长沙规划局的公示
"""

if __name__ == "__main__":
	# 获取规划公示
	r = requests.get("http://ghj.changsha.gov.cn/xxgk/ghgs//index.jsonp")
	# 提取数据
	res = r.text.encode(encoding="ISO-8859-1").decode(encoding="utf-8")
	# 数据格式： viewdatas([...])
	# 正则比较渣，直接截取了。。。
	# 截取为[{
	# 'xm_title': '宝能公馆批前公示',
	# 'pubdate': '2018-11-27',
	# 'puburl': 'http://ghj.changsha.gov.cn/xxgk/ghgs/201811/t20181127_2892533.html'
	# },...]
	json_str = res[10: -1]
	# 替换掉换行符
	json_ = re.sub(r"\s+", "", json_str)
	# 字符串类型的数据转换为列表list
	json_ = eval("{}".format(json_))
	
	# 获取指定的楼盘所有的公示
	# 如果没有指定，则查看所有的公示
	name = ""
	# name = "保利西海岸"
	ret_list = []
	for j in json_:
		if name:
			temp_name = j["xm_title"]
			if temp_name.find(name) != -1:
				ret_list.append(j)
		else:
			ret_list.append(j)
	# 按公示日期降序排序，最近的公示放上面
	ret_list.sort(key=lambda ret: ret["pubdate"], reverse=True)
	
	print(ret_list)
