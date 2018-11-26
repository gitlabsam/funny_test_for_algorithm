#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import paramiko
import time
import os
import traceback
import uuid
import zipfile
import sys
import logging
import urllib.request as request
import datetime


max_narrow = 50

# 文件和控制台都打印日志
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('D:\\log\\log_trasfer_log.log')
ch = logging.StreamHandler()
# 定义handler的输出格式formatter
formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(message)s')

fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


def create_ssh_client(hostname, port, username, password):
	"""
    创建ssh连接
	:param hostname:
	:param port:
	:param username:
	:param password:
	:return:
	"""
	# paramiko.util.log_to_file("paramiko.log")
	
	client = paramiko.SSHClient()
	client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	
	client.connect(hostname=hostname, port=port, username=username, password=password)
	return client


def sshclient_execmd(client, execmd):
	"""
	执行指定执行
	:param client:
	:param execmd:
	:return:
	"""
	stdin, stdout, stderr = client.exec_command(execmd)
	stdin.write("Y")  # Generally speaking, the first connection, need a simple interaction.
	# 格式化输出信息
	for line in stdout:
		logger.info(line.strip("\n"))
	# 格式化错误信息
	for line in stderr:
		logger.info(line.strip("\n"))
	# print(stdout.read())
	# client.close()


def ssh_client_sftp(client):
	# 新建 sftp session
	return client.open_sftp()


def sftp_process_callback(size, file_size):
	"""
	sftp回调函数，sftp将调用此函数，告知已传输大小size和文件总大小file_size
	在此，我们转换成动态的进度条特效
	:param size:
	:param file_size:
	:return:
	"""
	percent = size / file_size  # 计算完成进度，格式为xx.xx%
	num_arrow = int(percent * max_narrow)  # 计算显示多少个'>'
	
	num_line = max_narrow - num_arrow # 计算显示多少个'-'
	
	file_size = round(file_size / 1024 / 1024, 2)
	
	size /= 1024
	show_unit = "k"
	if size > 1:
		size /= 1024
		show_unit = "m"
	
	process_bar = '[' + '>' * num_arrow + '=' * num_line + ']  ' \
	              + '%.2f' % (percent * 100) + '%'+'(%s%s/%sm)' \
	              % (round(size, 2), show_unit, file_size) + '\r'  # 带输出的字符串，'\r'表示不换行回到最左边
	# print("文件大小:%s,已传输大小:%s" % (file_size,size))
	sys.stdout.write(process_bar)  # 这两句打印字符到终端
	sys.stdout.flush()


def create_local_log_file_name(local_path, zip_file_name):
	"""
	文件已存在，或者已经下载过多次，则重新命名
	:param local_path:
	:param zip_file_name:
	:return:
	"""
	zip_file_name_without_suffix = zip_file_name.split(sep=".")[0]
	zip_file_name_without_suffix_ = zip_file_name.split(sep=".")[0]
	if os.path.exists(local_path):
		file_list = os.listdir(local_path)
		index = 1
		while file_list.__contains__(zip_file_name):
			zip_file_name_without_suffix = zip_file_name_without_suffix_ + "(%s)" % index
			zip_file_name = zip_file_name_without_suffix + ".zip"
			index += 1
	
	return local_path + "\\" + zip_file_name, local_path + "\\" + zip_file_name_without_suffix


def unzip_file(zfile_path, unzip_dir):
    '''
    function:解压
    params:
        zfile_path:压缩文件路径
        unzip_dir:解压缩路径
    description:
    '''
    try:
        with zipfile.ZipFile(zfile_path) as zfile:
            zfile.extractall(path=unzip_dir)
    except zipfile.BadZipFile as e:
	    logger.info(zfile_path + " is a bad zip file ,please check!")


def get_day_type(query_date):
    url = 'http://tool.bitefu.net/jiari/?d=' + query_date
    resp = request.urlopen(url)
    content = resp.read()
    if content:
        try:
            day_type = int(content)
        except ValueError:
            return -1
        else:
            return day_type
    else:
        return -1


def is_tradeday(query_date):
	"""
	指定日期是否为交易日
	:param query_date:
	:return:
	"""
	weekday = datetime.datetime.strptime(query_date, '%Y%m%d').isoweekday()
	# 周一到周五 + 非节假日 = 交易日
	if weekday <= 5 and get_day_type(query_date) == 0:
		return 1
	else:
		return 0


def today_is_tradeday():
	"""
	今天是否是交易日
	:return:
	"""
	query_date = datetime.datetime.strftime(datetime.datetime.today(), '%Y%m%d')
	return is_tradeday(query_date)

def main():
	logger.info("===========================start==================================")
	hostname = '127.0.0.1'
	port = 22
	username = 'XXXX'
	password = 'XXXX'
	
	# 创建连接客户端
	client = create_ssh_client(hostname, port, username, password)
	
	log_date = time.strftime('%Y%m%d', time.localtime(time.time()))
	
	local_path = 'Z:\\04.data\\server_log'
	local_zip_file_name = "log%s.zip" % log_date
	
	log_path = "/tmp/coin_trade/log"
	# log_path = "/tmp/coin_trade"
	remote_log_file_name = str(uuid.uuid1()) + ".zip"
	
	# 执行指令
	# /tmp/coin_trade/log  没有权限在log下创建zip文件了，但上级目录可以，所以放到上级目录
	zip_file_full_name = "/tmp/coin_trade/%s" % remote_log_file_name
	execmd = "cd %s && zip -r ../%s ./xnbo/*" % (log_path, remote_log_file_name)
	# print(execmd)
	# print(execmd)
	try:
		logger.info("开始压缩...")
		sshclient_execmd(client, execmd)
		logger.info("压缩完成")
		
		# 删除带有日期的log文件（只保留当天的日志文件）
		logger.info("正在删除除当天外的日志文件...")
		execmd = 'find %s -name "*[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]*.log" | xargs rm -f' % log_path
		sshclient_execmd(client, execmd)
		
		ftp_client = ssh_client_sftp(client)
		logger.info("正在传输文件:%s..." % zip_file_full_name)
		# 从远程主机下载文件，如果失败， 这个可能会抛出异常。
		local_zip_file_name_final, local_zip_file_name_final_without_suffix = create_local_log_file_name(local_path, local_zip_file_name)
		ftp_client.get(zip_file_full_name, local_zip_file_name_final, callback=sftp_process_callback)
		
		logger.info("\r完成传输文件")
		# 上传文件到远程主机，也可能会抛出异常
		# sftp.put('/home/test.sh', 'test.sh')
		logger.info("正在删除临时压缩包...")
		execmd = "rm -rf %s" % zip_file_full_name
		sshclient_execmd(client, execmd)
		logger.info("已删除压缩包")
		
		logger.info("开始解压本地压缩包...")
		unzip_file(local_zip_file_name_final, local_zip_file_name_final_without_suffix)
		logger.info("已解压到目录: %s" % local_zip_file_name_final_without_suffix)
		logger.info("============================end===================================")
	except:
		logger.info("出现异常！！！")
		print("出现异常！！！")
		logger.info(traceback.format_exc())
		
	client.close()


if __name__ == "__main__":
	os.system("title 从服务器导出日志")
	main()
	# 如果是交易日，则pause住，方便上班时直观看到日志，
	# 否则，非交易日不上班，pause的话，将导致计划任务一直挂起
	# if today_is_tradeday():
	# 	os.system("pause")
