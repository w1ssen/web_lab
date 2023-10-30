from part1.word_cut_jieba import word_cut0
from part1.word_cut_snownlp import word_cut1
import pandas as pd

# 读取表格文件
df = pd.read_excel('book_com.xlsx')

#data = df.iloc[2,11]
#print(data)

#text = '年假到底放几天到底几天'
#print(word_cut0(text))


# 将数据输出到Excel文件的指定位置
#df.iloc[2,12] = word_cut0(data)
#df1 = pd.read_excel('test.xlsx')

#df1.at[7,'关键词'] = str(word_cut0(data))

#data = df.iloc[1195,10]
    #print(', '.join(word_cut0(data)))
#df.at[1195,'关键词'] = ', '.join(word_cut0(data))
#data = df.iloc[1198,10]
    #print(', '.join(word_cut0(data)))
#df.at[1198,'关键词'] = ', '.join(word_cut0(data))
#data = df.iloc[1200,10]
    #print(', '.join(word_cut0(data)))
#df.at[1200,'关键词'] = ', '.join(word_cut0(data))

for i in range(0, 100):
    #print(i)
    data = df.iloc[i,0]
    #print('\n\n 原文:')
    #print(data)
    #print('\n jieba:')
    #print(', '.join(word_cut0(data)))
    #print('\n snow:')
    #print(', '.join(word_cut1(data)))
    #df.at[i,'jieba'] = ', '.join(word_cut0(data))
    df.at[i,'snownpl'] = ', '.join(word_cut1(data))
    
# 输出到Excel文件
df.to_excel('book_com.xlsx', index=False)  # index=False表示不保存索引