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

import warnings

warnings.filterwarnings('ignore')


# 按用户分组计算NDCG
def compute_ndcg(group):
    true_ratings = group['true'].tolist()
    pred_ratings = group['pred'].tolist()
    return ndcg_score([true_ratings], [pred_ratings], k=50)


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
from embedding import BookRatingDataset, MatrixFactorization, create_id_mapping

# 从二进制文件中读取映射表
with open('part2/data/tag_embedding_dict.pkl', 'rb') as f:
    tag_embedding_dict = pickle.load(f)

# 读loaded_data取保存的 CSV 文件
loaded_data = pd.read_csv('part2\\data\\book_score.csv')

# 显示加载的数据
print(loaded_data)

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
            # print((user_ids_np, pred_ratings_np, true_ratings_np))

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
