from typing import Callable

import requests
from django.db import transaction
from lxml import html

from games.models import Game
from players.models import Player, Score
from teams.models import Team


def get_html(url):
    # time.sleep(1)
    response = requests.get(url)
    response.encoding = 'utf-8'
    return html.fromstring(response.text)


def add_ranking_place(items: list, field: str):
    """
    Adds 'place' to all items according to their order.
    If the value of the specified field on any given item matches the value on the field of the previous item,
    then the item gets the same place as its predecessor.

    :param items: an already sorted list of items, ordered by `field`
    :param field: the field of the items to compare
    """
    for index, item in enumerate(items):
        item.place = index + 1
        if index > 0:
            previous = items[index - 1]
            if getattr(previous, field) == getattr(item, field):
                item.place = previous.place


def add_score(game: Game, team: Team, player_name: str, player_number: int,
              goals: int = 0, penalty_goals: int = 0, penalty_tries: int = 0,
              warning_time: str = None, first_suspension_time: str = None, second_suspension_time: str = None,
              third_suspension_time: str = None, disqualification_time: str = None, report_time: str = None,
              team_suspension_time: str = None, log_fun: Callable = print):
    log_fun('CREATING Score: {} {}'.format(game, player_name))

    divided_players = team.player_set.filter(name__regex="^{} \(\d+\)$".format(player_name))
    duplicate_scores = Score.objects.filter(player__name=player_name, player__team=team, game=game)
    if divided_players.exists() or duplicate_scores.exists():
        split_by_number(player_name, team)
        player_name = '{} ({})'.format(player_name, player_number)

    player, created = Player.objects.get_or_create(name=player_name, team=team)
    if created:
        log_fun('CREATED Player: {}'.format(player))
    else:
        log_fun('EXISTING Player: {}'.format(player))

    Score.objects.create(
        player=player,
        player_number=player_number,
        game=game,
        goals=goals,
        penalty_goals=penalty_goals,
        penalty_tries=penalty_tries,
        warning_time=warning_time,
        first_suspension_time=first_suspension_time,
        second_suspension_time=second_suspension_time,
        third_suspension_time=third_suspension_time,
        disqualification_time=disqualification_time,
        report_time=report_time,
        team_suspension_time=team_suspension_time
    )


@transaction.atomic
def split_by_number(original_name: str, team: Team, log_fun: Callable = print):
    log_fun("DIVIDING Player: {} ({})".format(original_name, team))

    matches = Player.objects.filter(name=original_name, team=team)
    if not matches.exists():
        log_fun("SKIPPING Player (not found): {} ({})".format(original_name, team))
        return

    original_player = matches[0]
    for score in original_player.score_set.all():
        new_name = "{} ({})".format(original_player.name, score.player_number)
        new_player, created = Player.objects.get_or_create(name=new_name, team=original_player.team)
        if created:
            log_fun("CREATED Player: {}".format(new_player))
        score.player = new_player
        score.save()

    if not original_player.score_set.all().exists():
        log_fun("DELETING Player (no dangling scores): {}".format(original_player))
        original_player.delete()
