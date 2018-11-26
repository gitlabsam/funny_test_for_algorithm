#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import traceback
import logging

from aip import AipOcr
import urllib.request
from http import cookiejar
from bs4 import BeautifulSoup
from urllib import parse
import time
import re
from dingtalkchatbot.chatbot import DingtalkChatbot

max_narrow = 50

# 文件和控制台都打印日志
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('D:\\log\\daily_query.log')
ch = logging.StreamHandler()
# 定义handler的输出格式formatter
formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(message)s')

fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

USER_AGENT_LIST = [
 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
  'Chrome/45.0.2454.85 Safari/537.36 115Browser/6.0.3',
 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
 'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0',
 'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'
]


# 百度识别图片验证码相关
""" 你的 APPID AK SK """
APP_ID = 'XXX'
API_KEY = 'XXX'
SECRET_KEY = 'XXX'

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

""" 读取图片 """
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

def read_local_image(image_path):
	"""
	识别本地图片
	:param image_path:
	:return:
	"""
	image = get_file_content(image_path)
	return client.basicGeneral(image)


def read_local_image_with_opt(image_path):
	image = get_file_content(image_path)
	""" 如果有可选参数 """
	options = {}
	options["language_type"] = "CHN_ENG"
	options["detect_direction"] = "true"
	options["detect_language"] = "true"
	options["probability"] = "true"
	
	""" 带参数调用通用文字识别, 图片参数为本地图片 """
	return client.basicGeneral(image, options)


def read_from_url(url):
	""" 调用通用文字识别, 图片参数为远程url图片 """
	return client.basicGeneralUrl(url)


def read_from_url_with_opt(url):
	""" 如果有可选参数 """
	options = {}
	options["language_type"] = "CHN_ENG"
	options["detect_direction"] = "true"
	options["detect_language"] = "true"
	options["probability"] = "true"
	
	""" 带参数调用通用文字识别, 图片参数为远程url图片 """
	return client.basicGeneralUrl(url, options)


def get_url_content(url, headers):
	"""
	获取网站url的cookies
	:param url:
	:return:
	"""
	# 通过cookieJar类构建一个cookieJar对象，用来保存cookie的设置、
	cookie = cookiejar.CookieJar()
	# 通过一个HttpCookieProcessor()处理器类构建一个处理器对象，用来处理cookie
	# 参数就是构建的cookieJar对象、
	cookie_handle = urllib.request.HTTPCookieProcessor(cookie)
	opener = urllib.request.build_opener(cookie_handle)
	urllib.request.install_opener(opener)
	# url = 'https://sz12333.gov.cn/rcyj/personstorage.do?method=toQureyList'
	request = urllib.request.Request(url, headers=headers)
	opener.open(request)
	return cookie


def get_person_page(url, headers):
	"""
	headers需要带上refer，否则非法
	:return:
	"""
	req = urllib.request.Request(url, headers=headers)
	res = urllib.request.urlopen(req)
	# 以html5lib格式的解析器解析得到BeautifulSoup对象
	# 还有其他的格式如：html.parser/lxml/lxml-xml/xml/html5lib
	soup = BeautifulSoup(res, 'html5lib')
	return soup


def read_code(image_path):
	"""
	识别验证码
	:param image_path:
	:return:
	"""
	rsp = read_local_image(image_path)
	if rsp and "words_result" in rsp:
		print(rsp["words_result"][0]["words"])
		return rsp["words_result"][0]["words"]


def find_event_list(html_str):
	"""
	发现办事进度主体条目
	:param html_str:
	:return:
	"""
	soup = BeautifulSoup(html_str, 'html5lib')
	tr_list = soup.tbody.find_all("tr")
	# event_title = ["姓名", "业务类型", "受理日期", "办理状态"]
	event_list = []
	for tr in tr_list:
		td_list = tr.find_all("td")
		temp = {}
		temp["姓名"] = re.sub(r"\s+", "", td_list[0].text)
		temp["业务类型"] = re.sub(r"\s+", "", td_list[1].text)
		temp["受理日期"] = re.sub(r"\s+", "", td_list[2].text)
		temp["办理状态"] = re.sub(r"\s+", "", td_list[3].text)
		
		event_list.append(temp)

	return event_list


def send_dingtalk_msg(ding_msg):
	# pip install DingtalkChatbot
	# 钉钉发送消息相关信息
	token = "XXX"
	# WebHook地址
	webhook = 'https://oapi.dingtalk.com/robot/send?access_token=' + token
	# 初始化机器人小丁
	xiaoding = DingtalkChatbot(webhook)
	# Text消息@所有人
	# xiaoding.send_text(msg='我就是小丁，小丁就是我！', is_at_all=True)
	# Text消息之@指定用户
	at_mobiles = ['XXX', 'XXX']
	xiaoding.send_text(msg=ding_msg, at_mobiles=at_mobiles)


def main():
	logger.info("===========================start==================================")
	try:
		default_headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) "
			              "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
		}
		# 请求首页
		url = "https://sz12333.gov.cn/rcyj/personstorage.do?method=toQureyList"
		host_url = "https://sz12333.gov.cn"
		cookie = get_url_content(url, default_headers)
		jsession_id = ""
		if cookie:
			for item in cookie:
				if item.name == "JSESSIONID" or item.name == "jsessionid":
					jsession_id = item.value
					break
		
		# 请求这个页面，需要加上refer
		# Refer：https://sz12333.gov.cn/rcyj/personstorage.do?method=toQureyList&JSESSIONID=B92nbnRN69ydxGT5nh4Bw7jL12TlK08Gqp2LdpGXCDsPvg3s0HRT!873050859
		person_url = "https://sz12333.gov.cn/rcyj/jsplib/unit/personstorage/personstorage_list_index.jsp"
		headers = {
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
			"Accept-Encoding": "gzip, deflate, br",
			"Accept-Language": "zh-CN,zh;q=0.9",
			"Connection": "keep-alive",
			"Cookie": "JSESSIONID=" + jsession_id,
			"Host": "sz12333.gov.cn",
			"Referer": "https://sz12333.gov.cn/rcyj/personstorage.do?method=toQureyList",
			"Upgrade-Insecure-Requests": "1",
			"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
		}
		
		soup = get_person_page(person_url, headers)
		img_src = soup.img.attrs["src"]
		# 加上sessionid，验证之后的结果，可以通过后台验证，否则是无法通过验证的
		# 因为图片每次请求，都是不一样的
		# 后台验证逻辑是通过sessionid进行匹配，只要保证我们本次查询所有的请求sessionid一致，就能通过验证
		img_url = host_url + img_src + "&JSESSIONID=" + jsession_id
		# 保存验证码图片到本地
		# 直接传入url到百度去验证的话，无法通过，可能是服务器做了跨域的限制，所以先保存到本地，再从本地验证
		image_path = "D:\\CVerifyCode.jpg"
		img_header = {
				"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
				"Accept-Encoding": "gzip, deflate, br",
				"Accept-Language": "zh-CN,zh;q=0.9",
				"Cache-Control": "max-age=0",
				"Connection": "keep-alive",
				"Cookie": "JSESSIONID=" + jsession_id,
				"Host": "sz12333.gov.cn",
				"Upgrade-Insecure-Requests": "1",
				"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
				}
		
		import requests
		res = requests.get(img_url, headers=img_header)
		f = open('D:\\CVerifyCode.jpg', 'wb')
		f.write(res.content)  # save to page.html
		f.close()
		# urllib.request.urlretrieve(img_url, image_path)
		# 调用百度的接口识别验证码
		code = read_code(image_path)
		# 发送查询
		# 姓名
		person_name = "XXX"
		# 身份证
		cardid = "XXX"
		qry_url = "https://sz12333.gov.cn/rcyj/personstorage.do?method=toDQureyList"
		data = {"personName": person_name, "cardid": cardid, "selfpercode": code}
		post_header = {
			"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
			"Accept-Encoding": "gzip, deflate, br",
			"Accept-Language": "zh-CN,zh;q=0.9",
			"Cache-Control": "max-age=0",
			"Connection": "keep-alive",
			"Content-Length": "72",
			"Content-Type": "application/x-www-form-urlencoded",
			"Cookie": "JSESSIONID=" + jsession_id,
			"Host": "sz12333.gov.cn",
			"Origin": "https://sz12333.gov.cn",
			"Referer": "https://sz12333.gov.cn/rcyj/jsplib/unit/personstorage/personstorage_list_index.jsp",
			"Upgrade-Insecure-Requests": "1",
			"User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
			}
		data = urllib.parse.urlencode(data, encoding="gb2312").encode("gb2312")
		req = urllib.request.Request(qry_url, headers=post_header, data=data)  # POST方法
		page = urllib.request.urlopen(req).read().decode('gbk')
		# print(page)
		event_list = find_event_list(page)
		print("查询时间: %s  " % time.strftime("%Y-%m-%d %H:%M:%S"))
		print("查询结果: %s " % event_list)
		# 接收结果并发送钉钉短信
		ding_msg = "查询时间: %s \n" % time.strftime("%Y-%m-%d %H:%M:%S")
		ding_msg += "查询结果: "
		if event_list:
			for ev in event_list:
				ding_msg += ev["办理状态"]
				ding_msg += "-"
				ding_msg += ev["受理日期"]
				ding_msg += "-"
				ding_msg += ev["姓名"]
				ding_msg += "-"
				ding_msg += ev["业务类型"]
				ding_msg += "\n"
		else:
			ding_msg += "暂无任何进度\n"
		
		send_dingtalk_msg(ding_msg[:-1])
		
	except:
		logger.info("出现异常！！！")
		print("出现异常！！！")
		logger.info(traceback.format_exc())


if __name__ == "__main__":
	main()