import requests
from bs4 import BeautifulSoup
session_requests = requests.session()
from requests_futures.sessions import FuturesSession
import time
import re

def get_items():
    'gets list of available podcast for download'
    url = 'http://angriesttrainer.libsyn.com/rss'
    result = session_requests.get(url)
    bs4_obj = BeautifulSoup(result.content, 'html.parser')
    print(bs4_obj.prettify())

    b = bs4_obj.find_all('item')
    items_ = []
    for i in b:
        try:
            print('title: ', i.find('title'))
            print('url: ', i.find('enclosure')['url'])
            item_ = {
                'title': i.find('title').get_text(),
                'url': i.find('enclosure')['url']
            }
            items_.append(item_)
        except:
            pass

    print('items lenght: ', len(items_))
    print('items: ', items_)
    return items_

class _session():
    def __init__(self, index):
        s = FuturesSession()
        s.index = index

class downloader():
    'gets response in background, then saves data in foreground, wrapped in class'
    def __init__(self, toget):
        self.done = 0
        self.results_queue = []
        i=0
        self.toget_ = []
        for each in toget:
            each['id'] = i
            se = FuturesSession()
            se.index = i
            each['sess'] = se
            i = i + 1
            self.toget_.append(each)
        print('toget_ : ', self.toget_)
    def guess_filenames(self, items):
        'creates filenames from titles'
        p = re.compile('Episode\s\d\d\d\d')
        print('filenames: ')
        itemsout = []
        for each in items:
            m = p.search(each['title'])
            try:
                each['filename'] = m.group()
            except(AttributeError):
                each['filename'] = each['title']
            itemsout.append(each)
            print('   ', each['filename'])
            #print('   ', m)
        return itemsout
    def bg_cg(self, sess, resp):
        'background_callback function - called when data is complete'
        print('id: ', sess.index)
        print('data retrieved in class, i:' + str(sess.index)) #str(sess.request.params)) #str(sess.headers))
        self.results_queue.append(sess.index)
    def getdata(self):
        'gets and saves data'
        self.requests = []
        for each in self.toget_:
            self.requests.append(each['sess'].get(each['url'], background_callback=self.bg_cg))
        while self.done < len(self.toget_):
            if len(self.results_queue) > 0:
                id_to_save = self.results_queue.pop(0)
                open(self.toget_[id_to_save]['filename'] + '.mp3', 'wb').write(self.requests[id_to_save].result().content)
                print('data saved: ' + self.toget_[id_to_save]['filename'])
                self.done = self.done + 1

def test1():
    items_ = get_items()
    toget = []
    toget.append(items_[5])
    toget.append(items_[6])
    toget.append(items_[7])
    toget.append(items_[8])
    print(toget)

    dl = downloader(toget)
    dl.toget_ = dl.guess_filenames(items_)
    #dl.getdata()

#test1()

#print('...done...')

#input()