#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  book.py
@Date    :  2022/02/10
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :  
"""

import os
import abc
import requests
import lxml.etree
import zipfile
from requests.adapters import HTTPAdapter
from concurrent.futures import ThreadPoolExecutor


CHAPTER_FOLDER_PATH = './download/{author}/{title}/chapters'
BOOK_FILE_PATH = './download/{author}/{title}.txt'


class BookImp(metaclass=abc.ABCMeta):
    def __init__(self):
        self.weburl = ''
        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=3))
        self.session.mount('https://', HTTPAdapter(max_retries=3))

    def _getHtml_(self, url):
        retry = 3
        while retry > 0:
            try:
                content = self.session.get(url, timeout=(5, 10)).content.decode('utf-8')
                html = lxml.etree.HTML(content)
                return html
            except requests.exceptions.RequestException as e:
                retry -= 1
                if retry <= 0:
                    print("Err: _getHtml_ failed." + str(e))
                    raise e

    @abc.abstractmethod
    def search(self, title, author=None) -> list:
        """搜索

        Args:
            title (str): 标题
            author (str): 作者

        Returns:
            list: [{
                    'title': 标题,
                    'author': 作者,
                    'url': 链接
                }]
        """
        pass

    @abc.abstractmethod
    def getBookInfo(self, url) -> dict:
        """获取书籍信息

        Args:
            url (str): 书籍url

        Returns:
            dict: {
                'title': 标题,
                'author': 作者,
                'url': 链接,
                'image': 封面,
                'about': 介绍,
                'new_chapter': 最新章节名,
                'chapters': [{
                    'name': 章节名称,
                    'url': 章节链接
                    }],
                }
        """
        pass

    def getChaptersContent(self, url: str) -> str:
        """获取章节内容

        Args:
            url (str): 章节链接

        Returns:
            str: 章节内容
        """
        html = self._getHtml_(url)

        lines = html.xpath('//div[@id="content"]/text()')
        for index, content in enumerate(lines):
            content = content.replace(u'\x20', u'\n')
            content = content.replace(u'\xa0', u'')
            content = content.replace(u'\u3000', ' ')
            lines[index] = content

        content = '\n'.join(lines)
        return content

    def _removePathLimitChar_(self, path: str):
        """去除目录的限制符号"""
        newChar = '-'
        path = path.replace(':', newChar)
        path = path.replace('/', newChar)
        path = path.replace('?', newChar)
        path = path.replace('<', newChar)
        path = path.replace('>', newChar)
        path = path.replace('|', newChar)
        path = path.replace('\\', newChar)
        path = path.replace('*', newChar)
        path = path.replace('\"', newChar)
        path = path.replace('\n', '')
        path = path.replace('\t', '')
        path = path.rstrip('.')
        path = path.strip(' ')
        return path

    def _formatPath_(self, bookInfo, format: str) -> str:
        """格式目录"""
        path = format
        path = path.replace('{author}', self._removePathLimitChar_(bookInfo['author']))
        path = path.replace('{title}', self._removePathLimitChar_(bookInfo['title']))
        path = path.replace('{weburl}', self._removePathLimitChar_(self.weburl))
        return path

    def _existChapterSum_(self, path: str):
        """获取目录下有多少章节文件"""
        folder = os.path.exists(path)
        if not folder:
            os.makedirs(path)
            return 0
        return len(os.listdir(path))

    def mkdirs(self, path: str):
        path = path.replace("\\", "/")
        path = path.strip()
        path = path.rstrip("/")
        if not os.path.exists(path):
            os.makedirs(path)

    def downloadChapters(self, bookInfo):
        """下载章节"""
        title = bookInfo['title']
        author = bookInfo['author']

        # 保存目录
        path = self._formatPath_(bookInfo, CHAPTER_FOLDER_PATH)
        self.mkdirs(path)

        # 获取章节链接+路径集合
        todoLists = []
        for index, item in enumerate(bookInfo['chapters']):
            itemUrl = item['url']
            itemPath = f"{path}/{str(index).rjust(4, '0')}_{self._removePathLimitChar_(item['name'])}"
            todoLists.append([itemUrl, itemPath, item['name']])
        
        # 获取目录内最新章节
        existSum = self._existChapterSum_(path)
        startIndex = existSum if existSum > 0 else 0
        
        # 下载章节
        print(f'====Download [{title}] chapters from {startIndex} to {len(bookInfo["chapters"])}')
        
        def __thread_download__(url, path, name):
            file = open(path, 'w', encoding="utf-8")
            file.write(self.getChaptersContent(url))
            file.close()
            print(f'== SUCCESS: {name} ==')
        
        theard_pool = ThreadPoolExecutor(max_workers=10)
        for index, item in enumerate(todoLists):
            if index < startIndex:
                continue
            theard_pool.submit(__thread_download__, item[0], item[1], item[2])
        theard_pool.shutdown(wait=True)
        

    def combineBook(self, bookInfo, isZip=False) -> str:
        """合并书籍文件"""
        chapterPath = self._formatPath_(bookInfo, CHAPTER_FOLDER_PATH)
        array = os.listdir(chapterPath)
        if len(array) <= 0:
            raise Exception('章节目录不存在，请先下载章节文件')

        bookPath = self._formatPath_(bookInfo, BOOK_FILE_PATH)
        file = open(bookPath, 'w', encoding="utf-8")
        for item in array:
            itemName = item.split('_')[1]
            with open(chapterPath + '/' + item, 'r', encoding="utf-8") as fd:
                itemLines = fd.readlines()
                file.write(itemName + '\n')
                file.writelines('　　' + x + '\n' for x in itemLines)
                file.writelines("\n\n")
        file.close()

        if not isZip:
            return bookPath

        zipHandle = zipfile.ZipFile(bookPath + '.zip', 'w')
        zipHandle.write(bookPath, compress_type=zipfile.ZIP_DEFLATED)
        zipHandle.close()
        return bookPath + '.zip'
