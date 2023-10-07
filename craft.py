import requests
from bs4 import BeautifulSoup
import random
import pandas as pd
import time
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
LIST_POSITION = 0
LIST_SIZE = 100

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
    'X-Forwarded-For':
    ip,
    'Cookie':
    'bid=HNf-ab2-lJI; gr_user_id=031667b7-5f8a-4ede-b695-e52d9181fe11; __gads=ID=60db1851df53b133:T=1583253085:S=ALNI_MbBwCgmPG1hMoA4-Z0HSw_zcT0a0A; _vwo_uuid_v2=DD32BB6F8D421706DCD1CDE1061FB7A45|ef7ec70304dd2cf132f1c42b3f0610e7; viewed="1200840_27077140_26943161_25779298"; ll="118165"; __yadk_uid=5OpXTOy4NkvMrHZo7Rq6P8VuWvCSmoEe; ct=y; ap_v=0,6.0; push_doumail_num=0; push_noty_num=0; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1583508410%2C%22https%3A%2F%2Fwww.pypypy.cn%2F%22%5D; _pk_ses.100001.4cf6=*; dbcl2="131182631:x7xeSw+G5a8"; ck=9iia; _pk_id.100001.4cf6=17997f85dc72b3e8.1583492846.4.1583508446.1583505298.',
}

# proxies = {"http": None, "https": None}


# 给定id搜索电影
def search_douban_movie(id):
    # ID
    print('ID:', id)
    # 随机生成IP
    ip = random_ip()
    # 将IP加入到报头中
    headers['X-Forwarded-For'] = ip
    # 构造搜索URL
    search_url = f"https://movie.douban.com/subject/{id}/"
    # 发送HTTP请求并获取页面内容
    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        print("请求失败", response.status_code)
        delay = random.randint(0, 5)  # 随机间隔0-5s访问
        time.sleep(delay)
        search_douban_movie(id)
        return
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
                sheet_name="{0}-{1}".format(LIST_POSITION * LIST_SIZE + 1,
                                            (LIST_POSITION + 1) *
                                            LIST_SIZE))  # 存表，去除原始索引列（0,1,2...）


def search_douban_book(id):
    # ID
    print('ID:', id)
    # 随机生成IP
    ip = random_ip()
    # 将IP加入到报头中
    headers['X-Forwarded-For'] = ip
    # 构造搜索URL
    search_url = f"https://book.douban.com/subject/{id}/"
    # 发送HTTP请求并获取页面内容
    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        print("请求失败", response.status_code)
        print(search_url)
        delay = random.randint(0, 5)  # 随机间隔0-5s访问
        time.sleep(delay)
        search_douban_movie(id)
        return
    # 使用BeautifulSoup解析页面内容
    soup = BeautifulSoup(response.text, 'html.parser')
    body = soup.find('body')
    name = body.find('h1').find('span', {'property': 'v:itemreviewed'}).text
    print("书名:", name)
    # 获取评分
    temp = soup.find('strong', {'property': "v:average"})
    if (temp is not None):
        rate = temp.text
        # print('评分:', rate)
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
    # 作者
    author = info[index_1 + len('作者:'):index_2 - 1].replace('\n', '').replace(
        ' ', '')
    # print('作者:', author)
    # 出版社
    if (index_3 != -1):
        publisher = info[index_2 + len('出版社:'):index_3 - 1].replace('\n', '')
        # print('出版社:', publisher)
    else:
        publisher = info[index_2 + len('出版社:'):index_5 - 1].replace('\n', '')
        # print('出版社:', publisher)
    # 原作名
    if (index_3 != -1 and index_4 != -1):
        origin_name = info[index_3 + len('原作名:'):index_4 - 1].replace('\n', '')
        # print('原作名:', origin_name)
    else:
        origin_name = None
    # 译者
    if (index_4 != -1 and index_5 != -1):
        translator = info[index_4 + len('译者:'):index_5 - 1].replace(
            '\n', '').replace(' ', '')
        # print('译者:', translator)
    else:
        translator = None
    # 出版年
    if (index_5 != -1 and index_6 != -1):
        year = info[index_5 + len('出版年:'):index_6 - 1]
        # print('出版年:', year)
    else:
        year = None
    if (index_7 != -1):
        # 丛书
        books = info[index_7 + len('丛书:'):index_8 - 1].replace('\n',
                                                               '').replace(
                                                                   ' ', '')
        # print('丛书:', books)
    else:
        books = None
    # ISBN
    ISBN = info[index_8 + len('ISBN:'):]
    # print('ISBN:', ISBN)
    detail = soup.find('span', {'class': 'all hidden'})  # 展开简介
    if (detail is None):  # 不需要展开简介
        detail = soup.find('span', {'property': 'v:summary'})
    if (detail is None):  # 其他类型
        detail = soup.find('div', {'class': 'intro'})
    detail = detail.text.strip().replace(' ', '')
    detail = detail.replace('\n\u3000\u3000', '')
    # print('简介:\n', detail)
    print("=" * 40)
    response.close()
    pass
    global book_list
    book_list.append({
        "id": id,
        "name": name,
        "rate": rate,
        "author": author,
        "publisher": publisher,
        "origin_title": origin_name,
        "translater": translator,
        "year": year,
        "series": books,
        "ISBN": ISBN,
        "syno": detail
    })
    # 信息字典
    pass
    # 作者简介
    # 随机生成IP
    ip = random_ip()
    # 将IP加入到报头中
    headers['X-Forwarded-For'] = ip
    url = body.find('div', {'id': 'info'}).a['href']
    if (url.find('https') == -1):
        author_url = f"https://book.douban.com{url}"
    else:
        author_url = url
    delay = random.randint(0, 5)  # 随机间隔0-5s访问
    time.sleep(delay)
    response = requests.get(author_url, headers=headers, verify=False)
    if response.status_code != 200:
        print("请求失败", response.status_code)
        return
    soup2 = BeautifulSoup(response.text, 'html.parser')
    content = soup2.find('div', {'id': 'intro', 'class': 'mod'})
    if (content is None):
        author_info = None
    else:
        content = content.find('div', {'class': 'bd'})
        author_info = content.find('span', {'class': 'all hidden'})  # 展开简介
        if (author_info is None):  # 不需要展开简介
            author_info = content
        author_info = author_info.text.strip()
        response.close()
        print('\n作者信息:\n', author_info)
    print("=" * 40)


def book_toExcel(data, fileName):  # pandas库储存数据到excel
    ids = []
    names = []
    rates = []
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
        rates.append(data[i]["rate"])
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
        '评分': rates,
        '作者': authors,
        '出版社': publishers,
        '原作名': origin_titles,
        '译者': translaters,
        '出版年': years,
        '丛书': seriess,
        'ISBN': ISBNs,
        '简介': synos
    }
    df = pd.DataFrame(dfData)  # 创建DataFrame
    df.to_excel(fileName, index=False)  # 存表，去除原始索引列（0,1,2...）


if __name__ == "__main__":

    movie_list = []  # 字典列表
    count = 0
    times = 0
    for id in movie_id_data:
        if (count < LIST_POSITION * 100):
            count = count + 1
            continue
        if (times >= LIST_SIZE):
            break
        times = times + 1
        search_douban_movie(id)
        # os.remove('movie.xlsx')
        movie_toExcel(movie_list, 'movie.xlsx')
        delay = random.randint(0, 5)  # 随机间隔0-5s访问
        time.sleep(delay)

    book_list = []  # 字典列表
    for id in book_id_data:
        id = "4886245"
        search_douban_book(id)
        # os.remove('movie.xlsx')
        book_toExcel(book_list, 'book.xlsx')
        delay = random.randint(0, 5)  # 随机间隔0-5s访问
        time.sleep(delay)

    # movie_list = []  # 字典列表
    # for id in movie_id_data:
    #     # id = '3543690'  # 指定id
    #     search_douban_movie(id)
    #     # os.remove('movie.xlsx')
    #     movie_toExcel(movie_list, 'movie.xlsx')
    #     delay = random.randint(0, 5)  # 随机间隔0-5s访问
    #     time.sleep(delay)
