#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import traceback
import logging

max_narrow = 50

# 文件和控制台都打印日志
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('D:\\log\\git_pull.log')
ch = logging.StreamHandler()
# 定义handler的输出格式formatter
formatter = logging.Formatter('%(asctime)s %(filename)s[line:%(lineno)d] %(message)s')

fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


def main():
	logger.info("===========================start==================================")
	try:
		root_dir = "E:"
		# 代码所在路径
		repo_dir = "E:\\blues\\company\\weai\\code"
		if os.path.exists(repo_dir):
			file_list = os.listdir(repo_dir)
			for file_name in file_list:
				temp_dir = os.path.join(repo_dir, file_name)
				logger.info("开始更新路径%s下的仓库代码..." % temp_dir)
				os.system("%s && cd %s && git pull" % (root_dir, temp_dir))
				logger.info("更新完毕")
			logger.info("所有仓库已全部更新.")
		else:
			logger.info("指定路径%s不存在." % repo_dir)
	except:
		logger.info("出现异常！！！")
		logger.info(traceback.format_exc())


if __name__ == "__main__":
	os.system("title 批量pull所有仓库信息")
	main()
	logger.info("===========================end==================================")
	# os.system("pause")
