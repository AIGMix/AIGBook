#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :  81zw.py
@Date    :  2022/02/14
@Author  :  Yaronzz
@Version :  1.0
@Contact :  yaronhuang@foxmail.com
@Desc    :  
"""
from aigbook.book import BookImp

class Zw81(BookImp):
    def __init__(self) -> None:
        super().__init__()
        self.weburl = 'www.81zw.com'

    def search(self, title, author=None):
        url = f"https://www.81zw.com/search.php?q={title}"
        html= self._getHtml_(url)
        
        # 解析请求对比返回是否一致
        req_names = html.xpath('/html/body/div[3]/div/div[2]/h3/a/span/text()')
        req_authors = html.xpath('/html/body/div[3]/div/div[2]/div/p[1]/span[2]/text()')
        req_urls = html.xpath('/html/body/div[3]/div/div[2]/h3/a/@href')

        array = []
        for index in range(len(req_authors)):
            itemName = req_names[index]
            itemAuthor = req_authors[index]
            itemUrl = 'https://www.81zw.com' + req_urls[index]

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
        bookAbout = html.xpath('//*[@id="intro"]/text()')[0]
        bookNewChapterName = html.xpath('//*[@id="info"]/p[4]/a/text()')[0]
        bookChapterNameList = html.xpath('//*[@id="list"]/dl/dt[1]//following-sibling::*/a/text()')
        bookChapterUrlList = html.xpath('//*[@id="list"]/dl/dt[1]//following-sibling::*/a/@href')

        # 获取章节列表
        chapters = []
        for index in range(len(bookChapterNameList)):
            chapters.append({
                'name': bookChapterNameList[index],
                'url': "http://www.81zw.com" + bookChapterUrlList[index]
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



