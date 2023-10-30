import torch
import pickle
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
loaded_data = pd.read_csv('data\selected_book_top_1200_data_tag.csv')
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
with open('data/tag_embedding_dict.pkl', 'wb') as f:
    pickle.dump(tag_embedding_dict, f)

# 从二进制文件中读取映射表
with open('data/tag_embedding_dict.pkl', 'rb') as f:
    tag_embedding_dict = pickle.load(f)

# 读loaded_data取保存的 CSV 文件
loaded_data = pd.read_csv('data\\book_score.csv')

# 显示加载的数据
print(loaded_data)
'''
这段代码定义了两个类和一个函数。

1. `BookRatingDataset`类是一个自定义的数据集类，用于加载和处理评分数据。它的构造函数`__init__`接受四个参数：`data`是原始评分数据，`user_to_idx`是用户ID到索引的映射字典，`book_to_idx`是图书ID到索引的映射字典，`tag_embedding_dict`是图书标签的向量表示字典。`__len__`方法返回数据集的长度，`__getitem__`方法根据给定的索引返回数据集中的一个样本。在`__getitem__`方法中，首先根据索引获取数据集中的一行，然后将用户ID和图书ID转换为对应的索引，将评分转换为浮点数，最后获取图书标签的向量表示。返回的样本包括用户索引、图书索引、评分和图书标签的向量表示。

2. `MatrixFactorization`类是一个矩阵分解模型，用于预测用户对图书的评分。它的构造函数`__init__`接受四个参数：`num_users`是用户的数量，`num_books`是图书的数量，`embedding_dim`是嵌入维度，`hidden_state`是隐藏状态的维度。在`__init__`方法中，定义了用户和图书的嵌入层，以及将隐藏状态映射到嵌入维度的线性层和输出层。`forward`方法接受用户索引、图书索引和图书标签的向量表示作为输入，通过嵌入层获取用户和图书的嵌入表示，将图书标签的向量表示通过线性层进行投影，然后将图书嵌入和投影后的图书标签嵌入相加，最后通过点积运算和汇总得到预测的评分。

3. `create_id_mapping`函数用于创建ID到索引的映射字典。它接受一个ID列表作为参数，首先去除重复的ID并进行排序，然后创建一个将原始ID映射到连续索引的字典，同时创建一个将连续索引映射回原始ID的字典。最后返回这两个映射字典。

4. `compute_ndcg`函数用于按用户分组计算NDCG（归一化折损累计增益）。它接受一个分组数据作为参数，其中包含了真实评分和预测评分。首先将真实评分和预测评分转换为列表形式，然后调用`ndcg_score`函数计算NDCG值，最后返回计算得到的NDCG值。
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


# 按用户分组计算NDCG
def compute_ndcg(group):
    true_ratings = group['true'].tolist()
    pred_ratings = group['pred'].tolist()
    return ndcg_score([true_ratings], [pred_ratings], k=50)


'''
这段代码是一个推荐系统的训练过程。下面是对代码的解释：

1. `user_ids = loaded_data['User'].unique()`：获取数据中所有不重复的用户ID。
2. `book_ids = loaded_data['Book'].unique()`：获取数据中所有不重复的图书ID。
3. `user_to_idx, idx_to_user = create_id_mapping(user_ids)`：创建用户ID到索引的映射关系。
4. `book_to_idx, idx_to_book = create_id_mapping(book_ids)`：创建图书ID到索引的映射关系。
5. `train_data, test_data = train_test_split(loaded_data, test_size=0.5, random_state=42)`：将数据划分为训练集和测试集，比例为0.5，随机种子为42。
6. `train_dataset = BookRatingDataset(train_data, user_to_idx, book_to_idx, tag_embedding_dict)`：创建训练集的数据集对象，该对象用于加载训练数据，并将用户ID、图书ID和标签嵌入字典传递给数据集对象。
7. `test_dataset = BookRatingDataset(test_data, user_to_idx, book_to_idx, tag_embedding_dict)`：创建测试集的数据集对象，该对象用于加载测试数据，并将用户ID、图书ID和标签嵌入字典传递给数据集对象。
8. `train_dataloader = DataLoader(train_dataset, batch_size=4096, shuffle=True, drop_last=True)`：创建训练集的数据加载器，用于批量加载训练数据，每批次大小为4096，打乱顺序，并丢弃最后不完整的批次。
9. `test_dataloader = DataLoader(test_dataset, batch_size=4096, shuffle=False, drop_last=True)`：创建测试集的数据加载器，用于批量加载测试数据，每批次大小为4096，不打乱顺序，并丢弃最后不完整的批次。
10. `num_users = loaded_data['User'].nunique()`：获取数据中不重复的用户数量。
11. `num_books = loaded_data['Book'].nunique()`：获取数据中不重复的图书数量。
12. `embedding_dim, hidden_state = 32, 768`：设置嵌入维度和隐藏状态的维度。
13. `model = MatrixFactorization(num_users, num_books, embedding_dim, hidden_state).to(device)`：创建一个矩阵分解模型，该模型用于推荐系统的训练，输入参数为用户数量、图书数量、嵌入维度和隐藏状态的维度，并将模型移动到指定的设备上。
14. `criterion = nn.MSELoss()`：创建均方误差损失函数，用于衡量模型预测值与真实值之间的差距。
15. `optimizer = torch.optim.Adam(model.parameters(), lr=0.01)`：创建Adam优化器，用于更新模型的参数，学习率为0.01。

'''

user_ids = loaded_data['User'].unique()
book_ids = loaded_data['Book'].unique()

user_to_idx, idx_to_user = create_id_mapping(user_ids)
book_to_idx, idx_to_book = create_id_mapping(book_ids)

# 划分训练集和测试集
train_data, test_data = train_test_split(loaded_data,
                                         test_size=0.5,
                                         random_state=42)

# 创建训练集和测试集的数据集对象
train_dataset = BookRatingDataset(train_data, user_to_idx, book_to_idx,
                                  tag_embedding_dict)
test_dataset = BookRatingDataset(test_data, user_to_idx, book_to_idx,
                                 tag_embedding_dict)

# 创建训练集和测试集的数据加载器
train_dataloader = DataLoader(train_dataset,
                              batch_size=4096,
                              shuffle=True,
                              drop_last=True)
test_dataloader = DataLoader(test_dataset,
                             batch_size=4096,
                             shuffle=False,
                             drop_last=True)

num_users = loaded_data['User'].nunique()
num_books = loaded_data['Book'].nunique()
embedding_dim, hidden_state = 32, 768

model = MatrixFactorization(num_users, num_books, embedding_dim,
                            hidden_state).to(device)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)
'''
这段代码是推荐系统的训练过程的一部分，包括了模型的训练和评估。下面是对代码的解释：

1. `num_epochs = 20`：设置训练的总轮数为20。
2. `lambda_u, lambda_b = 0.001, 0.001`：设置正则化项的权重。
3. `for epoch in range(num_epochs):`：对每个轮数进行循环训练。
4. `model.train()`：将模型设置为训练模式，启用批量归一化和dropout。
5. `total_loss_train, total_loss_test = 0.0, 0.0`：初始化训练集和测试集的总损失为0。
6. `for idx, (user_ids, book_ids, ratings, tag_embedding) in tqdm(enumerate(train_dataloader)):`：对训练集的每个批次进行循环训练。
7. `optimizer.zero_grad()`：将优化器的梯度置零，清除之前的梯度。
8. `predictions = model(user_ids.to(device), book_ids.to(device), tag_embedding.squeeze(1).to(device))`：使用模型对用户ID、图书ID和标签嵌入进行预测。
9. `loss = criterion(predictions, ratings.to(device)) + lambda_u * model.user_embeddings.weight.norm(2) + lambda_b * model.book_embeddings.weight.norm(2)`：计算损失函数，包括预测值与真实值之间的差距以及正则化项。
10. `loss.backward()`：计算损失函数关于模型参数的梯度。
11. `optimizer.step()`：更新模型的参数。
12. `total_loss_train += loss.item()`：累加训练集的总损失。
13. `output_loss_train = total_loss_train / (idx + 1)`：计算平均训练集损失。
14. `results = []`：创建一个空列表，用于存储评估结果。
15. `model.eval()`：将模型设置为评估模式，禁用批量归一化和dropout。
16. `with torch.no_grad():`：在评估过程中，不需要计算梯度。
17. `for idx, (user_ids, item_ids, true_ratings, tag_embedding) in enumerate(test_dataloader):`：对测试集的每个批次进行循环评估。
18. `pred_ratings = model(user_ids.to(device), item_ids.to(device), tag_embedding.squeeze(1).to(device))`：使用模型对用户ID、图书ID和标签嵌入进行预测。
19. `loss = criterion(pred_ratings, ratings.to(device))`：计算损失函数，包括预测值与真实值之间的差距。
20. `total_loss_test += loss.item()`：累加测试集的总损失。
21. `user_ids_np = user_ids.long().cpu().numpy().reshape(-1, 1)`：将用户ID转换为numpy数组，并进行相应的处理。
22. `pred_ratings_np = pred_ratings.cpu().numpy().reshape(-1, 1)`：将预测评分转换为numpy数组，并进行相应的处理。
23. `true_ratings_np = true_ratings.numpy().reshape(-1, 1)`：将真实评分转换为numpy数组，并进行相应的处理。
24. `batch_results = np.column_stack((user_ids_np, pred_ratings_np, true_ratings_np))`：将用户ID、预测评分和真实评分合并为一个二维数组。
25. `results.append(batch_results)`：将批次的结果添加到结果列表中。
26. `results = np.vstack(results)`：将结果列表转换为一个大的numpy数组。
27. `results_df = pd.DataFrame(results, columns=['user', 'pred', 'true'])`：将结果转换为DataFrame，包括用户ID、预测评分和真实评分。
28. `results_df['user'] = results_df['user'].astype(int)`：将用户ID转换为整数类型。
29. `ndcg_scores = results_df.groupby('user').apply(compute_ndcg)`：计算每个用户的NDCG评分。
30. `avg_ndcg = ndcg_scores.mean()`：计算平均NDCG评分。
31. `print(f'Epoch {epoch}, Train loss: {output_loss_train}, Test loss:, {total_loss_test / (idx + 1)}, Average NDCG: {avg_ndcg}')`：打印每个轮数的训练集损失、测试集损失和平均NDCG评分。

'''

num_epochs = 20
lambda_u, lambda_b = 0.001, 0.001

for epoch in range(num_epochs):
    model.train()
    total_loss_train, total_loss_test = 0.0, 0.0

    for idx, (user_ids, book_ids, ratings,
              tag_embedding) in tqdm(enumerate(train_dataloader)):
        # 使用user_ids, book_ids, ratings进行训练

        optimizer.zero_grad()

        predictions = model(user_ids.to(device), book_ids.to(device),
                            tag_embedding.squeeze(1).to(device))
        loss = criterion(
            predictions,
            ratings.to(device)) + lambda_u * model.user_embeddings.weight.norm(
                2) + lambda_b * model.book_embeddings.weight.norm(2)

        loss.backward()
        optimizer.step()

        total_loss_train += loss.item()

        # if idx % 100 == 0:
        #     print(f'Step {idx}, Loss: {loss.item()}')

    output_loss_train = total_loss_train / (idx + 1)

    results = []
    model.eval()

    with torch.no_grad():
        for idx, (user_ids, item_ids, true_ratings,
                  tag_embedding) in enumerate(test_dataloader):
            pred_ratings = model(user_ids.to(device), item_ids.to(device),
                                 tag_embedding.squeeze(1).to(device))

            loss = criterion(pred_ratings, ratings.to(device))
            total_loss_test += loss.item()

            # 将结果转换为 numpy arrays
            user_ids_np = user_ids.long().cpu().numpy().reshape(-1, 1)
            pred_ratings_np = pred_ratings.cpu().numpy().reshape(-1, 1)
            true_ratings_np = true_ratings.numpy().reshape(-1, 1)

            # 将这三个 arrays 合并成一个 2D array
            batch_results = np.column_stack(
                (user_ids_np, pred_ratings_np, true_ratings_np))

            # 将这个 2D array 添加到 results
            results.append(batch_results)

        # 将结果的 list 转换为一个大的 numpy array
        results = np.vstack(results)

        # 将结果转换为DataFrame
        results_df = pd.DataFrame(results, columns=['user', 'pred', 'true'])
        results_df['user'] = results_df['user'].astype(int)

        ndcg_scores = results_df.groupby('user').apply(compute_ndcg)

        # 计算平均NDCG
        avg_ndcg = ndcg_scores.mean()
        print(
            f'Epoch {epoch}, Train loss: {output_loss_train}, Test loss:, {total_loss_test / (idx + 1)}, Average NDCG: {avg_ndcg}'
        )
