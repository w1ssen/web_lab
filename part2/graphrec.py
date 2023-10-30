import torch
import pickle
import numpy as np
import pandas as pd
from torch import nn
from tqdm import tqdm
from utils import collate_fn
from graph_rec_model import GraphRec
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import ndcg_score

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
device
'''
这段代码的作用是读取保存的CSV文件并创建用户和图书的索引映射。

1. `loaded_data = pd.read_csv('data\\book_score.csv')`读取名为`book_score.csv`的CSV文件，并将其存储在变量`loaded_data`中。这个CSV文件包含了评分数据。

2. `print(loaded_data)`打印加载的数据，将其显示在控制台上。

3. `create_id_mapping`函数定义了一个函数，用于创建ID到索引的映射字典。它接受一个ID列表作为参数。

4. `unique_ids = sorted(set(id_list))`从ID列表中删除重复项并创建一个排序的列表。`set(id_list)`将ID列表转换为集合，去除了重复的ID，然后`sorted()`函数对集合进行排序，将结果存储在`unique_ids`中。

5. `id_to_idx = {id: idx for idx, id in enumerate(unique_ids, start = 1)}`创建将原始ID映射到连续索引的字典。`enumerate(unique_ids, start = 1)`将`unique_ids`中的元素与连续的索引配对，`start = 1`表示索引从1开始。然后使用字典推导式将原始ID映射到相应的索引，将结果存储在`id_to_idx`中。

6. `idx_to_id = {idx: id for id, idx in id_to_idx.items()}`创建将连续索引映射回原始ID的字典。使用字典推导式将索引映射回原始ID，将结果存储在`idx_to_id`中。

7. `user_ids = loaded_data['User'].unique()`获取加载数据中的所有用户ID，并使用`unique()`函数去除重复的ID。

8. `book_ids = loaded_data['Book'].unique()`获取加载数据中的所有图书ID，并使用`unique()`函数去除重复的ID。

9. `user_to_idx, idx_to_user = create_id_mapping(user_ids)`调用`create_id_mapping`函数创建用户ID到索引的映射字典，将结果分别存储在`user_to_idx`和`idx_to_user`中。

10. `book_to_idx, idx_to_book = create_id_mapping(book_ids)`调用`create_id_mapping`函数创建图书ID到索引的映射字典，将结果分别存储在`book_to_idx`和`idx_to_book`中。
'''

# 读loaded_data取保存的 CSV 文件
loaded_data = pd.read_csv('part2\\data\\book_score.csv')

# 显示加载的数据
print(loaded_data)


def create_id_mapping(id_list):
    # 从ID列表中删除重复项并创建一个排序的列表
    unique_ids = sorted(set(id_list))

    # 创建将原始ID映射到连续索引的字典
    id_to_idx = {id: idx for idx, id in enumerate(unique_ids, start=1)}

    # 创建将连续索引映射回原始ID的字典
    idx_to_id = {idx: id for id, idx in id_to_idx.items()}

    return id_to_idx, idx_to_id


user_ids = loaded_data['User'].unique()
book_ids = loaded_data['Book'].unique()

user_to_idx, idx_to_user = create_id_mapping(user_ids)
book_to_idx, idx_to_book = create_id_mapping(book_ids)
'''
这段代码的作用是根据用户和图书的索引映射，将原始数据转换为以用户和图书为分组的列表形式。

1. `u_items_list, i_users_list = [(0, 0)], [(0, 0)]`初始化两个列表`u_items_list`和`i_users_list`，分别用于存储用户和图书的评分数据。初始时，列表中包含一个元组`(0, 0)`，这是为了保持索引和ID的对应关系。

2. `loaded_data['user_map'] = loaded_data['User'].map(user_to_idx)`使用`map()`函数将原始数据中的用户ID映射为索引，并将结果存储在`loaded_data`数据框的新列`user_map`中。

3. `loaded_data['book_map'] = loaded_data['Book'].map(book_to_idx)`使用`map()`函数将原始数据中的图书ID映射为索引，并将结果存储在`loaded_data`数据框的新列`book_map`中。

4. `grouped_user = loaded_data.groupby('user_map')`将`loaded_data`数据框按照`user_map`列进行分组，得到一个以用户索引为分组的数据框。

5. `grouped_book = loaded_data.groupby('book_map')`将`loaded_data`数据框按照`book_map`列进行分组，得到一个以图书索引为分组的数据框。

6. `for user, group in tqdm(grouped_user):`遍历按用户索引分组后的数据框。`tqdm`函数用于在循环中显示进度条。

7. `books = group['book_map'].tolist()`从当前用户分组中获取图书索引，并将其转换为列表形式。

8. `rates = group['Rate'].tolist()`从当前用户分组中获取评分，并将其转换为列表形式。

9. `u_items_list.append([(book, rate) for book, rate in zip(books, rates)])`将当前用户的图书索引和评分组成的元组列表添加到`u_items_list`中。使用`zip()`函数将图书索引和评分一一对应，并使用列表推导式将它们组合成元组。

10. `for book, group in tqdm(grouped_book):`遍历按图书索引分组后的数据框。

11. `users = group['user_map'].tolist()`从当前图书分组中获取用户索引，并将其转换为列表形式。

12. `rates = group['Rate'].tolist()`从当前图书分组中获取评分，并将其转换为列表形式。

13. `i_users_list.append([(user, rate) for user, rate in zip(users, rates)])`将当前图书的用户索引和评分组成的元组列表添加到`i_users_list`中。使用`zip()`函数将用户索引和评分一一对应，并使用列表推导式将它们组合成元组。
'''

u_items_list, i_users_list = [(0, 0)], [(0, 0)]
loaded_data['user_map'] = loaded_data['User'].map(user_to_idx)
loaded_data['book_map'] = loaded_data['Book'].map(book_to_idx)

# 按映射后的用户 ID 分组
grouped_user = loaded_data.groupby('user_map')
grouped_book = loaded_data.groupby('book_map')

# 遍历排序后的分组
for user, group in tqdm(grouped_user):
    books = group['book_map'].tolist()
    rates = group['Rate'].tolist()

    u_items_list.append([(book, rate) for book, rate in zip(books, rates)])

for book, group in tqdm(grouped_book):
    users = group['user_map'].tolist()
    rates = group['Rate'].tolist()

    i_users_list.append([(user, rate) for user, rate in zip(users, rates)])
'''
这段代码的作用是读取社交关系数据，并将其转换为以用户为分组的列表形式。

1. `contact = {}`初始化一个空字典`contact`，用于存储用户之间的社交关系。

2. `with open('data\Contacts.txt', 'r') as f:`打开名为`Contacts.txt`的文件，并将其内容读取到变量`f`中。

3. `for line in f:`遍历文件中的每一行。

4. `user, friends = line.strip().split(':')`将当前行的内容按冒号进行分割，分割后的第一个元素为用户，第二个元素为该用户的朋友列表。

5. `if int(user) in user_to_idx:`判断当前用户是否在用户索引映射字典`user_to_idx`中。

6. `friends_list = [user_to_idx[int(friend)] for friend in friends.split(',') if int(friend) in user_to_idx]`将朋友列表转换为整数列表，并且只保留在用户索引映射字典中存在的朋友。

7. `contact[user_to_idx[int(user)]] = friends_list`将当前用户的索引作为键，朋友列表作为值，添加到`contact`字典中。

8. `contact_sorted = {k: v for k, v in sorted(contact.items())}`对`contact`字典按键进行排序，并将排序后的结果存储在`contact_sorted`字典中。

9. `u_users_list, u_users_items_list = [0], [[(0, 1)]]`初始化两个列表`u_users_list`和`u_users_items_list`，分别用于存储用户之间的社交关系和用户之间的图书评分数据。初始时，列表中包含一个元素0和一个元组`(0, 1)`，这是为了保持索引和ID的对应关系。

10. `for user, friends in tqdm(contact_sorted.items()):`遍历按用户索引排序后的社交关系字典。

11. `u_users_list.append(friends)`将当前用户的朋友列表添加到`u_users_list`中。

12. `u_users_items_list.append([u_items_list[uid] for uid in friends])`将当前用户的朋友的图书评分数据添加到`u_users_items_list`中。根据朋友的索引，从之前生成的`u_items_list`中获取对应的图书评分数据。
'''

# 初始化一个空字典来存储社交关系
contact = {}

# 打开文件并读取内容
with open('part2\data\Contacts.txt', 'r') as f:
    for line in f:
        # 分割每一行的内容
        user, friends = line.strip().split(':')
        # 将朋友列表转换为整数列表
        if int(user) in user_to_idx:
            friends_list = [
                user_to_idx[int(friend)] for friend in friends.split(',')
                if int(friend) in user_to_idx
            ]
            # 将朋友列表添加到字典中
            contact[user_to_idx[int(user)]] = friends_list

contact_sorted = {k: v for k, v in sorted(contact.items())}
# 打印字典的内容
print(contact_sorted)

u_users_list, u_users_items_list = [0], [[(0, 1)]]

# 按顺序遍历字典
for user, friends in tqdm(contact_sorted.items()):
    u_users_list.append(friends)
    u_users_items_list.append([u_items_list[uid] for uid in friends])
'''
这段代码定义了一个自定义的数据集类`BookRatingDataset`，用于加载和处理图书评分数据。

1. `def __init__(self, data, user_to_idx, book_to_idx, u_items_list, u_users_list, u_users_items_list, i_users_list):`定义了类的构造函数，接受以下参数：
   - `data`：包含图书评分数据的DataFrame。
   - `user_to_idx`：用户索引映射字典，将用户ID映射为索引。
   - `book_to_idx`：图书索引映射字典，将图书ID映射为索引。
   - `u_items_list`：按用户索引分组的图书评分数据列表。
   - `u_users_list`：按用户索引分组的用户之间的社交关系列表。
   - `u_users_items_list`：按用户索引分组的用户朋友的图书评分数据列表。
   - `i_users_list`：按图书索引分组的用户图书评分数据列表。

2. `self.data = data`将传入的图书评分数据赋值给类的`data`属性。

3. `self.user_to_idx = user_to_idx`将传入的用户索引映射字典赋值给类的`user_to_idx`属性。

4. `self.book_to_idx = book_to_idx`将传入的图书索引映射字典赋值给类的`book_to_idx`属性。

5. `self.u_items_list = u_items_list`将传入的按用户索引分组的图书评分数据列表赋值给类的`u_items_list`属性。

6. `self.u_users_list = u_users_list`将传入的按用户索引分组的用户之间的社交关系列表赋值给类的`u_users_list`属性。

7. `self.u_users_items_list = u_users_items_list`将传入的按用户索引分组的用户朋友的图书评分数据列表赋值给类的`u_users_items_list`属性。

8. `self.i_users_list = i_users_list`将传入的按图书索引分组的用户图书评分数据列表赋值给类的`i_users_list`属性。

9. `def __getitem__(self, index):`定义了类的`__getitem__`方法，用于获取指定索引的数据。
   - `row = self.data.iloc[index]`获取指定索引的图书评分数据行。
   - `user = self.user_to_idx[row['User']]`根据用户ID从用户索引映射字典中获取用户索引。
   - `book = self.book_to_idx[row['Book']]`根据图书ID从图书索引映射字典中获取图书索引。
   - `rating = row['Rate'].astype(np.float32)`获取评分，并将其转换为浮点数类型。
   - `u_items = self.u_items_list[user]`根据用户索引从按用户索引分组的图书评分数据列表中获取该用户的图书评分数据。
   - `u_users = self.u_users_list[user]`根据用户索引从按用户索引分组的用户之间的社交关系列表中获取该用户的社交关系数据。
   - `u_users_items = self.u_users_items_list[user]`根据用户索引从按用户索引分组的用户朋友的图书评分数据列表中获取该用户朋友的图书评分数据。
   - `i_users = self.i_users_list[book]`根据图书索引从按图书索引分组的用户图书评分数据列表中获取该图书的用户评分数据。
   - 返回一个元组，包含了用户索引、图书索引和评分，以及相关的用户图书评分数据。

10. `def __len__(self):`定义了类的`__len__`方法，用于获取数据集的长度。
   - 返回图书评分数据的行数，即数据集的长度。
'''


class BookRatingDataset(Dataset):

    def __init__(self, data, user_to_idx, book_to_idx, u_items_list,
                 u_users_list, u_users_items_list, i_users_list):
        self.data = data
        self.user_to_idx = user_to_idx
        self.book_to_idx = book_to_idx
        self.u_items_list = u_items_list
        self.u_users_list = u_users_list
        self.u_users_items_list = u_users_items_list
        self.i_users_list = i_users_list

    def __getitem__(self, index):
        row = self.data.iloc[index]
        user = self.user_to_idx[row['User']]
        book = self.book_to_idx[row['Book']]
        rating = row['Rate'].astype(np.float32)
        u_items = self.u_items_list[user]
        u_users = self.u_users_list[user]
        u_users_items = self.u_users_items_list[user]
        i_users = self.i_users_list[book]

        return (user, book, rating), u_items, u_users, u_users_items, i_users

    def __len__(self):
        return len(self.data)


'''
这段代码定义了一个函数`compute_ndcg`，用于按用户分组计算NDCG（Normalized Discounted Cumulative Gain）指标。

1. `def compute_ndcg(group):`定义了函数`compute_ndcg`，接受一个参数`group`，表示按用户分组的数据。

2. `true_ratings = group['true'].tolist()`从`group`中获取`true`列的值，并将其转换为列表形式，表示真实的评分。

3. `pred_ratings = group['pred'].tolist()`从`group`中获取`pred`列的值，并将其转换为列表形式，表示预测的评分。

4. `return ndcg_score([true_ratings], [pred_ratings], k = 50)`调用`ndcg_score`函数计算NDCG指标，传入真实评分列表和预测评分列表作为参数，同时指定参数`k`为50，表示只考虑前50个评分。

5. 返回计算得到的NDCG指标值。
'''


# 按用户分组计算NDCG
def compute_ndcg(group):
    true_ratings = group['true'].tolist()
    pred_ratings = group['pred'].tolist()
    return ndcg_score([true_ratings], [pred_ratings], k=50)


'''
这段代码主要进行了以下操作：

1. `train_test_split(loaded_data, test_size=0.5, random_state=42)`使用`train_test_split`函数将加载的数据集`loaded_data`划分为训练集和测试集，其中测试集占总数据的50%，随机种子为42。划分后的训练集和测试集分别存储在`train_data`和`test_data`中。

2. `train_dataset = BookRatingDataset(train_data, user_to_idx, book_to_idx, u_items_list, u_users_list, u_users_items_list, i_users_list)`创建训练集的数据集对象`train_dataset`，使用`BookRatingDataset`类，传入训练集数据`train_data`以及相关的索引和数据列表。

3. `test_dataset = BookRatingDataset(test_data, user_to_idx, book_to_idx, u_items_list, u_users_list, u_users_items_list, i_users_list)`创建测试集的数据集对象`test_dataset`，使用`BookRatingDataset`类，传入测试集数据`test_data`以及相关的索引和数据列表。

4. `train_dataloader = DataLoader(train_dataset, batch_size=4096, shuffle=True, collate_fn = collate_fn, drop_last = True)`创建训练集的数据加载器`train_dataloader`，使用`DataLoader`类，传入训练集的数据集对象`train_dataset`，设置批量大小为4096，打乱数据顺序，使用`collate_fn`函数进行数据的批量处理，丢弃最后一个不完整的批次。

5. `test_dataloader = DataLoader(test_dataset, batch_size=4096, shuffle=False, collate_fn = collate_fn, drop_last = True)`创建测试集的数据加载器`test_dataloader`，使用`DataLoader`类，传入测试集的数据集对象`test_dataset`，设置批量大小为4096，不打乱数据顺序，使用`collate_fn`函数进行数据的批量处理，丢弃最后一个不完整的批次。

6. `num_users = loaded_data['User'].nunique()`获取数据集中的用户数量。

7. `num_books = loaded_data['Book'].nunique()`获取数据集中的图书数量。

8. `embedding_dim = 32`设置嵌入维度为32，用于表示用户和图书的特征向量。

9. `model = GraphRec(num_users + 1, num_books + 1, 7, embedding_dim).to(device)`创建`GraphRec`模型的实例`model`，传入用户数量、图书数量、社交关系维度、嵌入维度等参数，并将模型移动到指定的设备上。

10. `criterion = nn.MSELoss()`定义损失函数为均方误差（MSE）损失。

11. `optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=1e-5)`定义优化器为Adam优化器，传入模型的参数、学习率和权重衰减参数。
'''

# 划分训练集和测试集
train_data, test_data = train_test_split(loaded_data,
                                         test_size=0.5,
                                         random_state=42)

# 创建训练集和测试集的数据集对象
train_dataset = BookRatingDataset(train_data, user_to_idx, book_to_idx,
                                  u_items_list, u_users_list,
                                  u_users_items_list, i_users_list)
test_dataset = BookRatingDataset(test_data, user_to_idx, book_to_idx,
                                 u_items_list, u_users_list,
                                 u_users_items_list, i_users_list)

# 创建训练集和测试集的数据加载器
train_dataloader = DataLoader(train_dataset,
                              batch_size=4096,
                              shuffle=True,
                              collate_fn=collate_fn,
                              drop_last=True)
test_dataloader = DataLoader(test_dataset,
                             batch_size=4096,
                             shuffle=False,
                             collate_fn=collate_fn,
                             drop_last=True)

num_users = loaded_data['User'].nunique()  # 假设有1000个用户
num_books = loaded_data['Book'].nunique()  # 假设有500本书
embedding_dim = 32

model = GraphRec(num_users + 1, num_books + 1, 7, embedding_dim).to(device)
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=1e-5)
'''
这段代码是模型的训练和测试的过程，具体解释如下：

1. `num_epochs = 20`设置训练的轮数为20。

2. `for epoch in range(num_epochs):`开始迭代训练轮数。

3. `model.train()`将模型设置为训练模式，启用Batch Normalization和Dropout。

4. `total_loss_train, total_loss_test = 0.0, 0.0`初始化训练集和测试集的总损失为0。

5. `for idx, (user_ids, book_ids, ratings, u_items, u_users, u_users_items, i_users) in tqdm(enumerate(train_dataloader)):`
   - 使用`enumerate(train_dataloader)`遍历训练集的数据加载器，获取批次索引`idx`和批次数据`user_ids, book_ids, ratings, u_items, u_users, u_users_items, i_users`。
   - `optimizer.zero_grad()`清零优化器的梯度。
   - `predictions = model(user_ids.to(device), book_ids.to(device), u_items.to(device), u_users.to(device), u_users_items.to(device), i_users.to(device))`使用模型预测用户对图书的评分。
   - `loss = criterion(predictions.squeeze(1), ratings.to(device))`计算预测值和真实值之间的损失。
   - `loss.backward()`反向传播计算梯度。
   - `optimizer.step()`更新模型的参数。
   - `total_loss_train += loss.item()`累加训练集的损失。

6. `output_loss_train = total_loss_train / (idx + 1)`计算平均训练集损失。

7. `model.eval()`将模型设置为评估模式，禁用Batch Normalization和Dropout。

8. `with torch.no_grad():`关闭梯度计算。

9. `for idx, (user_ids, item_ids, true_ratings, u_items, u_users, u_users_items, i_users) in enumerate(test_dataloader):`
   - 使用`enumerate(test_dataloader)`遍历测试集的数据加载器，获取批次索引`idx`和批次数据`user_ids, item_ids, true_ratings, u_items, u_users, u_users_items, i_users`。
   - `pred_ratings = model(user_ids.to(device), book_ids.to(device), u_items.to(device), u_users.to(device), u_users_items.to(device), i_users.to(device))`使用模型预测用户对图书的评分。
   - `loss = criterion(pred_ratings.squeeze(1), ratings.to(device))`计算预测值和真实值之间的损失。
   - `total_loss_test += loss.item()`累加测试集的损失。
   - 将批次数据转换为NumPy数组，并将用户ID、预测评分和真实评分合并为一个2D数组。
   - 将这个2D数组添加到结果列表中。

10. `results = np.vstack(results)`将结果列表转换为一个大的NumPy数组。

11. `results_df = pd.DataFrame(results, columns=['user', 'pred', 'true'])`将结果转换为DataFrame，列名为'user'、'pred'和'true'。

12. `results_df['user'] = results_df['user'].astype(int)`将'user'列的数据类型转换为整数。

13. `ndcg_scores = results_df.groupby('user').apply(compute_ndcg)`计算每个用户的NDCG得分。

14. `avg_ndcg = ndcg_scores.mean()`计算平均NDCG得分。

15. `print(f'Epoch {epoch}, Loss: {output_loss_train}, MSE loss:, {total_loss_test / (idx + 1)}, Average NDCG: {avg_ndcg}')`打印当前轮数的训练集损失、测试集损失和平均NDCG得分。'''

num_epochs = 20

for epoch in range(num_epochs):
    model.train()
    total_loss_train, total_loss_test = 0.0, 0.0

    for idx, (user_ids, book_ids, ratings, u_items, u_users, u_users_items,
              i_users) in tqdm(enumerate(train_dataloader)):
        # 使用user_ids, book_ids, ratings进行训练

        optimizer.zero_grad()

        predictions = model(user_ids.to(device), book_ids.to(device),
                            u_items.to(device), u_users.to(device),
                            u_users_items.to(device), i_users.to(device))
        loss = criterion(predictions.squeeze(1), ratings.to(device))

        loss.backward()
        optimizer.step()

        total_loss_train += loss.item()

        # if idx % 100 == 0:
        #     print(f'Step {idx}, Loss: {loss.item()}')
    output_loss_train = total_loss_train / (idx + 1)

    results = []
    model.eval()

    with torch.no_grad():
        for idx, (user_ids, item_ids, true_ratings, u_items, u_users,
                  u_users_items, i_users) in enumerate(test_dataloader):
            pred_ratings = model(user_ids.to(device), book_ids.to(device),
                                 u_items.to(device), u_users.to(device),
                                 u_users_items.to(device), i_users.to(device))

            loss = criterion(pred_ratings.squeeze(1), ratings.to(device))
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
            f'Epoch {epoch}, Loss: {output_loss_train}, MSE loss:, {total_loss_test / (idx + 1)}, Average NDCG: {avg_ndcg}'
        )
