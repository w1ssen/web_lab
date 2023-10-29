from tyc import tyc
from snownlp import SnowNLP
import re

def word_cut1(mytext):
    #s = SnowNLP(u'SnowNLP类似NLTK，是针对中文处理的一个Python工具库。')
    #words = s.words
    #print(words)
    
    # 文本预处理 ：去除字符剩下中文
    new_data = re.findall('[\u4e00-\u9fa5]+', mytext, re.S)
    new_data = " ".join(new_data)
    
    # 分词
    s = SnowNLP(new_data)
    words = s.words
    result_list = []
    
    # 加载停用词
    with open('stop_words.txt', encoding='utf-8') as f:
        con = f.readlines()
        stop_words = set()
        for i in con:
            i = i.replace("\n", "")   # 去掉每一行的\n
            stop_words.add(i)

    # 去除停用词 去除单字
    for word in words:
        if word not in stop_words and len(word) > 1:
            result_list.append(word) 
            
    #print(result_list)
    
    #print(tyc(result_list))
    
    new_list = list(set(tyc(result_list)))
    new_list.sort(key = tyc(result_list).index)
    
    return new_list
