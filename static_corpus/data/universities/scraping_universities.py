import xlrd
import pickle
import pandas as pd
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

csv_reader=pd.read_csv('school_and_country_table.csv',encoding='utf-8')
data = xlrd.open_workbook('Barons 360 university names 10-11-17.xlsx')
table = data.sheets()[0]
universities= []
for i in range(1, table.nrows):
    universities.append(table.row_values(i)[0])

for i in csv_reader.iloc[:, 0]:
    universities.append(i)

with open('universities','wb') as fp:
    pickle.dump(universities,fp)

with open('universities.txt','wb') as fp:
    for i in universities:
        fp.write(i+'\n')