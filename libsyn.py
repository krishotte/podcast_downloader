import requests
from bs4 import BeautifulSoup
from requests_futures.sessions import FuturesSession
import re
from os import path, mkdir

session_requests = requests.session()


class Downloader:
    """
    gets response in background, then saves data in foreground, wrapped in class
    """
    def __init__(self, data_dir):  # , toget):
        self.done = 0
        self.results_queue = []
        i = 0
        self.toget_ = []
        self.items_ = []
        self.data_dir = data_dir
        if not path.isdir(self.data_dir):
            mkdir(self.data_dir)
            print('directory created: ', self.data_dir)
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

    def get_items(self, url):
        """
        gets list of available podcast for download
        :param url: url to scrape
        :return: list of items - dictionaries
        """
        url = 'http://angriesttrainer.libsyn.com/rss'
        result = session_requests.get(url)
        bs4_obj = BeautifulSoup(result.content, 'html.parser')
        # print(bs4_obj.prettify())
        b = bs4_obj.find_all('item')
        items_ = []
        for i in b:
            try:
                print('title: ', i.find('title'))
                print('url: ', i.find('enclosure')['url'])
                print('duration: ', i.find('itunes:duration').get_text())
                # print('desc: ', i.find('description').get_text())
                item_ = {
                    'title': i.find('title').get_text(),
                    'url': i.find('enclosure')['url'],
                    'duration': i.find('itunes:duration').get_text(),
                    'desc': i.find('description').get_text()
                }
                items_.append(item_)
            except:
                pass
        print('items length: ', len(items_))
        # print('items: ', items_)
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
                each['filename'] = m.group() + '.mp3'
            except(AttributeError):
                each['filename'] = each['title'] + '.mp3'
            itemsout.append(each)
            print('   ', each['filename'])
            # print('   ', m)
        self.items_ = itemsout
        # print('items w filenames: ', self.items_)
        return itemsout

    def check_saved(self):
        'checks which files are already saved'
        itemsout = []
        for each in self.items_:
            saved = path.isfile(path.join(self.data_dir, each['filename']))
            each['saved'] = saved
            each['selectable'] = not saved
            if saved:
                print('file ', each['filename'], ' is saved')
            itemsout.append(each)
        # print('items check saved: ', itemsout)
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
        print('toget items: ') #, self.toget_)
        for each in self.toget_:
            print('   ', each['url'])

    def bg_cg(self, sess, resp):
        'background_callback function - called when data is complete'
        print('id: ', sess.index)
        print('data retrieved in class, i:' + str(sess.index)) #str(sess.request.params)) #str(sess.headers))
        self.results_queue.append(sess.index)

    def getdata(self, datadir):
        'gets and saves data'
        self.requests = []
        self.done = 0
        for each in self.toget_:
            self.requests.append(each['sess'].get(each['url'], background_callback=self.bg_cg))
        while self.done < len(self.toget_):
            if len(self.results_queue) > 0:
                id_to_save = self.results_queue.pop(0)
                open(path.join(datadir, self.toget_[id_to_save]['filename']), 'wb').write(self.requests[id_to_save].result().content)
                print('data saved: ' + self.toget_[id_to_save]['filename'])
                self.done = self.done + 1


class Downloader2(Downloader):
    def get_items(self, url):
        print('url: ', url)
        result = session_requests.get(url)
        bs4_obj = BeautifulSoup(result.content, 'html.parser')
        # print(bs4_obj.prettify())
        b = bs4_obj.find_all('item')
        items_ = []
        for i in b:
            try:
                print('title: ', i.find('title'))
                print('url: ', i.find('enclosure')['url'])
                print('length: ', i.find('enclosure')['length'])
                # print('desc: ', i.find('description').get_text())
                item_ = {
                    'title': i.find('title').get_text(),
                    'url': i.find('enclosure')['url'],
                    'length': i.find('enclosure')['length'],
                    'duration': i.find('itunes:duration').get_text(),
                    'desc': i.find('description').get_text()
                }
                items_.append(item_)
            except:
                pass
        print('items lenght: ', len(items_))
        # print('items: ', items_)
        self.items_ = items_
        return items_

    def guess_filenames(self):
        'creates filenames from urls or titles'
        # TODO: use various search strategies, title can contain characters not allowed for file names
        # TODO: function for re search
        p = re.compile('Episode.[0-9]{1,3}[^\.]{1,32}')
        print('filenames: ')
        itemsout = []
        for each in self.items_:
            m = p.search(each['url'])
            try:
                each['filename'] = m.group()
            except AttributeError:
                each['filename'] = each['title']
            itemsout.append(each)
            print('   ', each['filename'])
            #print('   ', m)
        self.items_ = itemsout
        # print('items w filenames: ', self.items_)
        return itemsout


class Downloader3(Downloader2):
    """
    uses different strategies for file name generation
    """
    def guess_filenames(self):
        itemsout = []
        for each in self.items_:  # [0:10]:
            # print('url: ', each['url'])
            file_name = self._re_strategy2(each['url'])
            file_name_2 = self._re_strategy1(each['url'])
            print('    filename 1: ', file_name)
            print('    filename 2: ', file_name_2)
            if file_name_2 != '':
                each['filename'] = file_name_2
            else:
                each['filename'] = file_name
            print('   filename: ', each['filename'])
            itemsout.append(each)
        self.items_ = itemsout
        return itemsout

    def _re_strategy1(self, string):
        strategy = re.compile('Episode.{0,3}[0-9]{1,4}[^\.]{1,32}')
        print('string to search: ', string)
        match = strategy.search(string)
        try:
            found_string = match.group()
            found_string = found_string + '.mp3'
        except AttributeError:
            found_string = ''
        #print('strategy1, found_string: ', found_string)
        return found_string

    def _re_strategy2(self, string):
        delimiter = re.compile('/')
        d_count = len(delimiter.findall(string))
        # print('delimiter matches: ', d_count)
        start = 0
        positions = []
        for i in range(d_count):
            match = delimiter.search(string, start)
            start = match.end()
            positions.append(start)
        # print('  positions: ', positions)

        strategy1 = re.compile('[0-9]{1,4}')
        strategy2 = re.compile('.{1,64}\.mp3')
        # print('string to search: ', string)
        match1 = strategy1.search(string, positions[-2], positions[-1])
        match2 = strategy2.search(string, positions[-1])
        try:
            found_string = match1.group() + '_'
        except AttributeError:
            found_string = ''
        try:
            found_string_2 = match2.group()
        except AttributeError:
            found_string_2 = ''
        # print('strategy2, found_string: ', found_string + found_string_2)
        return found_string + found_string_2


def test2():
    dl2 = Downloader('C:\\Users\\pkrssak\\AppData\\Roaming\\podcast_downloader\\data')
    dl2.get_items('http://angriesttrainer.libsyn.com/rss')
    dl2.guess_filenames()
    dl2.check_saved()
    # lst = [1, 2, 4]
    # dl2.create_toget(lst)
    # dl2.getdata('C:\\Users\\pkrssak\\AppData\\Roaming\\podcast_downloader\\data')


def test3():
    dl3 = Downloader2('C:\\Users\\pkrssak\\AppData\\Roaming\\podcast_downloader\\data2')
    dl3.get_items('https://www.podcastinit.com/feed/mp3/')
    dl3.guess_filenames()
    dl3.check_saved()
    lst = [1, 2, 3, 4, 5]
    dl3.create_toget(lst)
    # dl3.getdata('C:\\Users\\pkrssak\\AppData\\Roaming\\podcast_downloader\\data2')


def test_downloader3():
    url1 = 'https://talkpython.fm/episodes/rss'
    url2 = 'https://www.podcastinit.com/feed/mp3/'
    url3 = 'http://angriesttrainer.libsyn.com/rss'
    dl = Downloader3('C:\\Users\\pkrssak\\AppData\\Roaming\\podcast_downloader\\data3')
    dl.get_items(url1)
    dl.guess_filenames()
    dl.check_saved()
    # lst = [1, 2, 3]
    # dl.create_toget(lst)
    # dl.getdata('C:\\Users\\pkrssak\\AppData\\Roaming\\podcast_downloader\\data3')


if __name__ == '__main__':
    # test3()
    # test2()
    test_downloader3()
    print('...done...')
    # input()
