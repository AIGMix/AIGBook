#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  __init__.py
@Date    :  2022/02/15
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :  
"""

import prettytable
import sys
import os
import aigbook.book
import aigbook
import aigpy
from aigbook.gebiqu import GeBiqu
from aigbook.zw81 import Zw81


def getBookFroms():
    return ['gebiqu', 'zw81']    
    

def getBookHandle(sfrom: str):
    if sfrom == 'gebiqu':
        return GeBiqu()
    elif sfrom == 'zw81':
        return Zw81()
    return None


def getTable(columns, rows):
    tb = prettytable.PrettyTable()
    tb.field_names = list(aigpy.cmd.green(item) for item in columns)
    tb.align = 'l'
    for item in rows:
        tb.add_row(item)
    return tb


def main():
    if len(sys.argv) < 2:
        aigpy.cmd.printErr("请输入待搜索的名称！")
        return

    tool = aigbook.getBookHandle('gebiqu')
    books = tool.search(sys.argv[1])
    if len(books) <= 0:
        aigpy.cmd.printErr("搜索不到任何结果！")
        return

    tb = getTable(["序号", "标题", "作者"], list([index, item['title'], item['author']] for index, item in enumerate(books)))
    print(tb)

    index = aigpy.cmd.inputInt(aigpy.cmd.green("请输入下载的序号："), 0)
    if index < 0 or index >= len(books):
        aigpy.cmd.printErr("序号有误！")
        return

    info = tool.getBookInfo(books[index]['url'])
    tool.downloadChapters(info)
    ret = tool.combineBook(info)

    aigpy.cmd.printSuccess(os.path.abspath(ret))


if __name__ == '__main__':
    main()
