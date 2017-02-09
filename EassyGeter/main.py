#!/usr/bin/env python
# encoding=utf-8
import sys
import ConfPartFunc
import elpaisGeter

JOURNAL_URL = 'http://dblp.uni-trier.de/db/journals/tpds/'
VOLUME_URL = 'http://dblp.uni-trier.de/db/journals/tocs/tocs34.html'
REGEX_PAT = r'consis|repli'

ELPAIS_INTERNATIONAL = 'http://elpais.com/tag/c/15148420ba519668342b7a63149cad97'
ELPAIS_OPINION_EDITORIAL = 'http://elpais.com/tag/c/514bd6a205caa1702b2026725f48a60d'
REGEX_PAT_2 = r'una terror|la terror|las terror|terrorista'
SUB_REGEX_PAT = r'una'

BREAKPOINT_URL = 'http://elpais.com/tag/c/514bd6a205caa1702b2026725f48a60d/1537'

if __name__ == '__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8')
    writeFile = open('tryWrite.md', 'w')
    try:
        titles, urls = elpaisGeter.single_column_analyze(BREAKPOINT_URL, REGEX_PAT_2, SUB_REGEX_PAT, 19991220,
                                                         writeFile)
        # i = 0
        # while i < len(titles):
        #     writeFile.write('#####')
        #     writeFile.write(titles[i])
        #     writeFile.write('\n')
        #     writeFile.write(urls[i])
        #     writeFile.write('\n')
        #     i += 1
    finally:
        writeFile.close()
        #  readUrl.close()
