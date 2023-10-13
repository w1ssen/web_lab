from word_cut_jieba import word_cut0
from tyc import tyc
import pandas as pd

# 读取表格文件
df = pd.read_excel('movie.xlsx')

data = df.iloc[2,11]
#print(data)

#text = '年假到底放几天到底几天'
#print(word_cut0(text))


# 将数据输出到Excel文件的指定位置
#df.iloc[2,12] = word_cut0(data)
#df1 = pd.read_excel('test.xlsx')

#df1.at[7,'关键词'] = str(word_cut0(data))



for i in range(0, 117):
    data = df.iloc[i,11]
    #print(data)
    df.at[i,'关键词'] = str(word_cut0(data))
    
# 输出到Excel文件
df.to_excel('movie.xlsx', index=False)  # index=False表示不保存索引