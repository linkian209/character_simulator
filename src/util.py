'''util.py

This module contains utility functions for the script and data entry
'''
import csv
import json
import math

#
# Main Script Functions
#
def stat_mod_from_score(score):
    '''
    This function calculates the modifier for a stat from its score

    Arguments:
        :param score: (int) The ability score

    Returns:
        int/None: The modifier for the ability, None if input is not an int
    '''
    if(type(score) == 'int'):
        return math.floor((10 - score) / 2)

    return None



#
# Data Entry Functions
#
def spell_csv_to_dict(csv_path):
    retval = {
        'SpellsKnown':{},
        'CantripsKnown':{},
        'SpellSlots': {}
    }
    with open(csv_path) as fp:
        reader = csv.DictReader(fp)
        for row in reader:
            if('Spells Known' in row):
                retval['SpellsKnown'][row['Level']] = int(row['Spells Known'])
            if('Cantrips Known' in row):
                retval['CantripsKnown'][row['Level']] = int(row['Cantrips Known'])
            if('6th' in row):
                retval['SpellSlots'][row['Level']] = {
                    "1st": int(row["1st"]),
                    "2nd": int(row["2nd"]),
                    "3rd": int(row["3rd"]),
                    "4th": int(row["4th"]),
                    "5th": int(row["5th"]),
                    "6th": int(row["6th"]),
                    "7th": int(row["7th"]),
                    "8th": int(row["8th"]),
                    "9th": int(row["9th"])
                }
            else:
                retval['SpellSlots'][row['Level']] = {
                    "1st": int(row["1st"]),
                    "2nd": int(row["2nd"]),
                    "3rd": int(row["3rd"]),
                    "4th": int(row["4th"]),
                    "5th": int(row["5th"])
                }
    return retval

def dump_to_json_file(data, json_file):
    with open(json_file, 'w') as fp:
        json.dump(data, fp, indent=2)

def level_table_csv_to_dict(csv_path):
    retval = {
        "Headers": [],
        "Levels": {}
    }
    with open(csv_path) as fp:
        reader = csv.DictReader(fp)
        retval["Headers"] = reader.fieldnames
        for row in reader:
            if('Features' in row):
                if(row['Features'] == ''):
                    row['Features'] = []
                else:
                    row["Features"] = row["Features"].split(', ')
            retval['Levels'][row['Level']] = dict(row)
    return retval