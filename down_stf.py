from requests_html import HTMLSession
import magic
from os import rename
from os.path import isfile
from lxml.etree import ParserError

sessions = HTMLSession()

def log(n_log):
    with open('craw.log', 'w') as f:
        f.write(n_log)

all_links = list()
for i in range(307900572, 307999999):
    print(i)
    url = 'http://portal.stf.jus.br/processos/downloadPeca.asp?id=%d' % i
    content = sessions.get(url).content
    with open('tmp_file', 'wb') as f:
        f.write(content)
        file_type = magic.from_file('tmp_file', mime=True).split('/')[1]
        if 'empty' in file_type:
            print('empty file, continuing')
            continue
        print(file_type)
        file_type = ''
        file_name = str(i) + '.' + file_type
        rename('tmp_file', file_name)
