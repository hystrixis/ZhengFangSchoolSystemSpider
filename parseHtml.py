# coding=utf-8
import os

from bs4 import BeautifulSoup



# 从网页中解析学生信息
def getStudentInfor(response):
    html = response.content.decode("gb2312")
    soup = BeautifulSoup(html.decode("utf-8"), "html.parser")
    d = {}
    d["studentnumber"] = soup.find(id="xh").string
    d["idCardNumber"] = soup.find(id="lbl_sfzh").string
    d["name"] = soup.find(id="xm").string
    d["sex"] = soup.find(id="lbl_xb").string
    d["enterSchoolTime"] = soup.find(id="lbl_rxrq").string
    d["birthsday"] = soup.find(id="lbl_csrq").string
    d["highschool"] = soup.find(id="lbl_byzx").string
    d["nationality"] = soup.find(id="lbl_mz").string
    d["hometown"] = soup.find(id="lbl_jg").string
    d["politicsStatus"] = soup.find(id="lbl_zzmm").string
    d["college"] = soup.find(id="lbl_xy").string
    d["major"] = soup.find(id="lbl_zymc").string
    d["classname"] = soup.find(id="lbl_xzb").string
    d["gradeClass"] = soup.find(id="lbl_dqszj").string
    return d


# 从网页中解析课表信息
def getClassScheduleFromHtml(response):
    html = response.content.decode("gb2312","ignore")
    soup = BeautifulSoup(html.decode("utf-8"), "html.parser")
    __VIEWSTATE = soup.find('input',{'name':'__VIEWSTATE'}).get('value')
    #
    trs = soup.find(id='Table6')

    def save_text():
        with open(os.getcwd() + "\\" +"table.xls", 'w')as f:
            f.write(str(trs))
    save_text()


    return {"__VIEWSTATE": __VIEWSTATE,"content":trs}

def getClassFileName(stuNumber):
    classes = stuNumber+"text.xls"
    return classes

def get__VIEWSTATE(response):
    html = response.content.decode("gb2312")
    soup = BeautifulSoup(html.decode("utf-8"), "html.parser")
    viewState=soup.find('input',{'name':'__VIEWSTATE'}).get('value')
    print viewState
    return viewState


def getGrade(response):
    html = response.content.decode("gb2312")
    soup = BeautifulSoup(html.decode("utf-8"), "html.parser")
    trs = soup.find(id="Datagrid1").findAll("tr")[1:]
    Grades = []
    for tr in trs:
        tds = tr.findAll("td")
        tds = tds[:2] + tds[3:5] + tds[6:9]
        oneGradeKeys = ["year", "term", "name", "type", "credit","gradePonit","grade"]
        oneGradeValues = []
        for td in tds:
            oneGradeValues.append(td.string)
        oneGrade = dict((key, value) for key, value in zip(oneGradeKeys, oneGradeValues))
        Grades.append(oneGrade)
    return Grades

