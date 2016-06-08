

import kivy

from kivy.app import App

from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen


from core import CannedDataSource
from models import CharacterModel

# set the minimum Kivy version
kivy.require('1.7.0')



#
# TODO: Move this to controller_core.py or something
#

class CharacterScreenChanger(GridLayout):

    def __init__(self, screen_class, page_callback, **kwargs):
        super(CharacterScreenChanger, self).__init__(**kwargs)

        self.cols = 2
        self.screen_class = screen_class
        self.page_callback = page_callback

        self.add_widget(Label(text=screen_class.title))
        self.btn = Button(text='>')
        self.btn.bind(on_press=self.goto_screen)
        self.add_widget(self.btn)

    def goto_screen(self, instance ):
        if instance == self.btn:
            self.page_callback(self.screen_class)
        return True







#
# TODO: Move These 2 classes to their own file
#

class SpellsKnownListItemView(GridLayout):

    def __init__(self, spell, **kwargs):
        super(SpellsKnownListItemView, self).__init__(**kwargs)

        self.cols = 1

        self.add_widget(Label(text='Message'))


class SpellsKnownListView(GridLayout, Screen):

    title = 'Spells Known'

    def __init__(self, character, dataSource, **kwargs):
        kwargs['name'] = self.__class__.title
        super(SpellsKnownListView, self).__init__(**kwargs)

        self.cols = 1

        self.add_widget(SpellsKnownListItemView(spell=None))








#
# DailySpellsView
#


class DailySpellsView(GridLayout, Screen):
    title = 'Daily Spells'

    def __init__(self, character, dataSource, **kwargs):
        kwargs['name'] = self.__class__.title
        super(DailySpellsView, self).__init__(**kwargs)

        self.cols = 1

        self.add_widget(Label(text='Daily Spalls'))


#
# TODO: Move this to its own thingie
#


class CharacterStatsView(GridLayout):

    def __init__(self, character, **kwargs):
        super(CharacterStatsView, self).__init__(**kwargs)

        self.cols = 3
        self.character = character

        self.init_widgets()

    def init_widgets(self):
        stats = [
            'str', 'dex', 'con', 'int', 'wis', 'cha'
        ]
        for stat in stats:
            self.add_widget(Label(text=stat))
            self.add_widget(Label(text=str(self.character.stats[stat])))
            mod = str(self.character.mod(stat))
            if mod[0] != '-':
                mod = '+' + mod
            self.add_widget(Label(text=mod))


class CharacterDetailInfoView(GridLayout):

    def __init__(self, character, **kwargs):
        super(CharacterDetailInfoView, self).__init__(**kwargs)

        self.cols = 4
        self.character = character

        self.init_widgets()

    def init_widgets(self):
        self.add_widget(Label(text=self.character.name, font_size=24))
        self.add_widget(Label(text=self.character.get_level_as_string()))
        self.add_widget(Label(text=self.character.race))

        self.add_widget(CharacterStatsView(self.character))


class CharacterDetailView(GridLayout, Screen):

    title = 'Character Detail'

    def __init__(self, character, callback, page_callback, **kwargs):
        kwargs['name'] = self.__class__.title
        super(CharacterDetailView, self).__init__(**kwargs)

        self.cols = 1

        self.character = character
        self.callback = callback
        self.page_callback = page_callback

        self.init_widgets()

    def init_widgets(self):
        self.add_widget(CharacterDetailInfoView(self.character))
        self.add_widget(CharacterScreenChanger(SpellsKnownListView, self.page_callback))
        self.add_widget(CharacterScreenChanger(DailySpellsView, self.page_callback))








#
# TODO: Move this to its own view file thing
#



class CharacterListItemView(GridLayout):

    def __init__(self, character_model, callback, **kwargs):
        super(CharacterListItemView, self).__init__(**kwargs)
        self.cols = 4
        self.character = character_model
        self.callback = callback

        self.init_widgets()

    def init_widgets(self):

        self.add_widget(Label(text=self.character.name))
        self.add_widget(Label(text=self.character.get_level_as_string()))
        self.add_widget(Label(text=self.character.race))
        btn = Button(text='>')
        btn.bind(on_press=self.open_character)
        self.add_widget(btn)

    def open_character(self, instance):
        self.callback(self.character)
        return False


class CharacterListView(Screen):

    title = 'Character List View'

    def __init__(self, character_list, callback, **kwargs):
        kwargs['name'] = self.__class__.title
        super(CharacterListView, self).__init__(**kwargs)

        self.cols = 1
        self.callback = callback

        for character in character_list:
            self.add_widget(CharacterListItemView(character, callback))









class PathfinderScreenManager(ScreenManager):

    def __init__(self, **kwargs):
        super(PathfinderScreenManager, self).__init__(**kwargs)

        self.data_source = CannedDataSource()
        characters = self.data_source.get(CharacterModel)

        self.selected_character = None
        self.detail_view = None

        self.add_widget(CharacterListView(characters, self.set_character))
        self.current = CharacterListView.title

    def set_character(self, character=None):
        self.selected_character = character

        if self.selected_character:
            # TODO: Go through all the children and delete CharacterDetailView
            self.detail_view = CharacterDetailView(character, self.set_character, self.set_screen)
            self.add_widget(self.detail_view)
            self.current = CharacterDetailView.title
        else:
            print 'going to the next one'
            self.current = CharacterListView.title

    def set_screen(self, cls):
        # TODO: Going to the screen cls
        new_screen = cls(self.selected_character, self.data_source)
        self.add_widget(new_screen)

        self.current = cls.title

    def goto_back(self):
        print('Going back to the whatever')




class HamburgerMenuView(GridLayout):
    def __init__(self, return_callback, **kwargs):
        super(HamburgerMenuView, self).__init__(**kwargs)

        self.cols = 3
        self.return_callback = return_callback

        btn = Button(text='<')
        btn.bind(on_press=self.return_callback)
        self.add_widget(btn)

        self.add_widget(Label(text='HAMBURGER'))
        self.add_widget(Label(text='='))





class PathFinderWidget(GridLayout):
    def __init__(self, **kwargs):
        super(PathFinderWidget, self).__init__(**kwargs)

        self.cols = 1
        self.pathfinder_screen_manager = PathfinderScreenManager()

        self.add_widget(HamburgerMenuView(self.return_callback))
        self.add_widget(self.pathfinder_screen_manager)

    def return_callback(self, instance):
        # Defer it to the screen manager
        self.pathfinder_screen_manager.goto_back()






class PathfinderAppView(App):

    def build(self):
        return PathFinderWidget()


if __name__ == '__main__':
    PathfinderAppView().run()

