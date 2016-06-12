"""
This is the core library for the pathfinder app
 - put general solutions here
"""

import json


class Model(object):
    "Base class for all models"

    def save(self):
        "Saves the model"
        pass

    def update(self):
        "Updates the model"
        pass


class Collection(object):
    "This is a group of models"

    def __init__(self, model_type):
        self.items = []
        self.model_type = model_type

    def load(self, items):
        "Loads in an array of dictionaries, and creates models out of them"
        for item in items:
            self.items.append(self.model_type(item))

    def __getitem__(self, index):
        return self.items[index]

    def get_by_field(self, field, value):
        "Retrieves the first item where its `field` matches its value"
        for item in self.items:
            if item.__dict__[field] == value:
                return item
        return None


class CannedDataSource(object):
    "Returns data from magic arrays (replace me)"

    def __init__(self):
        pass

    def get(self, model):
        "This retrieves all models of the type model"
        collection = Collection(model)
        if model.name == 'class':
            collection.load(CannedDataSource._class_data)
        if model.name == 'character':
            with open('data/characters.json') as data_file:
                data = json.load(data_file)
                collection.load(data)
        return collection

    _class_data = [{
        'name': 'wizard',
        'levels': [
            {
                'level': 1,
                'baseAttack': 0,
                'fortSave': 0,
                'refSave': 0,
                'willSave': 2,
                'spd': {
                    '0': 3,
                    '1': 1,
                },
            },
            {
                'level': 2,
                'baseAttack': 1,
                'fortSave': 0,
                'refSave': 0,
                'willSave': 3,
                'spd': {
                    '0': 4,
                    '1': 1,
                },
            },
            {
                'level': 3,
                'baseAttack': 1,
                'fortSave': 1,
                'refSave': 1,
                'willSave': 3,
                'spd': {
                    '0': 4,
                    '1': 1,
                    '2': 1,
                },
            },
        ]
    }]
