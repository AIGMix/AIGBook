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

aigbook.book.CHAPTER_FOLDER_PATH = '/www/wwwroot/alist.yaronzz.com/books/{weburl}/{author}/{title}/chapters'
aigbook.book.BOOK_FILE_PATH = '/www/wwwroot/alist.yaronzz.com/books/{weburl}/{author}/{title}.txt'

if __name__ == '__main__':
    obj = aigbook.getBookHandle('gebiqu')
    array = obj.search('某霍格沃茨的魔文教授')
    if len(array) <= 0:
        print("Err: no search result.")
    else:
        info = obj.getBookInfo(array[0]['url'])
        obj.downloadChapters(info)
        obj.combineBook(info)
