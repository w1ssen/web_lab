# web_lab
9.21 jy上传craft.py
可以实现输入指定名字后的豆瓣搜索，并将搜索得到的页面信息解析并输出。问题在于，只有相当简略的信息，不能具体点开一个链接查看电影的具体信息

9.25 jy更新craft.py 更新README.md
可以进入搜索结果中的网页，查询详细的信息（名称，演员，导演，编剧，语言，地区，类型，评分，简介等），需要将结果写入表格或文档，需要处理“查看更多”的问题
通过随机生成IP，手动添加报头来解决反爬虫机制

9.25 jy修改网页获取方式，读取表格获取电影ID并访问页面获取数据，添加访问随机延时0-5s来避免反爬虫机制，书籍的信息搜集还需要另外写

9.25 jy添加了书籍信息查询的功能。但是由于书籍页面结构不同，不一定能跑所有的书籍

10.1 wyz更新craft.py

可以将爬取内容写入excel？
