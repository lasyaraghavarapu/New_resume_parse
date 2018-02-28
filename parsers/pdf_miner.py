# -*- coding: utf-8 -*-
import re
import string
from itertools import chain
from pdfminer.layout import *
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfpage import PDFTextExtractionNotAllowed


def pdf_to_txt(filename):
    #打开一个pdf文件
    fp = open(filename, 'rb')
    #创建一个PDF文档解析器对象
    parser = PDFParser(fp)
    #创建一个PDF文档对象存储文档结构
    #提供密码初始化，没有就不用传该参数
    #document = PDFDocument(parser, password)
    document = PDFDocument(parser)
    #检查文件是否允许文本提取
    if not document.is_extractable:
        raise PDFTextExtractionNotAllowed
    #创建一个PDF资源管理器对象来存储共享资源
    #caching = False不缓存
    rsrcmgr = PDFResourceManager(caching = False)
    # 创建一个PDF设备对象
    laparams = LAParams()
    # 创建一个PDF页面聚合对象
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    #创建一个PDF解析器对象
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    #处理文档当中的每个页面

    text_list = []  # 包含所有的LTTextLineHorizontal对象

    pageid = 0
    for page in PDFPage.create_pages(document):
        interpreter.process_page(page)
        # 接受该页面的LTPage对象
        layout=device.get_result()
        # 这里layout是一个LTPage对象 里面存放着 这个page解析出的各种对象, 一般包括LTTextBox, LTFigure, LTImage, LTTextBoxHorizontal 等等
        for x in layout:
            if isinstance(x,LTTextBoxHorizontal):
                for y in x:
                    #if y.get_text().encode('utf-8').replace(" ","")!="\n" and isinstance(y,LTTextLineHorizontal):
                    if isinstance(y,LTTextLineHorizontal) and len(filter(str.isalnum, y.get_text().encode('utf-8')))>0:
                        y.set_bbox((y.x0, y.y0 - 1000 * pageid, y.x1, y.y1 - 1000 * pageid))
                        text_list.append(y)
        pageid += 1
    text_list.sort(key=lambda x: (int(x.y0/10),-x.x0),reverse=True)
    #for i in text_list:
        #print i

    # raw_text只包含文本，不包含对象(与text_list的对象一一对应
    raw_text = []
    for i in text_list:
        raw_text.append(filter(lambda ch: ch.isalnum() or ch in string.punctuation+" \n",i.get_text().encode("utf-8").replace("\xe2\x80\x93","-").replace("\xe2\x80\x99","'").replace("\t"," ").strip().strip("\n")))


    '''
    font_list = {}  # 字典，对所有LTTextLineHorizontal的text文本字体进行分类(一个对象可能包含多种字体
    for i in range(len(text_list)):
        x = text_list[i]  # x为每个LTTextLineHorizontal对
        font_m = []  # x包含的字体
        text_x = str(x.get_text().encode('utf-8').strip())
        Style = "digit" if len(filter(str.isalpha, text_x))==0 else "list" if not text_x[0].isalnum() else "Title Case" if text_x.istitle() else "Capitalize" if text_x.capitalize()==text_x else "UPPER" if text_x.isupper() else "lower" if text_x.islower() else "MIX"
        for c in x:  # c：LTChar对象，只包含单个字符
            #print c
            text = c.get_text().encode('utf-8').replace(" ","")
            if isinstance(c, LTChar) and text.isalnum():
                font_m.append((round(c.size,2), c.fontname, Style))
        font_m = list(set(font_m))  # 去除重复的字体，font_m: x所包含的字体(可能有多个
        for font in font_m:
            if font in font_list:
                #font_list[font].append(x)
                font_list[font].append(str(x.get_text().strip().strip("\n")).encode("utf-8"))  # 只保存x的文本信息
            else:
                #font_list[font] = [x]
                font_list[font] = [str(x.get_text().strip().strip("\n")).encode("utf-8")]
    '''

    #for font in font_list:
       #print font, font_list[font]
    #print font_list.keys()
    #print font_list.values()

    # text_list_split 只包含text内容，不包含对象
    #text_list_split1 = list(chain.from_iterable(map(lambda x: re.split(r"(\(.*[A-Za-z]+.*\))",x.get_text().encode('utf-8').strip().replace("\xe2\x80\x93","-")),text_list)))
    # text_list_split2 = list(chain.from_iterable(map(lambda x: re.split(r"(?=\))", x.get_text().encode('utf-8').strip()), text_list)))

    #regex2 = r"\b(\w+\sL[Tt][Dd]\.)\s*|(?<!\d\s)[,.;!?-]\s+(?=[A-Z0-9])"
    # text_list_split3 = list(chain.from_iterable([[y for y in re.split(regex2, x) if y and y.replace(" ","")] if "(" not in x and ")" not in x else [x] for x in text_list if x]))

    # return list(chain.from_iterable(map(lambda x:re.split(regex2,x.get_text().encode('utf-8').strip()),text_list)))
    return text_list, [x for x in raw_text if len(x)>1]


def get_font_name(object):
    font = []
    for char in object:  # c：LTChar对象，只包含单个字符
        text = char.get_text().encode('utf-8').replace(" ", "")
        if isinstance(char, LTChar) and text.isalnum():
            font.append((round(char.size), char.fontname))
    font = list(set(font))

    return font




