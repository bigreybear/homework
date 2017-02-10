#!/usr/bin/env python
# encoding=utf-8

import sys
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


def is_double_target_string(src, pat, sub_pat):
    if not is_target_string(src, pat):
        return False
    ret = re.search(sub_pat, src, re.I)
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
    #  to examian if the last char of the url is a \n, which could be a error
    if url[-1] == '\n':
        url = url[:-1]
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


def single_column_analyze(url, pat, sub_pat, valve, writer):
    ret_title = []
    ret_url = []
    #  loop
    #  judge if the report year is over the valve, if true, end the loop
    #  else analyze single page news
    #  get return list of title and url, add it to the record.
    #  get the next page url
    is_out_date = False
    next_page = url
    writer.write('Now we begin from here: ')
    writer.write(url)
    writer.write('\n')
    writer.flush()
    while is_out_date is False:
        print 'Now we will see in this page: ', next_page
        titles, urls, is_out_date, next_page = single_page_news_analyze(next_page, pat, sub_pat, valve)
        if len(titles) != len(urls):
            print 'there is some errors, infos follow:'
            print 'url: ', url
            return ret_title, ret_url
        i = 0
        while i < len(titles):
            writer.write('#####')
            writer.write(titles[i])
            writer.write('\n')
            writer.write(urls[i])
            writer.write('\n')
            i += 1
        writer.flush()
        ret_title.extend(titles)
        ret_url.extend(urls)
    return ret_title, ret_url


def single_page_news_analyze(url, pat, sub_pat, valve):
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
        if ret_2.a is None:
            break
        title = ret_2.a.get_text()
        if is_double_target_string(title, pat, sub_pat):
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


def get_time_stamp():
    time_str = time.strftime('%m%d-%H%M%S', time.localtime(time.time()))
    return time_str


def report_analyze(url, r_pat, rst_writer):
    # rst_writer.write(get_time_stamp())
    # rst_writer.write('\n')
    # rst_writer.flush()
    bs = basic_connect_test(url)
    #  print 'bs, url:', bs
    res = bs.find_all(name='p')
    for ee in res:
        exa = ee.get_text()
        #  print exa
        if is_target_string(exa, r_pat):
            rst_writer.write(url)
            rst_writer.write('\n')
            rst_writer.write(exa)
            rst_writer.write('\n\n')
            rst_writer.flush()
            print 'Succeed!'
            break
    return 0


def mid_reader(path, r_pat, rst_writer):
    mid_rdr = open(path, 'r')
    contents = mid_rdr.readlines()
    i = 2
    while i <= len(contents)-1:
        #  print 'url:', contents[i]
        if is_target_string(contents[i], r'http:|https:'):
            report_analyze(contents[i], r_pat, rst_writer)
            print 'processed ', i, ' / ', len(contents)-1
            if TEST_FLAG:
                print contents[i], contents[i-1]
        i += 1
    return 0


if __name__ == '__main__':
    # to test the funtion here
    reload(sys)
    sys.setdefaultencoding('utf-8')
    rigid_pat = r'una terrorista|la terrorista|las terroristas|de Oriente'
    pattern = r'una terroris|la terroris|las terroris|trump'
    international = 'http://elpais.com/tag/c/15148420ba519668342b7a63149cad97'
    elpaisUrl = 'http://www.elpais.com'
    exptURL = 'http://dblp.uni-trier.de/db/conf/spaa/'
    conf_url = 'http://dblp.uni-trier.de/db/conf/asplos/'
    paper_url = 'http://dblp.uni-trier.de/db/conf/icde/icde2016.html'
    report_url = 'http://internacional.elpais.com/internacional/2017/01/30/actualidad/1485745242_048891.html'
    result_writer_fak = open('./rst/tryResult'+get_time_stamp()+'.md', 'w')

    url_list_name_temp = 'internacional-una-terrorista.md'
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
    #  single_column_analyze(international, pattern, 20161200)
    try:
        #  print get_time_stamp()
        #  report_analyze(report_url, rigid_pat, result_writer_fak)
        mid_reader('./src/'+url_list_name_temp, rigid_pat, result_writer_fak)
    finally:
        result_writer_fak.close()

