#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  gebiqu.py
@Date    :  2022/02/10
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :  
"""

import re
from aigbook.book import BookImp

class GeBiqu(BookImp):
    def __init__(self) -> None:
        super().__init__()
        self.weburl = 'www.gebiqu.com'

    def search(self, title, author=None):
        url = f"https://www.gebiqu.com/modules/article/search.php?searchkey={title}"
        html = self._getHtml_(url)

        req_names = html.xpath('//*[@id="nr"]/td[1]/a/text()')
        req_authors = html.xpath('//*[@id="nr"]/td[3]/text()')
        req_urls = html.xpath('//*[@id="nr"]/td[2]/a/@href')

        array = []
        for index in range(len(req_authors)):
            itemName = req_names[index]
            itemAuthor = req_authors[index]
            itemUrl = re.sub(r'\d*.html$', '', str(req_urls[index]))

            if author is None or author == '' or author == itemAuthor:
                array.append({
                    'title': itemName,
                    'author': itemAuthor,
                    'url': itemUrl
                })
        return array

    def getBookInfo(self, url):
        html = self._getHtml_(url)
        
        bookName = html.xpath('//*[@id="info"]/h1/text()')[0]
        bookAuthor = html.xpath('//*[@id="info"]/p[1]/text()')[0].split('：')[1]
        bookImageUrl = html.xpath('//*[@id="fmimg"]/img/@src')[0]
        bookAbout = html.xpath('//*[@id="intro"]/p/text()')[0]
        bookNewChapterName = html.xpath('//*[@id="list"]/dl/dd[1]/a/text()')[0]
        bookChapterNameList = html.xpath('//*[@id="list"]/dl/dt[2]//following-sibling::*/a/text()')
        bookChapterUrlList = html.xpath('//*[@id="list"]/dl/dt[2]//following-sibling::*/a/@href')

        # 获取章节列表
        chapters = []
        for index in range(len(bookChapterNameList)):
            chapters.append({
                'name': bookChapterNameList[index],
                'url': "http://www.gebiqu.com" + bookChapterUrlList[index]
            })

        return {
            'title': bookName,
            'author': bookAuthor,
            'url': url,
            'image': bookImageUrl,
            'about': bookAbout,
            'new_chapter': bookNewChapterName,
            'chapters': chapters,
        }
