#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/12/7 16:02
# @Author  : Jonathon
# @File    : util.py
# @Software: PyCharm
# @ Motto : 客又至，当如何
import configparser
import sys
import pymysql
import pandas as pd
import datetime
import random
import time
import calendar

config = configparser.ConfigParser()
config.read("config.ini", encoding="utf-8")
host_port = int(config['db']['host_port'])
db_user = config['db']['db_user']
db_host = config['db']['db_host']
password = config['db']['password']
database = config['db']['database']


def time_dec(func):
    def wrapper(*args, **kwargs):
        st = time.time()
        res = func(*args, **kwargs)
        print(f'sql耗时:{time.time() - st}')

        return res

    return wrapper


class Db:
    def __init__(self, host, user, password, port, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port

        # 打开数据库连接
        self.db = pymysql.connect(host=self.host,
                                  user=self.user,
                                  password=self.password,
                                  port=self.port,
                                  database=self.database)

        # 使用 cursor() 方法创建一个游标对象 cursor
        self.cursor = self.db.cursor()

    @time_dec
    def exec_sql(self, string):
        # 使用 execute()  方法执行 SQL 查询,获取数据库版本
        self.cursor.execute(string)

        # 使用 fetchone() 方法获取单条数据.
        data = self.cursor.fetchall()

        return data

    def close(self):
        # 关闭不使用的游标对象
        self.cursor.close()
        # 关闭数据库连接
        self.db.close()


def genarate_temp():
    l_h = sorted(random.sample([i for i in range(5, 40)], 2))
    avg = sum(l_h) / 2
    l_h.append(avg)
    return l_h


def get_days(year, mon):
    year = int(year)
    mon = int(mon)
    return calendar.monthrange(year, mon)[1]


cur = Db(db_host, db_user, password, host_port, database)
if __name__ == '__main__':
    pass
    # cur = Db(db_host, db_user, password, host_port, database)
    #  全表查询更慢 但是间隔查询快一点
    # cur.exec_sql('select *from sum_table ;')
    # cur.exec_sql(
    #     """select air_time,low,high from 2019_y where air_time between  '2019-01-01 23:59:00' and  '2019-12-31 23:59:00';""")
    # cur.exec_sql("select low,high from sum_table where air_time like '2019%';")

    # cur.exec_sql("select * from sum_table where air_time like '2019%';")
