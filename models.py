

import json
import math

from core import Model, Collection, CannedDataSource


class SizeModel(Model):

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
        self.size = SizeModel( data['size'])

    def __str__(self):
        return str(self.name)






class SpellModel(Model):

    name = 'spell'

    def __init__(self, data):
        self.name = data['name']
        self.levels = data['levels']
        self.school = data['school']
        self.effect = data['effect']






class ClassLevelModel(Model):
    name = 'class-level'

    def __init__(self, data):
        self.level = data['level']
        self.base_attack = data['base_attack']
        self.fort_save = data['fort_save']
        self.ref_save = data['ref_save']
        self.will_save = data['will_save']
        try:
            self.spd = data['spd']
        except KeyError:
            self.spd = []


class UnknownRateError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class ClassModel(Model):
    name = 'class'

    def __init__(self, data):
        self.name = data['name']
        self.description = data['description']
        self.levels = Collection(ClassLevelModel)
        level_data = []

        for i in range(1, 20):
            level = {
                'level': i,
                'base_attack': ClassModel.get_rate_at_level(data['base_attack_rate'], i),
                'fort_save': ClassModel.get_rate_at_level(data['fort_save'], i),
                'ref_save': ClassModel.get_rate_at_level(data['ref_save'], i),
                'will_save': ClassModel.get_rate_at_level(data['will_save'], i),
            }
            try:
                level['spd'] = ClassModel.get_spd_at_level(data['spells_per_day_rate'], i)
            except KeyError:
                pass
            level_data.append(level)

        self.levels.load(level_data)

        try:
            self.bonus_spells_per_day = data['bonus_spells_per_day']
            self.casting_stat = data['casting_stat']
        except KeyError:
            self.bonus_spells_per_day = False
            self.casting_stat = None


    @staticmethod
    def get_rate_at_level(rate, level):
        # Base attack bonuses
        if rate == 'fast':
            return level
        if rate == 'average':
            return level / 1.5
        if rate == 'slow':
            return level / 2

        if rate == 'strong':
            return (level + 4) / 2
        if rate == 'weak':
            return level / 3

        raise UnknownRateError(rate)

    @staticmethod
    def wide_spell_count_at_level(char_level, spell_level):
        # =FLOOR(MIN(4,IF(C$2=0,1,0)+LOG(MAX(1,$B7 - (C$2*2)+3)) *4.5))
        log_arg = max(1.0, float(char_level) - (float(spell_level) * 2) + 3)
        real_answer = 1.0 if spell_level == 0 else 0
        real_answer += math.log(log_arg, 10) * 4.5
        real_answer = math.floor(min(4.0, real_answer))
        return real_answer

    @staticmethod
    def get_spd_at_level(rate, level):

        if rate == 'wide':
            spd = {}
            for i in range(0, 10):
                spd[str(i)] = ClassModel.wide_spell_count_at_level(level, i)
            return spd

        if rate == 'late':
            return {}

        raise UnknownRateError(rate)

    def at(self, level):
        return self.levels.get_by_field('level', level)



class SpellSlot():
    def __init__(self, **kwargs):

        self.reason = kwargs['reason']
        self.level = kwargs['level']
        self.cls = kwargs['cls']

        try:
            self.school = kwargs['school']
        except KeyError:
            self.school = None



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

        # Now getting all local data
        game_data = CannedDataSource()
        races = game_data.get(RaceModel)
        classes = game_data.get(ClassModel)

        self.race = races.get_by_field('name', data['race'])

        # Now load in the classes
        self.levels = {}
        self.classes = {}

        for cls in data['classes']:
            self.levels[cls] = data['classes'][cls]
            self.classes[cls] = classes.get_by_field('name', cls)


        # TODO: Make this into the choice system
        try:
            self.school_specialization = data['school_specialization']
        except KeyError:
            self.school_specialization = None

        self.spells_known = data['spells_known']
        self.spells = []

        self._spell_slots = None


    def get_level_as_string(self):
        levels = []
        for levelClass in self.levels:
            levels.append('{0} {1}'.format(levelClass, self.levels[levelClass]))
        return ' / '.join(levels)

    @property
    def spell_slots(self):
        text = {
            'int': 'smart',
            'wis': 'wise',
            'cha': 'charismatic',
        }

        if self._spell_slots:
            return self._spell_slots

        # For every class,
        #
        for cls in self.classes:
            class_level = self.classes[cls].at(self.levels[cls])

            print(class_level.__dict__)

            # For every spell-level you can cast
            #
            for spell_level in class_level.spd:

                spell_count = int(class_level.spd[spell_level])

                for x in range(0, spell_count):

                    # Add that many spells
                    #
                    self.add_spell_slot(
                       reason='Daily spells per level {} ({} of {})'.format(
                           spell_level, x, spell_count
                       ),
                       cls=self.classes[cls],
                       level=spell_level
                    )

            # Now add bonus spells for being smart, funny, wise
            #
            if self.classes[cls].bonus_spells_per_day:
                # Add lots of values
                casting_stat = self.classes[cls].casting_stat

                if self.stats[casting_stat] > 18:
                    self.add_extra_spell_slot(
                        reason='Being ' + text[casting_stat],
                        level=4,  # or whatever it is
                        cls=self.classes[cls]
                    )
                if self.stats[casting_stat] > 16:
                    self.add_extra_spell_slot(
                        reason='Being moderately ' + text[casting_stat],
                        level=3,  # or whatever it is
                        cls=self.classes[cls]
                    )
                if self.stats[casting_stat] > 14:
                    self.add_extra_spell_slot(
                        reason='Being reasonably ' + text[casting_stat],
                        level=2,  # or whatever it is
                        cls=self.classes[cls]
                    )
                if self.stats[casting_stat] > 12:
                    self.add_extra_spell_slot(
                        reason='Being above average ' + text[casting_stat],
                        level=1,  # or whatever it is
                        cls=self.classes[cls]
                    )

        return self._spell_slots

    def add_extra_spell_slot(self, **kwargs):
        """
            Same as add_spell_slot, except it checks that there's already
            a spell of the level that can be casted
        """
        # TODO: Check that the character can cast the spells:

        return self.add_spell_slot(**kwargs)

    def add_spell_slot(self, **kwargs):

        casting_stat = kwargs['cls'].casting_stat
        if int(kwargs['level']) + 10 > self.stats[casting_stat]:
            return False

        if not self._spell_slots:
            self._spell_slots = []

        self._spell_slots.append(
            SpellSlot(**kwargs)
        )

        return True

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
    def size(self):
        return self.race.size

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


