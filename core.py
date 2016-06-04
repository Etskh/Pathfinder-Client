

class Model(object):
    pass


class Collection(object):
    def __init__(self, model_type):
        self.items = []
        self.modelType = model_type

    def load(self, items):
        for item in items:
            self.items.append(self.modelType(item))

    def __getitem__(self, index):
        return self.items[index]

    def getByField(self, field, value):
        for item in self.items:
            if item.__dict__[field] == value:
                return item
        return None


class DataSource(object):
    pass


class CannedDataSource(DataSource):
    def __init__(self):
        pass

    def get(self, model):
        collection = Collection(model)
        if model.name == 'class':
            collection.load(self._class_data)
        if model.name == 'character':
            collection.load(self._character_data)
        return collection

    @property
    def _class_data(self):
        return [{
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

    @property
    def _character_data(self):
        return [{
            'name': 'Pig',
            'str': 9,
            'dex': 17,
            'con': 12,
            'int': 17,
            'wis': 13,
            'cha': 9,
            'classes': {
                'wizard': 3,
            },
            'race': 'goblin',
            'school_specialization': 'illusion',
            'spells_known': [
                'Silent Image',
                'Daze',
            ],
        }]
