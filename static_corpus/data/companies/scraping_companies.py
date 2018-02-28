import xlrd
import pickle
import sys
import string
reload(sys)
sys.setdefaultencoding( "utf-8" )

data = xlrd.open_workbook('Barons 19,380 company names list 10-11-17.xlsx')
table = data.sheets()[0]
companies = []
for i in range(0, table.nrows):
    companies.append(table.row_values(i)[0])

def clean_text(sent):
    while ' ' in sent:
        sent.remove(' ')
    while '' in sent:
        sent.remove('')
    texts_cleaned = []
    english_punctuations = [':', ';', '?', '[', ']', '&', '!', '*', '#', '$', '%', '/']
    for sentence in sent:
        str_com =[]
        sentence = sentence.split(' ')
        texts_filtered = [[word for word in document if not word in english_punctuations] for document in sentence]
        for list_letter in texts_filtered:
            str_com.append(''.join(list_letter))
        texts_cleaned.append(' '.join(str_com))
    return texts_cleaned

def clean_string(text):
    m = text
    for c in string.punctuation:
        m = m.replace(c, '')
    return ''.join(m.split(' '))

companies2 = clean_text(companies)
companies3 = []
for c in companies2:
    companies3.append(clean_string(c))

for com in companies3:
    print com

with open('company3','wb') as fp:
    pickle.dump(companies3,fp)

#with open('companies2.txt','a') as fp:
#    for u in companies2:
#        fp.write(str(u)+'\n')