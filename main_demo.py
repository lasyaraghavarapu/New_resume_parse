# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import time
import hashlib
import keywords_count
from sql_writer import sql_writer
from parsers import subtext_parser, exp_parser, edu_parser, details_parser, region_parser, industry_parser


# Create a unique identifier based on time
def create_id():
    m = hashlib.md5(str(time.clock()).encode('utf-8'))
    return m.hexdigest()


# Main function
def demo(file_path):
    for filename in os.listdir(file_path):
        if filename.endswith(".pdf"):
            print filename

            st = 'Select * From Personal_Info Where Personal_Info.file_name ="' + filename + '"'
            if sql_writer.sql.index(st):
                print "Exist"
                continue

            # fetch different paragraph
            user_id = create_id()

            exp_text, edu_text, language_text, raw_text = subtext_parser.fetch_subtext(file_path + "/" + filename)

            name = details_parser.fetch_username(filename)
            email = ";".join(details_parser.fetch_email(raw_text[:8]))
            phone = details_parser.fetch_phone(raw_text[:8])
            language = details_parser.fetch_language(language_text)

            experience_info, current_exp_info, error_exp = exp_parser.fetch_exp_details(exp_text)
            edu_info = edu_parser.fetch_edu_info(edu_text)

            sql_writer.sql.insert_data("Personal_Info", {"user_id": user_id, "user_name": name, "email": email,
                                                         "phone": phone, "language": language, "file_name": filename})

            miss_company = 0  # number of missing company errors
            miss_position = 0
            miss_exp_time_duration = 0
            miss_exp_duration = 0
            exp_duration_sum = 0
            for exp in experience_info:
                exp_info_id = create_id()
                exp.update({"experience_info_id": exp_info_id, "user_id": user_id})
                sql_writer.sql.insert_data("Experience_Info", exp)

                if exp['experience_duration(months)']:
                    exp_duration_sum += exp['experience_duration(months)']

                if not exp['position']:
                    miss_position += 1
                    error_exp.append(['Miss_position', exp['raw_data']])
                if not exp['company']:
                    miss_company += 1
                    error_exp.append(['Miss_company', exp['raw_data']])
                if not exp['time']:
                    miss_exp_time_duration += 1
                    error_exp.append(['Miss_time_&_duration', exp['raw_data']])
                if not exp['experience_duration(months)'] and exp['time']:
                    miss_exp_duration += 1
                    error_exp.append(['Miss_duration', exp['raw_data']])

            # Current_Experience_Info: store current work experience, if any
            if current_exp_info:
                current_exp_info.update({"user_id": user_id})
                sql_writer.sql.insert_data("Current_Experience_Info", current_exp_info)

            miss_university = 0
            miss_degree = 0
            miss_edu_time_duration = 0
            miss_edu_duration = 0
            for edu in edu_info:
                edu_info_id = create_id()
                edu.update({"education_info_id": edu_info_id, "user_id": user_id})
                sql_writer.sql.insert_data("Education_Info", edu)

                edu_error_type = ""
                if not edu['university']:
                    miss_university += 1
                    edu_error_type += "Miss_university, "
                if not edu['degree']:
                    edu_error_type += "Miss_degree, "
                    miss_degree += 1
                if not edu['time']:
                    edu_error_type += "Miss_time_&_duration, "
                    miss_edu_time_duration += 1
                if not edu['education_duration(months)'] and edu['time']:
                    edu_error_type += "Miss_duration, "
                    miss_edu_duration += 1

                # ErrorLog_for_Education: show errors in which education information
                sql_writer.sql.insert_data("ErrorLog_for_Education",
                                           {"education_info_id": edu_info_id, "user_id": user_id,
                                            "error_type": edu_error_type.strip().strip(',')})

            # ErrorLog_for_Experience: show experience errors in which raw data
            for e_exp in error_exp:
                exp_error_id = create_id()
                e_exp_dict = {"exp_error_id": exp_error_id, "user_id": user_id, "error_type": e_exp[0], "raw_data_of_error": e_exp[1]}
                sql_writer.sql.insert_data("ErrorLog_for_Experience", e_exp_dict)

            # total error numbers, show which the format of CV is not good
            miss_total = miss_university + miss_degree + miss_edu_time_duration + miss_edu_duration + miss_company + miss_position + miss_exp_time_duration + miss_exp_duration
            error_sum = {"user_id": user_id, "miss_university": miss_university, "miss_degree": miss_degree,
                         "miss_edu_time_duration": miss_edu_time_duration, "miss_edu_duration": miss_edu_duration,
                         "miss_company": miss_company, "miss_position": miss_position, "miss_exp_time_duration": miss_exp_time_duration,
                         "miss_exp_duration": miss_exp_duration, "miss_total": miss_total}
            sql_writer.sql.insert_data("ErrorLog_sum", error_sum)

            # count keywords_frequency to train every feature
            keywords_frequency = keywords_count.keyword_frequent(raw_text)
            for key in keywords_frequency:
                key = key.encode("utf-8")
                #print keywords_frequency[key]
                keywords_frequency[key].update({"user_id": user_id, "user_name": name})
                #print keywords_frequency[key]
                sql_writer.sql.insert_data(key, keywords_frequency[key])

            exp_duration_sum = round(exp_duration_sum/12.0)
            sql_writer.sql.insert_data("Years_of_Experience", {"user_id": user_id, "user_name": name, "Years of Experience": exp_duration_sum})


if __name__ == '__main__':
    fileDir = 'New JDs for testing(New)/Estee Digital Marketing Mgr BDI CV Ranking 2017-12-5/1st batch Testing/pdf'
    demo(fileDir)


