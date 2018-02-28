# -*- coding: utf-8 -*-
import sys
import subprocess
import os
import time


def word_to_pdf_mac(path):
    list_dirs = os.walk(path)
    for root, dirs, files in list_dirs:
        for file in files:
            try:
                input = "/".join([path, "word", file])
                output = "/".join([path, "pdf", file])
                start_time = time.time()
                subprocess.check_call(['/usr/local/bin/python', '/usr/local/bin/unoconv', '-f', 'pdf', '-o', output, '-d','document', input])
                end_time = time.time()
                print "time:\t", end_time-start_time

            except subprocess.CalledProcessError as e:
                print('Called Process Error:', file)


def word_to_pdf(path):
    sys_type = sys.platform
    if sys_type == "darwin":
        word_to_pdf_mac(path)
    else:
        print "Error: This system is not supported for word2pdf"


if __name__ == "__main__":
    word_to_pdf("/Users/lee/Downloads/Estee Digital Marketing Mgr BDI CV Ranking/")
