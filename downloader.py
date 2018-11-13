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
#from kivy.uix.recycleview.datamodel import RecycleDataModel
#from kivy.factory import Factory
from kivy.uix.label import Label
import libsyn
from m_file import ini2
from kivy.core.window import Window

dir_path = path.dirname(path.realpath(__file__))
file_path = path.join(dir_path, 'downloader.kv')
print(file_path)
with open(file_path, encoding='utf-8') as f: # Note the name of the .kv 
    Builder.load_string(f.read())

class RV(RecycleView):
    snodes = []
    def __init__(self, data_dir, **kwargs):
        super().__init__() #super(RV, self).__init__(**kwargs)
        self.data = []
        self.refresh()
        self.data_dir = data_dir
        print('datadir: ', self.data_dir)
        inifile = ini2()
        self.config = inifile.read(path.join(self.data_dir, 'downloader.json'))
        if not self.config:
            print('dictionary is empty')
            self.config['datadir'] = path.join(self.data_dir, 'data')
            #inifile.write(path.join(self.data_dir, 'downloader.json'), self.config)
        #print(dict1)
        print('directory exists: ', path.isdir(self.config['datadir']))
        if not path.isdir(self.config['datadir']):
            mkdir(self.config['datadir'])
            print('directory created')
    def download(self):
        'downloads selected podcast files'
        print('RV selected nodes: ', self.snodes)
        self.dl2.create_toget(self.snodes)
        self.dl2.getdata(self.config['datadir'])
    def refresh(self):
        'refreshes podcast list'
        self.dl2 = libsyn.downloader()
        self.dl2.get_items()
        self.dl2.guess_filenames()
        items = self.dl2.items_ #libsyn.get_items()
        items_ = []
        for i in range(len(items)):
            a = {}
            a['text'] = items[i]['title']
            a['idx'] = str(i)
            items_.append(a)
        self.data = items_
        print('self.data: ', self.data)

class MainV(BoxLayout):
    pass
class Item1(RecycleDataViewBehavior, BoxLayout):
    text = StringProperty()
    act = BooleanProperty()
    idx = NumericProperty()
    index = idx #None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    
    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        #print('rv: ', rv)
        #print('index: ', index)
        #print('data: ', data)
        return super(Item1, self).refresh_view_attrs(
            rv, index, data)
    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(Item1, self).on_touch_down(touch):
            return True
        if self.ids.slabel.collide_point(*touch.pos) and self.selectable:
            #print('node selected: ', self.index)
            return self.parent.select_with_touch(self.index, touch)
    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        #print('rv data index: ', rv.data[index])
        #if is_selected:
            #print("selection changed to {0}".format(rv.data[index]))
        #else:
            #print("selection removed for {0}".format(rv.data[index]))
    
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
        self.mainvidg = MainV()
        self.rvidg = RV(self.user_data_dir)
        self.mrbl = MyRecycleBoxLayout()
        #self.rvidg.add_widget(self.mrbl)
        self.mainvidg.add_widget(self.rvidg)
        Window.size = (400, 800)
        return self.mainvidg

if __name__ == '__main__':
    Podcast_Downloader().run()