from kivy.app import App
from kivy.uix.recycleview import RecycleView
from kivy.lang import Builder
from os import path
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

dir_path = path.dirname(path.realpath(__file__))
file_path = path.join(dir_path, 'downloader.kv')
print(file_path)
with open(file_path, encoding='utf-8') as f: # Note the name of the .kv 
    Builder.load_string(f.read())

class RV(RecycleView):
    snodes = []
    def __init__(self, **kwargs):
        super().__init__() #super(RV, self).__init__(**kwargs)
        #self.data = [{'text': str(x)} for x in range(40)]
        self.data = []
        '''for x in range(40):
            if x % 2 == 0:
                a = False #True
            else:
                a = False
            item = {
                'text': str(x),
                'act': a,
                'idx': x
            }
            self.data.append(item)'''
        self.refresh()
    def download(self):
        'downloads selected podcast files'
        print('RV selected nodes: ', self.snodes)
        
    def refresh(self):
        'refreshes podcast list'
        items = libsyn.get_items()
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
        print('rv: ', rv)
        print('index: ', index)
        print('data: ', data)
        return super(Item1, self).refresh_view_attrs(
            rv, index, data)
    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(Item1, self).on_touch_down(touch):
            return True
        if self.ids.slabel.collide_point(*touch.pos) and self.selectable:
            print('node selected: ', self.index)
            return self.parent.select_with_touch(self.index, touch)
    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        print('rv data index: ', rv.data[index])
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

class TestApp(App):
    def build(self):
        self.mainvidg = MainV()
        self.rvidg = RV()
        self.mrbl = MyRecycleBoxLayout()
        #self.rvidg.add_widget(self.mrbl)
        self.mainvidg.add_widget(self.rvidg)
        return self.mainvidg

if __name__ == '__main__':
    TestApp().run()