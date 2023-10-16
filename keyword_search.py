import pandas as pd

df_movie_data = pd.read_excel('movie.xlsx').fillna('')
df_book_data = pd.read_excel('book.xlsx').fillna('')
df_movie_list = pd.read_excel('movie_list.xlsx').fillna('')
df_book_list = pd.read_excel('book_list.xlsx').fillna('')

movie_id = df_movie_data['序号'].tolist()
movie_name = df_movie_data['中文名称'].tolist()
movie_type = df_movie_data['类型'].tolist()
movie_rate = df_movie_data['评分'].tolist()
movie_info = df_movie_data['简介'].tolist()

book_id = df_book_data['序号'].tolist()
book_name = df_book_data['书名'].tolist()
book_author = df_book_data['作者'].tolist()
book_rate = df_book_data['评分'].tolist()
book_info = df_book_data['简介'].tolist()
book_author_info = df_book_data['作者简介'].tolist()

movie_list_key = df_movie_list['关键词'].tolist()
movie_list_id = df_movie_list['ID'].tolist()

book_list_key = df_book_list['关键词'].tolist()
book_list_id = df_book_list['ID'].tolist()


# 打印搜索得到的ids的相关信息
def print_movie_info(ids):
    for id in ids:
        index = movie_id.find(id)  # 找到id的index
        print('ID:', id)
        print('电影名称:', movie_name[index])
        print('电影评分:', movie_rate[index])
        print('电影类型:', movie_type[index])
        print('电影简介:', movie_info[index])


def print_book_info(ids):
    for id in ids:
        index = book_id.find(id)  # 找到id的index
        print('ID:', id)
        print('书籍名称:', book_name[index])
        print('书籍评分:', book_rate[index])
        print('书籍作者:', book_author[index])
        print('书籍简介:', book_info[index])
        print('书籍作者简介:', book_author_info[index])


def input_to_keywords(input):
    keywords = input.split()
    return keywords


# 电影倒排表检索
def search_in_movielist(keywords):
    ids = []
    for keyword in keywords:
        if (keyword in movie_list_key):
            index = movie_list_key.index(keyword)
        else:
            last_keyword = keyword
            continue
        add_ids = movie_list_id[index]
        if ids:
            # 对结果集进行 AND 或 OR 操作
            if last_keyword == 'AND':
                pass
            elif last_keyword == 'OR':
                # 合并两个列表并删除重复项
                ids = list(set(ids + add_ids))

                # 如果需要，将集合转换回列表
                ids = list(ids)
        else:
            ids = add_ids
    print(ids)


# 书籍倒排表检索
def search_in_booklist(keywords):
    pass


# while (1):
#     print('选择检索类型：电影/书籍:')
#     answer = input()
#     search_type = 0
#     if (answer == '电影'):
#         search_type = 1
#         break
#     elif (answer == '书籍'):
#         search_type = 2
#         break
#     else:
#         print('输入错误')
# print('输入搜索关键词')
search_type = 1
# search_input = input()
search_input = '下狱 OR 剧情'
keywords = input_to_keywords(search_input)
if (search_type == 1):
    search_in_movielist(keywords)
else:
    search_in_movielist(keywords)
