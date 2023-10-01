import requests
from bs4 import BeautifulSoup
import random
import pandas as pd
import time
import os

# 读取Excel文件
df = pd.read_csv('Book_id.csv')
# 选择要读取的列
book_id_data = df['1046265'].tolist()
book_id_data.insert(0, '1046265')

df = pd.read_csv('Movie_id.csv')
movie_id_data = df['1292052'].tolist()
movie_id_data.insert(0, '1292052')
delay = random.randint(0, 1200)


def random_ip():
    ip = ".".join(str(random.randint(0, 255)) for _ in range(4))
    return ip


ip = random_ip()
# 手动添加的报头，用于规避豆瓣反爬(访问网页返回状态码418)
headers = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
    'X-Forwarded-For': ip,
}


# 给定id搜索电影
def search_douban_movie(id):
    # 随机生成IP
    ip = random_ip()
    # 将IP加入到报头中
    headers['X-Forwarded-For'] = ip
    # 构造搜索URL
    search_url = f"https://movie.douban.com/subject/{id}/"
    # 发送HTTP请求并获取页面内容
    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        print("请求失败")
        return
    # 使用BeautifulSoup解析页面内容
    soup = BeautifulSoup(response.text, "html.parser")

    # 提取搜索结果中的电影信息
    # 获取中英文名称
    # ID
    print('ID:', id)

    temp = soup.find('span', {'property': 'v:itemreviewed'})
    if (temp is not None):
        name = temp.text
        # 截取中文名
        print('中文名称:', name.split()[0])
        # 截取英文名
        print('英文名称:', ' '.join(name.split()[1:]))

    # 获取年份
    temp = soup.find('span', class_='year')
    if (temp is not None):
        year = temp.text.strip()
        print('年份:', year[1:5])

    # 获取评分
    temp = soup.find('strong', {'property': "v:average"})
    if (temp is not None):
        rate = temp.text
        print('评分:', rate)

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
        print('导演:', info[index_1 + len('导演: '):index_2 - 1])
    if (index_2 != -1 and index_3 != -1):
        print('编剧:', info[index_2 + len('编剧: '):index_3 - 1])
    if (index_3 != -1 and index_4 != -1):
        print('主演:', info[index_3 + len('主演: '):index_4 - 1])
    if (index_4 != -1 and index_5 != -1):
        print('类型:', info[index_4 + len('类型: '):index_5 - 1])
    if (index_5 != -1 and index_6 != -1):
        print('制片国家/地区:', info[index_5 + len('制片国家/地区: '):index_6 - 1])
    if (index_6 != -1 and index_7 != -1):
        print('语言:', info[index_6 + len('语言: '):index_7])
    detail = soup.find('span', {'class': 'all hidden'})  # 展开简介
    if (detail is None):  # 不需要展开简介
        detail = soup.find('span', {'property': 'v:summary'})
    detail = detail.text.strip().replace(' ', '')
    detail = detail.replace('\n\u3000\u3000', '')
    print('简介:\n', detail)
    print("=" * 40)
    global movie_list
    #信息字典
    movie_list.append({"id":id,"cname":name.split()[0],"ename":' '.join(name.split()[1:]),"year":year[1:5],"rate":rate,"director":info[index_1 + len('导演: '):index_2 - 1],"scr":info[index_2 + len('编剧: '):index_3 - 1],"star":info[index_3 + len('主演: '):index_4 - 1],"type":info[index_4 + len('类型: '):index_5 - 1],"area":info[index_5 + len('制片国家/地区: '):index_6 - 1],"lang":info[index_6 + len('语言: '):index_7],"syno":detail})

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
    df.to_excel(fileName, index=False)  # 存表，去除原始索引列（0,1,2...）




def search_douban_book(id):
    # 随机生成IP
    ip = random_ip()
    # 将IP加入到报头中
    headers['X-Forwarded-For'] = ip
    # 构造搜索URL
    search_url = f"https://book.douban.com/subject/{id}/"
    # 发送HTTP请求并获取页面内容
    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        print("请求失败")
        return
    # 使用BeautifulSoup解析页面内容
    soup = BeautifulSoup(response.text, 'html.parser')
    body = soup.find('body')
    name = body.find('h1').find('span', {'property': 'v:itemreviewed'}).text
    print("书名:", name)
    info = body.find('div', {'id': 'info'}).text.strip()
    # print(info)
    index_1 = info.find('作者')
    index_2 = info.find('出版社')
    index_3 = info.find('原作名')
    index_4 = info.find('译者')
    index_5 = info.find('出版年')
    index_6 = info.find('页数')
    index_7 = info.find('丛书')
    index_8 = info.find('ISBN')
    # ID
    print('ID:', id)
    # 作者
    author = info[index_1 + len('作者:'):index_2 - 1].replace('\n', '').replace(
        ' ', '')
    print('作者:', author)
    # 出版社
    if (index_3 != -1):
        publisher = info[index_2 + len('出版社:'):index_3 - 1].replace('\n', '')
        print('出版社:', publisher)
    else:
        publisher = info[index_2 + len('出版社:'):index_5 - 1].replace('\n', '')
        print('出版社:', publisher)
    # 原作名
    if (index_3 != -1 and index_4 != -1):
        origin_name = info[index_3 + len('原作名:'):index_4 - 1].replace('\n', '')
        print('原作名:', origin_name)
    # 译者
    if (index_4 != -1 and index_5 != -1):
        translator = info[index_4 + len('译者:'):index_5 - 1].replace(
            '\n', '').replace(' ', '')
        print('译者:', translator)
    # 出版年
    if (index_5 != -1 and index_6 != -1):
        year = info[index_5 + len('出版年:'):index_6 - 1]
        print('出版年:', year)
    if (index_7 != -1):
        # 丛书
        books = info[index_7 + len('丛书:'):index_8 - 1].replace('\n',
                                                               '').replace(
                                                                   ' ', '')
        print('丛书:', books)
    # ISBN
    print('ISBN:', info[index_8 + len('ISBN:'):])
    detail = soup.find('span', {'class': 'all hidden'})  # 展开简介
    if (detail is None):  # 不需要展开简介
        detail = soup.find('span', {'property': 'v:summary'})
    if (detail is None):  # 其他类型
        detail = soup.find('div', {'class': 'intro'})
    detail = detail.text.strip().replace(' ', '')
    detail = detail.replace('\n\u3000\u3000', '')
    print('简介:\n', detail)
    print("=" * 40)
    global book_list
    book_list.append({"id":id,"name":name,"author":author,"publisher":publisher,"origin_title":origin_name,"translater":translator,"year":year,"series":books,"ISBN":info[index_8 + len('ISBN:'):],"syno":detail})
    #信息字典
    pass

def book_toExcel(data, fileName):  # pandas库储存数据到excel
    ids = []
    names = []
    authors = []
    publishers = []
    origin_titles = []
    translaters = []
    years = []
    seriess = []
    ISBNs = []
    synos = []

    for i in range(len(data)):
        ids.append(data[i]["id"])
        names.append(data[i]["name"])
        authors.append(data[i]["author"])
        publishers.append(data[i]["publisher"])
        origin_titles.append(data[i]["origin_title"])
        translaters.append(data[i]["translater"])
        years.append(data[i]["year"])
        seriess.append(data[i]["series"])
        ISBNs.append(data[i]["ISBN"])
        synos.append(data[i]["syno"])
 
    dfData = {  # 用字典设置DataFrame所需数据
        '序号': ids,
        '书名': names,
        '作者': authors,
        '出版社': publishers,
        '原作名': origin_titles,
        '译者': translaters,
        '出版年':years,
        '丛书': seriess,
        'ISBN': ISBNs,
        '简介': synos
    }
    df = pd.DataFrame(dfData)  # 创建DataFrame
    df.to_excel(fileName, index=False)  # 存表，去除原始索引列（0,1,2...）



if __name__ == "__main__": 
    movie_list = [] #字典列表
    for id in movie_id_data:
        search_douban_movie(id)
        os.remove('movie.xlsx')
        movie_toExcel(movie_list, 'movie.xlsx')
        delay = random.randint(0, 5)  # 随机间隔0-5s访问
        time.sleep(delay)

    book_list = [] #字典列表
    for id in book_id_data:
        search_douban_book(id)
        os.remove('book.xlsx')
        book_toExcel(book_list, 'book.xlsx')
        delay = random.randint(0, 5)  # 随机间隔0-5s访问
        time.sleep(delay)


