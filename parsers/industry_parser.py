# -*- coding: utf-8 -*-
import re
import xlrd
import pickle


def fetch_industry(text):#parameter is a list
    textStr = '\n'.join(text);

    with open("static_corpus/data/industries/industry_cosmetic", 'rb') as fp:
        cosmetic_company = pickle.load(fp)

    with open("static_corpus/data/industries/industry_fashion and apparel", 'rb') as fp:
        fashion_and_apparel_company = pickle.load(fp)

    with open("static_corpus/data/industries/industry_food and beverage", 'rb') as fp:
        food_and_beverage_company = pickle.load(fp)

    with open("static_corpus/data/industries/industry_luxury and jewelry", 'rb') as fp:
        luxury_and_jewelry_company = pickle.load(fp)

    with open("static_corpus/data/industries/industry_consumer electronic", 'rb') as fp:
        consumer_electronic_company = pickle.load(fp)

    with open("static_corpus/data/industries/industry_sporting", 'rb') as fp:
        sporting_company = pickle.load(fp)

    industry_arr=[]
    cosmetic=[]
    fashion_and_apparel=[]
    food_and_beverage=[]
    luxury_and_jewelry=[]
    consumer_electronic=[]
    sporting=[]

    for c in cosmetic_company:
        if re.search(r'\s'+c.lower()+r'\s', textStr.lower()):
            cosmetic.append(c)

    for c in fashion_and_apparel_company:
        if re.search(c.lower()+r'\s', textStr.lower()):
            fashion_and_apparel.append(c)

    for c in food_and_beverage_company:
        if re.search(c.lower()+r'\s', textStr.lower()):
            food_and_beverage.append(c)

    for c in luxury_and_jewelry_company:
        if re.search(c.lower()+r'\s', textStr.lower()):
            luxury_and_jewelry.append(c)

    for c in consumer_electronic_company:
        if re.search(c.lower()+r'\s', textStr.lower()):
            consumer_electronic.append(c)

    for c in sporting_company:
        if re.search(c.lower()+r'\s', textStr.lower()):
            sporting.append(c)

    '''       
    for c in consumer_electronic_company:
        if textStr.find(c):
            consumer_electronic.append(c)
    for c in sporting_goods_company:
        if textStr.find(c):
            sporting_goods.append(c)
    '''

    industry_arr.append({"type": "cosmetic", "companies": cosmetic, "cnt": len(cosmetic)})
    industry_arr.append({"type": "fashion and apparel", "companies": fashion_and_apparel, "cnt": len(fashion_and_apparel)})
    industry_arr.append({"type": "food and beverage", "companies": food_and_beverage, "cnt": len(food_and_beverage)})
    industry_arr.append({"type": "luxury and jewelry", "companies": luxury_and_jewelry, "cnt": len(luxury_and_jewelry)})
    industry_arr.append({"type": "consumer electronic", "companies": consumer_electronic, "cnt": len(consumer_electronic)})
    industry_arr.append({"type": "sporting", "companies": sporting, "cnt": len(sporting)})

    return industry_arr


def init_pickle(file_path, output_path):
    data = xlrd.open_workbook(file_path)
    table = data.sheets()[0]
    companies = []
    for i in range(1, table.nrows):
        companies.append(table.row_values(i)[0])

    with open(output_path+".txt", 'wb') as fp:
        for u in companies:
            if u != '':
                if isinstance(u, float):
                    u=str(u)
                fp.write(u.encode('utf-8').strip() + '\n')

    company_name = []
    file = open(output_path+'.txt')
    for line in file.readlines():
        company_name.append(line.strip('\n'))
    file.close()

    file_Name = output_path
    fileObject = open(file_Name, 'wb')
    pickle.dump(company_name, fileObject)
    fileObject.close()


if __name__ == "__main__":
    init_pickle("static_corpus/data/industries/Sub Industry - Cosmetic company lists (138)  11-1-17.xlsx", "data/industries/industry_cosmetic")
    init_pickle("static_corpus/data/industries/Sub Industry - Fashion and Apparel (436 ) 11-1-17.xlsx", "data/industries/industry_fashion and apparel")
    init_pickle("static_corpus/data/industries/Sub Industry - Food & Beverage (531) 11-1-17.xlsx", "data/industries/industry_food and beverage")
    init_pickle("static_corpus/data/industries/Sub Industry - Luxury Goods and Jewelry lists {113) 11-1-17.xlsx", "data/industries/industry_luxury and jewelry")
    init_pickle("static_corpus/data/industries/Sub  Industry - Consumer electronic company (607) lists 11-1-17.xlsx", "data/industries/industry_consumer electronic")
    init_pickle("static_corpus/data/industries/Sub Industry - Sporting Goods lists  (185) 11-1-17.xlsx", "data/industries/industry_sporting")