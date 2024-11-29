import random
from Players import Player
import pickle
import json
import os
from exceptions import BlankException, CustomException, too_much_exception, not_enough_exception


def shuffle(player_pool, team1):
    for i in range(0, 5):
        rand = random.randint(0, len(player_pool) - 1)
        team1.append(player_pool[rand])
        player_pool.pop(rand)
    return team1


def show_player_pool():
    players = load_data("players.dat")
    return json.dumps([str(p.__dict__) for p in players], indent=2)


def show_game_pool():
    players = load_data("game_pool.dat")
    return json.dumps([str(p.__dict__) for p in players], indent=2)


def length_check(player_pool, number):
    if len(player_pool) > number:
        raise too_much_exception
    elif len(player_pool) < number:
        raise not_enough_exception
    elif len(player_pool) == number:
        return True


def save(player: Player):
    players = load_data("players.dat")
    players.append(player)
    save_data(players, "players.dat")

    return json.dumps([{"name": p.name,
                        "nick": p.nick,
                        "mmr": int(p.mmr)}
                       for p in players])


def load_data(name):
    try:
        with open(name, 'rb') as f:
            pl = list(pickle.load(f))
    except:
        pl = []
    return pl


def save_data(pl, name):
    with open(name, "wb") as f:
        pickle.dump(pl, f, pickle.HIGHEST_PROTOCOL)


def duplicate_check(player: Player, array: list):
    for players in array:
        if player.name == players.name:
            raise CustomException
    return array





def player_delete(name):
    team = load_data("players.dat")
    index = -1
    for idx, x in enumerate(team):
        if x.name == name:
            index = idx
            break
    if index >= 0:
        team.pop(index)
        save_data(team, "players.dat")

    return json.dumps([{"name": p.name,
                        "nick": p.nick,
                        "mmr": int(p.mmr)}
                       for p in team], indent=2)


def game_pool_player_delete(name):
    team = load_data("game_pool.dat")
    index = -1
    for idx, x in enumerate(team):
        if x.name == name:
            index = idx
            break
    if index >= 0:
        team.pop(index)
        save_data(team, "game_pool.dat")

    return json.dumps([{"name": p.name,
                        "nick": p.nick,
                        "mmr": int(p.mmr)}
                       for p in team], indent=2)


def participate(player):
    players = load_data("players.dat")
    game_pool = load_data("game_pool.dat")
    check = False
    for p in players:
        if p.nick == player:
            check = True
            is_in_team = True
            for t in game_pool:
                if t.nick == p.nick:
                    is_in_team = False
            if is_in_team:
                game_pool.append(p)
                save_data(game_pool, "game_pool.dat")
    if not check:
        raise BlankException

    return json.dumps([{"name": p.name, "nick": p.nick, "mmr": int(p.mmr)}
                       for p in game_pool], indent=2)

def other_player_participate(player):
    players = load_data("players.dat")
    game_pool = load_data("game_pool.dat")
    check = False
    for p in players:
        if p.name == player:
            check = True
            is_in_team = True
            for t in game_pool:
                if t.nick == p.nick:
                    is_in_team = False
            if is_in_team:
                game_pool.append(p)
                save_data(game_pool, "game_pool.dat")
            else:
                raise too_much_exception
    if not check:
        raise BlankException

    return json.dumps([{"name": p.name, "nick": p.nick, "mmr": int(p.mmr)}
                       for p in game_pool], indent=2)


def game_pool_delete():
    os.remove("game_pool.dat")