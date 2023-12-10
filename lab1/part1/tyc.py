import jieba


def tyc(string1):
    # txt是同义词表，每行是一系列同义词，用 分割
    # 读取同义词表：并生成一个字典。
    combine_dict = {}
    for line in open("part1/jyc.txt", "r", encoding='utf-8'):
        # print(line)
        seperate_word = line.strip().split(" ")
        # print(seperate_word)
        num = len(seperate_word)
        # print(num)
        for i in range(1, num):
            combine_dict[seperate_word[i]] = seperate_word[0]

    # 将分词以/为间隔合并
    # seg_list = jieba.lcut(string1, cut_all = False)
    # print(seg_list)
    # f = "/".join(string1)
    # print (f)

    str0 = []
    strlen = len(string1)
    for j in range(0, strlen):
        if string1[j] in combine_dict:
            str0.append(combine_dict[string1[j]])
        else:
            str0.append(string1[j])

    # print final_sentence
    return str0
