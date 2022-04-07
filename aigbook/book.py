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
import aigpy
import requests
import lxml.etree
import zipfile
from requests.adapters import HTTPAdapter


CHAPTER_FOLDER_PATH = './download/{author}/{title}/chapters'
BOOK_FILE_PATH = './download/{author}/{title}.txt'


class BookImp(metaclass=abc.ABCMeta):
    def __init__(self):
        self.weburl = ''
        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=3))
        self.session.mount('https://', HTTPAdapter(max_retries=3))
        self.progress = None

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
                    raise e

    @abc.abstractmethod
    def search(self, title, author=None) -> dict:
        """搜索

        Args:
            title (str): 标题
            author (str): 作者

        Returns:
            dict: {
                    'title': 标题,
                    'author': 作者,
                    'url': 链接
                }
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
                'chapters': {
                    'name': 章节名称,
                    'url': 章节链接
            },
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

    def _formatFolder_(self, folder: str):
        """去除目录的限制符号"""
        return aigpy.path.replaceLimitChar(folder, '-')

    def _formatChapterFolderPath_(self, bookInfo, format: str = CHAPTER_FOLDER_PATH) -> str:
        """格式化章节目录"""
        path = format
        path = path.replace('{author}', self._formatFolder_(bookInfo['author']))
        path = path.replace('{title}', self._formatFolder_(bookInfo['title']))
        path = path.replace('{weburl}', self._formatFolder_(self.weburl))
        return path

    def _formatBookFilePath_(self, bookInfo, format: str = BOOK_FILE_PATH):
        """格式化书籍文件路径"""
        path = format
        path = path.replace('{author}', self._formatFolder_(bookInfo['author']))
        path = path.replace('{title}', self._formatFolder_(bookInfo['title']))
        path = path.replace('{weburl}', self._formatFolder_(self.weburl))
        return path

    def _existChapterSum_(self, path: str):
        """获取目录下有多少章节文件"""
        folder = os.path.exists(path)
        if not folder:
            os.makedirs(path)
            return 0
        return len(os.listdir(path))

    def _printProgress(self, sum, index, msg):
        print(msg)
        if self.progress is not None:
            self.progress(sum, index, msg)

    def downloadChapters(self, bookInfo):
        """下载章节"""
        title = bookInfo['title']
        author = bookInfo['author']

        # 保存目录
        path = self._formatChapterFolderPath_(bookInfo, CHAPTER_FOLDER_PATH)
        if not aigpy.path.mkdirs(path):
            return False

        # 获取目录内最新章节
        downloadSum = len(bookInfo['chapters'])
        existSum = self._existChapterSum_(path)
        startIndex = existSum if existSum > 0 else 0

        self._printProgress(startIndex, 
                            downloadSum,
                            f'====Download [{title}] chapters from {startIndex} to {len(bookInfo["chapters"])}')

        for index, item in enumerate(bookInfo['chapters']):
            if index < startIndex:
                continue
            content = self.getChaptersContent(item['url'])
            itemPath = f"{path}/{str(index).rjust(4, '0')}_{self._formatFolder_(item['name'])}"
            file = open(itemPath, 'w', encoding="utf-8")
            file.write(content)
            file.close()

            self._printProgress(index + 1,
                                downloadSum,
                                f'== SUCCESS {index + 1}/{len(bookInfo["chapters"])} {item["name"]}')
        return True

    def combineBook(self, bookInfo, isZip=False):
        """合并书籍文件"""
        chapterPath = self._formatChapterFolderPath_(bookInfo, CHAPTER_FOLDER_PATH)
        if not os.path.exists(chapterPath):
            return ''

        array = os.listdir(chapterPath)
        if len(array) <= 0:
            return ''

        bookPath = self._formatBookFilePath_(bookInfo, BOOK_FILE_PATH)
        file = open(bookPath, 'w', encoding="utf-8")
        for item in array:
            itemName = item.split('_')[1]
            itemLines = aigpy.file.getLines(chapterPath + '/' + item, encoding="utf-8")
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

    def setProgressFunc(self, func):
        """设置进度回调

        Args:
            func (_type_): xxx(sum, index, msg)
        """
        self.progress = func
