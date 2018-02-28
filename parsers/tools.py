# -*- coding: utf-8 -*-
import itertools
import pickle
import random
import re
import string
import sys
import time
from multiprocessing import Process, Lock
import os
import nltk
from fuzzywuzzy import fuzz

import unified_tagger

path = os.getcwd()
print path

reload(sys)
sys.setdefaultencoding("utf-8")

u_name, c_name, co_name, times, none, indus   = [], [], [], [], [], []

with open('static_corpus/data/universities.txt') as file1, open('static_corpus/data/colleges.txt') as file2:
    for line in file1.readlines():
        u_name.append(line.strip('\n'))
    for line in file2.readlines():
        c_name.append(line.strip('\n'))

with open('static_corpus/data/companies2.txt') as file3, open('static_corpus/data/time2.txt') as file4:
    for line in file3.readlines():
        co_name.append(line.strip('\n'))
    for line in file4.readlines():
        times.append(line.strip('\n'))

with open('static_corpus/data/none.txt') as  file5, open('static_corpus/data/industries/industry_consumer electronic') as file6:
    for line in file5.readlines():
        none.append(line.strip('\n'))
    indus.append(line.strip('\n'))


#------------------------------------------------
def block_text(raw_text):
    all_text = re.split('\n', raw_text)
    while '' in all_text:
        all_text.remove('')
    cut_text = []
    processed_text = []
    patternAvoid = re.compile('\(.*?,.*?\)')
    for line in all_text:
        if ',' in line:
            if not line[line.find(',')-1] == '.' and not patternAvoid.search(line):
                cut_text = cut_text + [l.strip() for l in line.split(',')]
            else:
                cut_text.append(line.strip())
        else:
            cut_text.append(line.strip())

    pattern = re.compile('.\\s{3,}')
    for line in cut_text:
        result = re.search(pattern, line)
        if result:
            processed_text = processed_text + re.split('\\s{3,}', line)
        else:
            processed_text.append(line)
    while '' in processed_text:
        processed_text.remove('')
    return processed_text


def partial_time_classifier(time_text):
    if re.match(r"[a-z]",time_text[0]):
        return ""
    if time_classifier.classify(po_feature(time_text)):
        return time_text
    else:
        words = [w for w in time_text.split(" ") if len(w.replace(" ",""))>0]
        part_word = [words[i:j + 1] for i, j in itertools.combinations(range(len(words)), 2)]
        part_word.sort(key=lambda x: len(x), reverse=True)
        for w in part_word:
            if re.match(r"[a-z]",w[0]):
                continue
            if len([x for x in w if x.isalnum()]) < 3 or len(w) < len(words) / 4.0:
                return ""
            if time_classifier.classify(po_feature(" ".join(w))):
                return " ".join(w)

    return ""

# def clean_text(all_text):
#     while ' ' in all_text:
#         all_text.remove(' ')
#     while '' in all_text:
#         all_text.remove('')
#     english_stopwords = stopwords.words('english')
#     english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '#', '$', '%']
#     texts_cleaned = []
#     for sentence in all_text:
#         texts_tokenized = nltk.sent_tokenize(sentence.strip())
#         texts_tokenized = [nltk.word_tokenize(sent) for sent in texts_tokenized]
#         texts_filtered_stopwords = [[word for word in document if not word in english_stopwords] for document in texts_tokenized]
#         texts_filtered = [[word for word in document if not word in english_punctuations] for document in texts_filtered_stopwords]
#         texts_cleaned.append(texts_filtered)
#     return texts_cleaned


def clean_string(text):
    m = text
    for c in string.punctuation:
        m = m.replace(c, '')
    return ''.join(m.split(' '))


def text_preprocess(sentences):
    sentences = nltk.sent_tokenize(sentences)
    sentences = [nltk.word_tokenize(sent) for sent in sentences]
    sentences = [nltk.pos_tag(sent) for sent in sentences]
    return sentences


#define a feature function
def entity_feature(name):
    # split the university's name by space
    words = name.split(' ')
    while '' in words:
        words.remove('')
    feature = {}
    feature['len'] = len(words)
    for i in range(0,len(words)):
        #wfkey = 'wf' + str(i)
        fkey = 'firstletter' + str(i)
        lkey = 'lastletter' + str(i)
        feature.update({fkey: words[i][0]})
        feature.update({lkey: words[i][-1]})
    return feature


def po_feature(text):
    #words = re.split(r"(["+string.punctuation+"])|\s",text)#
    #words = text.split(' ')

    words = re.split(r"([-/])|\s",text)

    while '' in words:
        words.remove('')
    feature = {}
    feature.update(dict(('contains(%s)' % w, True) for w in words if w))
    return feature


def po_feature2(text):
    words = text.lower().split(' ')
    while '' in words:
        words.remove('')
    feature = {}
    feature.update(dict(('contains', w) for w in words))
    return feature


#-------------------recognize in text-------------------
def fetch_company(text):
    positions_path = 'static_corpus/data/companies/company'
    temp_path = 'static_corpus/data/companies/company3'
    with open(positions_path, 'rb') as fp:
        coms = pickle.load(fp)
    with open(temp_path, 'rb') as c3:
        cleaned_coms = pickle.load(c3)
    fetched_com = []
    pattern = re.compile('[\s]Ltd', re.IGNORECASE)
    for i, com in enumerate(cleaned_coms):
        if com in clean_string(text) or pattern.search(text):
            fetched_com.append(coms[i])
        elif coms[i] in text:
            fetched_com.append(coms[i])
        elif pattern.search(text):
            fetched_com.append(text)
        elif coms[i] in text:
            fetched_com.append(coms[i])
    return fetched_com


def fuzzy_substring(needle, haystack):
    haystack = haystack.strip()
    m, n = len(needle), len(haystack)

    # base cases
    #if m == 1: return not needle in haystack
    if not n: return m

    row1 = range(n+1)#[0] * (n+1)
    for i in range(0,m):
        row2 = [i+1]
        for j in range(0,n):
            cost = ( needle[i].lower() != haystack[j].lower() )
            row2.append( min(row1[j+1] + 1,       # deletion
                               row2[j] + 1,       # insertion
                               row1[j] + cost)    # substitution
                           )
        row1 = row2
    return row1[-1]

def fuzzy_subsentence(needle, haystack, titlecost):
    ns = [x for x in re.split(r"["+re.escape(string.punctuation)+" "+"]+",needle) if len(x.replace(" ",""))>0]
    hs = [x for x in re.split(r"["+re.escape(string.punctuation)+" "+"]+",haystack) if len(x.replace(" ",""))>0]
    m, n = len(ns), len(hs)
    row1 = [0] * (n + 1)
    for i in range(0, m):
        row2 = [i + 1]
        for j in range(0, n):
            cost = fuzzy_substring(ns[i], hs[j])
            if i==0:
                cost += 0 if hs[j][0].istitle() else 1*titlecost
            row2.append(min(row1[j + 1] + len(ns[i]),  # deletion
                            row2[j] + len(hs[j]),  # insertion
                            row1[j] + cost)  # substitution
                        )
        row1 = row2
    return min(row1)

def upper_first_letter(text):
    str_list = text.split()
    new_text_list = []
    for word in str_list:
        new_word = word[0].upper() + word[1:]
        new_text_list.append(new_word)
    return ' '.join(new_text_list)


def islikelt_company(text):
    pDNum = re.compile(r'[1-2][0-9]+[\s|a-z|A-Z|-]|in [1-2][0-9]+')
    pStart = re.compile(r'^and |^a |^-| and$')
    pDigit = re.compile(r'\s[0-9]\s|[0-9]%')
    if pDNum.search(text) and False:
        #print "num"
        return False
    elif pStart.search(text):
        #print "start"
        return False
    elif pDigit.search(text) and False:
        #print "digit"
        return False
    else:
        return True


def fetch_industry(indus_dict, com_list, industry_list, industry_name, lock, FuzzyRatio=99):
    with lock:
        for indus in industry_list:
            for com_name in com_list:
                if fuzz.token_set_ratio(indus, com_name) > FuzzyRatio:
                    indus_dict[com_name] = industry_name
    return indus_dict


def fetch_company_info(text, Ratio=0.5, uselist=True, Com_FuzzyRatio=99, Indus_FuzzyRatio=95):
    """
    :param text: str - resume_text
    :param Ratio: float - selection ratio(better effect with 0.6 ~ 0.7)
    :param uselist: boolean - if use all_company list
    :param Com_FuzzyRatio: float - fuzzy company search ratio (the higher, the more accurate and the lower,the more result)
    :param Indus_FuzzyRatio: float - fuzzy industry search ratio
    :return: list, list ,dict - company list, position list, industry[company] dict}
    """

    # Method: capital feature searching
    pS = re.compile('\s+')
    pSplit = re.compile(' at | in ')
    text_ps = re.sub(pS, ' ', text)

    company, position = [], []
    count = 0
    titled_text = upper_first_letter(text_ps)
    word_num = len(text_ps.split())

    for i in range(len(text_ps.strip())):
        if text_ps[i] != titled_text[i]:
            count += 1
    capital_letter_ratio = float((word_num - count))/word_num

    if capital_letter_ratio >= Ratio and word_num >= 2 and islikelt_company(text_ps):
        if ' at ' in text_ps or ' in ' in text_ps:
            fetched_result = re.split(pSplit, text_ps)
            noun_num = 0
            word_num = 0
            flag, p = uni.isJob_tag(fetched_result[0])
            flag2, c = uni.isLocation_tag(fetched_result[1])
            if "(" in fetched_result[0] and not ")" in fetched_result[0]:
                #print "inside sentence" ,text_ps
                pass
            elif time_classifier.classify(po_feature(fetched_result[1].split(" ")[0])):
                #print "before time", text_ps
                pass
            elif flag2 and ' in ' in text_ps:
                #print "before region", text_ps
                pass
            elif fetched_result[1].startswith('the '):
                #print "before the", text_ps
                pass
            #elif re.match(r"^[^a-zA-Z]*[A-Z]",fetched_result[1]):
            #    position.append(fetched_result[0])
            #    company.append(fetched_result[1])
            elif flag and not re.match(r"^\w+ing\s|charge of",fetched_result[1]):
                #print "contain position", text_ps
                position.append(fetched_result[0])
                company.append(fetched_result[1])
            else:
                if re.search(r"\w+.\s(Ltd\.|Limited\s|Ltd\s|Co\.|Co\s|Inc\.|Inc\s)", " " + fetched_result[1] + " ", re.IGNORECASE):
                    if not (")" in fetched_result[0] and "(" not in fetched_result[0]):
                        position.append(fetched_result[0])
                    company.append(fetched_result[1])
                elif uselist:
                    fuzz_com = []
                    for i in all_companies_list:
                        if fuzz.partial_token_set_ratio(i, text_ps) > Com_FuzzyRatio:
                            fuzz_com.append(i)
                    for com in fuzz_com:
                        if fuzzy_subsentence(com.lower(), text_ps.lower(), 0) < 1:
                            if not (")" in fetched_result[0] and "(" not in fetched_result[0]):
                                position.append(fetched_result[0])
                            company.append(fetched_result[1])
                        elif fuzzy_substring(com, text_ps) < 1:
                            if not (")" in fetched_result[0] and "(" not in fetched_result[0]):
                                position.append(fetched_result[0])
                            company.append(fetched_result[1])
                if not company and re.match(r"^[^a-zA-Z]*[A-Z]",fetched_result[1]):
                    chunks =  nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(fetched_result[0])))
                    #if len(nltk.word_tokenize(fetched_result[0]))>8:
                    #    return company, position, {}
                    for j in range(len(chunks)):
                        chunk = chunks[j]
                        if hasattr(chunk, 'label'):  # and chunk.label() == 'PERSON':
                            chunk = chunk[0]
                        (name, tag) = chunk
                        if name.isalpha():
                            if (tag == 'NN' or tag == "NNP" or tag=="NNS") and name[0].istitle() and len(name)>1:
                                #print "I guess position", fetched_result[0], name
                                if not (")" in fetched_result[0] and "(" not in fetched_result[0]):
                                    position.append(fetched_result[0])
                                company.append(fetched_result[1])
                                break
                            elif tag == "VBD" or tag == "JJ" or tag == "VBG" or tag == "VBN":
                                if j+1<len(chunks):
                                    chunk = chunks[j+1]
                                    if hasattr(chunk,'label'):
                                        chunk = chunk[0]
                                    (name, tag) = chunk
                                    if not tag == "NN" and not tag == "NNP":
                                        #print "I guess not position", fetched_result[0], name, tag
                                        break
                            elif tag == "VBZ" or tag == "IN" or tag=="TO":
                                #print "I guess not position", fetched_result[0], name
                                break
                            else:
                                #print "What:", chunk
                                pass
        if company:
            pass
        elif re.search(r"\s(Ltd\.|Limited\.|Limited\s|Ltd\s|Co\.|Co\s|Inc\.|Inc\s)"," "+text_ps+" ", re.IGNORECASE):
            company.append(text_ps)
        elif uselist:
            fuzz_com = []
            for i in all_companies_list:
                if fuzz.partial_token_set_ratio(i, text_ps) > Com_FuzzyRatio:
                    fuzz_com.append(i)
            for com in fuzz_com:
                if fuzzy_subsentence(com, text_ps, 1) < 1:
                    company.append(com)
                elif fuzzy_substring(com, text_ps) < 1:
                    company.append(com)

    lock = Lock()
    indus_dict = {}
    Process(target=fetch_industry, args=(indus_dict, company, consumer_electronic_list, lock, 'Consumer Electronic', Indus_FuzzyRatio))
    Process(target=fetch_industry, args=(indus_dict, company, cosmetic_companies_list, lock, 'Cosmetic', Indus_FuzzyRatio))
    Process(target=fetch_industry, args=(indus_dict, company, food_beverage_list, lock, 'Food and Beverage', Indus_FuzzyRatio))
    Process(target=fetch_industry, args=(indus_dict, company, luxury_goods_list, lock, 'Luxury Goods', Indus_FuzzyRatio))

    return company, position, indus_dict


def fetch_university(text):
    u_path = 'static_corpus/data/universities/universities'
    c_path = 'static_corpus/data/college/college'
    with open(u_path, 'rb') as fp:
        us = pickle.load(fp)
    with open(c_path, 'rb') as fp:
        cs = pickle.load(fp)
    cu = us + cs
    fetched_u = []
    for u in cu:
        if str(u).lower() in text.lower():
            fetched_u.append(u)
    return fetched_u


def del_duplicate(a_list):
    b_list = []
    for a in a_list:
        flag = True
        for i in range(len(b_list)):
            b = b_list[i]
            if a in b:
                flag = False
                break
            if b in a:
                b_list[i] = a
                flag = False
        if flag:
            b_list.append(a)


#output = text_block(cut_text)
#path = 'static_corpus/data/sample/CAI, Cora Xue Min 11-12-2004.pdf'
#raw_text = converter.pdf_to_txt(path)
#output = block_text(raw_text)

rate = 0.7
co_len = int(len(co_name)/200)
random.shuffle(co_name)

cu_tuple = ([(u,True) for u in u_name] + [(c,True) for c in c_name] + [(ind,False) for ind in indus] + [(no,False) for no in none])
time_tuple = ([(t,True) for t in times] + [(t,True) for t in times] + [(t,True) for t in times] + [(t,True) for t in times] + [(no,False) for no in none] + [(u,False) for u in u_name] + [(c,False) for c in c_name] + [(co,False) for co in co_name[:co_len]])
random.shuffle(cu_tuple)
random.shuffle(time_tuple)

train_set = [(po_feature(n),l) for (n,l) in cu_tuple[:int(rate*len(cu_tuple))]]
time_train_set = [(po_feature(t),l) for (t,l) in time_tuple]

cu_classifier = nltk.NaiveBayesClassifier.train(train_set)
time_classifier = nltk.NaiveBayesClassifier.train(time_train_set)

all_companies_path = 'static_corpus/data/company_with_industry/all_companies'
consumer_electronic_path = 'static_corpus/data/company_with_industry/Consumer_Electronic_companies'
cosmetic_companies_path = 'static_corpus/data/company_with_industry/Cosmetic_companies'
food_beverage_path = 'static_corpus/data/company_with_industry/Food_Beverage_companies'
luxury_goods_path = 'static_corpus/data/company_with_industry/Luxury_Goods_Jewelry_companies'

with open(all_companies_path, 'rb') as ac, open(consumer_electronic_path, 'rb') as ce, open(cosmetic_companies_path, 'rb') as cc:
    all_companies_list = pickle.load(ac)
    consumer_electronic_list = pickle.load(ce)
    cosmetic_companies_list = pickle.load(cc)

with open(food_beverage_path, 'rb') as fb, open(luxury_goods_path, 'rb') as lg:
    food_beverage_list = pickle.load(fb)
    luxury_goods_list = pickle.load(lg)


uni = unified_tagger.uniTagger()


class ErrorLog:
    def __init__(self,filename):
        self.error_file = open(filename, 'w')
        self.error_file.writelines(str(time.time()) + "\n")

    def write_error(self, target_file, error_message):
        for msg in error_message:
            self.error_file.writelines(target_file+","+",".join(msg)+"\n")

    def __del__(self):
        self.error_file.close()

#errorLogger = ErrorLog("error_log.txt")
