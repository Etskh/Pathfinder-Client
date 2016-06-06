

import kivy

from kivy.animation import Animation

from kivy.app import App

from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen


from core import CannedDataSource
from models import CharacterModel, ClassModel

# set the minimum Kivy version
kivy.require('1.7.0')


class CharacterDetailView(GridLayout, Screen):

    title = 'Character Detail'

    def __init__(self, character, callback, back_callback, **kwargs):
        kwargs['name'] = CharacterDetailView.title
        super(CharacterDetailView, self).__init__(**kwargs)

        self.cols = 3

        self.character = character
        self.callback = callback
        self.back_callback = back_callback

        # TODO: Add the name and stuff as widgets
        # TODO: Add the long buttons for different sections
        # TODO: First, add the spells known button
        self.spellsKnown = 0

        self.init_widgets()

        # TEST
        # self.select_page(CharacterSpellsKnownView)

    def init_widgets(self):
        self.add_widget(Label(text=self.character.name))
        self.add_widget(Label(text=self.character.get_level_as_string()))
        self.add_widget(Label(text=self.character.race))


    def select_page(self, page):
        self.callback(page)


class CharacterListView(Screen):

    title = 'Character List View'

    def __init__(self, character_list, callback, **kwargs):
        kwargs['name'] = CharacterListView.title
        super(CharacterListView, self).__init__(**kwargs)

        self.cols = 1
        self.callback = callback

        for character in character_list:
            self.add_widget(CharacterListItemView(character, callback))


class CharacterListItemView(GridLayout):

    def __init__(self, character_model, callback, **kwargs):
        super(CharacterListItemView, self).__init__(**kwargs)
        self.cols = 4
        self.character_model = character_model
        self.callback = callback

        self.add_widget(Label(text=character_model.name))
        self.add_widget(Label(text=character_model.get_level_as_string()))
        self.add_widget(Label(text=character_model.race))
        btn = Button(text='>')
        btn.bind(on_touch_down=self.open_character)
        self.add_widget(btn)

    def open_character(self, instance, mouse_motion_event):
        self.callback(self.character_model)


class PathfinderWidget(ScreenManager):

    def __init__(self, **kwargs):
        super(PathfinderWidget, self).__init__(**kwargs)

        data_source = CannedDataSource()
        characters = data_source.get(CharacterModel)

        self.selected_character = None
        self.detail_view = None

        self.add_widget(CharacterListView(characters, self.set_character))
        self.current = CharacterListView.title

    def set_character(self, character=None):
        self.selected_character = character
        if self.selected_character:
            self.detail_view = CharacterDetailView(character, self.set_screen, self.set_character)
            self.add_widget(self.detail_view)
            self.current = CharacterDetailView.title
        else:
            # TODO: Go back to the list of characters
            print('TODO: Go back to the list of characters')
        print("setting the character")

    def set_screen(self, cls):
        # TODO: Going to the screen cls
        print("Going to the screen " + cls)


pfw = PathfinderWidget()


class PathfinderAppView(App):

    def build(self):
        return pfw


if __name__ == '__main__':
    PathfinderAppView().run()

