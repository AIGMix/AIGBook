# AIGBOOK
小说搜索与获取

## 📺 安装 
需要 Python 版本大于或等于 3.7
```shell
pip3 install aigbook --upgrade
```

## 🤖 功能

- 搜索
- 获取书籍信息
- 获取章节内容
- 下载章节
- 合并书籍文件


## 🎄使用

```python
import aigbook
import aigbook.book

# 获取书籍源列表
sources = aigbook.getBookFroms()
# 获取句柄
handle = aigbook.getBookHandle(sources[0])

```

## 💽 测试

1. 简单样例

```shell
cd test
cp default_config.json config.json
python ./test_download.py
```

2. GUI样例

```shell
cd test
cp default_config.json config.json
pip3 install pyqt5 --upgrade
pip3 install qt-material --upgrade
python ./test_gui.py
```


## 📜 免责声明 
1. 本软件为免费开源项目，无任何形式的盈利行为
2. 本软件仅供个人学习与测试
3. 严禁使用本软件进行盈利、损坏官方、散落任何违法信息等行为