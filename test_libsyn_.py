import requests
from bs4 import BeautifulSoup
session_requests = requests.session()
from requests_futures.sessions import FuturesSession
import time

session = FuturesSession(session=session_requests)
url = 'http://angriesttrainer.libsyn.com/rss'
result = session_requests.get(
            url,
            headers = dict(referer=url)
        )
bs4_obj = BeautifulSoup(result.content, 'html.parser')
#print(bs4_obj.prettify())

a = bs4_obj.find_all('enclosure')
for i in a:
    print(i['url']) #.find('url'))
    print('whole item: ', i)

"""
#gets response (blocking) and saves data in foreground
for i in range(3):
    url = a[i]['url'] #http://traffic.libsyn.com/angriesttrainer/1on1_MikhaliaPeterson_0918-REDO.mp3?dest-id=117301'
    print('about to download')
    result = session_requests.get(
                url,
                headers = dict(referer=url),
                allow_redirects=True
            )

    open(str(i) + 'a.mp3', 'wb').write(result.content)
    print('done')
"""

#gets response in the background, then saves data in foreground
url = a[3]['url']
urls = [a[3]['url'], a[4]['url']]
lengths = [int(a[3]['length']), int(a[4]['length'])]
done = False
def bg_cb(sess, resp):
    #resp.data = resp.json()
    global done
    done = True
    print('data retrieved') #len(resp.json()))
    #print(str(len(resp.json())))
    #return resp
def getdata():
    req1 = session.get(url, background_callback=bg_cb)
    while done == False:
        pass
    open('b01.mp3', 'wb').write(req1.result().content)

class downloader():
    'gets response in background, then saves data in foreground, wrapped in class'
    def __init__(self):
        self.url = a[0]['url']
        self.done = False

    def bg_cg(self, sess, resp):
        self.done = True
        print('i: ', sess.index)
        print('data retrieved in class, i:' + str(sess.headers)) #str(sess.request.params)) #str(sess.headers))

    def getdata(self):
        session.index = 6
        # self.req1 = session.get(self.url, background_callback=self.bg_cg, stream=True) #, background_callback_args=(5))
        # self.req1 = session_requests.get(self.url, stream=True)

        sess = []
        reqs = []
        done = []
        files = []

        j = 0
        for each in urls:
            sessn_ = requests.session()
            sess.append(sessn_)
            reqs.append(sessn_.get(each, stream=True))
            done.append(False)
            files.append(open(f'aa{j}.mp3', 'wb'))
            j += 1

        i = 0

        while sum(done) < len(done):
            print(' iteration: ', i)
            j = 0
            for each in reqs:
                try:
                    data = next(each.iter_content(chunk_size=10000000))
                    print(' downloading, session: ', j, ' % done: ', round((i * 10000000 + len(data))*100 / lengths[j], 1))
                    files[j].write(data)
                except (StopIteration, requests.exceptions.StreamConsumedError):
                    print(j, ' session download done')
                    done[j] = True
                j += 1
            i += 1

        for file in files:
            file.close()

        """
        while True:  # self.done == False:
            print(' iteration: ', i, ' length: ', self.req1)
            # data = self.req1.raw.read(1000)
            data = next(self.req1.iter_content(chunk_size=10000000))
            # print(' read data: ', data)
            i += 1
            # time.sleep(1)
        # open('c01.mp3', 'wb').write(self.req1.result().content)
        
        
        for chunk in self.req1.iter_content(chunk_size=3000000):
            print(' i: ', i)
            print(' chunk length:', len(chunk))
            # print(' chunk data:', chunk)
            i += 1
        """

        print('data saved in class')


#getdata()

dl = downloader()
dl.getdata()

#print(req1.content)
#res1 = req1.result()

#print(str(len(res1.data)))
print('...done...')
# input()