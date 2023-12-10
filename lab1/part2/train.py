import torch
import pickle
import numpy as np
import pandas as pd
from torch import nn
from tqdm import tqdm
from torch.utils.data import Dataset
from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
import warnings

warnings.filterwarnings('ignore')

# print(torch.cuda.is_available())
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
    print(f'Epoch {epoch}, Train loss: {output_loss_train}')

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

        print(f'Epoch {epoch}, Test loss:, {total_loss_test / (idx + 1)}')

        # 将结果转换为DataFrame
        results_df = pd.DataFrame(results, columns=['user', 'pred', 'true'])
        results_df['user'] = results_df['user'].astype(int)

outputpath = '.\part2\points.csv'
results_df.to_csv(outputpath, sep=',', index=False, header=True)
