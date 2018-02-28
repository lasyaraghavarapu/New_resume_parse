import pickle
import re
import string

from fuzzywuzzy import fuzz

import tools


class uniTagger:

    def __init__(self):
        degree_path = 'static_corpus/data/qualifications/qualification_degree'
        with open(degree_path, 'rb') as fp:
            self.qualifications = sorted(pickle.load(fp), key=lambda ch:len(ch), reverse=True)

        all_companies_path = 'static_corpus/data/company_with_industry/all_companies'
        consumer_electronic_path = 'static_corpus/data/company_with_industry/Consumer_Electronic_companies'
        cosmetic_companies_path = 'static_corpus/data/company_with_industry/Cosmetic_companies'
        food_beverage_path = 'static_corpus/data/company_with_industry/Food_Beverage_companies'
        luxury_goods_path = 'static_corpus/data/company_with_industry/Luxury_Goods_Jewelry_companies'
        with open(all_companies_path, 'rb') as ac,\
                open(consumer_electronic_path, 'rb') as ce,\
                open(cosmetic_companies_path, 'rb') as cc:
            self.all_companies_list = sorted(pickle.load(ac), key=lambda ch:len(ch), reverse=True)
            self.consumer_electronic_list = pickle.load(ce)
            self.cosmetic_companies_list = pickle.load(cc)

        with open(food_beverage_path, 'rb') as fb, open(luxury_goods_path, 'rb') as lg:
            self.food_beverage_list = pickle.load(fb)
            self.luxury_goods_list = pickle.load(lg)

        with open('static_corpus/data/skills/skills', 'rb') as fp:
            self.skills = sorted(pickle.load(fp), key=lambda ch:len(ch), reverse=True)

        positions_path = 'static_corpus/data/job_positions/positions'
        with open(positions_path, 'rb') as fp:
            self.jobs = sorted(pickle.load(fp), key=lambda ch:len(ch), reverse=True)

        u_path = 'static_corpus/data/universities/universities'
        c_path = 'static_corpus/data/college/college'
        with open(u_path, 'rb') as fp:
            us = pickle.load(fp)
        with open(c_path, 'rb') as fp:
            cs = pickle.load(fp)
        self.cu = sorted(us + cs, key=lambda ch:len(ch), reverse=True)

        with open('static_corpus/data/regions/cities_asia_pacific','rb') as fp:
            self.regions = sorted(pickle.load(fp), key=lambda ch:len(ch), reverse=True)

        with open('static_corpus/data/languages/languages','rb') as lang:
            self.languages = pickle.load(lang)

    def isTime_tag(self, c):  # c: a line/sentence
        c = filter(lambda ch: ch.isalnum() or ch in string.punctuation + " ", c)
        if tools.time_classifier.classify(tools.po_feature(c)):
            return True
        else:
            return False

    def isTime_tag2(self, c):  # c: a line/sentence
        c = filter(lambda ch: ch.isalnum() or ch in string.punctuation + " ", c)
        time = tools.partial_time_classifier(c)
        time_num = filter(lambda ch: ch in "0123456789/- ", time)
        time_num = time_num.strip().strip("-").strip("/").strip()
        if time_num:
            return True, time_num
        else:
            return False, ''

    def isDegree_tag(self, c):  # c: a line/sentence
        degrees = ''
        for qualification in self.qualifications:
            qual_regex = r'[^a-zA-Z]' + re.escape(qualification) + r'[^a-zA-Z]'
            # qual_regex = qualification
            regular_expression = re.compile(qual_regex, re.IGNORECASE)
            resume_text = " " + c + " "
            regex_result = re.search(regular_expression, resume_text)

            while regex_result:
                regex_more = re.search(r'(?<=[^a-zA-Z])('+qualification+r")( of [A-Z]+[a-z]+)*( in [A-Z]+[a-z]+)*(?=[ "+string.punctuation+"])", resume_text)
                if regex_more:
                    if resume_text[regex_more.start():regex_more.end()].lower() not in degrees.lower():
                        degrees += ', '+ resume_text[regex_more.start():regex_more.end()]
                else:
                    if qualification.lower() not in degrees.lower():
                        degrees += ', '+ qualification
                resume_text = resume_text[regex_result.end():]
                regex_result = re.search(regular_expression, resume_text)
        if degrees:
            return True, degrees.strip(',').strip()#sorted(degrees,key=lambda ch:len(ch), reverse=True)
        else:
            return False, ''

    def isDegree_tag2(self, c):  # c: a line/sentence
        degree = ''
        for qualification in self.qualifications:
            qual_regex = r'[^a-zA-Z]' + re.escape(qualification) + r'[^a-zA-Z]'
            # qual_regex = qualification
            regular_expression = re.compile(qual_regex, re.IGNORECASE)
            resume_text = " " + c + " "
            regex_result = re.search(regular_expression, resume_text)

            if regex_result:
                regex_more = re.search(r'(?<=[^a-zA-Z])('+qualification+r")( of [A-Z]+[a-z]+)*( in [A-Z]+[a-z]+)*(?=[ "+string.punctuation+"])", resume_text)
                if regex_more:
                    degree = resume_text[regex_more.start():regex_more.end()]
                else:
                    degree = qualification
                break

        if degree:
            return True, degree
        else:
            return False, ''


    def isCompany_tag(self, c, Ratio=0.6, uselist=True, Com_FuzzyRatio=100):
        pS = re.compile('\s+')
        pSplit = re.compile(' at | in ')

        # Method: capital feature searching
        text_ps = filter(lambda ch: ch.isalnum() or ch in string.punctuation+" ",re.sub(pS, ' ', c))

        count = 0
        titled_text = tools.upper_first_letter(text_ps)
        #word_num = len(text_ps.split())
        word_num = 1

        #print text_ps, titled_text
        for i in range(len(text_ps.strip())):
            if text_ps[i] != titled_text[i]:
                count += 1
            if i>0 and text_ps[i-1]==" ":
                word_num += 1
            if text_ps[i] in string.punctuation+"\n":
                break
        try:
            capital_letter_ratio = 1.0#float((word_num - count)) / word_num
        except:
            print "zero:", text_ps


        if capital_letter_ratio >= Ratio and word_num >= 2 and tools.islikelt_company(text_ps):
            if ' at ' in text_ps or ' in ' in text_ps:
                fetched_result = re.split(pSplit, text_ps)
                flag, job = self.isJob_tag(fetched_result[0])
                return flag, fetched_result[1], fetched_result[0]
            elif re.search(r"([\s\S]*)(Ltd\.|Ltd\s|Co\.|Co\s|Inc\.|Inc\s)",text_ps):
                                                    #'Ltd.' in text_ps.title() or 'Co.' in text_ps.title() or ' Ltd ' in text_ps.title() or ' Co ' in text_ps.title():
                me = re.search(r"([\s\S]*)(Ltd\.|Ltd\s)",text_ps)
                if me:
                    #print p[0][:me.end()]
                    #company.append(p[0][:me.end()])
                    print "Success", text_ps[:me.end()]
                    return True, text_ps[:me.end()], None
                else:
                    print "Wrong", text_ps
            elif uselist:
                fuzz_com = []
                for i in self.all_companies_list:
                    if fuzz.partial_token_set_ratio(i.title(), text_ps.title()) >= Com_FuzzyRatio:
                        fuzz_com.append(i)
                #print fuzz_com
                for com in fuzz_com:
                    try:
                        if tools.fuzzy_substring(com.title(), text_ps.title()) < 1:
                            return True, com.title(), None
                    except:
                        print text_ps.title()
        return False, None, None

    def isLocation_tag(self, c):
        for loc in self.regions:
            loc_regex = r'^' + loc + r'[^a-zA-Z]'
            regular_expression = re.compile(loc_regex, re.IGNORECASE)
            if regular_expression.search(c.strip()+" "):
                #print c
                return True, c
        return False, None

    def isUniversity_tag(self, c):  # c: a line/sentence
        university = ''
        if c.strip()[0] == '(' and c.strip()[-1] == ')':
            university = ''
        else:
            c = filter(lambda ch:ch.isalnum() or ch in string.punctuation+" ", c)
            if tools.cu_classifier.classify(tools.po_feature2(c)):
                for u in self.cu:
                    if u.lower() in c.lower():
                        university = u
                        break

            if not university and \
                            'university' in c.lower() or 'college' in c.lower() or 'school' in c.lower() or 'institute' in c.lower():
                university = c

        if university:
            return True, university.strip()
        else:
            return False, ''

    def isJob_tag(self, c):
        jobs_list = []
        cleaned_resume = " " + c + " "
        for job in self.jobs:
            job_regex = r'[^a-zA-Z]' + job + r'[^a-zA-Z]'
            regular_expression = re.compile(job_regex, re.IGNORECASE)
            regex_result = re.search(regular_expression, cleaned_resume)
            if regex_result and job.lower()!="student":
                hasIN = False
                for j in range(len(jobs_list)):
                    b = jobs_list[j]
                    if b in job.lower():
                        jobs_list[j] = job.lower()
                        hasIN = True
                    if job.lower() in b:
                        hasIN = True
                        break
                if not hasIN:
                     jobs_list.append(job.lower())
        if jobs_list:
            return True, jobs_list
        return False, None

    def isSkill_tag(self, c):
        skill_set = []
        for skill in self.skills:
            if re.search(r'[^a-zA-Z]'+re.escape(skill.lower())+ r'[^a-zA-Z]', c):
                hasIN = False
                for j in range(len(skill_set)):
                    b = skill_set[j]
                    if b in skill.lower():
                        skill_set[j] = str(skill).lower()
                        hasIN = True
                    elif skill.lower() in b:
                        hasIN = True
                        break
                if not hasIN:
                    skill_set.append(skill.lower())

        if skill_set:
            return True, skill_set
        return False, None

    def isLanguage_tag(self, c):  # c: a word
        if c in self.languages:
            return True
        else:
            return False



