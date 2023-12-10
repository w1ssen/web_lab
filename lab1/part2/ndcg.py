from sklearn.metrics import ndcg_score
import pandas as pd
import numpy as np


# 按用户分组计算NDCG
def compute_ndcg(group):
    true_ratings = group['true'].tolist()
    pred_ratings = group['pred'].tolist()
    return ndcg_score([true_ratings], [pred_ratings], k=50)


file = './part2/points.csv'
csv_data = pd.read_csv(file, low_memory=False)
csv_df = pd.DataFrame(csv_data)
ndcg_scores = csv_df.groupby('user').apply(compute_ndcg)
# 计算平均NDCG
avg_ndcg = ndcg_scores.mean()
print(f'Average NDCG: {avg_ndcg}')
