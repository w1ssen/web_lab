from part1.tyc import tyc
import jieba
import re

def word_cut0(mytext):
    #jieba.load_userdict('exception.txt')  
    jieba.initialize()  # 初始化jieba
    
    # 文本预处理 ：去除字符剩下中文
    new_data = re.findall('[\u4e00-\u9fa5]+', mytext, re.S)
    new_data = " ".join(new_data)
    
    # 分词
    seg_list_exact = jieba.lcut(new_data)
    result_list = []
    
    # 加载停用词
    with open('stop_words.txt', encoding='utf-8') as f:
        con = f.readlines()
        stop_words = set()
        for i in con:
            i = i.replace("\n", "")   # 去掉每一行的\n
            stop_words.add(i)

    # 去除停用词 去除单字
    for word in seg_list_exact:
        if word not in stop_words and len(word) > 1:
            result_list.append(word) 
            
    #print(result_list)
    
    #print(tyc(result_list))
    
    new_list = list(set(tyc(result_list)))
    new_list.sort(key = tyc(result_list).index)
    
    return new_list

