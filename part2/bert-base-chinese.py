import torch
import numpy as np
import pandas as pd
from torch import nn
from tqdm import tqdm
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import ndcg_score

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

from transformers import BertTokenizer, BertModel
import torch

tokenizer = BertTokenizer.from_pretrained('bert-base-chinese')
model = BertModel.from_pretrained('bert-base-chinese').cuda()

# 读取和处理CSV文件中的数据，并使用BERT模型对标签进行编码，最终将编码后的标签向量保存为二进制文件。
# 使用pandas库的`read_csv`函数从CSV文件中读取数据，并将其存储在`loaded_data`变量中。
loaded_data = pd.read_csv('part2\data\selected_book_top_1200_data_tag.csv')
# 创建一个空字典，用于存储标签的向量表示。
tag_embedding_dict = {}
# 在此代码块中，禁用梯度计算，以提高代码的运行效率。
with torch.no_grad():
    # 对`loaded_data`中的每一行进行迭代。
    for index, rows in tqdm(loaded_data.iterrows()):
        # 将标签列表转换为字符串
        tags_str = " ".join(rows.Tags)
        # print(tags_str)
        # 使用BERT模型的tokenizer对标签文本进行编码。参数truncation=True指示tokenizer在需要时截断文本，return_tensors='pt'表示返回PyTorch张量格式的编码结果。
        inputs = tokenizer(tags_str, truncation=True, return_tensors='pt')
        # print(inputs)
        # 使用BERT模型model来对输入的编码结果进行处理，通过inputs.input_ids、inputs.token_type_ids和inputs.attention_mask传入模型。这将生成一个关于标签的嵌入表示。
        outputs = model(inputs.input_ids.cuda(), inputs.token_type_ids.cuda(),
                        inputs.attention_mask.cuda())
        # 使用最后一层的平均隐藏状态作为标签的向量表示
        tag_embedding = outputs.last_hidden_state.mean(dim=1).cpu()
        tag_embedding_dict[rows.Book] = tag_embedding

import pickle

# 将映射表存储为二进制文件
with open('part2/data/tag_embedding_dict.pkl', 'wb') as f:
    pickle.dump(tag_embedding_dict, f)

# 从二进制文件中读取映射表
with open('part2/data/tag_embedding_dict.pkl', 'rb') as f:
    tag_embedding_dict = pickle.load(f)

# 读loaded_data取保存的 CSV 文件
loaded_data = pd.read_csv('part2\\data\\book_score.csv')

# 显示加载的数据
print(loaded_data)