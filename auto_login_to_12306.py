#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#12306 自动打开12306网站，并输入用户名、密码和验证码，并登录12306，
#author bigluo
#email: 3490699170@qq.com
#modified by gitlab_sam, blues24@foxmail.com   @ 2018-11-29

#coding=utf-8

from selenium import webdriver
import time
from PIL import Image
from selenium.webdriver.common.action_chains import ActionChains
import os
import requests
import numpy
import traceback
from bs4 import BeautifulSoup


#指定button id和button文本值，并点击，连续点击5次
#return:
#0  click successfully
#-1 连续5次均failed
#1  txt != dest_text，所以不点击
def click_button(b,id,dest_text,j):        #在当前页面查找并点击指定text，错误返回 -1.连续5次，错误时延时1秒
    txt=''
    for i in range(0,5):
       try:
          txt=b.find_element_by_id(id).text
          if txt == dest_text:
              b.find_element_by_id(id).click()
              return 0 
          else:
              return 1
          
       except:
          time.sleep(1)
          continue

    return -1                         #5次都失败了


#给定button id和text，find a given text
#0 found
#-1 not found
def find_button(b,id,dest_text):
    txt=''
    try:
          txt=b.find_element_by_id(id).text
          if txt == dest_text:
              return 0
    except:      
          #print("find_button Error --page txt is "+txt+" input text is "+dest_text)
          return -1
          
    return -1

#click refresh pic button
def click_refresh(b):
    try:
	    b.find_element_by_class_name("lgcode-refresh").click()
    except:
        print("click_refresh:exception!!!!")

#初始化浏览器   
def init_browser(b):
    b.maximize_window()

#进入登录页，必须是未登录状态
# 0 ： 成功
#-1 ： 出错了
def visit_login_page(b):
    url = 'https://kyfw.12306.cn/otn/resources/login.html'
    b.get(url)
    # 访问login page后休息3秒，等待整个网页加载完
    time.sleep(3)
    b.find_element_by_link_text("账号登录").click()
    # 点击之后休息4秒，等待验证码刷新出来
    time.sleep(4)
    
    # 如果已经登录，则登出
    if b.find_element_by_id("J-header-logout"):
	    b.find_element_by_class_name("logout").click()
    return 0

#截取一张验证码图片，保存为aa.png
def get_a_verify_pic(b):
    # imgelement=b.find_element_by_xpath("//*[@id='loginForm']/div/ul[2]/li[4]/div/div/div[3]")
    imgelement=b.find_element_by_id("J-loginImgArea")
    location = imgelement.location  #获取验证码x,y轴坐标
    size=imgelement.size  #获取验证码的长宽
    rangle=(int(location['x']),int(location['y']),int(location['x']+293),int(location['y']+190)) #写成我们需要截取的位置坐标
    b.save_screenshot('aa.png')
    i=Image.open("aa.png") #打开截图
    pic_name='verify_code'+".png" #标准12306验证图片
    frame4=i.crop(rangle)  #使用Image的crop函数，从截图中再次截取我们需要的区域
    frame4.save(pic_name)
    return pic_name


#破解图片验证码
def ana_pic(b,pic_name):
      
    body_list=[]
    url='''http://littlebigluo.qicp.net:47720/'''
    files={'file':(pic_name,open(pic_name,'rb'),'image/png')}
    res=requests.post(url,files=files)              #post pic

    if res.status_code == 200:                      #return ok
        try:
            #print(res.text)
            # 没认出来图片，重新来一次
            if "不好意思，您这图片好难，木有认出来" in res.text:
	            return -1, None
            
            if u"图片貌似选" in res.text:             #识别验证码成功
                soup = BeautifulSoup(res.text, "html5lib")
                body_str_1 = soup.find("b").text
                body_list = body_str_1.split(" ")
                return 0,numpy.array(body_list)
                
        except:
            print("ana pic failed!!!!")
            print(traceback.format_exc())
            return -1,None
       
    return -1,None                    #验证码解析失败


#按输入的下标，点击一张验证码图片
def click_one_pic(b,i):
    try:
        imgelement=b.find_element_by_id("J-loginImgArea")
        if i<=4:
            ActionChains(b).move_to_element_with_offset(imgelement,40+72*(i-1),73).click().perform()
        else:
            i -= 4
            ActionChains(b).move_to_element_with_offset(imgelement,40+72*(i-1),145).click().perform()
    except:
	    print(traceback.format_exc())
	    print("Wa -- click one pic except!!!")
  
#按bodylist 指示，点击指定验证图片
def click_pic(b,body_list):
    for i in body_list:
        click_one_pic(b,int(i))
        time.sleep(1)
        
#输入用户名密码，并点击验证码登陆
#0:login successfully
#1:verify code failed,
#-1 error happened
def login(b):
    pic_name = None
    try:
        
        ret_val = -1
        body_list = []
        img_src = ""
        # ret_val为-1的话，认为没识别出来图片
        while ret_val == -1:
	        pic_name=get_a_verify_pic(b)           #截取12306验证码图片
	        ret_val,body_list=ana_pic(b,pic_name)  #破解12306验证码
	        img_src = b.find_element_by_id("J-loginImg").get_attribute("src")
	        if ret_val == -1:
		        print("未识别出验证码，将点击刷新再来一次")
		        click_refresh(b)
          
        username=b.find_element_by_id('J-userName')
        username.clear()
        user_name = "XXXXX"
        username.send_keys(user_name)
        password=b.find_element_by_id('J-password')
        password.clear()
        user_pwd = "XXXXXX"
        password.send_keys(user_pwd)
        time.sleep(2)
                        
        click_pic(b,body_list)
        time.sleep(1)                       #休息1秒再点击登陆按钮
        
        b.find_element_by_id("J-login").click()
    except:
        if None != pic_name:
            os.remove(pic_name)
        print(traceback.format_exc())#exception occured
        print("login:exception!!")
        return -1
    
    time.sleep(5)                      #查看验证码是否正确??
    ret_val=find_button(b,u"error_msgmypasscode1",u"请点击正确的验证码")
    if ret_val == 0:                 #验证码错误
        print("login--Verified code error!!!")
        return 1
    
    os.remove(pic_name)
    print("login--successfully!!!")
    return 0


#循环login
#返回
#0：登陆成功-正常返回
#-1：登陆失败或异常返回
#1 ：验证码未识别出来
def try_login(b):
       
    for k in range(0,5):                   #连续尝试5次
        rt_val=login(b)
        if  rt_val < 0:                     #error happened
            print("verify got exception!!")
            time.sleep(10)
            continue
        elif rt_val == 1:                   #verified code error
            print("verify - code error!!")
            time.sleep(5)
            continue                       #login again
        else:                               #login successfully
            print("login successfully!!!")
            return 0                
        
    return -1                   #login failed

if __name__ == "__main__": 
   
    b = webdriver.Chrome()
    init_browser(b)
    visit_login_page(b)
      
    ret_val = try_login(b)  #尝试登录
    if ret_val<0:
        print("main -- try_login failed!!!")
    else:
        print("main -- try_login successfully!!!")


    print("Good job！bigluo！！")