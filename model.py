# coding=utf-8

from peewee import *

db = SqliteDatabase('ZhengFang.db')


class Student(Model):
    stuName = CharField(null=True)  # 姓名
    urlName = CharField(null=True)  # url编码后的姓名
    stuNumber = CharField(null=True)  # 学号
    password = CharField(null=True)  # 教务系统密码
    idCardNumber = CharField(null=True)  # 身份证号
    sex = CharField(null=True)  # 性别
    enterSchoolTime = CharField(null=True)  # 入学时间
    birthday = CharField(null=True)  # 出生日期
    highSchool = CharField(null=True)  # 毕业中学
    nationality = CharField(null=True)  # 民族
    hometown = CharField(null=True)  # 籍贯
    politicsStatus = CharField(null=True)  # 政治面貌
    college = CharField(null=True)  # 学院
    major = CharField(null=True)  # 专业
    className = CharField(null=True)  # 所在班级
    gradeClass = CharField(null=True)  # 年级

    class Meta:
        database = db

class Code(Model):
    # 验证码
    identifying_code =CharField(null=True)
    # 验证码错误代码
    identifying_code_error=CharField(null=True)


    class Meta:
        database = db

class ClassSchedule(Model):
    student = ForeignKeyField(Student, related_name="classSchedule")  # 学生
    year = CharField(null=True)  # 年度
    term = IntegerField(null=True)  # 学期

    class Meta:
        database = db



class Class(Model):
    filename = CharField(null=True)
    content=CharField(null=True)

    class Meta:
        database = db

# 按学年查询
class YearGrade(Model):
    student = ForeignKeyField(Student, related_name="grades")  # 归属学生
    year = CharField(null=True) # 学年
    yearGPA = DoubleField(null=True)  # 学年GPA
    yearCredit = DoubleField(null=True)  # 学年总学分

    class Meta:
        database = db

# 按学期查询
class TermGrade(Model):
    year = ForeignKeyField(YearGrade,related_name="terms")  # 归属学年
    term = IntegerField(null=True) # 学期
    termGPA = DoubleField(null=True) # 学期GPA
    termCredit = DoubleField(null=True) #学期总学分

    class Meta:
        database = db


# 查询单个课程
class OneLessonGrade(Model):
    term = ForeignKeyField(TermGrade, related_name="lessonsGrades")  # 归属学期
    name = CharField(null=True)  # 课程名
    type = CharField(null=True)  # 课程性质
    credit = DoubleField(null=True)  # 学分
    gradePoint = DoubleField(null=True)  # 绩点
    grade = CharField(null=True)  # 成绩

    class Meta:
        database = db