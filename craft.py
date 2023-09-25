import requests
from bs4 import BeautifulSoup
import random


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


# 给定名字搜索，对搜索结果进行分析
def search_douban_movie(movie_name):
    # 构造搜索URL
    search_url = f"https://www.douban.com/search?q={movie_name}"
    # ip = random_ip()
    # 发送HTTP请求并获取页面内容
    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        print("请求失败")
        return

    # 使用BeautifulSoup解析页面内容
    soup = BeautifulSoup(response.text, "html.parser")

    # 提取搜索结果中的电影信息
    results = soup.find_all("div", class_="result")
    for result in results:
        # 随机生成IP
        ip = random_ip()
        headers["X-Forwarded-For"] = ip  # 将随机生成的IP添加到报头中
        # 获取条目类型
        type = result.find("h3").text.strip()
        type = type.split()[0]
        if (type[0] != '['):
            return
        begin = int(type.index('['))
        end = int(type.index(']'))
        type = type[begin + 1:end]
        if (type != '电影' and type != '电视剧' and type != '书籍'):
            return
        # 获取条目
        content = result.find("div", class_="content")
        # 获取条目的链接
        next_url = content.find("a").get("href")
        more_info(next_url)
        print("=" * 40)


def more_info(next_url):
    response = requests.get(next_url, headers=headers)
    if response.status_code != 200:
        print("请求失败")
    # 使用BeautifulSoup解析页面内容
    soup = BeautifulSoup(response.text, "html.parser")

    # 提取搜索结果中的电影信息
    # 获取中英文名称
    name = soup.find('span', {'property': 'v:itemreviewed'}).text
    # 截取中文名
    print('中文名称:', name.split()[0])
    # 截取英文名
    print('英文名称:', ' '.join(name.split()[1:]))
    # 获取年份
    year = soup.find('span', class_='year').text.strip()
    print('年份:', year[1:5])
    # 获取评分
    rate = soup.find('strong', {'property': "v:average"}).text
    print('评分:', rate)
    # 获取导演名单
    info = soup.find('div', {'id': 'info'}).text
    # print(info[1:], '\n')
    index_1 = info.find('导演: ')
    index_2 = info.find('编剧: ')
    index_3 = info.find('主演: ')
    index_4 = info.find('类型: ')
    index_5 = info.find('制片国家/地区: ')
    index_6 = info.find('语言: ')
    index_7 = info.find('首播: ')
    print('导演:', info[index_1 + len('导演: '):index_2 - 1])
    print('编剧:', info[index_2 + len('编剧: '):index_3 - 1])
    print('主演:', info[index_3 + len('主演: '):index_4 - 1])
    print('类型:', info[index_4 + len('类型: '):index_5 - 1])
    print('制片国家/地区:', info[index_5 + len('制片国家/地区: '):index_6 - 1])
    print('语言:', info[index_6 + len('语言: '):index_7 - 1])
    detail = soup.find('span', {'property': 'v:summary'}).text.replace(' ', '')
    print('简介:', detail)
    pass


if __name__ == "__main__":
    # movie_name = "憨豆先生"
    movie_name = input("请输入要搜索的电影名称: ")
    search_douban_movie(movie_name)
