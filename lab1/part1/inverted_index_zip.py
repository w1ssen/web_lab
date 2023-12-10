import pickle
import pandas as pd
import os
import time

id_list = []  # 倒排索引


# 每100个关键词为一组，构建压缩索引表
def zip_inverted_index():
    if os.path.exists('part1/data/block_metadata.pkl'):  # 存在压缩的索引表后，不再构建压缩索引表
        return
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

    with open('part1/data/block_metadata.pkl', 'wb') as metadata_file:
        pickle.dump(block_metadata, metadata_file)


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


# 顺序检索
def search_in_list(keyword):
    if (keyword in movie_list_key):
        index = movie_list_key.index(keyword)
        ids = eval(movie_list_id[index])
        return ids
    else:
        return


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
