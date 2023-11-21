import copy
import gzip
import json
import os

import pandas as pd
import csv

# 构建movie,tag字典
movie_tags = pd.read_csv("Movie_tag.csv")
movie = {}
for i in range(len(movie_tags)):
    movie[movie_tags["id"][i]] = movie_tags['tag'][i]

# print(movie.keys())

movie_entity = {}
mvi_entities = [] #初始可匹配实体
mvi_entities2 = [] #一跳后可匹配实体
mvi_entities3 = [] #二跳后可匹配实体
with open('douban2fb.txt', 'rb') as f:
    for line in f:
        line = line.strip()
        list1 = line.decode().split('\t') # 电影ID与实体的字典
        mvi_entities.append(list1[1])
        mvi_entities2.append(list1[1])
        mvi_entities3.append(list1[1])
        movie_entity[list1[1]] = {"tag": movie[int(list1[0])]} # 构建实体_tag字典
# 将实体_tag字典转化为json格式
data = json.dumps(movie_entity, indent=1, ensure_ascii=False)
# print(data)
with open('movie_entity.json', 'w', newline='\n') as f:
    f.write(data)
f.close()


freebase_info_fpath = "freebase_douban.gz" #初始freebase
outfile1 = "graph_1step.txt" #一跳输出文件
outfile2 = "graph_2step.txt" #二跳输出文件

template_str = "http://rdf.freebase.com/ns/"
os.remove(outfile1)
wf = open(outfile1,"ab")
count = 0
with gzip.open(freebase_info_fpath,'rb') as f:
    for line in f:
        count = count + 1
        if count >100000 :
            break
        line_info = line.decode().split('\t')
        # 过滤不含有template前缀的实体
        if (template_str not in line_info[0]) or (template_str not in line_info[2]):
            continue
        print(line)
        # 提取"http://rdf.freebase.com/ns/"之后的内容:
        # 头实体
        head = line_info[0][len(template_str)+1:].strip('>')
        # 尾实体
        tail = line_info[2][len(template_str)+1:].strip('>')
        if (head in mvi_entities) or (tail in mvi_entities):
            wf.write(line)
            if (head not in mvi_entities) and (head not in mvi_entities2):
                mvi_entities2.append(head)
            if (tail not in mvi_entities) and (tail not in mvi_entities2):
                mvi_entities2.append(tail)
wf.close()       

print(mvi_entities2)
print("done1")

template_str = "http://rdf.freebase.com/ns/"
os.remove(outfile2)
wf = open(outfile2,"ab")
count = 0
with gzip.open(freebase_info_fpath,'rb') as f:
    for line in f:
        count = count + 1
        if count >100000 :
            break
        line_info = line.decode().split('\t')
        # 过滤不含有template前缀的实体
        if (template_str not in line_info[0]) or (template_str not in line_info[2]):
            continue
        print(line)
        # 提取"http://rdf.freebase.com/ns/"之后的内容:
        # 头实体
        head = line_info[0][len(template_str)+1:].strip('>')
        # 尾实体
        tail = line_info[2][len(template_str)+1:].strip('>')
        if (head in mvi_entities2) or (tail in mvi_entities2):
            wf.write(line)
            if (head not in mvi_entities2) and (head not in mvi_entities3):
                mvi_entities3.append(head)
            if (tail not in mvi_entities2) and (tail not in mvi_entities3):
                mvi_entities3.append(tail)
wf.close()       
print(mvi_entities3)
print("done2")

wf=open("fb.txt","w")
 
for line in mvi_entities3:
    wf.write(line+'\n')
wf.close()