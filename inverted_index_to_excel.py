import pandas as pd

df1 = pd.read_excel('movie.xlsx').fillna('')
ids = df1['序号'].tolist()
keys = df1['关键词'].tolist()
Inverted_Index = dict()
id_list = []

# # 创建倒排表
# def create_inverted_index():
#     for i in range(len(keys)):
#         keywords = keys[i].split(',')  # 将每个id的关键词用逗号切割，变成一个列表变量
#         for item in keywords:  # 遍历id的每个关键词
#             if item not in Inverted_Index:
#                 Inverted_Index[item] = []  # 不在倒排表中的关键词新建列表
#             Inverted_Index[item].append(str(ids[i]))  # 在倒排表对应的关键词位置添加id
#     for item in Inverted_Index:
#         id_list.append({'key': item, 'id': ','.join(Inverted_Index[item])})


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
    df.to_excel('movie_list.xlsx', index=False)


# 利用倒排表来搜索
def search_in_inverted_index():
    pass


create_inverted_index()
list_to_excel()
