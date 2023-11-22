import gzip
import json
import os
import pandas as pd
import csv
import time

# 开始计时
start_time = time.time()

# 设定参数:允许遍历的最大次数
max_run_times = 1000000

# 读取Movie_tag.csv文件，构建movie字典
movie_tags = pd.read_csv("./lab2/Movie_tag.csv")
movie = {
    movie_tags["id"][i]: movie_tags['tag'][i]
    for i in range(len(movie_tags))
}
template_str = "http://rdf.freebase.com/ns/"

# 构建实体_tag字典
movie_entity = {}
mvi_entities = set()  # 初始可匹配实体
mvi_entities2 = set()  # 一跳后可匹配实体
mvi_entities3 = set()  # 二跳后可匹配实体

# 记录实体相关三元组数量
entry_num = {}

# 构建实体-tag字典，同时匹配获得Freebase中对应的实体（共578个可匹配实体），加入到一跳可匹配实体
with open('./lab2/douban2fb.txt', 'rb') as f:
    for line in f:
        line = line.strip()
        parts = line.decode().split('\t')
        mvi_entities.add(parts[1])
        # mvi_entities2.add(parts[1])
        # mvi_entities3.add(parts[1])
        movie_entity[parts[1]] = {"tag": movie[int(parts[0])]}  # 构建实体_tag字典

# 将实体_tag字典转化为json格式
data = json.dumps(movie_entity, indent=1, ensure_ascii=False)
with open('movie_entity.json', 'w', newline='\n') as f:
    f.write(data)

# 提取一跳可达实体
freebase_info_fpath = "./lab2/freebase_douban.gz"  # 初始freebase
outfile1 = "./lab2/graph_1step.txt"  # 一跳输出文件
outfile2 = "./lab2/graph_2step.txt"  # 二跳输出文件
outfile3 = "./lab2/fb.txt"
# if os.path.exists(outfile1):
#     os.remove(outfile1)
wf = open(outfile1, "w")
count = 0
with gzip.open(freebase_info_fpath, 'rb') as f:
    count = 0
    for line in f:
        count += 1
        if count > max_run_times:
            break  # 超过设定上限即停止查找一跳可达实体
        # 过滤不含有template前缀的实体
        triple_parts = line.decode().split('\t')
        if (template_str not in triple_parts[0]) or (template_str
                                                     not in triple_parts[2]):
            continue
        # 头实体
        head = triple_parts[0][len(template_str) + 1:].strip('>')
        # 尾实体
        tail = triple_parts[2][len(template_str) + 1:].strip('>')

        if (head in mvi_entities) or (tail in mvi_entities):
            with open(outfile1, "ab") as wf1:
                wf1.write(line)  # 写入一跳可达实体
                if (head not in mvi_entities) and (head not in mvi_entities2):
                    mvi_entities2.add(head)
                if (tail not in mvi_entities) and (tail not in mvi_entities2):
                    mvi_entities2.add(tail)
                # 实体相关三元组计数
                if (head in entry_num):
                    entry_num[head] += 1
                else:
                    entry_num[head] = 1
                if (tail in entry_num):
                    entry_num[tail] += 1
                else:
                    entry_num[tail] = 1
print("done1")
# # 将一跳可达实体写入二跳可达的实体
# with open(outfile3, "w") as wf:
#     for line in mvi_entities2:
#         wf.write(line + '\n')

# if os.path.exists(outfile2):
#     os.remove(outfile2)
with gzip.open(freebase_info_fpath, 'rb') as f:
    count = 0
    for line in f:
        count += 1
        if count > max_run_times:
            break
        # 过滤不含有template前缀的实体
        triple_parts = line.decode().split('\t')
        if (template_str not in triple_parts[0]) or (template_str
                                                     not in triple_parts[2]):
            continue
        head = triple_parts[0][len(template_str) + 1:].strip('>')
        tail = triple_parts[2][len(template_str) + 1:].strip('>')

        if (head in mvi_entities2) or (tail in mvi_entities2):
            with open(outfile2, "ab") as wf2:
                wf2.write(line)

                if (head not in mvi_entities2) and (head not in mvi_entities3):
                    mvi_entities3.add(head)
                if (tail not in mvi_entities2) and (tail not in mvi_entities3):
                    mvi_entities3.add(tail)

                if (head in entry_num):
                    entry_num[head] += 1
                else:
                    entry_num[head] = 1
                if (tail in entry_num):
                    entry_num[tail] += 1
                else:
                    entry_num[tail] = 1
print("done2")

# 写入删选后的实体
# if os.path.exists(outfile3):
#     os.remove(outfile3)
with open(outfile3, "w") as wf:
    for line in mvi_entities3:
        if entry_num[line] >= 10:  # 频率高于10才能被选中
            wf.write(line + '\n')
            # print(line, entry_num[line])
print('done3')

# 结束时间
end_time = time.time()
print("time:", end_time - start_time)
