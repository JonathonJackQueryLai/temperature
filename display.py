#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2023/1/10 14:04
# @Author  : Jonathon
# @File    : pages.py
# @Software: PyCharm
# @ Motto : 客又至，当如何


'''
多窗口反复切换布局
'''
from PyQt5 import QtChart, QtCore
from PyQt5.QtChart import QLineSeries, QChartView, QValueAxis, QSplineSeries
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from atom_core.temperature.q_line import Temp_line
from util import cur
from PyQt5.QtWidgets import QHeaderView


class TableWidget(QWidget):
    control_signal = pyqtSignal(list)

    def __init__(self, *args, **kwargs):
        super(TableWidget, self).__init__(*args, **kwargs)
        self.__init_ui()

    def __init_ui(self):
        style_sheet = """
            QTableWidget {
                border: none;
                background-color:rgb(240,240,240)
            }
            QPushButton{
                max-width: 300ex;
                max-height: 100ex;
                font-size: 25px;
            }
            QLineEdit{
                max-width: 30px;
                font-size: 25px;
            }
            QLabel,Q{
                font-size: 25px;    
            }
        """
        self.row_name = ['low', 'high', 'mean', 'time', 'mon']
        self.table = QTableWidget(10, 5)  # 10 行 5 列的表格
        self.table.setHorizontalHeaderLabels(self.row_name)
        self.table.resize(1200, 800)
        self.table.verticalHeader().setDefaultSectionSize(80)
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive | QHeaderView.Stretch)  # 自适应宽度
        self.__layout = QVBoxLayout()
        self.__layout.addWidget(self.table)
        self.setLayout(self.__layout)
        self.setStyleSheet(style_sheet)

    def setPageController(self, page):
        """自定义页码控制器"""
        control_layout = QHBoxLayout()
        homePage = QPushButton("首页")
        prePage = QPushButton("<上一页")
        self.curPage = QLabel("1")
        nextPage = QPushButton("下一页>")
        finalPage = QPushButton("尾页")

        self.totalPage = QLabel("共" + str(page) + "页")
        skipLable_0 = QLabel("跳到")
        self.skipPage = QLineEdit()
        skipLabel_1 = QLabel("页")
        confirmSkip = QPushButton("确定")
        homePage.clicked.connect(self.__home_page)
        prePage.clicked.connect(self.__pre_page)
        nextPage.clicked.connect(self.__next_page)
        finalPage.clicked.connect(self.__final_page)
        confirmSkip.clicked.connect(self.__confirm_skip)
        control_layout.addStretch(1)
        control_layout.addWidget(homePage)
        control_layout.addWidget(prePage)
        control_layout.addWidget(self.curPage)
        control_layout.addWidget(nextPage)
        control_layout.addWidget(finalPage)
        control_layout.addWidget(self.totalPage)
        control_layout.addWidget(skipLable_0)
        control_layout.addWidget(self.skipPage)
        control_layout.addWidget(skipLabel_1)
        control_layout.addWidget(confirmSkip)
        control_layout.addStretch(1)

        self.__layout.addLayout(control_layout)

    def __home_page(self):
        """点击首页信号"""
        self.control_signal.emit(["home", self.curPage.text()])

    def __pre_page(self):
        """点击上一页信号"""
        self.control_signal.emit(["pre", self.curPage.text()])

    def __next_page(self):
        """点击下一页信号"""
        self.control_signal.emit(["next", self.curPage.text()])

    def __final_page(self):
        """尾页点击信号"""
        self.control_signal.emit(["final", self.curPage.text()])

    def __confirm_skip(self):
        """跳转页码确定"""
        self.control_signal.emit(["confirm", self.skipPage.text()])
        self.skipPage.clear()

    def showTotalPage(self):
        """返回当前总页数"""
        return int(self.totalPage.text()[1:-1])


class Temperature(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        hbox = QHBoxLayout(self)
        left = QFrame(self)

        # QFrame 控件添加StyledPanel样式能使QFrame 控件之间的界限更加明显
        left.setFrameShape(QFrame.StyledPanel)

        right = QFrame(self)
        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(left)
        splitter1.setSizes([20, ])  # 设置分隔条位置
        splitter1.addWidget(right)
        hbox.addWidget(splitter1)
        self.setLayout(hbox)

        # 树
        self.tree = QTreeWidget(left)
        self.tree.setStyleSheet("background-color:#eeeeee;border:outset;color:#215b63;font:20px")
        self.tree.setAutoScroll(True)
        self.tree.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed)
        self.tree.setTextElideMode(Qt.ElideMiddle)
        # self.tree.setIndentation(30)
        self.tree.setRootIsDecorated(True)
        self.tree.setUniformRowHeights(False)
        self.tree.setItemsExpandable(True)
        self.tree.setAnimated(False)
        self.tree.setHeaderHidden(True)
        self.tree.setExpandsOnDoubleClick(True)
        self.tree.setObjectName("tree")

        # 设置根节点
        root = QTreeWidgetItem(self.tree)

        root.setText(0, '系统管理')

        # 设置树形控件的列的宽度
        # self.tree.setColumnWidth(0, 150)
        # 设置子节点1
        child1 = QTreeWidgetItem()
        child1.setText(0, '列表')
        root.addChild(child1)
        # 设置子节点2
        child2 = QTreeWidgetItem(root)
        child2.setText(0, '趋势线图')
        # 加载根节点的所有属性与子控件
        self.tree.addTopLevelItem(root)
        # 设置stackedWidget
        self.stackedWidget = QStackedWidget(right)
        self.stackedWidget.resize(1300, 900)
        # 设置第一个面板

        self.table_widget = TableWidget()  # 实例化表格

        page = cur.exec_sql('select count(1) from sum_table; ')
        self.table_widget.setPageController(page[0][0] // 10)  # 表格设置页码控制
        self.table_widget.control_signal.connect(self.page_controller)

        # 表示从第几条索引开始，计算方式 （当前页-1）*每页显示条数
        res = cur.exec_sql('select low,high,mean,air_time,mon from sum_table limit 10;')

        for i in range(10):
            for j in range(5):
                self.table_widget.table.setItem(i, j, QTableWidgetItem(str(res[i][j])))
        # self.setCentralWidget(self.table_widget)
        # self.table_widget = QWidget()
        # self.formLayout1 = Q(self.table_widget)
        # self.label1.setText(列表"展示")
        # self.label1.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        # self.label1.setAlignment(Qt.AlignCenter)
        # self.label1.setFont(QFont("Roman times", 50, QFont.Bold))
        # self.formLayout1.addWidget(self.label1)

        # 设置第二个面板
        self.line_view = Temp_line()

        # 将两个面板，加入stackedWidget
        self.stackedWidget.addWidget(self.table_widget)
        self.stackedWidget.addWidget(self.line_view)

        # 树节点监听事件
        self.tree.clicked.connect(self.onClicked)

        # 窗口最大化
        self.resize(1500, 900)
        self.setWindowTitle('三年气温变化')
        self.show()

    # 分页控制
    def page_controller(self, signal):
        total_page = self.table_widget.showTotalPage()
        if "home" == signal[0]:
            self.table_widget.curPage.setText("1")
            curr_page = 1

        elif "pre" == signal[0]:
            if 1 == int(signal[1]):
                QMessageBox.information(self, "提示", "已经是第一页了", QMessageBox.Yes)

                return
            curr_page = str(int(signal[1]) - 1)
            self.table_widget.curPage.setText(curr_page)

        elif "next" == signal[0]:
            if total_page == int(signal[1]):
                QMessageBox.information(self, "提示", "已经是最后一页了", QMessageBox.Yes)

                return
            curr_page = str(int(signal[1]) + 1)
            self.table_widget.curPage.setText(curr_page)
        elif "final" == signal[0]:
            self.table_widget.curPage.setText(str(total_page))
            curr_page = total_page
        elif "confirm" == signal[0]:
            if not signal[1]:
                return
            if total_page < int(signal[1]) or int(signal[1]) < 0:
                QMessageBox.information(self, "提示", "跳转页码超出范围", QMessageBox.Yes)
                return
            self.table_widget.curPage.setText(signal[1])
            curr_page = signal[1]
        self.changeTableContent(curr_page)  # 改变表格内容

    def changeTableContent(self, curr_page):
        """根据当前页改变表格的内容"""

        res = cur.exec_sql(
            f'select low, high, mean, air_time, mon from sum_table limit {(int(curr_page) - 1) * 10} ,10;')

        for i in range(10):
            for j in range(5):
                self.table_widget.table.setItem(i, j, QTableWidgetItem(str(res[i][j])))

    def onClicked(self):
        item = self.tree.currentItem()
        if item.text(0) == '列表':
            self.on_pushButton1_clicked()
        elif item.text(0) == '趋势线图':
            self.on_pushButton2_clicked()
        else:
            print('返回主界面')

    # 按钮一：打开第一个面板
    def on_pushButton1_clicked(self):
        self.stackedWidget.setCurrentIndex(0)

    # 按钮二：打开第二个面板
    def on_pushButton2_clicked(self):
        self.stackedWidget.setCurrentIndex(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # print(sys.argv)
    ex = Temperature()
    sys.exit(app.exec_())
