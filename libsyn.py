import requests
from bs4 import BeautifulSoup
session_requests = requests.session()
from requests_futures.sessions import FuturesSession
import time
import re
from os import path

class downloader():
    'gets response in background, then saves data in foreground, wrapped in class'
    def __init__(self, data_dir): #, toget):
        self.done = 0
        self.results_queue = []
        i=0
        self.toget_ = []
        self.items_ = []
        self.data_dir = data_dir
        '''
        for each in self.toget:
            each['id'] = i
            se = FuturesSession()
            se.index = i
            each['sess'] = se
            i = i + 1
            self.toget_.append(each)
        print('toget_ : ', self.toget_)
        '''
    def get_items(self):
        'gets list of available podcast for download'
        url = 'http://angriesttrainer.libsyn.com/rss'
        result = session_requests.get(url)
        bs4_obj = BeautifulSoup(result.content, 'html.parser')
        #print(bs4_obj.prettify())
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
        #print('items: ', items_)
        self.items_ = items_
        return items_
    def guess_filenames(self): #, items):
        'creates filenames from titles'
        p = re.compile('Episode\s\d\d\d\d')
        print('filenames: ')
        itemsout = []
        for each in self.items_:
            m = p.search(each['title'])
            try:
                each['filename'] = m.group()
            except(AttributeError):
                each['filename'] = each['title']
            itemsout.append(each)
            print('   ', each['filename'])
            #print('   ', m)
        self.items_ = itemsout
        #print('items w filenames: ', self.items_)
        return itemsout
    def check_saved(self):
        'checks which files are already saved'
        itemsout = []
        for each in self.items_:
            saved = path.isfile(path.join(self.data_dir, each['filename'] + '.mp3'))
            each['saved'] = saved
            each['selectable'] = not saved
            if saved:
                print('file ', each['filename'], ' is saved')
            itemsout.append(each)
        #print('items check saved: ', itemsout)
        self.items_ = itemsout
    def create_toget(self, toget_list):
        self.toget_ = []
        idx = 0
        for i in toget_list:
            item = self.items_[i]
            se = FuturesSession()
            se.index = idx
            item['sess'] = se
            idx = idx + 1
            self.toget_.append(item)
        print('toget items: ', self.toget_)
    def bg_cg(self, sess, resp):
        'background_callback function - called when data is complete'
        print('id: ', sess.index)
        print('data retrieved in class, i:' + str(sess.index)) #str(sess.request.params)) #str(sess.headers))
        self.results_queue.append(sess.index)
    def getdata(self, datadir):
        'gets and saves data'
        self.requests = []
        for each in self.toget_:
            self.requests.append(each['sess'].get(each['url'], background_callback=self.bg_cg))
        while self.done < len(self.toget_):
            if len(self.results_queue) > 0:
                id_to_save = self.results_queue.pop(0)
                open(path.join(datadir, self.toget_[id_to_save]['filename'] + '.mp3'), 'wb').write(self.requests[id_to_save].result().content)
                print('data saved: ' + self.toget_[id_to_save]['filename'])
                self.done = self.done + 1

def test2():
    dl2 = downloader('C:\\Users\\pkrssak\\AppData\\Roaming\\podcast_downloader\\data')
    dl2.get_items()
    dl2.guess_filenames()
    dl2.check_saved()
    #lst = [1, 2, 4]
    #dl2.create_toget(lst)
    #dl2.getdata('C:\\Users\\pkrssak\\AppData\\Roaming\\podcast_downloader\\data')

#test1()
#test2()
#print('...done...')

#input()