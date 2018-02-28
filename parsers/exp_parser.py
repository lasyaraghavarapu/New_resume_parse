# -*- coding: utf-8 -*-
import itertools
import pickle
import re

import time_filter
import time_parser
import tools
from tools import time_classifier


def fetch_company_and_duration(exp_text):  # exp_text: a list
    company = []
    duration = []
    for p in exp_text:
        company_list = tools.fetch_company(p)
        if len(company_list) > 0:
            company.append(company_list[0])
        if time_classifier.classify(tools.po_feature(p)):
            duration.append(time_parser.extract_duration(p))
    return {"duration": duration, "company": company}


def fetch_exp_details(exp_text):  # exp_text: a list
    error_info_exp = []
    positions_path = 'static_corpus/data/job_positions/positions'
    with open(positions_path, 'rb') as fp:
        jobs = pickle.load(fp)

    experiences = []
    exp_tags = ''
    for z in exp_text:
        p = z
        # print p
        time = 0
        has_company = 0
        has_position = 0
        time_content=''
        company_content=''
        position_content=''

        words = re.split(r"([,.;])\s| ",p)
        word_num = 0.0
        title_num = 0.0
        comma_num = 0.0

        for w in words:
            if w and w in ",;":
                comma_num += 1
            elif w:
                word_num += 1
                if w[0] == w[0].title():
                    title_num += 1

        if (comma_num > max(word_num/2,3) or title_num < min(word_num/2,4)) and word_num>2:
            #print "Seems not Title", p, comma_num, title_num, word_num
            experiences.append([p, 'H', time_content, company_content, position_content])
            exp_tags += 'H'
            continue

        tempTime = tools.partial_time_classifier(filter(lambda ch: ch in " ,;-./%:" or ch.isalnum(), p))
        if len(tempTime) >= 2:
            dictlist = time_filter.t_f.list_to_dict([x for x in re.split(r"([-/])|[:;,.?\s()!@#$%^&*+\[\]]", tempTime) if x])
            dictresult = time_filter.t_f.dict_to_patt(dictlist)
            if not dictresult:
                #print tempTime
                pass
            else:
                time = 1
                time_content = tempTime
            #print time_content
            # print 'time'
        #match company

        company_info_list = tools.fetch_company_info(p)
        company_list = company_info_list[0]
        # company_list = tools.fetch_company(p)
        if len(company_list)>0:
            # print company_list[0]
            has_company=1
            company_content=company_list[0]
            # print company_content

        # use the position in the fetch_company_info result first
        if has_company > 0:
            position_list = company_info_list[1]
            if len(position_list) > 0:
                has_position = 1
                position_content = position_list[0]
                # print position_content

        if has_position < 1:# and re.search(r"[A-Z0-9]", p[:5]):
            #match position by regex
            len_job = len(position_content)
            for job in jobs.keys():
                job_regex = job
                regular_expression = re.compile(r"[^a-zA-Z]"+re.escape(job_regex)+"[^a-zA-Z]", re.IGNORECASE)
                regex_result = re.search(regular_expression," "+p+" ")
                if regex_result and len(job)>len_job and (p[regex_result.start()].istitle() or re.search(r"[A-Z0-9]", p[:3])):
                    if not re.match(r"[^A-Za-z0-9]{0,2}Report(ing)? to\s?.{0,2}\s?\w*"+re.escape(job_regex)+r"\w*", p, re.IGNORECASE):
                        has_position = 1
                        position_content = job
                        len_job = len(job)
                    else:
                        #print "A report sentence", p
                        pass

        if time > 0:
            if has_company > 0:
                if has_position > 0:
                    tag = 'G'
                else:
                    tag = 'D'
            else:
                if has_position > 0:
                    tag = 'E'
                else:
                    tag = 'A'
        else:
            if has_company > 0:
                if has_position > 0:
                    tag='F'
                else:
                    tag='B'
            else:
                if has_position > 0:
                    tag = 'C'
                else:
                    tag = 'H'

        experiences.append([p, tag, time_content, company_content, position_content])
        exp_tags += tag

    #print exp_tags
    # print [x for x in experiences if x[1]!='H']

    frequentpnts = []
    frequentnams = []
    pnts = ['FA', 'BCA', 'BE', 'CD', 'G', 'D', 'E', 'F', 'AB', 'AC', 'BC']

    for pnt in pnts:
        if len(pnt) > 1:
            for pairs in itertools.permutations(pnt, len(pnt)):
                # print "[^DGEF]??".join(pairs)
                frequentpnts.append("(?P<" + "".join(pairs) + ">" + "[^DGEF]??".join(pairs) + ")")
                frequentnams.append("".join(pairs))
        else:
            frequentpnts.append("(?P<" + pnt + ">" + pnt + ")")
            frequentnams.append(pnt)
    frequent = "|".join(frequentpnts)
    #print frequent
    #frequent = '(F[^DGEF]??A|A[^DGEF]??F|B[^DGEF]??CA|B[^DGEF]??E|E[^DGEF]??B|ACB|ABC|CBA|G|B[^DGEF]??A|B[^DGEF]??C|C[^DGEF]??B|A[^DGEF]??B|C[^DGEF]??A|A[^DGEF]??C|D|E|F)'
    #for m in re.finditer('(?='+frequent+')', exp_tags):
    #    print m.groupdict()
    start_index = [(m.start(),m.start()+len([m.groupdict()[u] for u in frequentnams if m.groupdict()[u]][0]), [u for u in frequentnams if m.groupdict()[u]][0]) for m in re.finditer('(?='+frequent+')', exp_tags)]

    #stop_index = [m.start()+len(m.group(1)) for m in re.finditer('(?=' + frequent + ')', exp_tags)]

    #print start_index
    #print stop_index

    start_index.append((len(experiences),len(experiences),'H'))
    previous = (0,0,'H')

    score = {'A':1,'B':1,'C':1,'D':2,'E':2,'F':2,'G':3,'H':-0.1}
    def symbol_score(symbol):
        ts = 'A' in symbol or 'D' in symbol or 'E' in symbol or 'G' in symbol
        cs = 'B' in symbol or 'D' in symbol or 'F' in symbol or 'G' in symbol
        ps = 'C' in symbol or 'E' in symbol or 'F' in symbol or 'G' in symbol
        return ts + cs + ps

    experience_arr = []
    current_exp = {}
    for i, k, symbol in start_index:
        if k <= previous[1] and i!=len(experiences):
            if symbol_score(previous[2])<symbol_score(symbol):
                if experience_arr:
                    for j in range(previous[0],i):
                        experience_arr[-1]['raw_data'] += experiences[j][0]
                previous = (i, k, symbol)
                continue
            elif symbol_score(previous[2])>symbol_score(symbol):
                # previous = (i,k,symbol)
                continue
            else:
                len_p = len([x for x in start_index if previous[2]==x[2]])
                len_s = len([x for x in start_index if symbol==x[2]])
                if len_p <= len_s:
                    if experience_arr:
                        for j in range(previous[0], i):
                            experience_arr[-1]['raw_data'] += experiences[j][0]
                    previous = (i, k, symbol)
                    continue
                elif len_s < len_p:
                    continue
        elif i < previous[1] and i!=len(experiences):
            if symbol_score(previous[2])<symbol_score(symbol):
                if experience_arr:
                    for j in range(previous[0],i):
                        experience_arr[-1]['raw_data'] += experiences[j][0]
                previous = (i, k, symbol)
                continue
            elif symbol_score(previous[2]) > symbol_score(symbol):
                # previous = (i,k,symbol)
                continue
            else:
                len_p = (len([x for x in start_index if previous[2] == x[2]]),len([x for x in start_index if x[2].startswith(previous[2][0]) or x[2].endswith(previous[2][-1])]))
                len_s = (len([x for x in start_index if symbol == x[2]]),len([x for x in start_index if x[2].startswith(symbol[0]) or x[2].endswith(previous[2][-1])]))
                if len_p < len_s:
                    if experience_arr:
                        for j in range(previous[0], i):
                            experience_arr[-1]['raw_data'] += experiences[j][0]
                    previous = (i, k, symbol)
                    continue
                elif len_s < len_p:
                    continue
                else:
                    for j in range(i, previous[1]):  # previous[0],i):
                        error_info_exp.append(["Duplicate", experiences[j][0]])
        if previous[0] == 0:
            previous = (i, k, symbol)
        else:
            tempStr = ''
            time = ''
            duration = 0
            company = ''
            position = ''
            getTime = 0
            getCompany = 0
            getPosition = 0
            isCurrent = 0
            c_index = []
            p_index = []
            # print experiences[previous[0]],experiences[i]
            for j in range(previous[0], max(i,previous[1])):
                if getTime == 0 and experiences[j][1] == 'A' or experiences[j][1] == 'D' or experiences[j][1] == 'E' or experiences[j][1] == 'G':
                    time=experiences[j][2]
                    extract_duration_result = time_parser.extract_duration(time)
                    duration = extract_duration_result[0]
                    isCurrent = extract_duration_result[1]
                    getTime = 1
                if getCompany == 0 and experiences[j][1] == 'B' or experiences[j][1] == 'D' or experiences[j][1] == 'F' or experiences[j][1] == 'G':
                    company = experiences[j][3]
                    c_index.append(j)
                    # print company
                    getCompany = 1
                if getPosition == 0 and experiences[j][1] == 'C' or experiences[j][1] == 'E' or experiences[j][1] == 'F' or experiences[j][1] == 'G':
                    position = experiences[j][4]
                    if not experiences[j][1] == 'F':
                        p_index.append(j)
                    # print position
                    getPosition = 1
                '''
                if experiences[j][1] == 'H' and j<i-1 and experiences[j+1][1] != 'H' and j+1<max(i,previous[1]):
                    if getCompany>0 and j-1 in c_index:
                        company += experiences[j][0]
                    if getPosition>0 and j-1 in p_index:
                        position += experiences[j][0]
                '''

                tempStr += experiences[j][0]+' '

            start_date, end_date = time_parser.extract_start_end_dates(time)
            if isCurrent:
                if start_date and end_date:
                    current_exp = {'time': time.encode('utf-8'), 'start_date': start_date, 'end_date': "Present", 'current_experience_duration(months)': duration, 'company': company.encode('utf-8'), 'position': position.encode('utf-8')}
                else:
                    current_exp = {'time': time.encode('utf-8'), 'current_experience_duration(months)': duration, 'company': company.encode('utf-8'), 'position': position.encode('utf-8')}

            if start_date and end_date:
                experience_arr.append({'time': time.encode('utf-8'), 'start_date': start_date, 'end_date': end_date, 'experience_duration(months)': duration, 'company': company.encode('utf-8'), 'position': position.encode('utf-8'), 'raw_data': tempStr.encode('utf-8')})
            else:
                experience_arr.append({'time': time.encode('utf-8'), 'experience_duration(months)': duration, 'company': company.encode('utf-8'), 'position': position.encode('utf-8'), 'raw_data': tempStr.encode('utf-8')})

            previous = (i, k, symbol)

    return experience_arr, current_exp, error_info_exp

