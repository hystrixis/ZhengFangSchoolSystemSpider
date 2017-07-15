# -*- coding: utf-8 -*-
import os
import random
import urllib

import MySQLdb
import urllib2

import datetime

import re
from bs4 import BeautifulSoup
import pytesseract
from lxml import etree
import requests
import sys
from PIL import Image
from marshmallow import Schema,fields
from parseHtml import getClassScheduleFromHtml, getStudentInfor, get__VIEWSTATE, getGrade, getClassFileName
from model import Student, db, ClassSchedule, Class, YearGrade, OneLessonGrade, TermGrade, Code

# 设置编码

reload(sys)
sys.setdefaultencoding("utf-8")

# TODO 这里改成你学校教务系统的首地址
baseUrl = "http://61.147.254.75:81/(m4qowf45aqesuu45sq5o3vq5)"
session = requests.session()
# 含验证码登陆
def getCode():
    imgUrl = baseUrl + "/CheckCode.aspx?"
    imgresponse = session.get(imgUrl, stream=True)
    image = imgresponse.content
    DstDir = os.getcwd() + "\\"
    print("保存验证码到：" + DstDir + "code.jpg" + "\n")
    try:
        with open(DstDir +"code.jpg", "wb") as jpg:
            jpg.write(image)
    except IOError:
        print("IO Error\n")

def login(stuNumber,password):
    loginurl = baseUrl + "/default2.aspx"
    response = session.get(loginurl)
    selector = etree.HTML(response.content)
    __VIEWSTATE = selector.xpath('//*[@id="form1"]/input/@value')[0]
    getCode()
    code = raw_input("验证码是：")
    RadioButtonList1 = u"学生".encode('gb2312', 'replace')
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36'
    headers = {'User-Agent': user_agent}
    data = {
        "RadioButtonList1": RadioButtonList1,
        "__VIEWSTATE": __VIEWSTATE,
        "TextBox1": stuNumber,
        "TextBox2": password,
        "TextBox3": code,
        "Button1": "",
        "lbLanguage": ""
    }
    # 登陆教务系统
    loginResponse =session.post(loginurl, data=data,headers=headers)
    if loginResponse.status_code == requests.codes.ok:
        print "成功进入教务系统！"
        error_code=""
        # 获取学生基本信息
        def getInfor(response):
            content = response.content.decode('gb2312')  # 网页源码是gb2312要先解码
            soup = BeautifulSoup(content.decode("utf-8"), "html.parser")
            html=soup.find(id="xhxm")
            try:
                for infor in html:
                    return infor.string
            except:
                print "验证码输入错误，请重新输入"

        try:
            text=getInfor(loginResponse)
            print text
            text = text.replace(" ", "")
            student.stuName = text[:10].replace("同学", "")
            print "姓名：" + student.stuName
        except:
            print "登陆失败，错误代码："+error_code
        student.stuNumber=stuNumber
        student.password=password
# 获取学生基本信息

def getStudentInfo():
    student.urlName = urllib.quote_plus(student.stuName.encode('gb2312'))
    print student.urlName
    session.headers['Referer'] = baseUrl + "/xs_main.aspx?xh=" + student.stuNumber
    url = baseUrl + "/xsgrxx.aspx?xh=" + student.stuNumber + "&xm="+student.urlName+"&gnmkdm=N121605"
    response = session.get(url)
    d = getStudentInfor(response)
    student.idCardNumber = d["idCardNumber"]
    student.sex = d["sex"]
    student.enterSchoolTime = d["enterSchoolTime"]
    student.birthday = d["birthsday"]
    student.highSchool = d["highschool"]
    student.nationality = d["nationality"]
    student.hometown = d["hometown"]
    student.politicsStatus = d["politicsStatus"]
    student.college = d["college"]
    student.major = d["major"]
    student.className = d["classname"]
    student.gradeClass = d["gradeClass"]

    student.save()
    print "读取学生基本信息成功"

# 获取学生成绩

def getStudentGrade():
    # 准备进入成绩查询页面
    url = baseUrl + "/xscj_gc.aspx?xh=" + student.stuNumber + "&xm=" + student.urlName + "&gnmkdm=N121605"
    session.headers['Referer'] = url
    response = session.get(url)
    viewState = get__VIEWSTATE(response)

    data = {
        "__VIEWSTATE": viewState,
        "ddlXN": "",
        "ddlXQ": "",
        # 在校学习成绩查询
        "Button2":"%D4%DA%D0%A3%D1%A7%CF%B0%B3%C9%BC%A8%B2%E9%D1%AF"
    }
    response = session.post(url, data=data)

    grades = getGrade(response)
    for onegrade in grades:
        year = onegrade["year"]
        term = onegrade["term"]
        try:
            yearGrade = YearGrade.get(YearGrade.year == year, YearGrade.student == student)
        except:
            yearGrade = YearGrade(year=year, student=student)
            yearGrade.save()
        try:
            termGrade = TermGrade.get(TermGrade.year == yearGrade, TermGrade.term == int(term))
        except:
            termGrade = TermGrade(year=yearGrade, term=int(term))
            termGrade.save()
        try:
            gradePoint = float(onegrade["gradePonit"])
        except:
            gradePoint = None
        oneLessonGrade = OneLessonGrade(term=termGrade, name=onegrade["name"], type=onegrade["type"],
                                        credit=float(onegrade["credit"]), gradePoint=gradePoint,
                                        grade=onegrade["grade"])
        oneLessonGrade.save()
    print "获取成绩成功"


# 这里获取的是专业推荐课表，因为我们学校个人课表一栏为空白QAQ
def getClassSchedule():
    session.headers['Referer'] = baseUrl + "/xs_main.aspx?xh=" + student.stuNumber
    url = baseUrl + "/tjkbcx.aspx?xh=" + student.stuNumber + "&xm=" + student.urlName + "&gnmkdm=N121605"
    response = session.get(url, allow_redirects=False)
    viewState = getClassScheduleFromHtml(response)["__VIEWSTATE"]
    content=getClassScheduleFromHtml(response)["content"]

    data = {
        "__VIEWSTATE": viewState,
    }

    classes = getClassFileName(student.stuNumber)
    # 课程表文件名
    oneClass = Class(filename=classes,content=content)
    oneClass.save()

    print "成功获取课表"


if __name__ == "__main__":

    # 连接数据库，建立数据表
    try:
        db.connect()
        db.create_tables([Student,Code, ClassSchedule,Class,YearGrade,TermGrade,OneLessonGrade])
    except:
        pass

    # 查找学生，若不存在则创建账号
    try:
        student = Student.get(Student.stuNumber == "你的学号")
    except Exception ,e:
        student = Student(stuNumber="你的学号", password="你的密码")#用自己的教务系统账号密码
        student.save()
        print e

    # 实例化爬虫
    login("你的学号","你的密码")
    getStudentInfo()
    getStudentGrade()
    getClassSchedule()



