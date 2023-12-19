# web信息处理与应用 lab2

## 第一阶段：知识感知推荐——图谱抽取

### 实验目标：

在本次实验中，我们要求各位同学从公开图谱中匹配指定电影对应的实体，并抽取合适的部分图谱，按照规则对抽取到的图谱进行处理

1. 根据实验一中提供的电影ID列表，匹配获得Freebase中对应的实体（共578个可匹配实体）
2. 以578个可匹配实体为起点，通过三元组关联，提取一跳可达的全部实体，以形成新的起点集合。重复若干次该步骤，并将所获得的全部实体及对应三元组合并用于下一阶段实验的知识图谱子图
3. 

### 实验过程：

#### 1.获取初始电影实体

构建实体-tag字典，同时匹配获得Freebase中对应的实体（共578个可匹配实体），加入到一跳可匹配实体

```python
# 读取 id 列表
import pickle

origin_movies = set()
def entry0():

    # 构建实体-tag字典，同时匹配获得Freebase中对应的实体（共578个可匹配实体），加入到一跳可匹配实体
    with open('douban2fb.txt', 'rb') as f:
        for line in f:
            line = line.strip()
            parts = line.decode().split('\t')
            origin_movies.add(parts[1])
    print("entry0:", len(origin_movies))
    with open("entry0.pkl", "wb") as f:
        pickle.dump(origin_movies, f)


entry0()
```

通过二进制读写文件可以大幅缩短运行时间。最终得到起始实体的数量是578。同时把这578个实体存在集合中，用于后续的筛选

![image-20231218214759402](figs\image-20231218214759402.png)

#### 2.获取一跳子图，并对实体和关系计数

以578个可匹配实体为起点，通过三元组关联，提取一跳可达的全部实体，以形成新的起点集合。

```python
import gzip
import pickle
from tqdm import tqdm

template_str = "http://rdf.freebase.com/ns/m."
template_str2 = "http://rdf.freebase.com/ns/"
freebase_info_fpath = "freebase_douban.gz"  # 初始freebase
outfile1 = "graph_1step.gz"  # 一跳输出文件
outfile2 = "graph_2step.gz"  # 二跳输出文件
outfile3 = "graph_3step.gz"

entry_num = {}
def step1():
    # 以 mvi_entities 为起点生成一跳子图，保存到 grarph1step.gz 文件中
    with gzip.open(outfile1, 'wb') as ans:
        with open('entry0.pkl', 'rb') as f1:
            mvi_entities = pickle.load(f1)
        with gzip.open(freebase_info_fpath, 'rb') as f:

            for line in tqdm(f, total=395577070):
                line = line.strip()
                triple_parts = line.decode().split('\t')
                if (template_str not in triple_parts[0]
                        or template_str2 not in triple_parts[1]
                        or template_str not in triple_parts[2]):
                    continue
                # 头实体
                head = triple_parts[0][len(template_str2) + 1:].strip('>')
                
                # 关系
                rel = triple_parts[1][len(template_str2) + 1:].strip('>')
                # 尾实体
                tail = triple_parts[2][len(template_str2) + 1:].strip('>')

                # 保存头实体在 mvi_entities 中的三元组
                if head in mvi_entities:
                    ans.write(f'{head}\t{rel}\t{tail}\n'.encode('utf-8'))
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


step1()
print(entry_num)
```

根据我们前期筛选的情况和给出的578个电影实体的情况来看，电影对应的实体都是以"http://rdf.freebase.com/ns/m."为前缀的，因此将这个字符串用于头实体尾实体的前缀筛选，同时用"http://rdf.freebase.com/ns/"筛选关系。

筛选以m.为前缀的实体的另外一个原因是，如果不做如下筛选，二跳会得到很多三元组(上亿)，而非电影的实体对我们没什么帮助。

将筛选出来的三元组写入gzip文件，并对实体、关系计数，用于后面的一跳子图筛选

#### 3.筛选一跳子图，提取一跳实体

只保留至少出现在20个三元组中的实体，同时只保留出现超过50次的关系，由此得到的一跳子图包含了728个实体。

```python
def Select1():
    with gzip.open(outfile1, 'rb') as f:
        mvi_entities2 = set()
        with open("entry0.pkl", "rb") as f1:
            mvi_entities = pickle.load(f1)
        count = 0
        for line in tqdm(f, total=110759):
            triple_parts = line.decode().split('\t')[:3]
            # 头实体
            head = triple_parts[0]
            # 关系
            rel = triple_parts[1]
            # 尾实体
            tail = triple_parts[2][:-1] # 删除末尾的\n
            if ((head in mvi_entities or entry_num[head] > 20)
                    and (entry_num[tail] > 20)
                    and (rel in mvi_entities or entry_num[rel] > 50)):
                mvi_entities2.add(head)
                mvi_entities2.add(tail)
            count += 1
        print("1step:", count)
        print("entry1:", len(mvi_entities2))
        with open("entry1.pkl", "wb") as f:
            pickle.dump(mvi_entities2, f)


Select1()
```

根据上一步得到的实体、关系计数，筛选上一步得到的三元组，并将三元组中的头尾实体保存起来，用于获取二跳子图

同时需要注意，如果头尾实体属于初始的578个实体，也需要保存，以保证最后得到的实体集合包含这578个实体

此时包含728个实体，110759个三元组

![image-20231218223042337](figs\image-20231218223042337.png)

#### 4.获取二跳子图，并对实体和关系计数

以728个可匹配实体为起点，通过三元组关联，提取一跳可达的全部实体，以形成新的起点集合。

```python
entry_num2 = {}  # 二跳元素存储


def step2():
    with gzip.open(outfile2, 'wb') as ans:
        with open('entry1.pkl', 'rb') as f1:
            mvi_entities = pickle.load(f1)
        with gzip.open(freebase_info_fpath, 'rb') as f:
            for line in tqdm(f, total=395577070):
                line = line.strip()
                triple_parts = line.decode().split('\t')
                if (template_str not in triple_parts[0]
                        or template_str2 not in triple_parts[1]
                        or template_str not in triple_parts[2]):
                    continue
                # 头实体
                head = triple_parts[0][len(template_str2) + 1:].strip('>')
                # 关系
                rel = triple_parts[1][len(template_str2) + 1:].strip('>')
                # 尾实体
                tail = triple_parts[2][len(template_str2) + 1:].strip('>')

                # 保存头实体在 mvi_entities 中的三元组
                if head in mvi_entities:
                    ans.write(f'{head}\t{rel}\t{tail}\n'.encode('utf-8'))
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


step2()
```

二跳子图的获取方式和一跳子图类似，不再赘述

#### 5.第一次筛选二跳实体

先过滤掉出现超过20000次的实体和出现少于50次的关系对两跳子图进行第一次清洗。

```python
def Select2():
    count = 0
    with gzip.open(outfile2, 'rb') as f:
        mvi_entities2 = set()
        with open("entry1.pkl", "rb") as f1:
            mvi_entities = pickle.load(f1)
        for line in tqdm(f, total=1119177):
            triple_parts = line.decode().split('\t')[:3]
            # 头实体
            head = triple_parts[0]
            # 关系
            rel = triple_parts[1]
            # 尾实体
            tail = triple_parts[2][:-1]
            if ((head in mvi_entities or entry_num2[head] <= 20000)
                    and (entry_num2[tail] <= 20000)
                    and (rel in mvi_entities or entry_num2[rel] > 50)):
                mvi_entities2.add(head)
                mvi_entities2.add(tail)
                count += 1
        print('step2:',count)
        print("entry2:", len(mvi_entities2))
        with open("entry2.pkl", "wb") as f:
            pickle.dump(mvi_entities2, f)


Select2()
```

此时包含67多万个实体，111多万个三元组。后面还要继续筛选

![image-20231218223443985](figs\image-20231218223443985.png)

#### 6.保存第一次筛选过后的二跳子图

筛选过实体后，还需要对三元组进行筛选，因此保存第一次筛选过后的三元组

```python
def Select2():
    count = 0
    with gzip.open(outfile2, 'rb') as f:
        mvi_entities2 = set()
        with open("entry1.pkl", "rb") as f1:
            mvi_entities = pickle.load(f1)
        for line in tqdm(f, total=1119177):
            triple_parts = line.decode().split('\t')[:3]
            # 头实体
            head = triple_parts[0]
            # 关系
            rel = triple_parts[1]
            # 尾实体
            tail = triple_parts[2][:-1]
            if ((head in mvi_entities or entry_num2[head] <= 20000)
                    and (entry_num2[tail] <= 20000)
                    and (rel in mvi_entities or entry_num2[rel] > 50)):
                mvi_entities2.add(head)
                mvi_entities2.add(tail)
                count += 1
        print('step2:',count)
        print("entry2:", len(mvi_entities2))
        with open("entry2.pkl", "wb") as f:
            pickle.dump(mvi_entities2, f)


Select2()
```

具体的筛选方式是查看头尾实体是否都在上一步得到的实体集合中

#### 7.二次筛选二跳子图

第一次筛选之后，还需要筛选掉出现次数少于15次的实体和出现次数少于50次的关系。

由于每次筛选后，对于实体、关系的计数也会发生改变，因此需要多次筛选，直到实体数量不变。

筛选函数：

```python
def Select(triplets):
    entry_num = {}
    for triplet in triplets:
        if (triplet[0] not in entry_num):
            entry_num[triplet[0]] = 0
        entry_num[triplet[0]] += 1
        if (triplet[2] not in entry_num):
            entry_num[triplet[2]] = 0
        entry_num[triplet[2]] += 1
        if (triplet[1] not in entry_num):
            entry_num[triplet[1]] = 0
        entry_num[triplet[1]] += 1
    ans = []
    for triplet in triplets:
        if ((triplets[0] in origin_movies or entry_num[triplet[0]]>15)and(triplets[2] in origin_movies or entry_num[triplet[2]]>15)and(entry_num[triplet[1]]>50)):
            ans.append(triplet)
    return ans
```

二次筛选二跳子图：

```python
import gzip
import pickle
from tqdm import tqdm


freebase_info_fpath = "freebase_douban.gz"  # 初始freebase
outfile1 = "graph_1step.gz"  # 一跳输出文件
outfile2 = "graph_2step.gz"  # 二跳输出文件
outfile3 = "graph_3step.gz"


def Select3():
    before_selected = []
    with gzip.open(outfile3, 'rb') as f:
        for line in tqdm(f, total=1116079):
            triple_parts = line.decode().split('\t')[:3]
            # 头实体
            head = triple_parts[0]
            # 关系
            rel = triple_parts[1]
            # 尾实体
            tail = triple_parts[2][:-1]
            before_selected.append((head, rel, tail))
        selected = Select(before_selected)
        print('筛选后:', len(selected), '筛选前:', len(before_selected))

    while len(selected) < len(before_selected):  # 迭代筛选
        before_selected = selected
        selected = Select(before_selected)
        print('筛选后:', len(selected), '筛选前:', len(before_selected))

    with gzip.open('final.gz', 'wb') as ans:
        count = 0
        mvi_entities2 = set()
        for triplet in selected:
            mvi_entities2.add(triplet[0])
            mvi_entities2.add(triplet[2])
            ans.write(f'{triplet[0]}\t{triplet[1]}\t{triplet[2]}\n'.encode('utf-8'))
        print("final:", len(selected))
        print("entry3:", len(mvi_entities2))
        with open("entry3.pkl", "wb") as f:
            pickle.dump(mvi_entities2, f)


Select3()
```

最终包含2319个实体，47006个三元组，符合助教给出的子图规模

![image-20231218232804156](figs\image-20231218232804156.png)

## 第二阶段：知识感知推荐——图谱推荐

### 实验目标：

在我们给出的训练集文件 train.txt 和测试集文件 test.txt 中，提供了每个用户打分≥4 的电影集合，这些电影被视为该用户的正样本，其中每一行对应一个用户，每一行的第一个值为该用户的 ID，余下的值为该用户的正样本 ID 集合。此外我们将用户的 ID 和电影的 ID 映射到从 0 开始的索引值，映射关系分别保存在 user_id_map.txt 和 movie_id_map.txt 这两个文件中。通过图谱实体 ID 到电影 ID 之间的映射关系（douban2fb.txt）以及电影 ID 到从 0 开始的索引值之间的映射关系（movie_id_map.txt），第一阶段抽取的电影图谱能够轻松地整合到推荐系统中。

1. 根据映射关系，将电影实体的ID 映射到[0, 𝑛𝑢𝑚 𝑜𝑓 𝑚𝑜𝑣𝑖𝑒𝑠)范围内。将图谱中的其余实体映射到[𝑛𝑢𝑚 𝑜𝑓 𝑚𝑜𝑣𝑖𝑒𝑠, 𝑛𝑢𝑚 𝑜𝑓 𝑒𝑛𝑡𝑖𝑡𝑖𝑒𝑠)范围内，将关系映射到[0, 𝑛𝑢𝑚 𝑜𝑓 𝑟𝑒𝑙𝑎𝑡𝑖𝑜𝑛𝑠)范围内。再根据这些映射关系，将第一阶段获得的电影图谱映射为由索引值组成的三元组，即（头实体索引值，关系索引值，尾实体索引值），并保存到 stage2\data\Douban\kg_final.txt 文件中。
2. 熟悉 baseline 的框架代码，包括数据加载部分（stage2\data_loader 文件夹下的 loader_base.py 和 loader_KG_free.py），模型搭建部分（stage2\model文件夹下的 KG_free.py ）， 以及模型训练部分（ stage2 文件夹下main_KG_free.py）
3. 基于 baseline 框架代码，完成基于图谱嵌入的模型，包括数据加载部分（stage2\data_loader 文件夹下的 loader_Embedding_based.py）和模型搭建部分（stage2\model 文件夹下的 Embedding_based.py）的相关代码模块
4. 本次实验的评价指标采用 Recall@5，NDCG@5，Recall@10 和 NDCG@10。需要分析设计的图谱嵌入方法对知识感知推荐性能的影响，同时需要对比分析知识感知推荐与 MF 的实验结果。

### 实验过程：

#### 1.构建三元组映射

根据给出的578个实体的相关信息，先构建出578个实体的映射：

```python
import gzip
from tqdm import tqdm

file3 = 'data/Douban/movie_id_map.txt'  # 电影ID的映射
file4 = 'data/Douban/douban2fb.txt'  # 实体-Id映射
outfile2 = 'data/Douban/entry-mapping.pkl'  # 实体映射


def movie_entry_mapping():  # 将电影实体的ID 映射到[0, 𝑛𝑢𝑚 𝑜𝑓 𝑚𝑜𝑣𝑖𝑒𝑠)范围内,0-577
    ids = []
    with open(file3, 'r') as f2:
        for line in f2:
            id = line.strip().split()[0]
            ids.append(id)
    with open(file4, 'r') as f3:
        for line in f3:
            id = line.strip().split()[0]
            entry = line.strip().split()[1]
            if (id in ids):
                idx = ids.index(id)
                ids[idx] = entry
    with open(outfile2, 'wb') as f1:
        count = 0
        for id in ids:
            f1.write(f'{count}\t\t{id}\n'.encode('utf-8'))
            count += 1

movie_entry_mapping()
```

然后是遍历我们阶段一得到的47006个三元组，对578个实体以外的实体赋予编号，并对关系编号，从而实现映射关系。

```python
file1 = '../../Stage1/final.gz'
outfile1 = 'data/Douban/kg_final.txt'  # 三元组映射
outfile2 = 'data/Douban/entry-mapping.pkl'  # 实体映射
outfile3 = 'data/Douban/relation-mapping.pkl'  # 关系映射


def entry_index_mapping():
    entries = []  # 通过按顺序加载到list中，来实现映射功能
    relations = []  # 关系映射
    with open(outfile2, 'rb') as f1:  # 已经映射过的一部分实体
        for line in f1:
            entry = line.decode().strip().split()[1]
            entries.append(entry)
    triples = []
    with open(outfile1, 'w') as f1:
        with gzip.open(file1, 'rb') as f:
            for line in tqdm(f, total=47006):
                triple_parts = line.decode().strip().split('\t')
                if (triple_parts[0] not in entries):
                    entries.append(triple_parts[0])
                if (triple_parts[1] not in relations):
                    relations.append(triple_parts[1])
                if (triple_parts[2] not in entries):
                    entries.append(triple_parts[2])
                idx1 = entries.index(triple_parts[0])
                idx2 = relations.index(triple_parts[1])
                idx3 = entries.index(triple_parts[2])
                f1.write(f'{idx1} {idx2} {idx3}\n')
    with open(outfile2, 'wb') as f1:
        count = 0
        for entry in entries:
            f1.write(f'{count}\t\t{entry}\n'.encode('utf-8'))
            count += 1
    with open(outfile3, 'wb') as f2:
        count = 0
        for relation in relations:
            f2.write(f'{count}\t\t{relation}\n'.encode('utf-8'))
            count += 1


entry_index_mapping()
```

通过遍历所有的三元组，对实体和关系进行编号，从而实现三元组到编号的映射。

结果如下：

![image-20231218235123933](figs\image-20231218235123933.png)

#### 2.熟悉代码框架

通过查阅资料和解读代码熟悉了 baseline 的框架代码，包括数据加载部分（stage2\data_loader 文件夹下的 loader_base.py 和 loader_KG_free.py），模型搭建部分（stage2\model文件夹下的 KG_free.py ）， 以及模型训练部分（ stage2 文件夹下的main_KG_free.py）。

#### 3.完成基于图谱嵌入的模型







#### 4.不同图谱嵌入方法结果对比

KG_free运行结果：

```c
2023-12-19 16:31:27,241 - root - INFO - Best CF Evaluation: Epoch 0040 | Precision [0.2966, 0.2532], Recall [0.0660, 0.1094], NDCG [0.3110, 0.2829]
```

多任务+相加的注入实体信息：

```c
2023-12-19 16:56:10,549 - root - INFO - Best CF Evaluation: Epoch 0040 | Precision [0.3016, 0.2535], Recall [0.0690, 0.1128], NDCG [0.3108, 0.2819]
```

多任务+相乘的注入实体信息：

```c
Best CF Evaluation: Epoch 0050 | Precision [0.2899, 0.2575], Recall [0.0646, 0.1110], NDCG [0.3055, 0.2848]
```

多任务+拼接的注入实体信息：

```c
Best CF Evaluation: Epoch 0040 | Precision [0.3016, 0.2535], Recall [0.0690, 0.1128], NDCG [0.3107, 0.2819]
```



表格对比如下：

|                           | Recall@5 | Recall@10 | NDCG@5 | NDCG@10 |
| ------------------------- | -------- | --------- | ------ | ------- |
| MF                        | 0.0660   | 0.1094    | 0.3110 | 0.2829  |
| 多任务+相加的注入实体信息 | 0.0690   | 0.1128    | 0.3110 | 0.2819  |
| 多任务+相乘的注入实体信息 | 0.0646   | 0.1110    | 0.3055 | 0.2848  |
| 多任务+拼接的注入实体信息 | 0.0690   | 0.1128    | 0.3107 | 0.2819  |

根据数据表格，可以看出不同的图谱嵌入方法和MF在不同指标下的表现：

1. 对比不同图谱嵌入方法的性能：
   - 在Recall@5方面，多任务+相加的注入实体信息和多任务+拼接的注入实体信息方法表现相似，略优于MF和多任务+相乘的注入实体信息方法。
   - 在Recall@10方面，多任务+相加的注入实体信息和多任务+拼接的注入实体信息方法同样表现相似，略优于MF和多任务+相乘的注入实体信息方法。
   - 在NDCG@5和NDCG@10方面，多任务+相加的注入实体信息方法表现略优于其他方法，而多任务+拼接的注入实体信息方法也表现较好。

2. 对比知识感知推荐与MF的实验结果：
   - 在Recall@5和Recall@10方面，多任务+相加的注入实体信息和多任务+拼接的注入实体信息方法都略优于MF。
   - 在NDCG@5方面，多任务+相加的注入实体信息方法与MF表现相似，而多任务+拼接的注入实体信息方法略优于MF。
   - 在NDCG@10方面，MF略优于多任务+相加的注入实体信息和多任务+拼接的注入实体信息方法。

综合来看，多任务+相加的注入实体信息和多任务+拼接的注入实体信息方法在Recall@5和Recall@10方面略优于MF，而在NDCG@5方面多任务+相加的注入实体信息方法与MF表现相似，多任务+拼接的注入实体信息方法略优于MF。然而，在NDCG@10方面，MF略优于这两种方法。

因此，根据不同的评估指标和具体需求，可以选择最适合的图谱嵌入方法来进行知识感知推荐。
