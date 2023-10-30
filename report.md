# Web信息处理与应用 lab1

## 第一阶段：爬虫&检索

### 一.爬虫

#### 实验要求：

1.对于电影数据，至少爬取其基本信息、剧情简介、演职员表；鼓励抓取更多有用信息（可能有益于第2阶段的分析）；

2.对于书籍数据，至少爬取其基本信息、内容简介、作者简介；鼓励抓取更多有用信息（可能有益于第2阶段的分析）；

3.爬虫方式不限，网页爬取和 API 爬取两种方式都可，介绍使用的爬虫方式工具；

4.针对所选取的爬虫方式，发现并分析平台的反爬措施，并介绍采用的应对策略；

5.针对所选取的爬虫方式，使用不同的内容解析方法，并提交所获取的数据；

6.该阶段无评测指标要求，在实验报告中说明爬虫（反爬）策略和解析方法即可。

#### 实验步骤

##### 1.爬取页面（+反爬应对措施）

使用 python 的 requests 库，直接请求对应的 url来获取 html 的内容。

爬取过程中通过生成随机ip，手动添加报头，爬取休息来规避平台反爬

```python
# 生成随机ip
def random_ip():
    ip = ".".join(str(random.randint(0, 255)) for _ in range(4))
    return ip
ip = random_ip()

# 手动添加的报头，用于规避豆瓣反爬(访问网页返回状态码418)
headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'X-Forwarded-For':
    ip,
    'Cookie':
    'bid=HNf-ab2-lJI; gr_user_id=031667b7-5f8a-4ede-b695-e52d9181fe11; __gads=ID=60db1851df53b133:T=1583253085:S=ALNI_MbBwCgmPG1hMoA4-Z0HSw_zcT0a0A; _vwo_uuid_v2=DD32BB6F8D421706DCD1CDE1061FB7A45|ef7ec70304dd2cf132f1c42b3f0610e7; viewed="1200840_27077140_26943161_25779298"; ll="118165"; __yadk_uid=5OpXTOy4NkvMrHZo7Rq6P8VuWvCSmoEe; ct=y; ap_v=0,6.0; push_doumail_num=0; push_noty_num=0; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1583508410%2C%22https%3A%2F%2Fwww.pypypy.cn%2F%22%5D; _pk_ses.100001.4cf6=*; dbcl2="131182631:x7xeSw+G5a8"; ck=9iia; _pk_id.100001.4cf6=17997f85dc72b3e8.1583492846.4.1583508446.1583505298.',
}

# 爬取休息
if __name__ == "__main__":
    ...
	delay = random.randint(0, 5)  # 随机间隔0-5s访问
    time.sleep(delay)
```

##### 2.内容解析

使用BeautifulSoup解析页面内容，之后提取页面中的各个信息。

以解析电影内容为例：

```python
def search_douban_movie(id):
    ...
    # 使用BeautifulSoup解析页面内容
    soup = BeautifulSoup(response.text, "html.parser")

    # 提取搜索结果中的电影信息
    # 获取中英文名称
    temp = soup.find('span', {'property': 'v:itemreviewed'})
    if (temp is not None):
        name = temp.text
        # 截取中文名
        chinese_name = name.split()[0]
        print('中文名称:', chinese_name)
        # 截取其他名称
        if (name.split()[1:] != []):
            other_name = ' '.join(name.split()[1:])
            # print('其他名称:', other_name)
        else:
            other_name = None
    else:
        print("空页面\n")
        return
    
    # 获取年份
    temp = soup.find('span', class_='year')
    if (temp is not None):
        year = temp.text.strip()[1:5]
        # print('年份:', year)
    else:
        year = None

    # 获取评分
    temp = soup.find('strong', {'property': "v:average"})
    if (temp is not None):
        rate = temp.text
        # print('评分:', rate)
    else:
        rate = None
    
    # 获取其他信息
    info = soup.find('div', {'id': 'info'}).text

    # print(info[1:], '\n')
    index_1 = info.find('导演: ')
    index_2 = info.find('编剧: ')
    index_3 = info.find('主演: ')
    index_4 = info.find('类型: ')
    index_5 = info.find('制片国家/地区: ')
    index_6 = info.find('语言: ')
    index_7 = info.find('\n', index_6)
    if (index_1 != -1 and index_2 != -1):
        diretor = info[index_1 + len('导演: '):index_2 - 1]
        # print('导演:', diretor)
    else:
        diretor = None
    if (index_2 != -1 and index_3 != -1):
        scriptwriter = info[index_2 + len('编剧: '):index_3 - 1]
        # print('编剧:', scriptwriter)
    else:
        scriptwriter = None
    if (index_3 != -1 and index_4 != -1):
        actor = info[index_3 + len('主演: '):index_4 - 1]
        # print('主演:', actor)
    else:
        actor = None
    if (index_4 != -1 and index_5 != -1):
        type = info[index_4 + len('类型: '):index_5 - 1]
        # print('类型:', type)
    else:
        type = None
    if (index_5 != -1 and index_6 != -1):
        area = info[index_5 + len('制片国家/地区: '):index_6 - 1]
        # print('制片国家/地区:', area)
    else:
        area = None
    if (index_6 != -1 and index_7 != -1):
        language = info[index_6 + len('语言: '):index_7]
        # print('语言:', language)
    else:
        language = None
    detail = soup.find('span', {'class': 'all hidden'})  # 展开简介
    if (detail is None):  # 不需要展开简介
        detail = soup.find('span', {'property': 'v:summary'})
    detail = detail.text.strip().replace(' ', '')
    detail = detail.replace('\n\u3000\u3000', '')
    # print('简介:\n', detail)
    print("=" * 40)

```

##### 3.内容写入

使用pandas库中的数据结构DataFrame，先将爬取的数据转化为DataFrame类型，然后将数据写入到word文档。

以电影为例：

```py
def search_douban_movie(id):
    ...
    global movie_list
    # 信息字典
    movie_list.append({
        "id": id,
        "cname": chinese_name,
        "ename": other_name,
        "year": year,
        "rate": rate,
        "director": diretor,
        "scr": scriptwriter,
        "star": actor,
        "type": type,
        "area": area,
        "lang": language,
        "syno": detail
    })
def movie_toExcel(data, fileName):  # pandas库储存数据到excel
    ids = []
    cnames = []
    enames = []
    years = []
    rates = []
    directors = []
    scrs = []
    stars = []
    types = []
    areas = []
    langs = []
    synos = []

    for i in range(len(data)):
        ids.append(data[i]["id"])
        cnames.append(data[i]["cname"])
        enames.append(data[i]["ename"])
        years.append(data[i]["year"])
        rates.append(data[i]["rate"])
        directors.append(data[i]["director"])
        scrs.append(data[i]["scr"])
        stars.append(data[i]["star"])
        types.append(data[i]["type"])
        areas.append(data[i]["area"])
        langs.append(data[i]["lang"])
        synos.append(data[i]["syno"])

    dfData = {  # 用字典设置DataFrame所需数据
        '序号': ids,
        '中文名称': cnames,
        '英文名称': enames,
        '年份': years,
        '评分': rates,
        '导演': directors,
        '编剧': scrs,
        '主演': stars,
        '类型': types,
        '制片国家/地区': areas,
        '语言': langs,
        '简介': synos
    }

    df = pd.DataFrame(dfData)  # 创建DataFrame
    df.to_excel(fileName,
                index=False,
                sheet_name="{0}-{1}".format(LIST_POSITION, LIST_POSITION +
                                            LIST_SIZE))
```

##### 4.实验结果

部分实验结果如下，全部结果见文件movie.xlsx和文件book.xlsx（部分页面为空页面，故爬取总数不足1200）。

![image-20231030111515139](C:\Users\wyzhou\AppData\Roaming\Typora\typora-user-images\image-20231030111515139.png)

![image-20231030111539240](C:\Users\wyzhou\AppData\Roaming\Typora\typora-user-images\image-20231030111539240.png)

### 二.检索

#### 实验要求：

1.对一阶段中爬取的电影和书籍数据进行预处理，将文本表征为关键词集合。

2.在经过预处理的数据集上建立倒排索引表𝑺，并以合适的方式存储生成的倒排索引文件。

3.对于给定的 bool 查询𝑸𝒃𝒐𝒐𝒍（例如 动作 and 剧情），根据你生成的倒排索引表 𝑺，返回符合查询规则𝑸𝒃𝒐𝒐𝒍的电影或/和书籍集合𝑨𝒃𝒐𝒐𝒍 = {𝑨𝒃𝒐𝒐𝒍, 𝑨𝒃𝒐𝒐𝒍, … }，并以合适的方式展现给用户（例如给出电影名称和分类或显示部分简介等）。

4.任选一种课程中介绍过的索引压缩加以实现，如按块存储、前端编码等，并比较压缩后的索引在存储空间和检索效率上与原索引的区别。

#### 实验步骤：

##### 1.分词



##### 2.建立倒排表



##### 3.布尔查询



##### 4.引索压缩



## 第二阶段：使用豆瓣数据进行推荐