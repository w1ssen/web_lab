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
file1 = '../../Stage1/final.gz'
outfile1 = 'data/Douban/kg_final.txt'  # 三元组映射
outfile2 = 'data/Douban/entry-mapping.pkl'  # 实体映射
outfile3 = 'data/Douban/relation-mapping.pkl'  # 关系映射


# with open(file1, 'rb') as f1:
#     count = 0
#     for line in f1:
#         if count % 1000000 == 0:
#             print(count)
#         count += 1
#     print(count)
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
            for line in tqdm(f, total=2382802):
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
                f1.write(f'{idx1}\t{idx2}\t{idx3}')
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
