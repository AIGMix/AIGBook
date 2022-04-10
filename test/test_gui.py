#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  test.py
@Date    :  2022/03/28
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :  
"""
import os
import sys
import json
import aigbook
import _thread

from PyQt5.QtCore import Qt
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtWidgets
from qt_material import apply_stylesheet

os.chdir(sys.path[0])

SOURCE = 'gebiqu'
with open('./config.json', 'r') as fd:
    config = json.load(fd)
    aigbook.book.CHAPTER_FOLDER_PATH = config['chapter_folder_path']
    aigbook.book.BOOK_FILE_PATH = config['book_file_path']
    SOURCE = config['source']

class MainView(QtWidgets.QWidget):
    s_downloadEnd = pyqtSignal(str, bool, str)

    def __init__(self, ) -> None:
        super().__init__()
        self.initView()
        self.setMinimumSize(600, 500)
        self.setWindowTitle("AIGBook")
        
    def initView(self):
        self.c_lineSearch = QtWidgets.QLineEdit()
        self.c_btnSearch = QtWidgets.QPushButton("搜索")
        self.c_btnDownload = QtWidgets.QPushButton("下载")
        
        columnNames = ['#', '标题', '作者', '链接']
        self.c_tableInfo = QtWidgets.QTableWidget()
        self.c_tableInfo.setColumnCount(len(columnNames))
        self.c_tableInfo.setRowCount(0)
        self.c_tableInfo.setShowGrid(False)
        self.c_tableInfo.verticalHeader().setVisible(False)
        self.c_tableInfo.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.c_tableInfo.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.c_tableInfo.horizontalHeader().setStretchLastSection(True)
        self.c_tableInfo.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.c_tableInfo.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.c_tableInfo.setFocusPolicy(Qt.NoFocus)
        for index, name in enumerate(columnNames):
            item = QtWidgets.QTableWidgetItem(name)
            self.c_tableInfo.setHorizontalHeaderItem(index, item)
            
        self.lineGrid = QtWidgets.QHBoxLayout()
        self.lineGrid.addWidget(self.c_lineSearch)
        self.lineGrid.addWidget(self.c_btnSearch)
        
        self.mainGrid = QtWidgets.QVBoxLayout(self)
        self.mainGrid.addLayout(self.lineGrid)
        self.mainGrid.addWidget(self.c_tableInfo)
        self.mainGrid.addWidget(self.c_btnDownload)
        
        self.c_btnSearch.clicked.connect(self.search)
        self.c_btnDownload.clicked.connect(self.download)
        self.s_downloadEnd.connect(self.downloadEnd)

    def addItem(self, rowIdx: int, colIdx: int, text):
        if isinstance(text, str):
            item = QtWidgets.QTableWidgetItem(text)
            self.c_tableInfo.setItem(rowIdx, colIdx, item)
    
    def search(self):
        text = self.c_lineSearch.text()
        handle = aigbook.getBookHandle(SOURCE)
        array = handle.search(text)
        
        if len(array) <= 0:
            QtWidgets.QMessageBox.information(self, '提示', '没有结果！', QtWidgets.QMessageBox.Yes)
            return
        
        self.c_tableInfo.setRowCount(len(array))
        for index, item in enumerate(array):
            self.addItem(index, 0, str(index + 1))
            self.addItem(index, 1, item['title'])
            self.addItem(index, 2, item['author'])
            self.addItem(index, 3, item['url'])
    
    def download(self):
        index = self.c_tableInfo.currentIndex().row()
        if index < 0:
            QtWidgets.QMessageBox.information(self, '提示', '请先选中一行', QtWidgets.QMessageBox.Yes)
            return
        
        title = self.c_tableInfo.item(index, 1).text()
        url = self.c_tableInfo.item(index, 3).text()

        self.c_btnDownload.setEnabled(False)
        self.c_btnDownload.setText(f"下载[{title}]中...")
        
        def __thread_download__(model: MainView, title: str, url: str):
            try:
                handle = aigbook.getBookHandle(SOURCE)
                info = handle.getBookInfo(url)
                handle.downloadChapters(info)
                ret = handle.combineBook(info)
                model.s_downloadEnd.emit(info['title'], True, ret)
            except Exception as e:
                model.s_downloadEnd.emit(info['title'], False, f"下载失败：{str(e)}")

        _thread.start_new_thread(__thread_download__, (self, title, url))
    
    def downloadEnd(self, title, result, msg):
        self.c_btnDownload.setEnabled(True)
        self.c_btnDownload.setText(f"下载")
        
        if result:        
            QtWidgets.QMessageBox.information(self, '提示', f'下载[{title}]完成。', QtWidgets.QMessageBox.Yes)
        else:
            QtWidgets.QMessageBox.warning(self, '提示', f'下载[{title}]失败：{msg}', QtWidgets.QMessageBox.Yes)
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    apply_stylesheet(app, theme='dark_blue.xml')

    window = MainView()
    window.show()

    app.exec_()
