'''classes.py

This module contains all the classes and enums used by the main script
'''
import enum
import json
import random
import sys
import uuid
from . import util


class StatSelection(enum.Enum):
    '''
    This enumation tells how we will be doing stats
    '''
    ROLL_4D6_DROP_ONE = 1
    STANDARD_ARRAY    = 2
    ROLL_3D6          = 3
    RANDOM            = 4


class HPSelection(enum.Enum):
    '''
    This enumeration tells how this character will gain HP on level up
    '''
    ROLL_HP  = 1
    TAKE_AVG = 2
    RANDOM   = 3


class ASISelection(enum.Enum):
    '''
    This enumeration tells how this character will handle ASIs
    '''
    STRICT_FOCUS      = 1
    FOCUS_ODD_TO_EVEN = 2
    FOCUS_NON_NEG_MOD = 3
    RANDOM            = 4


class MultiClassLevelSelection(enum.Enum):
    '''
    This enumeration tells how this character will level when multiclassed
    '''
    GROUP     = 1
    ALTERNATE = 2
    RANDOM    = 3


class ASIRecord():
    '''
    This class contains an instance of an ASI, recording what we did

    Members:
        method: (ASISelection) What method was used for this ASI
        old_stats: (dict) The stats of the character before ASI
        new_stats: (dict) The stats of the character after ASI
        chosen_stats: (list) The stat(s) we improved
        stat_focus: (list) The order to focus stats

    Static Methods:
        choose_stats(method, stat_focus, cur_stats, stat_opts=None): Chooses what stat(s) to improve
        perform_asi(cur_stats, chosen_stats): Improves the chosen stats
    '''
    def __init__(self, method, cur_stats, stat_focus, rng=random.Random()):
        '''
        This method initializes the instance of this object

        Arguments:
            :param self: (ASIRecord) This record
            :param method: (ASISelection) The method to do this ASI
            :param cur_stats: (dict) The current stats of this character
            :param stat_focus: (list) The order to focus stats
            :param rng: (Random) RNG to use
        '''
        self.method = method
        self.old_stats = cur_stats.copy()
        self.stat_focus = stat_focus.copy()
        self.chosen_stats = self.choose_stats(method, stat_focus, self.old_stats, rng)
        self.new_stats = self.perform_asi(self.old_stats, self.chosen_stats)

    @staticmethod
    def choose_stats(method, stat_focus, cur_stats, rng=random.Random(), stat_opts=None):
        '''
        This method chooses stats for this ASI and sets the record of it

        Arguments:
            :param method: (ASISelection) The method to determine which stats
            :param stat_focus: (list) The order to focus stats
            :param cur_stats: (dict) The current stats of the character
            :param rng: (Random) rng to use
            :param stat_opts: (list/None) Options for to choose from

        Returns:
            list: The stat(s) to improve
        '''
        retval = []
        # Determine which stats to improve

        # This method means to strictly focus on improving stats in order
        # until we can no longer improve that stat
        if(method == ASISelection.STRICT_FOCUS):
            for stat in stat_focus:
                # First see if we can improve this stat
                if(stat_opts is not None and stat not in stat_opts):
                    continue
                
                # Make sure we don't go over 20
                if(cur_stats[stat] < 20):
                    # We can, see how much we can improve it
                    diff_from_20 = 20 - cur_stats[stat] + retval.count(stat)
                    
                    # If we are two or more away, just improve this one twice
                    if(diff_from_20 >= 2):
                        retval.append(stat)
                        # Potential corner case. We have at least room for one
                        # improvement to be here.
                        if(len(retval) is 1):
                            retval.append(stat)
                    else:
                        if(diff_from_20 is 1):
                            # If we are one away, improve this stat once
                            retval.append(stat)
                
                # If we have chosen our 2 stats, break. We are done!
                if(len(retval) is 2):
                    break
        # This method means to improve stats whose score is odd, thus 
        # increasing the modifier. We take a pass first to ensure that all
        # stats are even, then improve based on focus
        elif(method == ASISelection.FOCUS_ODD_TO_EVEN):
            for stat in stat_focus:
                # See if we can improve this stat
                if(stat_opts is not None and stat not in stat_opts):
                    continue

                # Ignore 20s
                if(cur_stats[stat] >= 20):
                    continue

                # Check oddness
                if(cur_stats[stat] % 2 is 1):
                    # This stat is odd
                    retval.append(stat)

                # Now check if we have any more left
                if(len(retval) is 2):
                    break

            # After looping through, if we have any left, do focus order
            if(len(retval) < 2):
                for stat in stat_focus:
                    # See if we can improve this stat
                    if(stat_opts is not None and stat not in stat_opts):
                        continue

                    if(cur_stats[stat] < 20):
                        # We can, see how much we can improve it
                        diff_from_20 = 20 - cur_stats[stat] + retval.count(stat)
                        
                        # If we are two or more away, just improve this one twice
                        if(diff_from_20 >= 2):
                            retval.append(stat)
                            # Potential corner case. We have at least room for one
                            # improvement to be here.
                            if(len(retval) is 1):
                                retval.append(stat)
                        else:
                            if(diff_from_20 is 1):
                                # If we are one away, improve this stat once
                                retval.append(stat)

                    # Now check if we have any more left
                    if(len(retval) is 2):
                        break
        # This method means to improve stats whose score results in a
        # negative modifier. After we ensure every stat is 10 or greater,
        # improve in focus order
        elif(method == ASISelection.FOCUS_NON_NEG_MOD):
            for stat in stat_focus:
                # See if we can improve this stat
                if(stat_opts is not None and stat not in stat_opts):
                    continue

                # Ignore 20s
                if(cur_stats[stat] >= 20):
                    continue

                # Check if we have a negative mod
                if(cur_stats[stat] < 10):
                    # Calculate the difference from 10
                    diff_from_10 = 10 - cur_stats[stat] + retval.count(stat)
                        
                    # If we are two or more away, just improve this one twice
                    if(diff_from_10 >= 2):
                        retval.append(stat)
                        # Potential corner case. We have at least room for one
                        # improvement to be here.
                        if(len(retval) is 1):
                            retval.append(stat)
                    else:
                        if(diff_from_10 is 1):
                            # If we are one away, improve this stat once
                            retval.append(stat)

                # Now check if we have any more left
                if(len(retval) is 2):
                    break

            # After looping through, if we have any left, do focus order
            if(len(retval) < 2):
                for stat in stat_focus:
                    # See if we can improve this stat
                    if(stat_opts is not None and stat not in stat_opts):
                        continue
                    if(cur_stats[stat] < 20):
                        # We can, see how much we can improve it
                        diff_from_20 = 20 - cur_stats[stat] + retval.count(stat)
                        
                        # If we are two or more away, just improve this one twice
                        if(diff_from_20 >= 2):
                            retval.append(stat)
                            # Potential corner case. We have at least room for one
                            # improvement to be here.
                            if(len(retval) is 1):
                                retval.append(stat)
                        else:
                            if(diff_from_20 is 1):
                                # If we are one away, improve this stat once
                                retval.append(stat)

                    # Now check if we have any more left
                    if(len(retval) is 2):
                        break
        # This method means randomly pick 2 stats that can be improved and 
        # improve them
        elif(method == ASISelection.RANDOM):
            while(len(retval) < 2):
                # Get random stat
                stat = rng.choice(stat_focus)

                # See if we can improve this stat
                if(stat_opts is not None and stat not in stat_opts):
                    continue

                # Check if this is legal
                if(cur_stats[stat] + retval.count(stat) < 20):
                    # Improve it
                    retval.append(stat)
        # Default to no improvements
        else:
            retval = []
        # Done! Return!
        return retval


    @staticmethod
    def perform_asi(cur_stats, chosen_stats):
        '''
        This method performs an ability score improvement based on the inputted
        stats.

        Arguments:
            :param cur_stats: (dict) The current status
            :param chosen_stats: (list) The chosen stats to improve

        Returns:
            dict: The stats after the ASI has been done
        '''
        retval = cur_stats.copy()
        for stat in chosen_stats:
            retval[stat] += 1

        return retval

class LevelRecord():
    '''
    This class keeps a record of the level up

    Members:
        level_class: (str) Class being leveled
        level: (int) Level obtained
        cur_stats: (dict) The character's current stats
        new_stats: (dict) The character's new stats
        features: (list) Features obtained in this level
        hp_method: (HPSelection) method for increasing HP
        asi_method: (ASISelection) method for performing ASIs
        hp_increase: (int) How much the character's HP increased this level
        asi: (ASIRecord/None) if we have an ASI this level, keep a record of it
        stat_focus: (list) Order to focus stats
    '''
    def __init__(self, level_class, level, cur_stats, hp_method, asi_method, stat_focus, rng=random.Random()):
        '''
        This method initializes this LevelRecord object.

        Arguments:
            :param self: (LevelRecord) This instance
            :param level_class: (str) The class being leveled
            :param level: (int) The level obtained
            :param cur_stats: (dict) The current stats of character
            :param hp_method: (HPSelection) Method for determining HP increase
            :param asi_method: (ASISelection) Method for performing ASI
            :param stat_focus: (list) Order to focus stats
            :param rng: (Random) Random Number Generator to use
        '''
        # First initialize what we got
        self.level_class = level_class
        self.level = level
        self.cur_stats = cur_stats.copy()
        self.hp_method = hp_method
        self.asi_method = asi_method
        self.stat_focus = stat_focus.copy()

        # Next load in class data
        with open('data/class_data.json') as fp:
            class_data = json.load(fp)

        # Now see what features we get
        self.features = class_data[self.level_class]['LevelTable'][str(level)]['Features']

        # Check if we get an ASI
        if("Ability Score Improvement" in self.features):
            # Lets do an ASI!
            self.asi = ASIRecord(self.asi_method, self.cur_stats, self.stat_focus)
            self.new_stats = self.asi.new_stats.copy()
        else:
            self.asi = None
            self.new_stats = self.cur_stats.copy()

        # Lastly, after doing ASI, let's increase HP
        if(hp_method == HPSelection.ROLL_HP):
            # HP for this level is rolling the hit dice and adding Con mod
            self.hp_increase = rng.randint(
                1, class_data[self.level_class]['HitDiceValue']
            ) + util.stat_mod_from_score(self.cur_stats['Con'])
        elif(hp_method == HPSelection.TAKE_AVG):
            # HP for this level is taking the average value of the hit dice
            # and adding Con mod
            self.hp_increase = (class_data[self.level_class]['HitDiceAvg'] + 
                               util.stat_mod_from_score(self.cur_stats['Con']))
        # Default to random
        else:
            rand_choice = rng.choice(list(HPSelection))
            if(rand_choice == HPSelection.ROLL_HP):
                # HP for this level is rolling the hit dice and adding Con mod
                self.hp_increase = rng.randint(
                    1, class_data[self.level_class]['HitDiceValue']
                ) + util.stat_mod_from_score(self.cur_stats['Con'])
            else:
                # HP for this level is taking the average value of the hit dice
                # and adding Con mod
                self.hp_increase = (class_data[self.level_class]['HitDiceAvg'] + 
                                    util.stat_mod_from_score(self.cur_stats['Con']))

class Character():
    '''
    This class contains the character. This will be used to store data
    throughout a simulation, including level up options, known features,
    HP, and stat levels

    Members:
        id: (uuid4) Id for this character
        race: (str) Race of this character
        subrace: (str) Subrace of this character
        seed: (int) Seed of RNG
        rng: (Random) Local Random Number Generator
        stat_focus: (list) Order in which to focus skills
        stat_select: (StatSelection) How we determine stats
        hp_select: (HPSelection) How we determine hp per level
        asi_select: (ASISelection) How we perform ASIs
        level_history: (list) History of level ups
        cur_stats: (dict) Current character stats
        hp: (int) Max HP for character
        hit_dice: (dict) Types and number of hit dice character has
        levels: (dict) Types and number of levels character has
        level: (int) Current overall character level
    '''
    def __init__(self, race, subrace, stat_focus, stat_select, hp_select, asi_select, id=None):
        '''
        This method initializes a character to be simulated.

        Arguments:
            :param self: (Character) This instance
            :param race: (str) Race for this character
            :param subrace: (str) Subrace for this character
            :param stat_focus: (list) Order to focus stats
            :param stat_select: (StatSelection) How we will determine stats
            :param hp_select: (HPSelection) How we will determine HP
            :param asi_select: (ASISelection) How we will perform ASIs
            :param id: (uuid) The id for this character
        '''
        self.id = id
        if(id is None):
            self.id = uuid.uuid4()
        self.race = race
        self.subrace = subrace
        self.seed = random.randrange(sys.maxsize)
        self.rng = random.Random()
        self.rng.seed(self.seed)
        self.stat_focus = stat_focus.copy()
        self.stat_select = stat_select
        self.hp_select = hp_select
        self.asi_select = asi_select
        self.level_history = []
        self.levels = {}
        self.hit_dice = {}
        self.level = 0

        # Determine starting stats
        scores = []

        # We will create 6 numbers by rolling 4d6 and dropping the lowest
        if(self.stat_select == StatSelection.ROLL_4D6_DROP_ONE):
            for i in range(6):
                cur_rolls = []
                for i in range(4):
                    cur_rolls.append(self.rng.randint(1,6))
                cur_rolls = sorted(cur_rolls, reverse=True)
                cur_rolls.pop()
                scores.append(sum(cur_rolls))
        # We will create 6 numbers by rolling 3d6 and adding them up
        elif(self.stat_select == StatSelection.ROLL_3D6):
            for i in range(6):
                scores.append(
                    self.rng.randint(1,6) + self.rng.randint(1,6) +
                    self.rng.randint(1,6)
                )
        # We will use the standard array
        elif(self.stat_select == StatSelection.STANDARD_ARRAY):
            scores = [15,14,13,12,10,8]
        # Randomly determine stats
        else:
            choice = self.rng.choice(list(StatSelection))
            # We will create 6 numbers by rolling 4d6 and dropping the lowest
            if(choice == StatSelection.ROLL_4D6_DROP_ONE):
                for i in range(6):
                    cur_rolls = []
                    for i in range(4):
                        cur_rolls.append(self.rng.randint(1,6))
                    cur_rolls = sorted(cur_rolls, reverse=True)
                    cur_rolls.pop()
                    scores.append(sum(cur_rolls))
            # We will create 6 numbers by rolling 3d6 and adding them up
            elif(choice == StatSelection.ROLL_3D6):
                for i in range(6):
                    scores.append(
                        self.rng.randint(1,6) + self.rng.randint(1,6) +
                        self.rng.randint(1,6)
                    )
            # Default to the standard array
            else:
                scores = [15,14,13,12,10,8]

        # Now assign scores to stats
        if(self.stat_select == StatSelection.RANDOM):
            stat_names = ['Str','Dex','Con','Int','Wis','Cha']
            self.rng.shuffle(stat_names)
            self.rng.shuffle(scores)
            self.stats = dict(zip(stat_names, scores))
        else:
            self.stats = dict(zip(self.stat_focus, sorted(scores, reverse=True)))

        # Now apply racial bonuses
        with open('data/race_data.json') as fp:
            race_data = json.load(fp)

        for stat in self.stat_focus:
            if(self.subrace is None):
                self.stats[stat] += race_data[self.race][stat]
            else:
                self.stats[stat] += race_data[self.race]['Subraces'][self.subrace][stat]

        # See if we have any optional ASIs to put in
        if(self.subrace is None):
            if('ASI' in race_data[self.race]):
                for i in range(int(race_data[self.race]['ASI']['number'])):
                    # See if we have some limitations
                    if('allowed' in race_data[self.race]['ASI']):
                        stats = race_data[self.race]['ASI']['allowed']
                    elif('not_allowed' in race_data[self.race]['ASI']):
                        stats = ['Str','Dex','Con','Int','Wis','Cha']
                    else:
                        stats = None

                    choices = ASIRecord.choose_stats(
                        self.asi_select, self.stat_focus, self.stats,
                        self.rng, stats
                    )
                    choices.pop()
                    self.stats = ASIRecord.perform_asi(self.stats, choices)
        else:
            if('ASI' in race_data[self.race]['Subraces'][self.subrace]):
                for i in range(int(race_data[self.race]['Subraces'][self.subrace]['ASI']['number'])):
                    # See if we have some limitations
                    if('allowed' in race_data[self.race]['Subraces'][self.subrace]['ASI']):
                        stats = race_data[self.race]['Subraces'][self.subrace]['ASI']['allowed']
                    elif('not_allowed' in race_data[self.race]['Subraces'][self.subrace]['ASI']):
                        stats = ['Str','Dex','Con','Int','Wis','Cha']
                    else:
                        stats = None

                    choices = ASIRecord.choose_stats(
                        self.asi_select, self.stat_focus, self.stats,
                        self.rng, stats
                    )
                    choices.pop()
                    self.stats = ASIRecord.perform_asi(self.stats, choices)
