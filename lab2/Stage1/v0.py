import gzip
import json
import os
import pandas as pd
import csv
import time
import pickle
import gzip
from tqdm import tqdm

# 设定参数:允许遍历的最大次数
max_run_times = 1000000

# # 读取Movie_tag.csv文件，构建movie字典
# movie_tags = pd.read_csv("Movie_tag.csv")
# movie = {
#     movie_tags["id"][i]: movie_tags['tag'][i]
#     for i in range(len(movie_tags))
# }
template_str = "http://rdf.freebase.com/ns/"

# 构建实体_tag字典
movie_entity = {}
# mvi_entities = set()  # 初始可匹配实体
# mvi_entities2 = set()  # 一跳后可匹配实体
# mvi_entities3 = set()  # 二跳后可匹配实体

# 记录实体相关三元组数量

entry_num = {}


def entry0():
    mvi_entities = set()
    # 构建实体-tag字典，同时匹配获得Freebase中对应的实体（共578个可匹配实体），加入到一跳可匹配实体
    with open('lab2/Stage1/douban2fb.txt', 'rb') as f:
        for line in f:
            line = line.strip()
            parts = line.decode().split('\t')
            mvi_entities.add(parts[1])
            movie_entity[parts[1]] = {
                "tag": movie[int(parts[0])]
            }  # 构建实体_tag字典
    print("entry0:", len(mvi_entities))
    with open("lab2/Stage1/entry0.pkl", "wb") as f:
        pickle.dump(mvi_entities, f)


def step1():
    # 以 mvi_entities 为起点生成一跳子图，保存到 grarph1step.gz 文件中
    with gzip.open(outfile1, 'wb') as ans:
        with open('lab2/Stage1/entry0.pkl', 'rb') as f1:
            mvi_entities = pickle.load(f1)
        with gzip.open(freebase_info_fpath, 'rb') as f:
            for line in tqdm(f, total=395577070):
                # if count > max_run_times:
                #     break  # 超过设定上限即停止查找一跳可达实体
                line = line.strip()
                triple_parts = line.decode().split('\t')
                if (template_str not in triple_parts[0]
                        or template_str not in triple_parts[1]
                        or template_str not in triple_parts[2]):
                    continue
                # 头实体
                head = triple_parts[0][len(template_str) + 1:].strip('>')
                # 关系
                rel = triple_parts[1][len(template_str) + 1:].strip('>')
                # 尾实体
                tail = triple_parts[2][len(template_str) + 1:].strip('>')

                # 保存头实体在 mvi_entities 中的三元组
                if head in mvi_entities:
                    ans.write(line + b'\n')
                    # 实体相关三元组计数
                    if (head in entry_num):
                        entry_num[head] += 1
                    else:
                        entry_num[head] = 1
                    if (tail in entry_num):
                        entry_num[tail] += 1
                    else:
                        entry_num[tail] = 1
                    if (rel in entry_num):
                        entry_num[rel] += 1
                    else:
                        entry_num[rel] = 1


def Select1():
    with gzip.open(outfile1, 'rb') as f:
        mvi_entities2 = set()
        with open("lab2/Stage1/entry0.pkl", "rb") as f1:
            mvi_entities = pickle.load(f1)
        for line in tqdm(f, total=395577070):
            triple_parts = line.decode().split('\t')[:3]
            # 头实体
            head = triple_parts[0][len(template_str) + 1:].strip('>')
            # 关系
            rel = triple_parts[1][len(template_str) + 1:].strip('>')
            # 尾实体
            tail = triple_parts[2][len(template_str) + 1:].strip('>')
            if ((head in mvi_entities or entry_num[head] > 20)
                    and (entry_num[tail] > 20)
                    and (rel in mvi_entities or entry_num[rel] > 50)):
                mvi_entities2.add(head)
                mvi_entities2.add(tail)
        print("entry1:", len(mvi_entities2))
        with open("lab2/Stage1/entry1.pkl", "wb") as f:
            pickle.dump(mvi_entities2, f)


entry_num2 = {}  # 二跳元素存储


def step2():
    with gzip.open(outfile2, 'wb') as ans:
        with open('lab2/Stage1/entry1.pkl', 'rb') as f1:
            mvi_entities = pickle.load(f1)
        with gzip.open(freebase_info_fpath, 'rb') as f:
            for line in tqdm(f, total=395577070):
                # if count > max_run_times:
                #     break  # 超过设定上限即停止查找一跳可达实体
                line = line.strip()
                triple_parts = line.decode().split('\t')
                if (template_str not in triple_parts[0]
                        or template_str not in triple_parts[1]
                        or template_str not in triple_parts[2]):
                    continue
                # 头实体
                head = triple_parts[0][len(template_str) + 1:].strip('>')
                # 关系
                rel = triple_parts[1][len(template_str) + 1:].strip('>')
                # 尾实体
                tail = triple_parts[2][len(template_str) + 1:].strip('>')

                # 保存头实体在 mvi_entities 中的三元组
                if head in mvi_entities:
                    ans.write(line + b'\n')
                    # 实体相关三元组计数
                    if (head in entry_num2):
                        entry_num2[head] += 1
                    else:
                        entry_num2[head] = 1
                    if (tail in entry_num2):
                        entry_num2[tail] += 1
                    else:
                        entry_num2[tail] = 1
                    if (rel in entry_num2):
                        entry_num2[rel] += 1
                    else:
                        entry_num2[rel] = 1


def Select2():
    with gzip.open(outfile2, 'rb') as f:
        mvi_entities2 = set()
        with open("lab2/Stage1/entry1.pkl", "rb") as f1:
            mvi_entities = pickle.load(f1)
        for line in tqdm(f, total=395577070):
            triple_parts = line.decode().split('\t')[:3]
            # 头实体
            head = triple_parts[0][len(template_str) + 1:].strip('>')
            # 关系
            rel = triple_parts[1][len(template_str) + 1:].strip('>')
            # 尾实体
            tail = triple_parts[2][len(template_str) + 1:].strip('>')
            if ((head in mvi_entities or entry_num2[head] <= 20000)
                    and (entry_num2[tail] <= 20000)
                    and (rel in mvi_entities or entry_num2[rel] > 50)):
                mvi_entities2.add(head)
                mvi_entities2.add(tail)
        print("entry2:", len(mvi_entities2))
        with open("lab2/Stage1/entry2.pkl", "wb") as f:
            pickle.dump(mvi_entities2, f)


entry_num3 = {}  # 二跳首次筛选后元素存储


def step3():
    with gzip.open(outfile3, 'wb') as ans:
        with open('lab2/Stage1/entry2.pkl', 'rb') as f1:
            mvi_entities = pickle.load(f1)
        with gzip.open(outfile2, 'rb') as f:
            for line in tqdm(f, total=395577070):
                # if count > max_run_times:
                #     break  # 超过设定上限即停止查找一跳可达实体
                line = line.strip()
                triple_parts = line.decode().split('\t')
                if (template_str not in triple_parts[0]
                        or template_str not in triple_parts[1]
                        or template_str not in triple_parts[2]):
                    continue
                # 头实体
                head = triple_parts[0][len(template_str) + 1:].strip('>')
                # 关系
                rel = triple_parts[1][len(template_str) + 1:].strip('>')
                # 尾实体
                tail = triple_parts[2][len(template_str) + 1:].strip('>')

                # 保存头实体在 mvi_entities 中的三元组
                if head in mvi_entities:
                    ans.write(line + b'\n')
                    # 实体相关三元组计数
                    if (head in entry_num3):
                        entry_num3[head] += 1
                    else:
                        entry_num3[head] = 1
                    if (tail in entry_num3):
                        entry_num3[tail] += 1
                    else:
                        entry_num3[tail] = 1
                    if (rel in entry_num3):
                        entry_num3[rel] += 1
                    else:
                        entry_num3[rel] = 1


def Select3():
    with gzip.open('lab2/Stage1/final.gz', 'wb') as ans:
        with gzip.open(outfile3, 'rb') as f:
            mvi_entities2 = set()
            with open("lab2/Stage1/entry2.pkl", "rb") as f1:
                mvi_entities = pickle.load(f1)
            for line in tqdm(f, total=395577070):
                triple_parts = line.decode().split('\t')[:3]
                # 头实体
                head = triple_parts[0][len(template_str) + 1:].strip('>')
                # 关系
                rel = triple_parts[1][len(template_str) + 1:].strip('>')
                # 尾实体
                tail = triple_parts[2][len(template_str) + 1:].strip('>')
                if ((head in mvi_entities or entry_num3[head] > 15)
                        and (entry_num3[tail] > 15)
                        and (rel in mvi_entities or entry_num3[rel] > 50)):
                    mvi_entities2.add(head)
                    mvi_entities2.add(tail)
                    ans.write(line + b'\n')
            print("entry3:", len(mvi_entities2))
            with open("lab2/Stage1/entry3.pkl", "wb") as f:
                pickle.dump(mvi_entities2, f)


# 提取一跳可达实体
freebase_info_fpath = "lab2/Stage1/freebase_douban.gz"  # 初始freebase
outfile1 = "lab2/Stage1/graph_1step.gz"  # 一跳输出文件
outfile2 = "lab2/Stage1/graph_2step.gz"  # 二跳输出文件
outfile3 = "lab2/Stage1/graph_3step.gz"
# if os.path.exists(outfile1):
# os.remove(outfile1)
# entry0()
# 开始计时
# step1()
# Select1()
# step2()
# Select2()
step3()
Select3()
