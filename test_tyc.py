from word_cut_jieba import word_cut0
from tyc import tyc
import pandas as pd
import re
import jieba

def tyc0(string1):
    # tongyici_tihuan.txt是同义词表，每行是一系列同义词，用tab分割
    # 1读取同义词表：并生成一个字典。
    combine_dict = {}
    for line in open("jyc.txt", "r", encoding='utf-8'):
        #print(line)
        seperate_word = line.strip().split(" ")
        #print(seperate_word)
        num = len(seperate_word)
        #print(num)
        for i in range(1, num):
            combine_dict[seperate_word[i]] = seperate_word[0]
            
    #print(combine_dict)


    # 3将语句切分
    seg_list = jieba.lcut(string1, cut_all = False)
    #print(seg_list)
    f = "/".join(seg_list)  # 不用utf-8编码的话，就不能和tongyici文件里的词对应上
    #print (f)

    # 4
    final_sentence = ""
    for word in f.split("/"):
        if word in combine_dict:
            word = combine_dict[word]
            final_sentence += word
        else:
            final_sentence += word
    # print final_sentence
    return final_sentence

# 读取表格文件
df = pd.read_excel('movie.xlsx')

data = df.iloc[2,11]
print(data)
print(word_cut0(data))

#line = "abc def ghi"


#print(line.split(" "))
#print(re.split(r'   ', line))

#string1 = '年假到底放几天？'
#print (tyc0(string1))

#print(data)

#text = '一场谋杀案使银行家安迪（蒂姆•罗宾斯TimRobbins饰）蒙冤入狱，谋杀妻子及其情人的指控将囚禁他终生。在肖申克监狱的首次现身就让监狱“大哥”瑞德（摩根•弗里曼MorganFreeman饰）对他另眼相看。瑞德帮助他搞到一把石锤和一幅女明星海报，两人渐成患难之交。很快，安迪在监狱里大显其才，担当监狱图书管理员，并利用自己的金融知识帮助监狱官避税，引起了典狱长的注意，被招致麾下帮助典狱长洗黑钱。偶然一次，他得知一名新入狱的小偷能够作证帮他洗脱谋杀罪。燃起一丝希望的安迪找到了典狱长，希望他能帮自己翻案。阴险伪善的狱长假装答应安迪，背后却派人杀死小偷，让他唯一能合法出狱的希望泯灭。沮丧的安迪并没有绝望，在一个电闪雷鸣的风雨夜，一场暗藏几十年的越狱计划让他自我救赎，重获自由！老朋友瑞德在他的鼓舞和帮助下，也勇敢地奔向自由。本片获得1995年奥斯卡10项提名，以及金球奖、土星奖等多项提名。###@'
#print(word_cut0(data))


# 将数据输出到Excel文件的指定位置
#df.iloc[2,12] = word_cut0(data)
#df1 = pd.read_excel('test.xlsx')

#df1.at[7,'关键词'] = str(word_cut0(data))



#for i in range(0, 117):
    #data = df.iloc[i,11]
    #print(data)
    #df.at[i,'关键词'] = str(word_cut0(data))
    
# 输出到Excel文件
#df.to_excel('movie.xlsx', index=False)  # index=False表示不保存索引