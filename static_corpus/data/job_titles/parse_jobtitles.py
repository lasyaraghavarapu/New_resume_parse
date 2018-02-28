import xlrd
import pickle
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

data = xlrd.open_workbook('Barons (9.xlsx')
table = data.sheets()[0]
job_titles = []
for i in range(1, table.nrows):
    job_titles.append(table.row_values(i)[0])

for i,j in enumerate(job_titles):
    job_titles[i] = j.strip('\n| ')

with open('job_titles','wb') as fp:
    pickle.dump(job_titles,fp)

with open('job_titles.txt','wb') as fp:
    for i in job_titles:
        fp.write(i+'\n')