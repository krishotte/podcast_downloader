from kivy.app import App
from kivy.uix.recycleview import RecycleView
from kivy.lang import Builder
from os import path, mkdir
from kivy.uix.boxlayout import BoxLayout
#from kivy.uix.checkbox import CheckBox
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
#from kivy.factory import Factory
from kivy.uix.label import Label
import libsyn
from m_file import ini2
from kivy.core.window import Window
from kivy.uix.relativelayout import RelativeLayout
from kivy.clock import Clock

dir_path = path.dirname(path.realpath(__file__))
file_path = path.join(dir_path, 'downloader.kv')
print(file_path)
with open(file_path, encoding='utf-8') as f: # Note the name of the .kv 
    Builder.load_string(f.read())


class RV(RecycleView):
    'recycle view class'
    snodes = []

    def __init__(self, config_dir, name, config_file, downloader_class, **kwargs):
        super().__init__() #super(RV, self).__init__(**kwargs)
        self.data = []
        self.config_dir = config_dir
        print('configdir: ', self.config_dir)
        inifile = ini2()
        self.config = inifile.read(path.join(self.config_dir, config_file)) #'downloader.json'))
        if not self.config:
            print('dictionary is empty')
            self.config['datadir'] = path.join(self.config_dir, 'data')
            inifile.write(path.join(self.config_dir, config_file), self.config)
        #print(dict1)
        print('directory exists: ', path.isdir(self.config['datadir']))
        if not path.isdir(self.config['datadir']):
            mkdir(self.config['datadir'])
            print('directory created')
        if downloader_class == 1:
            self.dl2 = libsyn.Downloader(self.config['datadir'], chunk=2000000)
        else:
            self.dl2 = libsyn.Downloader3(self.config['datadir'], chunk=2000000)
        self.refresh()

    def download(self):
        """
        downloads selected podcast files
        """
        print('RV selected nodes: ', self.snodes)
        self.dl2.create_toget(self.snodes)
        self.nodes_to_download = self.snodes
        # self.dl2.getdata(self.config['datadir'])
        # self.dl2.get_data_chunks(self.config['datadir'])

        self.refresh()
        self.dl2.start_download()
        self.download_event = Clock.schedule_once(self.check_download_status, 0.1)

        # self.refresh()

        for node in self.nodes_to_download:
            self.data[node]['download_progress'] = '0'

    def check_download_status(self, *args):
        """
        checks if download is in progress
        schedules itself again if download is not finished
        :return:
        """
        if self.dl2.check_done() is False:
            self.download_progress = self.dl2.get_data_chunk()
            print(' download progress: ', self.download_progress)

            # update displayed download progresses
            i = 0
            for node in self.nodes_to_download:
                self.data[node]['download_progress'] = str(self.download_progress[i])
                i += 1

            if self.dl2.check_done() is True:
                self.dl2.cleanup()
                self.nodes_to_download = []
                self.refresh()
            self.download_event = Clock.schedule_once(self.check_download_status, 0.05)
            self.refresh_from_data()

    def refresh(self):
        'refreshes podcast list and view, clears selection'
        self.snodes = []
        self.children[0].selected_nodes = []
        self.dl2.get_items(self.config['url'])
        self.dl2.guess_filenames()
        self.dl2.check_saved()
        items = self.dl2.items_  # libsyn.get_items()
        items_ = []
        for i in range(len(items)):
            a = {}
            a['text'] = items[i]['title']
            a['idx'] = str(i)
            a['saved'] = items[i]['saved'] 
            a['selectable'] = items[i]['selectable'] 
            a['selected'] = False
            a['duration'] = items[i]['duration']
            a['desc'] = items[i]['desc']
            a['download_progress'] = ''
            items_.append(a)
        self.data = items_
        #for each in self.data:
        #    print('self.data: ', each)
        self.refresh_from_data()        #need to be called to properly refresh view and clear selections

    def display_description(self, index):
        'displays description window'
        print('description displayed: ', index)
        self.parent.parent.parent.parent.descwindow.description = self.data[index]['desc']
        try:
            self.parent.parent.parent.parent.add_widget(self.parent.parent.parent.parent.descwindow)
        except:
            pass


class DescriptionWindow(BoxLayout):
    '''description window class'''
    description = StringProperty()

    def close_window(self):
        'closes description window'
        self.parent.remove_widget(self.parent.descwindow)


class MainV(BoxLayout):
    'contains controls and carousel with RVs'
    name = StringProperty()

    def __init__(self, config_dir):
        super().__init__()
        inifile = ini2()
        self.config = inifile.read(path.join(config_dir, 'config.json')) #'downloader.json'))
        if not self.config:
            print('missing config.json')
            config = [
                {
                    'name': 'Vinnie Tortorich',
                    'json': 'downloader.json',
                    'downloader class': 1
                },
                {
                    'name': 'podcast.__init__',
                    'json': 'downloader2.json',
                    'downloader class': 2
                }
            ]
            print('configuration to write: ', config)
            inifile.write(path.join(config_dir, 'config.json'), config)
            raise Exception('---')
        else:
            self.rvs = []
            for each in self.config:
                rv = RV(config_dir, each['name'], each['json'], each['downloader class'])
                self.rvs.append(rv)
            self.name = self.config[0]['name']

    def refresh(self):
        'calls refresh function of active RV'
        print('active RV: ', self.ids.kv_carousel.index)
        self.rvs[self.ids.kv_carousel.index].refresh()

    def download(self):
        'calls download function of active RV'
        print('active RV: ', self.ids.kv_carousel.index)
        print('selected nodes for download: ', self.rvs[self.ids.kv_carousel.index].snodes)
        self.rvs[self.ids.kv_carousel.index].download()

    def name_update(self):
        'updates name label - podcast title'
        self.name = self.config[self.ids.kv_carousel.index]['name']


class MainRelative(RelativeLayout):
    'main relative layout window, contains MainV and DescriptionWindow'
    descwindow = DescriptionWindow()


class Item1(RecycleDataViewBehavior, BoxLayout):
    'items class, list is built from instances of this class'
    text = StringProperty()
    act = BooleanProperty()
    idx = NumericProperty()
    index = idx
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    saved = BooleanProperty(False)
    duration = StringProperty()
    download_progress = StringProperty()

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(Item1, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(Item1, self).on_touch_down(touch):
            return True
        if self.ids.slabel.collide_point(*touch.pos) and self.selectable:
            print('node selected: ', self.index)
            return self.parent.select_with_touch(self.index, touch)
        if self.ids.title1.collide_point(*touch.pos):
            print('title pressed: ', self.index)
            return self.parent.parent.display_description(self.index)
        else:
            pass

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected


class MyRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    'modified RecycleBoxLayout with behavior capabilities'
    def apply_selection(self, index, view, is_selected):
        print('layout nodes selected: ', self.selected_nodes)
        self.parent.snodes = self.selected_nodes
        return super().apply_selection(index, view, is_selected)


class Podcast_Downloader(App):
    def get_data_dir(self):
        'Gets suitable datadir - android patch'
        try:
            self.my_data_dir = self.user_data_dir
            print('user datadir: ', self.my_data_dir)
            if not path.exists(self.my_data_dir):
                print('creating dir: ', self.my_data_dir)
                mkdir(self.my_data_dir)
            else:
                pass
        except:
            print('user datadir cannot be created. trying /storage/emulated/0')
            data_dir = path.join('/storage/emulated/0', self.name)
            if not path.exists(data_dir):
                print('creating dir: ', data_dir)
                try:
                    mkdir(data_dir)
                except:
                    pass
            self.my_data_dir = data_dir
        print('using user datadir: ', self.my_data_dir)

    def build(self):
        print('--------------')
        # print('user datadir: ', self.user_data_dir)
        self.get_data_dir()
        self.mainrel = MainRelative()
        self.mainvidg = MainV(self.my_data_dir)
        for each in self.mainvidg.rvs:
            self.mainvidg.ids.kv_carousel.add_widget(each)
        self.mainrel.add_widget(self.mainvidg)
        Window.size = (400, 800)
        return self.mainrel 


if __name__ == '__main__':
    Podcast_Downloader().run()
