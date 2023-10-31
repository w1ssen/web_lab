bert-base-chinese.py:使用BERT模型对中文标签进行编码并生成pkl文件

embedding.py:训练时用的类和数据集模型

train.py:根据映射表pkl训练，导出最终points.csv

points.csv:用户对作品的实际打分和预测打分

ndcg.py:导入points.csv，计算每个用户各自的ndcg并对全体用户的ndcg取平均

