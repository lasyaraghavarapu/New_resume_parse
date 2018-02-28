# -*- coding: utf-8 -*-
import logging
import pickle
import re

import time_parser
import tools
from tools import time_classifier


def fetch_exp_duration_sum(exp_text):  # exp_text: a list
    exp_date = []
    for text in exp_text:
        if time_classifier.classify(tools.po_feature(text)):
            exp_date.append(time_parser.extract_duration(text))

    duration_m = 0  # month
    for i in exp_date:
        duration_m += i[0]
    duration_y = round(duration_m/12.0)  # year

    return duration_m


'''
Utility function that fetches the Person Name from file path.
Because the filename format is fixed，
so we can easily use this function to fetch user's name.
Just fetch name from the file path.
'''
def fetch_username(filepath):  # filepath: str
    pattern = re.compile(r'[^/]+(?=\.pdf)')
    filename = pattern.findall(filepath)[0]
    #print filename
    user_name = ""
    for i in filename:
        if i.isalpha() or i == " " or i == "," or i == ".":
            user_name += i
        else:
            break
    user_name = user_name.strip()
    #print user_name
    return user_name


def fetch_language(language_text):  # language_text: a list
    if language_text:
        lang_list = []
        for p in language_text:
            words = re.split(' |\,|\:', p)
            for i in words:
                is_language = tools.uni.isLanguage_tag(i)
                if is_language:
                    lang_list.append(i)
        language = ', '.join(lang_list).encode("utf-8")

        return language
    else:
        return ""


def get_phone(i,j,n):
    # regex explanation in order:
    # optional braces open
    # optional +
    # one to three digit optional international code
    # optional braces close
    # optional whitespace separator
    # i digits
    # optional whitespace separator
    # j digits
    # optional whitespace separator
    # n-i-j digits
    return r"\(?(\+)?(\d{1,3})?\)?[\s-]{0,1}?(\d{"+str(i)+"})[\s\.-]{0,1}(\d{"+str(j)+"})[\s\.-]{0,1}(\d{"+str(n-i-j)+"})"


"""
Utility function that fetches phone number in the resume.
Params: resume_text type: string
returns: phone number type:string
"""
def fetch_phone(block_text):
    regular_expression = re.compile(get_phone(4, 4, 8), re.IGNORECASE)
    for resume_text in block_text:
        try:
            result = re.search(regular_expression, resume_text)
            phone = ''
            if result:
                result = result.group()
                for part in result:
                    if part:
                        phone += part
            if phone is '':
                for i in range(1, 10):
                    for j in range(1, 10-i):
                        regular_expression =re.compile(get_phone(i, j, 10), re.IGNORECASE)
                        result = re.search(regular_expression, resume_text)
                        if result:
                            result = result.groups()
                            for part in result:
                                if part:
                                    phone += part
                        if phone is not '':
                            return phone
            else:
                return phone
        except Exception, exception_instance:
                logging.error('Issue parsing phone number: ' + resume_text +
                str(exception_instance))
    return ''


"""
Utility function that fetches emails in the resume.
Params: resume_text type: string
returns: list of emails
"""
def fetch_email(block_text):
    regex_email = r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}"
    try:
        regular_expression = re.compile(regex_email, re.IGNORECASE)
        emails = []
        for resume_text in block_text:
            result = re.search(regular_expression, resume_text)
            while result:
                emails.append(result.group())
                resume_text = resume_text[result.end():]
                result = re.search(regular_expression, resume_text)
        return emails
    except Exception, exception_instance:
        logging.error('Issue parsing email: ' + str(exception_instance))
        return []


"""
Utility function that fetches the skills from resume
Params: cleaned_resume Type: string
returns: skill_set Type: List
"""
def fetch_skills(block_resume):
    #print cleaned_resume
    with open('static_corpus/data/skills/skills', 'rb') as fp:
        skills = pickle.load(fp)

    skill_set = []
    for p in block_resume: # skill = ' '+skill+' '
        if p[1] == "Empty":
            for skill in skills:
                if (" "+skill+" ").lower() in (" "+p[0]+" ").lower():
                    # skill_set.append(skill)
                    p[1] = "Skill"
    for i in range(len(block_resume)):
        if block_resume[i][1] == "Skill":
            count1 = len([j for j in range(i, min(i + 5, len(block_resume))) if block_resume[j][1] == 'Skill'])
            count2 = len([j for j in range(max(i - 5, 0), len(block_resume)) if block_resume[j][1] == 'Skill'])
            if count1 < 0.6*len(range(i, min(i + 5, len(block_resume)))) and count2 < 0.6*len(range(max(i - 5, 0), len(block_resume))):
                block_resume[i][1] = "Empty"
    return skill_set


"""
Utility function that fetches degree and degree-info from the resume.
Params: resume_text Type: string
returns:
degree Type: List of strings
info Type: List of strings
"""
def fetch_qualifications(block_resume):
    degree_path = 'static_corpus/data/qualifications/qualification_degree'
    with open(degree_path, 'rb') as fp:
        qualifications = pickle.load(fp)

    degree = []
    info = []
    for p in block_resume:
        for qualification in qualifications:
            qual_regex = r'[^a-zA-Z]'+qualification+r'[^a-zA-Z]'
            #qual_regex = qualification
            regular_expression = re.compile(qual_regex)#, re.IGNORECASE)
            resume_text = " "+p+" "
            regex_result = re.search(regular_expression, resume_text)
            while regex_result:
                degree.append(qualification)
                lines = [line.rstrip().lstrip() for line in resume_text.split('\n') if line.rstrip().lstrip()]
                if lines:
                    info.append(lines[0])
                resume_text = resume_text[regex_result.end()-len(qualification)-1:]
                regex_result = re.search(regular_expression, resume_text)
    return degree, info


"""
Utility function that fetches Job Position from the resume.
Params: cleaned_resume Type: string
returns: job_positions Type:List
"""
def fetch_jobs(block_resume):
    positions_path = 'static_corpus/data/job_positions/positions'
    with open(positions_path, 'rb') as fp:
        jobs = pickle.load(fp)

    job_positions = []
    positions = []
    for p in block_resume:
        cleaned_resume = " "+p[0]+" "
        for job in jobs.keys():
            job_regex = r'[^a-zA-Z]'+job+r'[^a-zA-Z]'
            regular_expression = re.compile(job_regex, re.IGNORECASE)
            regex_result = re.search(regular_expression, cleaned_resume)
            if regex_result:
                if p[1] in ["Exp","Empty"]:
                    positions.append(regex_result.start())
                    job_positions.append(job.capitalize())
                else:
                    print "Conflict", p, "jobs:",job
    job_positions = [job for (pos, job) in sorted(zip(positions, job_positions))]

    # For finding the most frequent job category
    hash_jobs = {}
    for job in job_positions:
        if jobs[job.lower()] in hash_jobs.keys():
            hash_jobs[jobs[job.lower()]] += 1
        else:
            hash_jobs[jobs[job.lower()]] = 1

    # To avoid the "Other" category and 'Student' category from
    # becoming the most frequent one.
    if 'Student' in hash_jobs.keys():
        hash_jobs['Student'] = 0
        hash_jobs['Other'] = -1

    return (job_positions, max(hash_jobs, key=hash_jobs.get).capitalize())


if __name__ == "__main__":
    '''
    fetch_username('New JDs for testing/Coach Merchandising Mgr BDI CV Ranking/CVs shorlisted (Checked)/pdf/BAI , Jerry Zong Yi 1-14-2011 ( Private Equity Associate).pdf')
    '''
