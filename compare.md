1、jieba分词

jieba库是目前做的最好的python分词组件。首先它的安装十分便捷，只需要使用pip安装；其次，它不需要另外下载其它的数据包，在这一点上它比其余五款分词工具都要便捷。另外，jieba库支持的文本编码方式为utf-8。

Jieba库包含许多功能，如分词、词性标注、自定义词典、关键词提取。基于jieba的关键词提取有两种常用算法，一是TF-IDF算法；二是TextRank算法。基于jieba库的分词，包含三种分词模式：

- **精准模式**：试图将句子最精确地切开，适合文本分析）；
- **全模式**：把句子中所有的可以成词的词语都扫描出来, 速度非常快，但是不能解决歧义）；
- **搜索引擎模式**：搜索引擎模式，在精确模式的基础上，对长词再次切分，提高召回率，适合用于搜索引擎分词。

```python
def word_cut0(mytext):
    #jieba.load_userdict('exception.txt')  
    jieba.initialize()  # 初始化jieba
    
    # 文本预处理 ：去除字符剩下中文
    new_data = re.findall('[\u4e00-\u9fa5]+', mytext, re.S)
    new_data = " ".join(new_data)
    
    # 分词
    seg_list_exact = jieba.lcut(new_data)
    result_list = []
    
	…… 
          
    
    return new_list
```

2、SnowNLP

是一个python写的类库，可以方便的处理中文文本内容，是受到了TextBlob的启发而写的，由于现在大部分的自然语言处理库基本都是针对英文的，于是写了一个方便处理中文的类库，并且和TextBlob不同的是，这里没有用NLTK，所有的算法都是自己实现的，并且自带了一些训练好的字典。注意本程序都是处理的unicode编码，所以使用时请自行decode成unicode。简单来说，snownlp是一个中文的自然语言处理的Python库，snownlp主要功能有：中文分词、词性标注、情感分析、文本分类、转换成拼音、繁体转简体、提取文本关键词、提取文本摘要、tf，idf、Tokenization、文本相似。

总结：snowNLP库的情感分析模块，使用非常方便，功能也很丰富。

```python
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
    
	…… 
            
    return new_list
```

3、效果对比

【图片】

可以看到两个分词工具效果差异不大。但是对于特定意思的长词汇，比如混血王子、第六部、狼图腾、中华文明、龙的传人、巴黎圣母院，snownlp工具就会把它们拆开，所以最终选用jieba工具。

比较结果输出在book_com.xlsx

4、去停用词

```python
    # 加载停用词表
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
```

5、去同义词

```python
def tyc(string1):
    # txt是同义词表，每行是一系列同义词，用 分割
    # 读取同义词表：并生成一个字典。
    combine_dict = {}
    for line in open("jyc.txt", "r", encoding='utf-8'):
        #print(line)
        seperate_word = line.strip().split(" ")
        #print(seperate_word)
        num = len(seperate_word)
        #print(num)
        for i in range(1, num):
            combine_dict[seperate_word[i]] = seperate_word[0]
            

    # 将分词以/为间隔合并
    #seg_list = jieba.lcut(string1, cut_all = False)
    #print(seg_list)
    #f = "/".join(string1)  
    #print (f)

    str0 = []
    strlen = len(string1)
    for j in range(0, strlen):
        if string1[j] in combine_dict:
            str0.append(combine_dict[string1[j]])
        else:
            str0.append(string1[j])

    # print final_sentence
    return str0
```

主函数中调用：

```python
	new_list = list(set(tyc(result_list)))
    new_list.sort(key = tyc(result_list).index)	#  保持原来顺序
```









Jieba中文含义结巴，jieba库是目前做的最好的python分词组件。首先它的安装十分便捷，只需要使用pip安装；其次，它不需要另外下载其它的数据包，在这一点上它比其余五款分词工具都要便捷。另外，jieba库支持的文本编码方式为utf-8。

Jieba库包含许多功能，如分词、词性标注、自定义词典、关键词提取。基于jieba的关键词提取有两种常用算法，一是TF-IDF算法；二是TextRank算法。基于jieba库的分词，包含三种分词模式：

- **精准模式**：试图将句子最精确地切开，适合文本分析）；
- **全模式**：把句子中所有的可以成词的词语都扫描出来, 速度非常快，但是不能解决歧义）；
- **搜索引擎模式**：搜索引擎模式，在精确模式的基础上，对长词再次切分，提高召回率，适合用于搜索引擎分词。



SnowNLP是一个python写的类库，可以方便的处理中文文本内容，是受到了TextBlob的启发而写的，由于现在大部分的自然语言处理库基本都是针对英文的，于是写了一个方便处理中文的类库，并且和TextBlob不同的是，这里没有用NLTK，所有的算法都是自己实现的，并且自带了一些训练好的字典。注意本程序都是处理的unicode编码，所以使用时请自行decode成unicode。简单来说，snownlp是一个中文的自然语言处理的Python库，snownlp主要功能有：中文分词、词性标注、情感分析、文本分类、转换成拼音、繁体转简体、提取文本关键词、提取文本摘要、tf，idf、Tokenization、文本相似。

总结：snowNLP库的情感分析模块，使用非常方便，功能也很丰富。



![image-20231029204151474](C:\Users\w1ssen\web_lab\image\image-20231029204151474.png)

![image-20231029204246708](C:\Users\w1ssen\web_lab\image\image-20231029204246708.png)

![image-20231029205108763](C:\Users\w1ssen\web_lab\image\image-20231029205108763.png)

可以看到两个分词工具效果差异不大。但是对于特定意思的长词汇，比如混血王子、第六部、狼图腾、中华文明、龙的传人、巴黎圣母院，snownlp工具就会把它们拆开，所以最终选用jieba工具。

比较结果输出在book_com.xlsx