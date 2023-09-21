import requests
from bs4 import BeautifulSoup


def search_douban_movie(movie_name):
    # 构造搜索URL
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.31'
    }
    search_url = f"https://www.douban.com/search?q={movie_name}"
    #print(search_url)

    # 发送HTTP请求并获取页面内容
    response = requests.get(search_url, headers=headers)
    #print(response.status_code)
    if response.status_code != 200:
        print("请求失败")
        return

    # 使用BeautifulSoup解析页面内容
    soup = BeautifulSoup(response.text, "html.parser")

    # 提取搜索结果中的电影信息
    results = soup.find_all("div", class_="result")
    for result in results:
        #获取条目类型
        type = result.find("h3").text.strip()
        type = type.split()[0]
        print(f"类型: {type}")
        #获取有关电影的信息
        content = result.find("div", class_="content")
        #获取书籍名
        title = content.find("a").text.strip()
        print(f"电影名称: {title}")
        #获取评分
        rate = content.find("span", class_="rating_nums").text.strip()
        print(f"电影评分: {rate}")
        #获取简介
        info = result.find("p").text.strip()
        print(f"电影简介: {info}")
        print("=" * 40)


if __name__ == "__main__":
    movie_name = input("请输入要搜索的电影名称: ")
    search_douban_movie(movie_name)
