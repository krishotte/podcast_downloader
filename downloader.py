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

dir_path = path.dirname(path.realpath(__file__))
file_path = path.join(dir_path, 'downloader.kv')
print(file_path)
with open(file_path, encoding='utf-8') as f: # Note the name of the .kv 
    Builder.load_string(f.read())

class RV(RecycleView):
    'recycle view class'
    snodes = []
    def __init__(self, config_dir, config_file, downloader_class, **kwargs): 
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
            self.dl2 = libsyn.downloader(self.config['datadir'])
        else:
            self.dl2 = libsyn.downloader2(self.config['datadir'])
        self.refresh()
    def download(self):
        'downloads selected podcast files'
        print('RV selected nodes: ', self.snodes)
        self.dl2.create_toget(self.snodes)
        self.dl2.getdata(self.config['datadir'])
        self.refresh()
    def refresh(self):
        'refreshes podcast list and view, clears selection'
        self.snodes = []
        self.children[0].selected_nodes = []
        self.dl2.get_items(self.config['url'])
        self.dl2.guess_filenames()
        self.dl2.check_saved()
        items = self.dl2.items_ #libsyn.get_items()
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
    'description window class'
    description = StringProperty()
    def close_window(self):
        'closes description window'
        self.parent.remove_widget(self.parent.descwindow)
class MainV(BoxLayout):
    'contains controls and carousel with RVs'
    def __init__(self, config_dir):
        super().__init__()
        self.rvidg = RV(config_dir, 'downloader.json', 1)
        self.rvidg2 = RV(config_dir, 'downloader2.json', 2)
        self.rvs = [self.rvidg, self.rvidg2]
    def refresh(self):
        'calls refresh function of active RV'
        print('active RV: ', self.ids.kv_carousel.index)
        self.rvs[self.ids.kv_carousel.index].refresh()
    def download(self):
        'calls download function of active RV'
        print('active RV: ', self.ids.kv_carousel.index)
        print('selected nodes for download: ', self.rvs[self.ids.kv_carousel.index].snodes)
        self.rvs[self.ids.kv_carousel.index].download()
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
    def build(self):
        print('--------------')
        print('user datadir: ', self.user_data_dir)
        self.mainrel = MainRelative()
        self.mainvidg = MainV(self.user_data_dir)
        for each in self.mainvidg.rvs:
            self.mainvidg.ids.kv_carousel.add_widget(each)
        self.mainrel.add_widget(self.mainvidg)
        Window.size = (400, 800)
        return self.mainrel 

if __name__ == '__main__':
    Podcast_Downloader().run()