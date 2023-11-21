import gzip


def match_freebase_entity(douban_movie_id):
    with open('douban2fb.txt', 'r', encoding='utf-8') as file:
        for line in file:
            # print(line)
            douban_id, freebase_id = line.strip().split('\t')
            # print(douban_id)
            if douban_id == douban_movie_id:
                return freebase_id
    return None

# 提供的电影ID列表
movie_ids = ['1291544', '1291546', '4190211']

for movie_id in movie_ids:
    freebase_entity_id = match_freebase_entity(movie_id)
    if freebase_entity_id:
        print(f"豆瓣电影ID {movie_id} 对应的Freebase实体ID为 {freebase_entity_id}")
        
    else:
        print(f"找不到豆瓣电影ID {movie_id} 对应的Freebase实体")