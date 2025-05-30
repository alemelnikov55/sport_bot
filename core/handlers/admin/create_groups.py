from itertools import combinations

GROUPS_LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']


def distribute_teams_to_groups(teams_dict, group_sizes):
    """
    Распределяет команды по группам на основе их индексов.

    :param teams_dict: словарь {название_команды: индекс_команды}
    :param group_sizes: список с количеством команд в каждой группе
    :return: словарь {название_группы: [индексы_команд]}
    """
    try:
        team_indices = [idx for name, idx in teams_dict.items()]
    except AttributeError:
        team_indices = teams_dict

    result = {}
    start = 0

    for i, size in enumerate(group_sizes):
        group_name = GROUPS_LETTERS[i]
        end = start + size
        result[group_name] = team_indices[start:end]
        start = end

    return result


def generate_group_matches(grouped_teams):
    """
    Генерирует матчи внутри каждой группы по принципу "каждый с каждым"

    :param grouped_teams: словарь {название_группы: [индексы_команд]}
    :return: словарь {название_группы: [(индекс1, индекс2), ...]}
    """
    group_matches = {}

    for group_name, teams in grouped_teams.items():
        # Генерируем все уникальные пары команд в группе
        matches = list(combinations(teams, 2))
        group_matches[group_name] = matches

    return group_matches
