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

import re
import os
import abc
import aigpy
import requests
import lxml.etree
from requests.adapters import HTTPAdapter


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
                print("Err: _getHtml_ failed." + str(e))
        return None

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
        if html is None:
            return None

        lines = html.xpath('//div[@id="content"]/text()')
        for index, content in enumerate(lines):
            content = content.replace(u'\x20', u'\n')
            content = content.replace(u'\xa0', u'')
            content = content.replace(u'\u3000', ' ')
            lines[index] = content
            
        content = '\n'.join(lines)
        return content
        
        
    def _formatFolder_(self, folder: str):
        return aigpy.path.replaceLimitChar(folder, '-')

    def _formatChapterFolderPath_(self, bookInfo, format: str = './download/{author}/{title}/chapters') -> str:
        path = format
        path = path.replace('{author}', self._formatFolder_(bookInfo['author']))
        path = path.replace('{title}', self._formatFolder_(bookInfo['title']))
        return path


    def _formatChapterFileName_(self, name: str):
        name = aigpy.path.replaceLimitChar(name, '-')
        # name = re.sub("(第[\u4e00-\u9fa5\u767e\u5343\u96f6]{1,10}章)|(第[0-9]{1,10}章)", "", name)
        return name


    def _formatBookFilePath_(self, bookInfo, format: str = './download/{author}/{title}.txt'):
        path = format
        path = path.replace('{author}', self._formatFolder_(bookInfo['author']))
        path = path.replace('{title}', self._formatFolder_(bookInfo['title']))
        return path


    def _existChapterSum_(self, path: str):
        folder = os.path.exists(path)
        if not folder:
            os.makedirs(path)
            return 0
        return len(os.listdir(path))


    def downloadChapters(self, bookInfo):
        title = bookInfo['title']
        author = bookInfo['author']

        # 保存目录
        path = self._formatChapterFolderPath_(bookInfo)
        if not aigpy.path.mkdirs(path):
            return False

        # 获取目录内最新章节
        existSum = self._existChapterSum_(path)
        startIndex = (existSum - 1) if existSum > 0 else 0

        print(f'====Download [{title}] chapters from {startIndex} to {len(bookInfo["chapters"])}')

        for index, item in enumerate(bookInfo['chapters']):
            if index < startIndex:
                continue
            content = self.getChaptersContent(item['url'])
            if content is None:
                print(f'== ERR {index + 1}/{len(bookInfo["chapters"])} {item["name"]}')
                return False

            itemPath = f"{path}/{index}_{self._formatChapterFileName_(item['name'])}"
            file = open(itemPath, 'w', encoding="utf-8")
            file.write(content)
            file.close()

            print(f'== SUCCESS {index + 1}/{len(bookInfo["chapters"])} {item["name"]}')
        return True


    def combineBook(self, bookInfo):
        chapterPath = self._formatChapterFolderPath_(bookInfo)
        if not os.path.exists(chapterPath):
            return ''

        array = os.listdir(chapterPath)
        if len(array) <= 0:
            return False

        bookPath = self._formatBookFilePath_(bookInfo)
        file = open(bookPath, 'w', encoding="utf-8")
        for item in array:
            lines = aigpy.file.getLines(chapterPath + '/' + item, encoding="utf-8")
            file.writelines(lines)
            file.writelines("\n")
        file.close()

        return bookPath
