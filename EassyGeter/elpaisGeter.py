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


def basic_connect_test(url):
    r = zx_page(url)
    bs = BeautifulSoup(r, "html.parser")
    return bs


def is_out_of_date_report(src, valve):
    #  examine the first news in the page, and make sure that its validate
    #  valve is formatted as yyyymmdd
    #  print valve/10000, ((valve%10000)/100), valve%100
    year, month, day = date_parser(src)
    if year > (valve/10000):
        return False
    if month > ((valve%10000)/100):
        return False
    if month < ((valve%10000)/100):
        return True
    if day > (valve%100):
        return False
    else:
        return True


def single_column_analyze(url, pat, valve):
    ret_title = []
    ret_url = []
    #  loop
    #  judge if the report year is over the valve, if true, end the loop
    #  else analyze single page news
    #  get return list of title and url, add it to the record.
    #  get the next page url
    is_out_date = False
    next_page = url
    while is_out_date is False:
        titles, urls, is_out_date, next_page = single_page_news_analyze(next_page, pat, valve)
        if len(titles) != len(urls):
            print 'there is some errors, infos follow:'
            print 'url: ', url
            return ret_title, ret_url
        ret_title.extend(titles)
        ret_url.extend(urls)
    return ret_title, ret_url


def single_page_news_analyze(url, pat, valve):
    page_news_count = 0
    is_out_date = False
    ret_title = []
    ret_url = []
    bs = basic_connect_test(url)
    ret_1 = bs.find_all(name='div', attrs={'class': 'articulo__interior'})
    for ee in ret_1:
        #  its a count re-feed block
        page_news_count += 1
        if page_news_count % 20 == 0:
            print 'I have read ', page_news_count, ' news in this page'
            print 'This news is at ', ee.time['datetime']

        is_out_date = is_out_of_date_report(ee.time['datetime'], valve)
        #  print is_out_date
        if is_out_date:
            break
        ret_2 = ee.find(name='h2', attrs={'itemprop': 'headline', 'class': 'articulo-titulo'})
        title = ret_2.a.get_text()
        if is_target_string(title, pat):
            ret_title.append(title)
            ret_url.append(ret_2.a['href'])
            if TEST_FLAG:
                print title, ret_2.a['href']

    next_page = bs.find(name='li', attrs={'class': 'paginacion-siguiente'})
    next_page = next_page.a['href']
    print 'There has been ', page_news_count, ' news in this page.'
    return ret_title, ret_url, is_out_date, next_page


def date_parser(src):
    #  src is formatted as 'yyyy-mm-dd...'
    year = month = day = 0
    ss = str(src)
    i = acc = 0

    year = int(ss[0:4])
    month  = int(ss[5:7])
    day = int(ss[8:10])

    return year, month, day


if __name__ == '__main__':
    # to test the funtion here
    pattern = r'una terroris|la terroris|las terroris|trump'
    international = 'http://elpais.com/tag/c/15148420ba519668342b7a63149cad97'
    elpaisUrl = 'http://www.elpais.com'
    exptURL = 'http://dblp.uni-trier.de/db/conf/spaa/'
    conf_url = 'http://dblp.uni-trier.de/db/conf/asplos/'
    paper_url = 'http://dblp.uni-trier.de/db/conf/icde/icde2016.html'
    # testString = 'Particle Routing in sa-Consistency Distributed Particle
    # \Filters for Large-Scale Spatial Temporal Systems. correct'
    # print is_target_string(testString, pattern)
    #  analyze_volume_to_name('http://dblp.uni-trier.de/db/journals/tpds/tpds26.html', pattern)
    #  urls = analyze_journal_to_volume('http://dblp.uni-trier.de/db/journals/tpds/')
    #  analyze_journal_to_volume(exptURL)
    #  print analyze_volume_to_name(paper_url, pattern)
    #  examine_page_list(pattern)
    #  basic_connect_test(elpaisUrl)
    #  single_page_news_analyze(international, pattern)
    #  print is_out_of_date_report('2017-02-06T21:33:33', 20170206)
    single_column_analyze(international, pattern, 20161200)

