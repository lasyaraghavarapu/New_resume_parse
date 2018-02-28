import xlrd
import pickle

data = xlrd.open_workbook('Barons 49 college names 10-11-17.xlsx')
table = data.sheets()[0]
college = []
for i in range(1, table.nrows):
    college.append(table.row_values(i)[0])

with open('college','wb') as fp:
    pickle.dump(college,fp)
