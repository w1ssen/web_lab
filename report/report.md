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

在part1/web_scraper.py文件中使用 python 的 requests 库，直接请求对应的 url来获取 html 的内容。

爬取过程中通过生成随机ip，手动添加报头，添加cookies，爬取休息来规避平台反爬

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

在part1/web_scraper.py文件中使用BeautifulSoup解析页面内容，之后提取页面中的各个信息。由于页面中的信息大部分是连续的text文本，很多信息会混在一起，通过字符串切割来获取需要的信息。同时因为网页格式不同，有的电影/书籍存在部分数据缺失的情况，需要添加判断语句避免程序报错。

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

在part1/web_scraper.py文件中使用pandas库中的数据结构DataFrame，先将爬取的数据转化为DataFrame类型，然后将数据写入到excel文档。

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

具体写入时，为了分段写入excel表格，做了以下处理：

```python
LIST_POSITION = 0 # 读取的起始行数
LIST_SIZE = 100 # 一次读取的行数

book_list = []  # 字典列表
    count = 0
    times = 0
    for id in book_id_data:
        if (count < LIST_POSITION):
            count = count + 1
            continue
        if (times >= LIST_SIZE):
            break
        times = times + 1
        search_douban_book(id)
        book_toExcel(book_list, 'data/book.xlsx')
        delay = random.randint(0, 5)  # 随机间隔0-5s访问
        time.sleep(delay)
```

##### 4.实验结果

部分实验结果如下，全部结果见文件part1/data/movie.xlsx和文件part1/data/book.xlsx（部分页面为空页面，直接跳过，故爬取总数不足1200）。

![image-20231030171146053](.\figs\image-20231030171146053.png)

![image-20231030171208270](.\figs\image-20231030171208270.png)

### 二.检索

#### 实验要求：

1.对一阶段中爬取的电影和书籍数据进行预处理，将文本表征为关键词集合。

2.在经过预处理的数据集上建立倒排索引表𝑺，并以合适的方式存储生成的倒排索引文件。

3.对于给定的 bool 查询𝑸𝒃𝒐𝒐𝒍（例如 动作 and 剧情），根据你生成的倒排索引表 𝑺，返回符合查询规则𝑸𝒃𝒐𝒐𝒍的电影或/和书籍集合𝑨𝒃𝒐𝒐𝒍 = {𝑨𝒃𝒐𝒐𝒍, 𝑨𝒃𝒐𝒐𝒍, … }，并以合适的方式展现给用户（例如给出电影名称和分类或显示部分简介等）。

4.任选一种课程中介绍过的索引压缩加以实现，如按块存储、前端编码等，并比较压缩后的索引在存储空间和检索效率上与原索引的区别。

#### 实验步骤：

##### 1.分词

在对电影简介/书籍简介分词结束写入表格后，part1/add_tag_to_key将提供的Tag也加入到关键词。下面以添加电影Tag为例：

```python
# 获取tag信息，并加入关键词
import pandas as pd
# 读取文件存入列表变量
df1 = pd.read_csv('part1/data/Movie_tag.csv').fillna('')
movie_id_1 = df1['Id'].tolist()
movie_tag = df1['Tag'].tolist()
df2 = pd.read_excel('part1/data/movie.xlsx').fillna('')
movie_id_2 = df2['序号'].tolist()
# movie_type = df2['类型'].tolist()
movie_id_key = df2['关键词'].tolist()
# 循环查找需要修改的地方
for i in range(len(movie_id_2)):
    movie_id_key[i] = movie_id_key[i].replace(' ', '')

    # 对指定单元格修改,方括号中的参数第一个是行号，第二个是列名
    df2.at[i, '关键词'] = movie_id_key[i]
    # print(movie_id_key[index])
# 写回文件，一定不能忘了这一步
df2.to_excel('part1/data/movie.xlsx', index=False)
```

##### 2.建立倒排表

在part1/in verted_index_to_excel中，对照获取到的关键词信息，通过pandas读取ID和对应的关键词，构建关键词-ID字典，再将字典写入excel表格。为了方便后续的Bool检索，ID采用集合数据结构。以电影为例：

```python
import pandas as pd

df1 = pd.read_excel('part1/data/movie.xlsx').fillna('')
ids = df1['序号'].tolist()
keys = df1['关键词'].tolist()
Inverted_Index = dict()
id_list = []


# 创建倒排表
def create_inverted_index():
    for i in range(len(keys)):
        keywords = keys[i].split(',')  # 将每个id的关键词用逗号切割，变成一个列表变量
        for item in keywords:  # 遍历id的每个关键词
            if item not in Inverted_Index:
                Inverted_Index[item] = set()  # 不在倒排表中的关键词新建集合
            Inverted_Index[item].add(ids[i])  # 在倒排表对应的关键词位置添加id
    for item in Inverted_Index:
        id_list.append({'key': item, 'id': Inverted_Index[item]})
    print(Inverted_Index)


def list_to_excel():
    keys = [item['key'] for item in id_list]
    ids = [item['id'] for item in id_list]
    dfData = {'关键词': keys, 'ID': ids}
    df = pd.DataFrame(dfData)  # 创建 DataFrame
    df.to_excel('part1/data/movie_list.xlsx', index=False)


create_inverted_index()
list_to_excel()
```

倒排表结果见part1/data/movie_list和part1/data/book_list

![image-20231030170747442](.\figs\image-20231030170747442.png)

![image-20231030171755887](.\figs\image-20231030171755887.png)

##### 3.布尔查询

在part1/keyword_search中实现了bool检索。

首先是根据对检索语句进行优先级，关键词的分析。按照bool检索的运算符优先级：括号>NOT>AND>OR，构建关键词栈和运算符栈，先进行高优先级运算符的计算。因为上一步采用了集合的数据结构存储倒排表中的ID，这一步对运算符的处理就可以直接调用集合运算了。

而对于关键词在倒排表中的查找，采用简单的列表查询就好。

```python
def search_in_movielist(search_input):
    # 使用正则表达式来分割查询字符串
    tokens = re.split(r'(\(|\)|AND|OR|NOT)', search_input)

    # 定义布尔操作的函数
    def intersection(posting1, posting2):
        return set(posting1) & set(posting2)

    def union(posting1, posting2):
        return set(posting1) | set(posting2)

    def negation(posting):
        all_docs = set(movie_list_key)
        return all_docs - set(posting)

    stack = []
    operator_stack = []

    for token in tokens:
        token = token.strip()
        if token.strip() == "":
            continue
        if token == "(":
            operator_stack.append(token)
        elif token == ")":
            while operator_stack and operator_stack[-1] != "(":
                operator = operator_stack.pop()
                if operator == "AND":
                    operand2 = stack.pop()
                    operand1 = stack.pop()
                    stack.append(intersection(operand1, operand2))
                elif operator == "OR":
                    operand2 = stack.pop()
                    operand1 = stack.pop()
                    stack.append(union(operand1, operand2))
        elif token == "AND" or token == "OR":
            while operator_stack and operator_stack[-1] in (
                    "AND", "OR") and operator_stack[-1] != "(":
                operator = operator_stack.pop()
                operand2 = stack.pop()
                operand1 = stack.pop()
                if operator == "AND":
                    stack.append(intersection(operand1, operand2))
                elif operator == "OR":
                    stack.append(union(operand1, operand2))
            operator_stack.append(token)
        elif token == "NOT":
            operator_stack.append(token)
        else:
            # 处理关键词
            if token in movie_list_key:
                index = movie_list_key.index(token)
                stack.append(eval(movie_list_id[index]))
            else:
                stack.append(set())  # 未知词的结果为空集

    while operator_stack:
        operator = operator_stack.pop()
        if operator == "AND" or operator == "OR":
            operand2 = stack.pop()
            operand1 = stack.pop()
            if operator == "AND":
                stack.append(intersection(operand1, operand2))
            elif operator == "OR":
                stack.append(union(operand1, operand2))
        elif operator == "NOT":
            operand = stack.pop()
            stack.append(negation(operand))
    print(stack[0])
    print_movie_info(stack[0])
```

当找到需要的id后，还需要以合适的形式呈现搜索结果

```python
# 打印搜索得到的ids的相关信息
def print_movie_info(ids):
    for id in ids:
        index = movie_id.index(id)  # 找到id的index
        print('ID:', id)
        print('电影名称:', movie_name[index])
        print('电影评分:', movie_rate[index])
        print('电影类型:', movie_type[index])
        print('电影简介:', movie_info[index])
        print(40 * "=")
```

下面是检索结果：



##### 4.引索压缩

因为涉及到的关键词多大25000个，这个规模的倒排表如果放在内存里很占用空间，且不利于检索。part1/inverted_index_zip通过分块存储对倒排表进行了压缩。

在这里将100个关键词作为一组。当组满时，生成一个二进制文件存储压缩的倒排表。最后生成一个元数据查询表，将块号和块内存储的关键词记录在元数据查询表中。

```python
# 每100个关键词为一组，构建压缩索引表
def zip_inverted_index():
    # if os.path.exists('part1/data/block_metadata.pkl'):  # 存在压缩的索引表后，不再构建压缩索引表
    #     return
    df_movie_list = pd.read_excel('part1/data/movie_list.xlsx').fillna('')
    movie_list_key = df_movie_list['关键词'].tolist()
    movie_list_id = df_movie_list['ID'].tolist()
    block_size = 100  # 块的大小
    block_number = 0  # 块的编号
    current_block = {}  # 当前块的倒排索引
    block_metadata = []  # 存储块的元数据信息
    for i in range(len(movie_list_id)):
        keyword = movie_list_key[i]
        current_block[keyword] = eval(movie_list_id[i])
        # current_block[keyword].add(eval(movie_list_id[i]))
        if len(current_block) >= block_size:
            block_number += 1
            block_filename = f"part1/block/block_{block_number}.pkl"  # 文件名示例
            with open(block_filename, 'wb') as block_file:
                pickle.dump(current_block, block_file)
            block_metadata.append({
                'block_number': block_number,
                'keywords': list(current_block.keys())
            })
            current_block = {}
    for item in current_block:
        id_list.append({'key': item, 'id': current_block[item]})

    with open('part1/block_metadata.pkl', 'wb') as metadata_file:
        pickle.dump(block_metadata, metadata_file)

```

下面需要利用压缩的倒排表进行检索。对于关键词keyword，需要遍历元数据查询表，找到后打开对应的块，并返回需要的ID

```python
# 压缩索引检索
def search_in_zip(keyword):
    with open('part1/data/block_metadata.pkl', 'rb') as metadata_file:
        block_metadata = pickle.load(metadata_file)

    for block_info in block_metadata:
        block_filename = f"part1/block/block_{block_info['block_number']}.pkl"
        with open(block_filename, 'rb') as block_file:
            current_block = pickle.load(block_file)
            if keyword in current_block:
                # print(current_block[keyword])
                return current_block[keyword]
```

为了体现性能差异，做如下对比

```python
zip_inverted_index()
# 检索性能计时,索引压缩
start_time = time.time()
# 模拟检索操作
keyword = "安迪"
search_in_zip(keyword)
keyword = "武士刀"
search_in_zip(keyword)
keyword = "大屏幕"
search_in_zip(keyword)
end_time = time.time()
elapsed_time = end_time - start_time
print(f"压缩检索代码运行时间: {elapsed_time} 秒")

# 检索性能计时，非压缩

start_time = time.time()
# 模拟检索操作
df_movie_list = pd.read_excel('part1/data/movie_list.xlsx').fillna('')
movie_list_key = df_movie_list['关键词'].tolist()
movie_list_id = df_movie_list['ID'].tolist()

keyword = "安迪"
search_in_list(keyword)
keyword = "武士刀"
search_in_list(keyword)
keyword = "大屏幕"
search_in_list(keyword)
end_time = time.time()
elapsed_time = end_time - start_time
print(f"顺序检索代码运行时间: {elapsed_time} 秒")
```

结果如下：

![image-20231030174246161](.\figs\image-20231030174246161.png)

对于在movie倒排表中随机选取的三个关键词，顺序检索花费的时间是远远大于压缩检索的。当检索关键词增多，这个差异会更加显著。而且如果将倒排表整个加载到非常占用空间。而压缩索引后，每次只需要把一个块的数据加载到内存，长期存在于内存中的只有元数据列表，极大地节省了空间。

## 第二阶段：使用豆瓣数据进行推荐

## 提交文件说明

```
├─part1 # 第一阶段
│  │  add_tag_to_keyword.py # 将Tag加入关键词
│  │  book_com.xlsx
│  │  inverted_index_to_excel.py # 创建倒排表并写入表格
│  │  inverted_index_zip.py # 索引压缩,以及顺序索引和压缩索引的性能对比
│  │  jyc.txt
│  │  keyword_search.py # bool检索
│  │  stop_words.txt
│  │  test_tyc.py
│  │  test_wordcut.py
│  │  tyc.py
│  │  web_scraper.py # 爬虫，搜集电影书籍信息
│  │  word_cut_jieba.py
│  │  word_cut_snownlp.py
│  │  ~$movie_list.xlsx
│  │
│  ├─block # 分块存储得到的二进制文件
│  └─data # 相关数据
│          block_metadata.pkl # 压缩后的倒排表
│          book.xlsx # 书籍的相关信息及关键词
│          Book_id.csv # 书籍ID
│          book_list.xlsx # 书籍倒排表
│          Book_tag.csv # 书籍Tag
│          movie.xlsx # 电影的相关信息及关键词
│          Movie_id.csv # 电影ID
│          movie_list.xlsx # 电影倒排表
│          Movie_tag.csv # 电影Tag
│
├─part2
│  │  graphrec.py
│  │  graph_rec_model.py
│  │  text_embedding.py
│  │  utils.py
│  │
│  └─data
│          book_score.csv
│          Contacts.txt
│          movie_score.csv
│          selected_book_top_1200_data_tag.csv
│          selected_movie_top_1200_data_tag.csv
│          tag_embedding_dict.pkl
│
├─report
│  │  report.md # 报告
│  │
│  └─figs #报告中的文件
├─useless # 中间数据以及一些数据的复制
│      book.xlsx
│      book_data.xlsx
│      movie copy 2.xlsx
│      movie_data.xlsx
│      test.xlsx
│
└─__pycache__
        jb.cpython-310.pyc
        jieba.cpython-310.pyc
        tyc.cpython-310.pyc
        word_cut_jieba.cpython-310.pyc
```

