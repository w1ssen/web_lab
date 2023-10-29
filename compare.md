Jieba中文含义结巴，jieba库是目前做的最好的python分词组件。首先它的安装十分便捷，只需要使用pip安装；其次，它不需要另外下载其它的数据包，在这一点上它比其余五款分词工具都要便捷。另外，jieba库支持的文本编码方式为utf-8。

Jieba库包含许多功能，如分词、词性标注、自定义词典、关键词提取。基于jieba的关键词提取有两种常用算法，一是TF-IDF算法；二是TextRank算法。基于jieba库的分词，包含三种分词模式：

- **精准模式**：试图将句子最精确地切开，适合文本分析）；
- **全模式**：把句子中所有的可以成词的词语都扫描出来, 速度非常快，但是不能解决歧义）；
- **搜索引擎模式**：搜索引擎模式，在精确模式的基础上，对长词再次切分，提高召回率，适合用于搜索引擎分词。



SnowNLP是一个python写的类库，可以方便的处理中文文本内容，是受到了TextBlob的启发而写的，由于现在大部分的自然语言处理库基本都是针对英文的，于是写了一个方便处理中文的类库，并且和TextBlob不同的是，这里没有用NLTK，所有的算法都是自己实现的，并且自带了一些训练好的字典。注意本程序都是处理的unicode编码，所以使用时请自行decode成unicode。简单来说，snownlp是一个中文的自然语言处理的Python库，snownlp主要功能有：中文分词、词性标注、情感分析、文本分类、转换成拼音、繁体转简体、提取文本关键词、提取文本摘要、tf，idf、Tokenization、文本相似。

总结：snowNLP库的情感分析模块，使用非常方便，功能也很丰富。



![image-20231029204151474](C:\Users\w1ssen\AppData\Roaming\Typora\typora-user-images\image-20231029204151474.png)

![image-20231029204246708](C:\Users\w1ssen\AppData\Roaming\Typora\typora-user-images\image-20231029204246708.png)

![image-20231029205108763](C:\Users\w1ssen\AppData\Roaming\Typora\typora-user-images\image-20231029205108763.png)

可以看到两个分词工具效果差异不大。但是对于特定意思的长词汇，比如混血王子、第六部、狼图腾、中华文明、龙的传人、巴黎圣母院，snownlp工具就会把它们拆开，所以最终选用jieba工具。

比较结果输出在book_com.xlsx