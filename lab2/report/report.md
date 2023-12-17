# web信息处理与应用 lab2

## 第一阶段：知识感知推荐—图谱抽取

#### 1.获取初始电影实体

构建实体-tag字典，同时匹配获得Freebase中对应的实体（共578个可匹配实体），加入到一跳可匹配实体

```python
def entry0():
    mvi_entities = set()
    with open('douban2fb.txt', 'rb') as f:
        for line in f:
            line = line.strip()
            parts = line.decode().split('\t')
            mvi_entities.add(parts[1])
            movie_entity[parts[1]] = {
                "tag": movie[int(parts[0])]
            }  # 构建实体_tag字典
    print("entry0:", len(mvi_entities))
    with open("entry0.pkl", "wb") as f:
        pickle.dump(mvi_entities, f)
```

#### 2.提取一跳实体

以578个可匹配实体为起点，通过三元组关联，提取一跳可达的全部实体，以形成新的起点集合。

```python
def step1():
    # 以 mvi_entities 为起点生成一跳子图，保存到 grarph1step.gz 文件中
    with gzip.open(outfile1, 'wb') as ans:
        with open('entry0.pkl', 'rb') as f1:
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
```

#### 3.筛选一跳所得实体

只保留至少出现在20个三元组中的实体，同时只保留出现超过50次的关系，由此得到的一跳子图包含了758个实体。

```python
def Select1():
    with gzip.open(outfile1, 'rb') as f:
        mvi_entities2 = set()
        with open("entry0.pkl", "rb") as f1:
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
        with open("entry1.pkl", "wb") as f:
            pickle.dump(mvi_entities2, f)
```

此时包含758个实体：

![image-20231210204604118](figs\image-20231210204604118.png)

#### 4.提取二跳实体

以758个可匹配实体为起点，通过三元组关联，提取一跳可达的全部实体，以形成新的起点集合。

```python
def step2():
    with gzip.open(outfile2, 'wb') as ans:
        with open('entry1.pkl', 'rb') as f1:
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
```

#### 5.筛选二跳实体

先过滤掉出现超过20000次的实体和出现少于50次的关系，然后再只保留出现次数大于15次的实体和出现大于50次的关系，对两跳子图进行清洗。

故此步需要筛选两次，第一次筛选后由于实体集合改变，故需重新生成gz文件，此时可从二跳生成的gz文件中筛选，减小运行时间。

二跳第一次筛选：

```python
def Select2():
    with gzip.open(outfile2, 'rb') as f:
        mvi_entities2 = set()
        with open("entry1.pkl", "rb") as f1:
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
        with open("entry2.pkl", "wb") as f:
            pickle.dump(mvi_entities2, f)
```

此时包含50231562个实体：

![image-20231210204710588](figs\image-20231210204710588.png)

生成新的gz文件：

```python
def step3():
    with gzip.open(outfile3, 'wb') as ans:
        with open('entry2.pkl', 'rb') as f1:
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
```

二跳后第二次筛选：

```python
def Select3():
    with gzip.open(outfile3, 'rb') as f:
        mvi_entities2 = set()
        with open("entry2.pkl", "rb") as f1:
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
        print("entry3:", len(mvi_entities2))
        with open("entry3.pkl", "wb") as f:
            pickle.dump(mvi_entities2, f)
```

最终包含17711个实体：

![image-20231210211311481](figs\image-20231210211311481.png)

## 第二阶段：