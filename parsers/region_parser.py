# -*- coding: utf-8 -*-
import re
import xlrd
import pickle


def fetch_region(text): #parameter is a list
    textStr = '\n'.join(text);

    with open("static_corpus/data/regions/cities_asia_pacific", 'rb') as fp:
        cities_asia_pacific = pickle.load(fp)

    region_arr=[]
    region_asia_pacific=[]
    for c in cities_asia_pacific:
        if re.search(r'\s'+c.lower()+r'\s', textStr.lower()):
            region_asia_pacific.append(c)
    region_arr.append({"AsiaPacific":region_asia_pacific})
    return region_arr


def init_pickle(file_path, output_path):
    data = xlrd.open_workbook(file_path)
    table = data.sheets()[0]
    city_list = []
    for i in range(3, table.nrows):
        if table.row_values(i)[1] != '':
            city_list.append(table.row_values(i)[1])
            for j in range (2, len(table.row_values(i))):
                city_list.append(table.row_values(i)[j])

    with open(output_path+".txt", 'wb') as fp:
        for u in city_list:
            if u != '':
                if isinstance(u, float):
                    u=str(u)
                fp.write(u.encode('utf-8').strip() + '\n')

    city_name = []
    file = open(output_path+'.txt')
    for line in file.readlines():
        city_name.append(line.strip('\n'))
    file.close()

    file_Name = output_path
    fileObject = open(file_Name, 'wb')
    pickle.dump(city_name, fileObject)
    fileObject.close()


if __name__ == "__main__":
    init_pickle("../../../static_corpus/data/regions/Barons Asia Pacific cities chart 10-17-17.xlsx", "../../../static_corpus/data/regions/cities_asia_pacific")