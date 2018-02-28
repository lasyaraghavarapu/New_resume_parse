# -*- coding: utf-8 -*-
import os
import re

import pandas as pd
import pdf_miner


def split_tag(block_resume):
    pattern_split = re.compile(r'(Experience|Work|career|employment|Education|ACADEMIC BACKGROUND|Professional Background|Language|interest|Certification|Certificate|Qualification|Honor|Award|Skill|Skills)([\s\S]*)', re.I)
    title = []
    for p in block_resume:
        if p.strip() == '':
            continue
        if pattern_split.search(p) and len([x for x in re.split(r"\s(\W)*",p) if x and re.match(r"\w+",x)]) <= 3 and p[0].isupper():
            title.append(p)
            #print re.split(r"(?<=\w)\s(\W+\s)*(?=\w)",p[0])
            #p[1] = "Split" if p[1] == "Empty" else p[1] + ",Split"
    return title


'''
Utility function that fetches keywords (title).
The simplest method without distinguishing fonts and coordinates.
'''
def fetch_keywords(raw_text):
    keywords = split_tag(raw_text)  # candidate keywords

    return keywords


'''
Utility function that fetches keywords (title).
Distinguishes fonts and coordinates, maybe delete some candidate keywords.
'''
def fetch_keywords_backup(raw_text):
    keywords = split_tag(raw_text)  # candidate keywords

    '''
    keywords_lower = [x.lower() for x in keywords]
    keywords_edu = []
    keywords_exp = []
    keywords_skill = []
    keywords_certification = []
    keywords_language = []
    keywords_interest = []
    keywords_others = []
    for i in range(len(keywords_lower)):
        if keywords_lower[i].find("education") != -1:
            keywords_edu.append(keywords[i])
        elif keywords_lower[i].find("experience") != -1 or keywords_lower[i].find("work") != -1:
            keywords_exp.append(keywords[i])
        elif keywords_lower[i].find("skill") != -1:
            keywords_skill.append(keywords[i])
        elif keywords_lower[i].find("certification") != -1:
            keywords_certification.append(keywords[i])
        elif keywords_lower[i].find("language") != -1:
            keywords_language.append(keywords[i])
        elif keywords_lower[i].find("interest") != -1:
            keywords_interest.append(keywords[i])
        else:
            keywords_others.append(keywords[i])

    if len(keywords_edu)>1 or len(keywords_exp)>1 or len(keywords_skill)>1:

        font = []  # fonts of candidate keywords
        font_list = []
        for word in keywords:
            word_font = converter.get_fontname(text_list[raw_text.index(word)])
            font.extend(word_font)
            font_list.append(word_font)
        print font
        print font_list
        font_keyword = Counter(font).most_common()[0][0]  # set the most frequent font as title font
        print font_keyword
        index1 = []
        for i in range(len(keywords)):
            if font_keyword not in font_list[i]:
                index1.append(i)
        for i in sorted(index1, reverse=True):
            del keywords[i]
        print keywords
    
        coordinate_x0 = []
        for word in keywords:
            word_x0 = round(text_list[raw_text.index(word)].x0 / 30)  # coordinate error = 30 (page:600*850)
            coordinate_x0.append(word_x0)
        print coordinate_x0
        x0_keyword = Counter(coordinate_x0).most_common()[0][0]
        print x0_keyword
        index2 = []
        for i in range(len(keywords)):
            if coordinate_x0[i] != x0_keyword:
                index2.append(i)
        for i in sorted(index2, reverse=True):
            del keywords[i]
    
        print keywords
    '''

    '''
    keywords_list = []  # LTTextLineHorizontal objects including title
    for word in keywords:
        keywords_list.append(text_list[raw_text.index(word)])
    '''

    return keywords


def fetch_subtext(filename):  # filename: str; keywords: a list
    #print filename
    text_list, raw_text = pdf_miner.pdf_to_txt(filename)
    #print raw_text
    keywords = fetch_keywords(raw_text)

    pattern_exp = re.compile(r'Experience|Work|career|employment([\s\S]*)', re.I)
    pattern_edu = re.compile(r'(Education|ACADEMIC BACKGROUND|Professional Background)([\s\S]*)', re.I)
    pattern_skill = re.compile(r'(Skill|Skills)([\s\S]*)', re.I)
    pattern_interest = re.compile(r'(interest)([\s\S]*)', re.I)
    pattern_language = re.compile(r'(Language)([\s\S]*)', re.I)
    pattern_certification = re.compile(r'(Certification|Certificate|Qualification)([\s\S]*)', re.I)
    pattern_honor = re.compile(r'(Honor|Award)([\s\S]*)', re.I)

    slice_keywords_lsit = []
    for i in range(len(keywords)-1):
        slice_keywords_lsit.append(keywords[i:i+2])
    slice_keywords_lsit.append([keywords[-1]])

    exp_text =[]
    edu_text = []
    skill_text = []
    interest_text = []
    language_text = []
    certification_text = []
    honor_text = []
    for s_list in slice_keywords_lsit:
        if len(s_list) == 2:
            first_keywords = s_list[0]
            second_keywords = s_list[1]
            if pattern_exp.search(first_keywords):
                exp_text.extend(raw_text[raw_text.index(first_keywords):raw_text.index(second_keywords)])
            if pattern_edu.search(first_keywords):
                edu_text.extend(raw_text[raw_text.index(first_keywords):raw_text.index(second_keywords)])
            if pattern_skill.search(first_keywords):
                skill_text.extend(raw_text[raw_text.index(first_keywords):raw_text.index(second_keywords)])
            if pattern_interest.search(first_keywords):
                interest_text.extend(raw_text[raw_text.index(first_keywords):raw_text.index(second_keywords)])
            if pattern_language.search(first_keywords):
                language_text.extend(raw_text[raw_text.index(first_keywords):raw_text.index(second_keywords)])
            if pattern_certification.search(first_keywords):
                certification_text.extend(raw_text[raw_text.index(first_keywords):raw_text.index(second_keywords)])
            if pattern_honor.search(first_keywords):
                honor_text.extend(raw_text[raw_text.index(first_keywords):raw_text.index(second_keywords)])

        if len(s_list) == 1:
            last_one_keywords = s_list[0]
            if pattern_exp.search(last_one_keywords):
                exp_text.extend(raw_text[raw_text.index(last_one_keywords):])
            if pattern_edu.search(last_one_keywords):
                edu_text.extend(raw_text[raw_text.index(last_one_keywords):])
            if pattern_skill.search(last_one_keywords):
                skill_text.extend(raw_text[raw_text.index(last_one_keywords):])
            if pattern_interest.search(last_one_keywords):
                interest_text.extend(raw_text[raw_text.index(last_one_keywords):])
            if pattern_language.search(last_one_keywords):
                language_text.extend(raw_text[raw_text.index(last_one_keywords):])
            if pattern_certification.search(last_one_keywords):
                certification_text.extend(raw_text[raw_text.index(last_one_keywords):])
            if pattern_honor.search(last_one_keywords):
                honor_text.extend(raw_text[raw_text.index(last_one_keywords):])

    '''
    print "\nexp_text:\n", exp_text
    print "\nedu_text:\n", edu_text
    print "\nskill_text:\n", skill_text
    print "\ninterest_text:\n", interest_text
    print "\nlanguage_text:\n", language_text
    print "\ncertification_text:\n", certification_text
    print "\nhonor_text:\n", honor_text
    '''
    return exp_text, edu_text, language_text, raw_text


if __name__ == "__main__":
    import details_parser

    relative_path = "New JDs for testing/Coach Merchandising Mgr BDI CV Ranking/CVs shorlisted (Checked)/pdf"
    path = "/".join([os.getcwd(), relative_path])
    files = os.listdir(path)
    files.sort(key=lambda x: x.lower()[0:6])
    edu_test = pd.DataFrame()
    language_test = pd.DataFrame()

    userid = []
    university = []
    degree = []
    time = []
    duration = []

    user_list = []
    language_list = []
    for file in files:
        filepath = os.path.join(relative_path, file)
        username = details_parser.fetch_username(filepath)
        print '\n[ ', username, ' ]'

        keywords = fetch_keywords(filepath)
        exp_text, edu_text, language_text, skill_text = fetch_subtext(filepath)
        print skill_text
        #edu_info = edu_parser.fetch_edu_info(edu_text)

    '''
        for i in edu_info:
            userid.append(username)
            university.append(i["university"])
            degree.append(i["degree"])
            time.append(i["time"])
            duration.append(i["duration"])

        language = edu_parser.fetch_language(language_text)
        user_list.append(username)
        language_list.append(language)

    edu_test["user-name"] = userid
    edu_test["university"] = university
    edu_test["degree"] = degree
    edu_test["time"] = time
    edu_test["duration"] = duration

    language_test["userid"] = user_list
    language_test["language"] = language_list

    edu_test.to_csv("edu_test7777.csv", index=False)
    language_test.to_csv("language_test.csv", index=False)
    '''






