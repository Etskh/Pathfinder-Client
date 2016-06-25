"""
The models for the pathfinder widget
"""

import json
import math

from core import Model, Collection, CannedDataSource


class SizeModel(Model):
    """
    Represents a size-class in the D&D world
    """

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
        """
        :return: The attack bonus granted to a character for its size
        """
        return self.ac_bonus

    @property
    def ac_bonus(self):
        """
        :return: The AC bonus granted to a character for its size
        """
        if self.index - 4 == 0:
            return 0
        return 2 ** (abs(self.index-4)-1) * (-1 if self.index < 4 else 1)

    @property
    def hide_bonus(self):
        """
        :return: The bonus granted to characters to stealth checks
        """
        return self.ac_bonus * 4

    @property
    def lightest(self):
        """
        :return: The lightest weight for this size
        """
        return 8.0 ** (self.index - 2.0)

    @property
    def heaviest(self):
        """
        :return: The heaviest weight
        """
        return self.lightest * 8.0

    def compute_weight_ratio(self, other_size):
        """
        :param other_size: another SizeModel instance
        :returns: the ratio between this size and another
        """
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
    """
    This is the concept of the race
    """

    name = 'race'

    def __init__(self, data):
        self.name = data['name']
        self.size = SizeModel(data['size'])

    def __str__(self):
        return str(self.name)






class SpellModel(Model):
    """
    Spell class to manage casting and effect
    """

    name = 'spell'

    def __init__(self, data):
        self.name = data['name']
        self.levels = data['levels']
        self.school = data['school']
        self.effect = data['effect']






class ClassLevelModel(Model):
    """
    Each level in a class has one of these
    """
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
    """
    Exception that is raised when the value is not one of
    the specified rates
    """
    def __init__(self, value):
        super(UnknownRateError, self).__init__()
        self.value = value

    def __str__(self):
        return repr(self.value)


class ClassModel(Model):
    """
    Important class of class
    """
    name = 'class'


    # pylint: disable:invalid-name
    # Fuck you pylint, I'll call my functions whatever I want

    def __init__(self, data):
        self.name = data['name']
        self.description = data['description']
        self.levels = Collection(ClassLevelModel)
        level_data = []

        for i in range(1, 20):
            level = {
                'level': i,
                'base_attack': ClassModel.rate_at_level(data['base_attack_rate'], i),
                'fort_save': ClassModel.rate_at_level(data['fort_save'], i),
                'ref_save': ClassModel.rate_at_level(data['ref_save'], i),
                'will_save': ClassModel.rate_at_level(data['will_save'], i),
            }
            try:
                level['spd'] = ClassModel.spd_at_level(data['spells_per_day_rate'], i)
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
    def rate_at_level(rate, level):
        """
        :param rate: one of 'fast', 'average', 'slow', 'strong', or 'weak'
        :param level: Integer (1-20)
        :return: the value of the algorithm at the level
        """
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
        """
        The "wide" spell per day implementation
        :param char_level: Integer (1-20)
        :param spell_level: Integer (0-9)
        :return: an integer of slots of that level per day
        """
        # =FLOOR(MIN(4,IF(C$2=0,1,0)+LOG(MAX(1,$B7 - (C$2*2)+3)) *4.5))
        log_arg = max(1.0, float(char_level) - (float(spell_level) * 2) + 3)
        real_answer = 1.0 if spell_level == 0 else 0
        real_answer += math.log(log_arg, 10) * 4.5
        real_answer = math.floor(min(4.0, real_answer))
        return real_answer

    @staticmethod
    def spd_at_level(rate, level):
        """
        :param rate: 'wide', 'late'
        :param level: 1-20
        :return: a dict of spells per day at a certain level
        """

        if rate == 'wide':
            spd = {}
            for i in range(0, 10):
                spd[str(i)] = ClassModel.wide_spell_count_at_level(level, i)
            return spd

        if rate == 'late':
            return {}

        raise UnknownRateError(rate)


    def at(self, level):
        """
        :param level: Integer
        :return: the ClassLevelModel instance at that level
        """
        return self.levels.get_by_field('level', level)


class SpellSlot(object):
    """
    This is just an object to act as a holder for some data
    """

    # pylint: disable=too-few-public-methods
    # This class will see the light of the sun!

    def __init__(self, **kwargs):

        self.reason = kwargs['reason']
        self.level = kwargs['level']
        self.cls = kwargs['cls']

        try:
            self.school = kwargs['school']
        except KeyError:
            self.school = None


class CharacterModel(Model):
    """
    The character class is the master controller class
    """
    name = 'character'

    # pylint: disable=too-many-instance-attributes
    # Character is like the master class!

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

        try:
            self.school_specialization = data['school_specialization']
        except KeyError:
            self.school_specialization = None

        self.spells_known = data['spells_known']

        self._spell_slots = None

    def get_level_as_string(self):
        """
        Returns something along the lines of Wizard 1/Rogue 2"
        :return: string of class and level
        """
        levels = []
        for level_class in self.levels:
            levels.append('{0} {1}'.format(level_class, self.levels[level_class]))
        return ' / '.join(levels)

    @property
    def spell_slots(self):
        """
        Property that is an array of spell_slots
        """
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

            # For every spell-level you can cast
            #
            for spell_level in class_level.spd:

                spell_count = int(class_level.spd[spell_level])

                for i in range(0, spell_count):

                    # Add that many spells
                    #
                    self.add_spell_slot(
                       reason='Daily spells per level {} ({} of {})'.format(
                           spell_level, i, spell_count
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
        """
        Adds a spell slot to the character's list of spells
        :param kwargs:
            cls: the class object
            level: the level of the class
        :returns: True on adding the spell, and False if it didn't
        """

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
        "String representation"
        return json.dumps(self.__dict__)

    def mod(self, stat):
        "Returns the modifier for the stat"
        return self.stats[stat] / 2 - 5

    def _get_class_value(self, value_name):
        """
        Obtains the value for a field within all classes and sums them
        """
        val = 0
        for cls in self.classes:
            level = self.levels[cls]
            val += self.classes[cls].at_level(level).__dict__[value_name]

        return val

    @property
    def size(self):
        "Returns the size of the character"
        return self.race.size

    @property
    def fort_save(self):
        "The base fort save"
        return self._get_class_value('fort_save') + self.mod('con')

    @property
    def ref_save(self):
        "The base-reflex save"
        return self._get_class_value('ref_save') + self.mod('dex')

    @property
    def will_save(self):
        "The base-will save"
        return self._get_class_value('will_save') + self.mod('wis')

    @property
    def base_attack(self):
        "Base attack property - just the summation of the class scores"
        return self._get_class_value('base_attack')


