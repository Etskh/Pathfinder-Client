

import kivy

from kivy.animation import Animation

from kivy.app import App

from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label


from core import CannedDataSource
from models import CharacterModel, ClassModel

# set the minimum Kivy version
kivy.require('1.0.6')


class CharacterDetailView(GridLayout):
    title = 'Character Detail'

    def __init__(self, character, callback, back_callback, **kwargs):
        self.character = character
        self.callback = callback
        self.back_callback = back_callback

        # TODO: Add the name and stuff as widgets
        # TODO: Add the long buttons for different sections
        # TODO: First, add the spells known button
        self.spellsKnown = 0

        # TEST
        # self.select_page(CharacterSpellsKnownView)

    def select_page(self, page):
        print 'Going to page ' + page.title
        self.callback(page)


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


class CharacterListView(GridLayout):
    title = 'Character List'

    def __init__(self, character_list, callback, **kwargs):
        super(CharacterListView, self).__init__(**kwargs)

        self.cols = 1
        self.callback = callback

        for character in character_list:
            self.add_widget(CharacterListItemView(character, callback))


class PathfinderWidget(GridLayout):

    def select_character(self, character):
        print 'character selected: ' + character.name
        self.character = character
        animation = Animation(pos=(-200, 0), t='out_bounce')

        animation.start(self.listView)

    def __init__(self, **kwargs):
        super(PathfinderWidget, self).__init__(**kwargs)

        self.cols = 1
        self.detailView = None

        self.character = None
        self.characterPage = None

        # Get the data-source
        self.dataSource = CannedDataSource()

        # Load all classes
        self.classes = self.dataSource.get(ClassModel)
        CharacterModel.classCollection = self.classes
        self.characters = self.dataSource.get(CharacterModel)

        self.listView = CharacterListView(self.characters, self.select_character)

        self.add_widget(self.listView)


class PathfinderAppView(App):

    def build(self):
        return PathfinderWidget()


if __name__ == '__main__':
    PathfinderAppView().run()

