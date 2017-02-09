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
    time.sleep(0.5)
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


def analyze_conf_to_volume(download):
    r = zx_page(download)
    bs = BeautifulSoup(r, "html.parser")

    main_page = bs.find(name='header', attrs={'class': 'headline noline'})

    conf_name = main_page.h1.get_text()
    #  print conf_name

    # now we have name of conf

    conf_link = []
    conf_title_list = []
    volumes = bs.find_all(name='div', attrs={'class': 'data', 'itemprop': 'headline'})
    for v_s in volumes:
        tts = v_s.find(name='span', attrs={'class': 'title', 'itemprop': 'name'})
        conf_title = tts.get_text()
        vss = v_s.find_all(name='a')
        for evss in vss:
            if evss.get_text() == u'[contents]':
                if check_year(evss['href'], 2013):
                    #  print evss['href']
                    #  print conf_title
                    conf_title_list.append(conf_title)
                    conf_link.append(evss['href'])
    return conf_link, conf_title_list, conf_name


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


def examian_single_page(url):
    pattern = r'consis|repli'
    #  exptURL = 'http://dblp.uni-trier.de/db/conf/podc/'
    #  conf_url = 'http://dblp.uni-trier.de/db/conf/asplos/'
    #  paper_url = 'http://dblp.uni-trier.de/db/conf/icde/icde2016.html'
    #  print is_target_string(testString, pattern)
    #  analyze_volume_to_name('http://dblp.uni-trier.de/db/journals/tpds/tpds26.html', pattern)
    #  urls = analyze_journal_to_volume('http://dblp.uni-trier.de/db/journals/tpds/')
    #  analyze_journal_to_volume(exptURL)
    #  print analyze_volume_to_name(paper_url, pattern)
    conf_link, conf_title_list, conf_name = analyze_conf_to_volume(url)
    print 'conf_name:', str(conf_name)
    print conf_link

    for link in conf_link:
        shows = analyze_volume_to_name(link, pattern)
        if len(shows) >= 1:
            print conf_title_list[conf_link.index(link)]
        for show in shows:
            print show


def examine_page_list(pattern):
    read_url = open('./url/confurl-test.txt', 'r')
    try:
        journal_url = read_url.readlines()
        for j_url in journal_url:
            urls, dates, conf_name = analyze_conf_to_volume(j_url)
            print conf_name
            for url in urls:
                show = analyze_volume_to_name(url, pattern)
                if len(show) >= 1:
                    print dates[urls.index(url)]
                for e_show in show:
                    print e_show
    finally:
        read_url.close()


if __name__ == '__main__':
    # to test the funtion here
    pattern = r'consis|repli'
    exptURL = 'http://dblp.uni-trier.de/db/conf/spaa/'
    conf_url = 'http://dblp.uni-trier.de/db/conf/asplos/'
    paper_url = 'http://dblp.uni-trier.de/db/conf/icde/icde2016.html'
    # testString = 'Particle Routing in sa-Consistency Distributed Particle Filters for Large-Scale Spatial Temporal Systems. correct'
    # print is_target_string(testString, pattern)
    #  analyze_volume_to_name('http://dblp.uni-trier.de/db/journals/tpds/tpds26.html', pattern)
    #  urls = analyze_journal_to_volume('http://dblp.uni-trier.de/db/journals/tpds/')
    #  analyze_journal_to_volume(exptURL)
    #  print analyze_volume_to_name(paper_url, pattern)
    examine_page_list(pattern)