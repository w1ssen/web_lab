import torch
from torch import nn
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
'''
这段代码定义了两个类和一个函数。

1. `BookRatingDataset`类是一个自定义的数据集类，用于加载和处理评分数据。它的构造函数`__init__`接受四个参数：`data`是原始评分数据，`user_to_idx`是用户ID到索引的映射字典，`book_to_idx`是图书ID到索引的映射字典，`tag_embedding_dict`是图书标签的向量表示字典。`__len__`方法返回数据集的长度，`__getitem__`方法根据给定的索引返回数据集中的一个样本。在`__getitem__`方法中，首先根据索引获取数据集中的一行，然后将用户ID和图书ID转换为对应的索引，将评分转换为浮点数，最后获取图书标签的向量表示。返回的样本包括用户索引、图书索引、评分和图书标签的向量表示。

2. `MatrixFactorization`类是一个矩阵分解模型，用于预测用户对图书的评分。它的构造函数`__init__`接受四个参数：`num_users`是用户的数量，`num_books`是图书的数量，`embedding_dim`是嵌入维度，`hidden_state`是隐藏状态的维度。在`__init__`方法中，定义了用户和图书的嵌入层，以及将隐藏状态映射到嵌入维度的线性层和输出层。`forward`方法接受用户索引、图书索引和图书标签的向量表示作为输入，通过嵌入层获取用户和图书的嵌入表示，将图书标签的向量表示通过线性层进行投影，然后将图书嵌入和投影后的图书标签嵌入相加，最后通过点积运算和汇总得到预测的评分。

3. `create_id_mapping`函数用于创建ID到索引的映射字典。它接受一个ID列表作为参数，首先去除重复的ID并进行排序，然后创建一个将原始ID映射到连续索引的字典，同时创建一个将连续索引映射回原始ID的字典。最后返回这两个映射字典。

'''


class BookRatingDataset(Dataset):
    # 类的构造函数，接受四个参数：data: 包含用户、书籍、评分和标签信息的数据帧（DataFrame）。user_to_idx: 一个将用户名称映射到索引的字典。book_to_idx: 一个将书籍名称映射到索引的字典。tag_embedding_dict: 一个包含书籍标签嵌入向量的字典，其中书籍名称是键，嵌入向量是值。
    def __init__(self, data, user_to_idx, book_to_idx, tag_embedding_dict):
        self.data = data
        self.user_to_idx = user_to_idx
        self.book_to_idx = book_to_idx
        self.tag_embedding_dict = tag_embedding_dict

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        row = self.data.iloc[index]
        user = self.user_to_idx[row['User']]
        book = self.book_to_idx[row['Book']]
        rating = row['Rate'].astype('float32')
        text_embedding = self.tag_embedding_dict.get(row['Book'])
        return user, book, rating, text_embedding


class MatrixFactorization(nn.Module):

    def __init__(self, num_users, num_books, embedding_dim, hidden_state):
        super(MatrixFactorization, self).__init__()
        self.user_embeddings = nn.Embedding(num_users, embedding_dim)
        self.book_embeddings = nn.Embedding(num_books, embedding_dim)
        self.linear_embedding = nn.Linear(hidden_state, embedding_dim)
        self.output = nn.Linear(embedding_dim, 6)

    def forward(self, user, book, tag_embedding):
        user_embedding = self.user_embeddings(user)
        book_embedding = self.book_embeddings(book)
        tag_embedding_proj = self.linear_embedding(tag_embedding)
        book_intergrate = book_embedding + tag_embedding_proj
        return (user_embedding * book_intergrate).sum(dim=1)


def create_id_mapping(id_list):
    # 从ID列表中删除重复项并创建一个排序的列表
    unique_ids = sorted(set(id_list))

    # 创建将原始ID映射到连续索引的字典
    id_to_idx = {id: idx for idx, id in enumerate(unique_ids)}

    # 创建将连续索引映射回原始ID的字典
    idx_to_id = {idx: id for id, idx in id_to_idx.items()}

    return id_to_idx, idx_to_id