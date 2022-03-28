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
    