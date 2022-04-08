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

import aigbook
import aigbook.book
import json
import os
import sys

os.chdir(sys.path[0])

HANDLE = None
with open('./config.json', 'r') as fd:
    config = json.load(fd)
    aigbook.book.CHAPTER_FOLDER_PATH = config['chapter_folder_path']
    aigbook.book.BOOK_FILE_PATH = config['book_file_path']
    HANDLE = aigbook.getBookHandle(config['source'])

if __name__ == '__main__':
    array = HANDLE.search('某霍格沃茨的魔文教授')
    if len(array) <= 0:
        print("Err: no search result.")
    else:
        info = HANDLE.getBookInfo(array[0]['url'])
        HANDLE.downloadChapters(info)
        HANDLE.combineBook(info)
