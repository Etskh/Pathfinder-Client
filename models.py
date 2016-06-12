

import json

from core import Model, Collection, CannedDataSource


class SizeModel(Model):

    # TODO: Turn the string-indexed indices into ACTUAL python objects

    def __init__(self, name):
        self.index = SizeModel._list[name]
        self.name = name
        # prop self.ac_bonus
        # prop self.attack_bonus
        # prop self.hide_bonus
        # prop self.lightest
        # prop self.heaviest

    @property
    def attack_bonus(self):
        return self.ac_bonus

    @property
    def ac_bonus(self):
        if self.index - 4 == 0:
            return 0
        return 2 ** (abs(self.index-4)-1) * (-1 if self.index < 4 else 1)

    @property
    def hide_bonus(self):
        self.ac_bonus * 4

    @property
    def lightest(self):
        return 8.0 ** (self.index - 2.0)

    @property
    def heaviest(self):
        return self.getLightest() * 8.0

    def compute_weight_ratio(self, other_size):
        this_delta = self.heaviest - self.lightest
        that_delta = other_size.heaviest - other_size.lightest
        return this_delta / that_delta

    _list = {
        'fine': -4,
        'diminutive': -3,
        'tiny': -2,
        'small': -1,
        'medium': 0,
        'large': 1,
        'huge': 2,
        'gargantuan': 3,
        'colossal': 4,
    }


class RaceModel(Model):

    name = 'race'

    def __init__(self, data):
        self.name = data['name']
        self.size = SizeModel('medium')

    def __str__(self):
        return str(self.name)






class SpellModel(Model):
    def __init__(self, data):
        self.name = data['name']
        self.levels = data['levels']
        self.school = data['school']
        self.effect = data['effect']

    @staticmethod
    def get_by_name(name):
        #
        # Initialize the spell objects
        SpellModel._initialize_spells()
        #
        # Now search for the spell
        for spell in SpellModel._all_spells:
            if spell.name == name:
                return spell
        return None

    @staticmethod
    def _initialize_spells():
        if not SpellModel._all_spells:
            SpellModel._all_spells = []
            for spell in SpellModel._spell_data:
                SpellModel._all_spells.append(SpellModel(spell))

    _all_spells = None
    _spell_data = [{
        'name': 'Message',
        'levels': {'wizard': 0},
        'school': 'abjuration',
        'effect': 'Point fingers at individuals and communicate',
    }, {
        'name': 'Daze',
        'levels': {'wizard': 0},
        'school': 'abjuration',
        'effect': 'Make one guy kinda fucked up a little',
    }, {
        'name': 'Silent Image',
        'levels': {'wizard': 1},
        'school': 'illusion',
        'effect': 'Creates a silent image',
    }]








class ClassLevelModel(Model):
    name = 'class-level'

    def __init__(self, data):
        self.level = data['level']
        self.baseAttack = data['baseAttack']
        self.fortSave = data['fortSave']
        self.refSave = data['refSave']
        self.willSave = data['willSave']







class ClassModel(Model):
    name = 'class'

    def __init__(self, data):
        self.name = data['name']
        self.levels = Collection(ClassLevelModel)
        self.levels.load(data['levels'])

    def atLevel(self, level):
        return self.levels.get_by_field('level', level)









class SpellSlotModel(Model):
    def __init__(self, description, character_req, spell_req):
        self.description = description
        self.character_req = character_req
        self.spell_req = spell_req

    def check_character(self, character):
        return self.character_req(character)

    def check_spell(self, spell):
        return self.spell_req(spell)








class CharacterModel(Model):

    name = 'character'
    classCollection = []

    def __init__(self, data):
        self.name = data['name']
        self.stats = {
            'str': int(data['str']),
            'dex': int(data['dex']),
            'con': int(data['con']),
            'int': int(data['int']),
            'wis': int(data['wis']),
            'cha': int(data['cha']),
        }

        # Now get the race from the data
        game_data = CannedDataSource()

        races = game_data.get(RaceModel)
        self.race = races.get_by_field('name', data['race'])

        # Now load in the classes
        self.levels = {}
        for cls in data['classes']:
            self.levels[cls] = data['classes'][cls]

        try:
            self.school_specialization = data['school_specialization']
        except KeyError:
            self.school_specialization = None

        self.spells_known = data['spells_known']
        self.spells = []

    def get_level_as_string(self):
        levels = []
        for levelClass in self.levels:
            levels.append('{0} {1}'.format(levelClass, self.levels[levelClass]))
        return ' / '.join(levels)

    def get_daily_spell_slots(self):
        slots = []
        for slot in CharacterModel.possibleSlots:
            if slot.check_character(self):
                slots.append(slot)

        # Now remove slots where there are zero known
        # spells that fit that criteria
        for knownSpellName in self.spells_known:
            spell = SpellModel.get_by_name(knownSpellName)
            if spell:
                self.spells.append(spell)

        # Check that every slot has at least one spell
        for slot in slots:
            has_spell = False
            for spell in self.spells:
                if slot.check_spell(spell):
                    has_spell = True
                    break

            if not has_spell:
                slots.remove(slot)

        return slots

    def __str__(self):
        return json.dumps(self.__dict__)

    def mod(self, stat):
        return self.stats[stat] / 2 - 5

    def _getClassValue(self, valueName):
        val = 0
        for cls in self.levels:
            level = self.levels[cls]
            classModel = CharacterModel.classCollection.get_by_field('name', cls)
            val += classModel.atLevel(level).__dict__[valueName]
        return val

    @property
    def fortSave(self):
        return self._getClassValue('fortSave') + self.mod('con')

    @property
    def refSave(self):
        return self._getClassValue('refSave') + self.mod('dex')

    @property
    def willSave(self):
        return self._getClassValue('willSave') + self.mod('wis')

    @property
    def baseAttack(self):
        return self._getClassValue('baseAttack')



    possibleSlots = [
        SpellSlotModel(
            'Wizard gets 3 0-level spells at 1st level (1)',
            lambda character: character.levels['wizard'] > 0,
            lambda spell: spell.levels['wizard'] == 0,
        ),
        SpellSlotModel(
            'Wizard gets 3 0-level spells at 1st level (2)',
            lambda character: character.levels['wizard'] > 0,
            lambda spell: spell.levels['wizard'] == 0,
        ),
        SpellSlotModel(
            'Wizard gets 3 0-level spells at 1st level (3)',
            lambda character: character.levels['wizard'] > 0,
            lambda spell: spell.levels['wizard'] == 0,
        ),
        SpellSlotModel(
            'Wizard gets 2 1-level spells at 1st level (1)',
            lambda character: character.levels['wizard'] > 0,
            lambda spell: spell.levels['wizard'] == 1,
        ),
        SpellSlotModel(
            'Wizard gets 2 1-level spells at 1st level (2)',
            lambda character: character.levels['wizard'] > 0,
            lambda spell: spell.levels['wizard'] == 1,
        ),
        SpellSlotModel(
            'Wizard gets 1 0-level spells at 2nd level',
            lambda character: character.levels['wizard'] > 1,
            lambda spell: spell.levels['wizard'] <= 0,
        ),
        SpellSlotModel(
            'Wizard gets 1 1-level spells at 2nd level',
            lambda character: character.levels['wizard'] > 1,
            lambda spell: spell.levels['wizard'] <= 1,
        ),
        SpellSlotModel(
            'Wizard with at least INT 12 gets an additional 1st level spell',
            lambda character: character.stats['int'] > 12 and character.levels['wizard'] > 0,
            lambda spell: spell.levels['wizard'] == 1,
        ),
        SpellSlotModel(
            'Wizard with at least INT 14 gets an additional 2nd level spell',
            lambda character: character.stats['int'] > 14 and character.levels['wizard'] > 0,
            lambda spell: spell.levels['wizard'] == 2,
        ),
        SpellSlotModel(
            'Wizard with at least INT 16 gets an additional 3rd level spell',
            lambda character: character.stats['int'] > 16 and character.levels['wizard'] > 0,
            lambda spell: spell.levels['wizard'] == 3,
        ),
        SpellSlotModel(
            'Wizard specialization for Illusion grants a 1st level Illusion spell (1)',
            lambda character: character.school_specialization == 'illusion' and character.levels['wizard'] > 1,
            lambda spell: spell.levels['wizard'] == 1 and spell.school == 'illusion',
        ),
    ]



