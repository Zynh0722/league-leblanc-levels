from typing import Iterable
import math

from colorama import Fore
from colorama import Style

ABILITY_BASE = {
    'q': ((65, 140), (90, 180), (115, 230), (140, 280), (165, 330)),
    'w': (75, 115, 155, 195, 235),
    'e': ((50, 80), (70, 120), (90, 160), (110, 200), (130, 240)),
}

ULT_BASE = {
    'q': (70, 140, 210),
    'w': (150, 300, 450),
    'e': (70, 140, 210),
}

ABILITY_SCALINGS = {
    'q': (40, 80),
    'w': 60,
    'e': (30, 70),
}

ULT_SCALING = {
    'q': 40,
    'w': 75,
    'e': 40,
}


def ability_generator(include_r=False):
    abilites = ['q', 'w', 'e']

    if include_r:
        abilites.append('r')

    for ability in abilites:
        yield ability


def get_ability_base(ability, level):
    return ABILITY_BASE[ability][level - 1] if level != 0 else 0


def get_ability_scaling(ability):
    return ABILITY_SCALINGS[ability]


def val_and_double(value):
    return value, value * 2


def get_ult_base(ability, level):
    if level != 0:
        match ability:
            case 'q' | 'e': return val_and_double(ULT_BASE[ability][level - 1]) 
            case _: return ULT_BASE[ability][level - 1]
    else:
        return 0


def get_ult_scaling(ability):
    match ability:
        case 'q' | 'e': return val_and_double(ULT_SCALING[ability])
        case _: return ULT_SCALING[ability]


def get_dmg_from_levels(ability_levels):
    dmg = {}

    for ability in ability_generator():
        dmg[ability] = get_ability_base(ability, ability_levels[ability])
        dmg[f'r_{ability}'] = get_ult_base(ability, ability_levels['r'])

    return dmg


def can_level_ult(ability_level, champ_level):
    match ability_level + 1:
        case 1: return champ_level >= 6
        case 2: return champ_level >= 11
        case 3: return champ_level >= 16
        case _: return False


def can_level_ability(ability, ability_level, champ_level):
    match ability:
        case 'r': return can_level_ult(ability_level, champ_level)
        case _: return ability_level + 1 <= min(math.ceil(champ_level/2), 5)


def increment_level(level, ability_levels, max_order, first_n):
    if level > len(first_n):
        for ability in max_order:
            if can_level_ability(ability, ability_levels[ability], level):
                ability_levels[ability] += 1
                break
    else:
        ability = first_n[level - 1]
        if can_level_ability(ability, ability_levels[ability], level):
            ability_levels[ability] += 1
            


def simulates_level_order(max_order: Iterable[str], first_n: Iterable[str]=()):
    ability_levels = {
        'q': 0,
        'w': 0,
        'e': 0,
        'r': 0
    }
    for level in range(1, 19):
        increment_level(level, ability_levels, max_order, first_n)
        yield {'damages': get_dmg_from_levels(ability_levels), 'level': level}


def print_with_indent(text, indent=0):
    print(" " * 4 * indent, text)


FUCK_PYTHON = '\t'

def print_level_stats(level_stats):
    print(f"LeBlanc Level: {level_stats['level']}")

    dmg = level_stats["damages"]
    for ability in ability_generator():
        print_with_indent(f"{ability.upper()}: {dmg[ability]}\t{FUCK_PYTHON * (ability == 'w')}Mimic {ability.upper()}: {dmg[f'r_{ability}']}", 1)
    

def safe_sum(val):
    try:
        iterator = iter(val)
    except TypeError:
        return val
    else:
        return sum(val)


def print_stat_table(all_level_stats):
    stat_lists = {}

    for ability in ability_generator():
        stat_lists[ability] = [
            (stat['damages'][ability], stat['damages'][f'r_{ability}']) 
            for stat in all_level_stats
        ]

    print("  ", end="")
    for i in range(1, 19):
        print(i, end=" ")
        if i < 10:
            print(" ", end="")
    print()
    for ability, stat_list in stat_lists.items():
        print(ability, end=" ")
        for level_stat in stat_list:
            print(f"{Fore.GREEN if safe_sum(level_stat[0]) > safe_sum(level_stat[1]) else Fore.RED}■■{Style.RESET_ALL}", end=" ")
        print()

if __name__ == '__main__':
    stats = [stat for stat in simulates_level_order(('r', 'q', 'w', 'e'), ('w', 'q', 'e'))]

    # for result in stats:
    #     print_level_stats(result)

    print_stat_table(stats)
