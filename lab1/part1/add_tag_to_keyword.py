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


# df1 = pd.read_csv('part1/data/Book_tag.csv').fillna('')
# movie_id_1 = df1['Id'].tolist()
# movie_tag = df1['Tag'].tolist()
# df2 = pd.read_excel('part1/data/book.xlsx').fillna('')
# movie_id_2 = df2['序号'].tolist()
# # movie_type = df2['类型'].tolist()
# movie_id_key = df2['关键词'].tolist()
# # 循环查找需要修改的地方
# for i in range(len(movie_id_2)):
#     movie_id_key[i] = movie_id_key[i].replace(' ', '')

#     # 对指定单元格修改,方括号中的参数第一个是行号，第二个是列名
#     df2.at[i, '关键词'] = movie_id_key[i]
#     # print(movie_id_key[index])
# # 写回文件，一定不能忘了这一步
# df2.to_excel('part1/data/book.xlsx', index=False)
