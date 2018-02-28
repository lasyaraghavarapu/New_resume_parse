# -*- coding: utf-8 -*-
import re
from calendar import monthrange
from datetime import timedelta, datetime
from my_date_extractor import extract_dates


def monthdelta(d1, d2):
    # the first method is too troublesome
    '''
    delta = 0
    while True:
        mdays = monthrange(d1.year, d1.month)[1]
        d1 += timedelta(days=mdays)
        if d1 <= d2:
            delta += 1
        else:
            break
    '''

    delta = round((d2 - d1).days/30.0)
    return delta


def extract_start_end_dates(text):
    text = text.lower()

    dates = extract_dates(text)
    if len(dates) <= 0:
        return '', ''
    elif len(dates) == 1:
        return dates[0].date(), dates[0].date()
    elif len(dates) == 2:
        return dates[0].date(), dates[1].date()
    else:
        return dates[0].date(), dates[-1].date()


def extract_duration(text):
    text = text.lower()
    present_regex = r'(present|now|current)'
    present_pattern = re.compile(present_regex,re.I)
    cur = ' '+datetime.now().strftime("%b %Y")
    #print cur
    isCurrent = 0
    if present_pattern.search(text):
        text += ' '+cur
        isCurrent = 1
    dates=extract_dates(text)
    #print text
    if len(dates)<=0:
        #print "No date found"
        return ["", isCurrent]
    elif len(dates) == 1:
        #print dates[0]
        #print "Only 1 date found"
        return ["", isCurrent]
    elif len(dates) == 2:
        #print dates[0]
        #print dates[1]
        return [monthdelta(dates[0], dates[1]), isCurrent]
    else:
        #print "More than 2 dates found"
        return [monthdelta(dates[0], dates[-1]), isCurrent]


#if __name__ == "__main__":
#     print extract_duration("1998-2003")