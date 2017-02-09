#!/usr/bin/env python
# encoding=utf-8

import partFunc

JOURNAL_URL = 'http://dblp.uni-trier.de/db/journals/tpds/'
VOLUME_URL = 'http://dblp.uni-trier.de/db/journals/tocs/tocs34.html'
REGEX_PAT = r'consis|repli'

if __name__ == '__main__':
    #  print partFunc.is_target_string('consis', REGEX_PAT)
    #  print partFunc.is_target_string('BlueDBM: Distributed Flash Storage for Big Data Analytics', REGEX_PAT)
    #  partFunc.analyze_volume_to_name(VOLUME_URL, REGEX_PAT)
    readUrl = open('JournalEssayUrls.txt', 'r')
    writeFile = open('tryWrite.md', 'w+')
    try:
        journalsUrl = readUrl.readlines()
        for j_url in journalsUrl:
            title, urls, dates = partFunc.analyze_journal_to_volume(j_url)
            print title
            writeFile.write('###')
            writeFile.write(title)
            writeFile.write('\n')
            for url in urls:
                show = partFunc.analyze_volume_to_name(url, REGEX_PAT)
                print dates[urls.index(url)]
                writeFile.write('####')
                writeFile.write(dates[urls.index(url)])
                writeFile.write('\n')
                for e_show in show:
                    print e_show
                    writeFile.write('*   ')
                    writeFile.write(e_show)
                    writeFile.write('\n')
    finally:
        writeFile.close()
        readUrl.close()
