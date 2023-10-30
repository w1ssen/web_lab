import pandas as pd
import re
import time

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
        index = movie_id.index(id)  # 找到id的index
        print('ID:', id)
        print('电影名称:', movie_name[index])
        print('电影评分:', movie_rate[index])
        print('电影类型:', movie_type[index])
        print('电影简介:', movie_info[index])
        print(40 * "=")


def print_book_info(ids):
    for id in ids:
        index = book_id.index(id)  # 找到id的index
        print('ID:', id)
        print('书籍名称:', book_name[index])
        print('书籍评分:', book_rate[index])
        print('书籍作者:', book_author[index])
        print('书籍简介:', book_info[index])
        print('书籍作者简介:', book_author_info[index])
        print(40 * "=")


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


# 书籍倒排表检索
def search_in_booklist(search_input):
    # 使用正则表达式来分割查询字符串
    tokens = re.split(r'(\(|\)|AND|OR|NOT)', search_input)

    # 定义布尔操作的函数
    def intersection(posting1, posting2):
        return set(posting1) & set(posting2)

    def union(posting1, posting2):
        return set(posting1) | set(posting2)

    def negation(posting):
        all_docs = set(book_list_key)
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
            if token in book_list_key:
                index = book_list_key.index(token)
                stack.append(eval(book_list_id[index]))
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
    print_book_info(stack[0])


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
# search_input = input()
# keywords = input_to_keywords(search_input)

# search_type = 1
# search_input = '剧情 OR 安迪 AND 下狱'
search_type = 2
search_input = '诺贝尔文学奖 AND 苏联'
if (search_type == 1):
    search_in_movielist(search_input)
else:
    search_in_booklist(search_input)
