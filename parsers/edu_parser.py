# -*- coding: utf-8 -*-
import re

import time_filter
import time_parser
import tools


def fetch_edu_info(edu_text):  # edu_text: list
    universities = []
    degrees = []
    times = []
    durations = []
    edu_experience = []
    edu_exp = []
    cleaned_edu_text = [line.strip() for line in edu_text]

    edu_tags = ''
    for c in cleaned_edu_text:
        for i in c:
            if ord(i) >= 128:  # delete special characters
                c = c.replace(i, ' ')
        c = re.sub(r'\s+', ' ', c.strip())

        isTime = False
        time = ''
        duration = 0
        tempTime = tools.partial_time_classifier(c)
        if len(tempTime) >= 2:
            dictlist = time_filter.t_f.list_to_dict([x for x in re.split(r"([-/])|[:;,.?\s()!@#$%^&*+\[\]]", tempTime) if x])
            dictresult = time_filter.t_f.dict_to_patt(dictlist)
            if not dictresult:
                pass
            else:
                isTime = True
                #tempTime = filter(lambda ch: ch in "0123456789/- ", tempTime)  # only keep the year, it's enough
                time = tempTime.strip().strip("-").strip("/").strip()
                duration = time_parser.extract_duration(c)[0]

        isUniversity, university = tools.uni.isUniversity_tag(c)
        isDegree, degree = tools.uni.isDegree_tag(c)

        if isUniversity:
            if isDegree:
                if isTime:
                    tag = 'G'
                else:
                    tag = 'D'
            else:
                if isTime:
                    tag = 'E'
                else:
                    tag = 'A'
        else:
            if isDegree:
                if isTime:
                    tag = 'F'
                else:
                    tag = 'B'
            else:
                if isTime:
                    tag = 'C'
                else:
                    tag = 'H'

        edu_experience.append([c, tag, university, degree, time, duration])
        edu_tags += tag
    tag_text = edu_tags
    result = re.search(r'BB+', tag_text)
    while result:
        start = result.start()
        end = result.end()
        while start+1 < end:
            edu_experience[result.start()][0] += ', ' + edu_experience[start+1][0]
            edu_experience[result.start()][3] += ', ' + edu_experience[start+1][3]
            edu_experience[start+1][1] = 'H'
            edu_experience[start+1][3] = ''
            start += 1
        new_edu_tags = ''
        for i in edu_experience:
            new_edu_tags += i[1]
        tag_text = new_edu_tags
        result = re.search(r'BB+', tag_text)

    for i in range(len(edu_experience)):
        if edu_experience[i][1] == 'A':
            universities.append(edu_experience[i][2])
        elif edu_experience[i][1] == 'B':
            degrees.append(edu_experience[i][3])
        elif edu_experience[i][1] == 'C':
            times.append(edu_experience[i][4])
            durations.append(edu_experience[i][5])
        elif edu_experience[i][1] == 'D':
            if i >= 1 and edu_experience[i - 1][1] == 'A' and \
                    (edu_experience[i - 1][1].lower() in edu_experience[i][1].lower() or edu_experience[i][1].lower() in
                        edu_experience[i - 1][1].lower()):
                degrees.append(edu_experience[i][3])
            else:
                universities.append(edu_experience[i][2])
                degrees.append(edu_experience[i][3])
        elif edu_experience[i][1] == 'E':
            universities.append(edu_experience[i][2])
            times.append(edu_experience[i][4])
            durations.append(edu_experience[i][5])
        elif edu_experience[i][1] == 'F':
            degrees.append(edu_experience[i][3])
            times.append(edu_experience[i][4])
            durations.append(edu_experience[i][5])
        elif edu_experience[i][1] == 'G':
            universities.append(edu_experience[i][2])
            degrees.append(edu_experience[i][3])
            times.append(edu_experience[i][4])
            durations.append(edu_experience[i][5])

    universities = [u.title() for u in universities]
    if universities:
        for i in range(len(universities)):
            if i < len(times):
                start_date, end_date = time_parser.extract_start_end_dates(times[i])
                if start_date and end_date:
                    edu_exp.append({'time': times[i], 'education_duration(months)': durations[i], 'start_date': start_date, 'end_date': end_date})
                else:
                    edu_exp.append({'time': times[i], 'education_duration(months)': durations[i]})
            else:
                edu_exp.append({'time': '', 'education_duration(months)': ''})
            edu_exp[i].update({'university': universities[i]})
            if i < len(degrees):
                edu_exp[i].update({'degree': degrees[i]})
            else:
                edu_exp[i].update({'degree': ''})

    # Remove duplicates
    new_edu_exp = []
    for i in edu_exp:
        if i not in new_edu_exp:
            new_edu_exp.append(i)

    if not new_edu_exp:
        new_edu_exp = [{'university': '', 'degree': '', 'education_duration(months)': '', 'time': ''}]

    return new_edu_exp


#if __name__ == '__main__':
#     with open('static_corpus/data/universities/universities', 'rb') as fp:
#         us = pickle.load(fp)
#     path = 'static_corpus/data/sample/1.pdf'
#     raw_text = converter.pdf_to_txt(path)
#     out_put = tools.block_text(raw_text)
#     print fetch_edu(fetch_edu_text(out_put))