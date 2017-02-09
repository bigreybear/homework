#!/usr/bin/env python
# encoding=utf-8


from xml.dom import minidom
import codecs
import traceback
import requests
from bs4 import BeautifulSoup
import jieba
import re
import time

TEST_FLAG = True


def is_target_string(src, pat):
    ret = re.search(pat, src, re.I)
    if ret is not None:
        return True
    else:
        return False


def zx_page(url):
    time.sleep(1)
    return requests.get(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36'
                      '(KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
    }).content


def check_year(src, valve):
    pat = r'[0123456789]+'
    ret = re.findall(pat, src)
    for e_ret in ret:
        if int(e_ret) > valve:
            return True
    return False


def check_tail_number_big_than(src, valve):
    now = 0
    p = -1
    k = 1
    while src[p].isdigit():
        now += k * int(src[p])
        p -= 1
        k *= 10

    if now > valve:
        return True
    else:
        return False


def analyze_journal_to_volume(download):
    r = zx_page(download)
    bs = BeautifulSoup(r, "html.parser")

    main_page = bs.find(name='header', attrs={'class': 'headline noline'})

    title = main_page.h1.string
    #  print title

    # now we have title in title

    main_index = bs.find(name='div', attrs={'id': 'main'})

    index = main_index.children

    for eis in index:
        if eis.name == 'ul':
            dc = eis
            break

    ret = []
    info_ret = []
    for e_dc in dc.children:
        print e_dc.encode()
        if check_year(e_dc.string, 2013):
            #  print e_dc.a['href'], e_dc.string
            ret.append(str(e_dc.a['href']))
            info_ret.append(e_dc.string)
    #  ret is a list of urls
    return title, ret, info_ret


def analyze_volume_to_name(vol, pat):
    r = zx_page(vol)
    bs = BeautifulSoup(r, "html.parser")

    main_page = bs.find_all(name='span', attrs={'class': 'title', 'itemprop': 'name'})

    ret = []
    for emp in main_page:
        if is_target_string(emp.get_text(), pat):
            #  print emp.get_text()
            ret.append(emp.get_text())
    return ret


if __name__ == '__main__':
    # to test the funtion here
    pattern = r'consis|repli'
    exptURL = 'http://dblp.uni-trier.de/db/journals/jpdc/'
    # testString = 'Particle Routing in sa-Consistency Distributed Particle Filters for Large-Scale Spatial Temporal Systems. correct'
    # print is_target_string(testString, pattern)
    #  analyze_volume_to_name('http://dblp.uni-trier.de/db/journals/tpds/tpds26.html', pattern)
    #  urls = analyze_journal_to_volume('http://dblp.uni-trier.de/db/journals/tpds/')
    #  analyze_journal_to_volume(exptURL)
    analyze_journal_to_volume(exptURL)

