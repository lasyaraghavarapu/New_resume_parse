# -*- coding: utf-8 -*-
import re
import itertools

years_4 = [str(x) for x in range(1960, 2020)]
years_2 = [x[-2:] for x in years_4]
years_n = ["Now", "now", "Present", "present", "Current", "current"]

month_n = [str(x)[-2:] for x in range(101, 113)] + [str(x) for x in range(1,10)]
month_s = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
           "November", "December"]
month_3 = [x[:3] for x in month_s]
month_4 = [x[:4] for x in month_s]

term = ["summer", "spring", "winter", "autumn", "fall"]
term += [x.title() for x in term]


class TimeFilter:

    def __init__(self):
        self.year_dict = {"y4":years_4, "y2":years_2, "yn":years_n}
        self.month_dict = {"md":month_n, "ms":month_s, "m3":month_3, "m4":month_4}
        self.term_dict = {"term":term}
        self.comma = {"/": "/", "-": "-"}
        self.initial_dict = {"year":self.year_dict,"month":self.month_dict,"term":self.term_dict,"comma":self.comma}

    def list_to_dict(self, time_str):
        all_dict = []
        for part_str in time_str:
            part_dict = {}
            for key in self.initial_dict:
                #part_dict[key] = {}
                sub_dict = {}
                for p in self.initial_dict[key]:
                    if part_str in self.initial_dict[key][p]:
                        sub_dict[p] = part_str
                if sub_dict:
                    part_dict[key] = sub_dict

            #print part_str, part_dict
            all_dict.append(part_dict)

        return all_dict

    def dict_to_patt(self, time_dict):

        all_dict = {"year":0,"month":0,"term":0,"comma":0}
        detail_dict = {"y4":0,"yn":0,"y2":0,"m4":0,"ms":0,"m3":0,"md":0,"term":0,"/":0,"-":0}
        for part in time_dict:
            for key in all_dict:
                if key in part:
                    all_dict[key] += 1
                    for p in part[key]:
                        detail_dict[p] += 1

        #print all_dict
        #print detail_dict

        if detail_dict["y4"]>=2:
            return True
        elif detail_dict["y4"]>=1 and (detail_dict["m4"]+detail_dict["m3"]+detail_dict["ms"])!=1:
            return True
        elif detail_dict["y2"]>=2 and detail_dict["-"]>=1:
            return True
        elif (detail_dict["m4"]+detail_dict["m3"]+detail_dict["ms"])>=2 and all_dict["year"]>=1:
            return True
        elif (detail_dict["m4"]+detail_dict["m3"]+detail_dict["ms"])>=1 and (detail_dict["y2"]+detail_dict["y4"])>=1 and detail_dict["yn"]>=1:
            return True
        elif detail_dict["md"]>=2 and detail_dict["y4"]>=1:
            return True
        elif detail_dict["md"]>=1 and detail_dict["y4"]>=1 and detail_dict["yn"]>=1:
            return True
        elif all_dict["term"] >= 1 and detail_dict["y4"]>=1:
            return True

        return False


t_f = TimeFilter()
time_dict = t_f.list_to_dict([x for x in re.split(r"([-/])|[:;,.?\s()!@#$%^&*+\[\]]",'Merchandising. -Increased 05 business up 34% from 04 on comp stores') if x])
#print tc.dict_to_patt(time_dict)

