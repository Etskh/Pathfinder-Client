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
    """
    This is a group of models
    """

    def __init__(self, model_type):
        self.items = []
        self.model_type = model_type

    def load(self, items):
        """
        Loads in an array of dictionaries, and creates models out of them
        :param items: python array of objects
        :return: nothing
        """
        for item in items:
            self.items.append(self.model_type(item))

    def __getitem__(self, index):
        return self.items[index]

    def get_by_field(self, field, value):
        """
        Retrieves the first item where its `field` matches its value
        :param field: String name of the field to search for (eg: "name")
        :param value: String value of the field (eg: "George")
        :return: the matching element or None
        """
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

        if model.name == 'race':
            return self.load_from_file(model, 'data/races.json')
        if model.name == 'class':
            return self.load_from_file(model, 'data/classes.json')
        if model.name == 'character':
            return self.load_from_file(model, 'data/characters.json')
        if model.name == 'spell':
            return self.load_from_file(model, 'data/spells.json')
        return None

    def load_from_file(self, model, filename):
        "Loads a collection of models from a file and returns it"

        collection = Collection(model)
        with open(filename) as data_file:
            data = json.load(data_file)
            collection.load(data)
        return collection
