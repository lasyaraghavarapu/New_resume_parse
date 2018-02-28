# -*- coding: utf-8 -*-
from parsers.subtext_parser import fetch_subtext
import nltk
from nltk.tokenize.mwe import MWETokenizer


def keyword_frequent(all_text):  # text: a list
    synonyms = {}
    feature_1 = ["English", "Cantonese", "Chinese"]
    feature_2 = ["Supervise", "Coach", "Team", "Staff"]
    feature_3 = ["Digital Marketing", "Digital Media Buy", "Search Engine Marketing", "Search Engine Optimization",
                 "Mobile", "Social Media", "Content Calendar", "Performance Marketing", "Channel", "Paid Social",
                 "Programmatic Display", "Remarketing", "Social Campaign", "Webiste Content", "KOLs",
                 "Content Marketing", "Digital Analytics"]
    feature_4 = ["Analysis", "Budget", "ROI", "KPI", "Forecasting", "Program", "Competitor Analysis"]
    feature_5 = ["University", "College"]

    feature = {"Language": feature_1, "Product_Experience": feature_2, "Functional_Experience": feature_3,
               "Digital_Marketing_Strategy": feature_4, "Education": feature_5}

    synonyms["Chinese"] = ["Mandarin", "Putonghua"]
    synonyms["Team"] = ["Team building"]
    synonyms["Digital Marketing"] = ["Online", "eDM", "Electronic Direct Marketing"]
    synonyms["Digital Media Buy"] = ["banner ads", "landing page"]
    synonyms["Search Engine Marketing"] = ["SEM"]
    synonyms["Search Engine Optimization"] = ["SEO"]
    synonyms["Social Media"] = ["Facebook", "WeChat", "Twitter", "Instagram", "IG", "Snapchat", "Line", "Myspace",
                                "Flickr", "LinkedIn", "Xing"]
    synonyms["KOLs"] = ["Key Opinion Leaders"]
    synonyms["ROI"] = ["Return on investment"]

    all_keywords = []
    for key in feature:
        all_keywords += feature[key]

    tokenizer = MWETokenizer([tuple(x.lower().split()) for x in all_keywords])
    all_frequency = nltk.FreqDist(tokenizer.tokenize(nltk.word_tokenize("\n".join(all_text).lower())))

    all_keywords_frequency = {}
    for key in feature.keys():
        freq_dict = {}
        for keyword in feature[key]:
            freq = all_frequency["_".join(keyword.lower().split())]
            # print keyword, expFreq["_".join(keyword.split())]
            if keyword in synonyms.keys():
                for syn in synonyms[keyword]:
                    # print keyword, syn, expFreq["_".join(syn.split())]
                    freq += all_frequency["_".join(syn.lower().split())]
            freq_dict[keyword] = freq
        all_keywords_frequency[key] = freq_dict

    return all_keywords_frequency


if __name__ == "__main__":
    path = "ABU, Verrena (ELC Digital Marketing Mgr BDI), 11-8-2017.pdf"
    exp_text, edu_text, language_text, raw_text = fetch_subtext(path)
    aaa = keyword_frequent(raw_text)
    print aaa

