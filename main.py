import asyncio
import random
import time

from telebot import types
from telebot.async_telebot import AsyncTeleBot

from Players import Player
from database import DataBase
from exceptions import too_much_exception, not_enough_exception, CustomException, too_many_iterations

db = DataBase(
    db_name='postgres',
    db_user='postgres',
    db_password='root',
    db_host='localhost',
    db_port=5432,
)


def length_check(player_pool, number):
    if len(player_pool) > number:
        raise too_much_exception
    elif len(player_pool) < number:
        raise not_enough_exception
    elif len(player_pool) == number:
        return True


def team_shuffle():
    start_time = time.time()
    time_limit = 5  # секунд
    while True:
        team1 = []
        p = DataBase.load_participants(connection)
        if length_check(p, 10):
            shuffle(p, team1)
        team2 = p
        sum1 = 0
        sum2 = 0
        for t in team1:
            sum1 = sum1 + t['mmr']
        for t in team2:
            sum2 = sum2 + t['mmr']
        if length_check(team1, 5) and length_check(team2, 5):
            if abs(sum1 / len(team1) - sum2 / len(team2)) > 100:
                if time.time() - start_time > time_limit:
                    raise too_many_iterations
                continue
            else:
                for player in team1:
                    DataBase.set_team_number_to_player(connection, player, 1)
                for player in team2:
                    DataBase.set_team_number_to_player(connection, player, 2)
                break
        else:
            raise too_much_exception
    return ('Team1' + str([t['name'] for t in team1]) + ' avg: ' + str(sum1 / len(team1)) + '\n' +
            'Team2' + str([t['name'] for t in team2]) + ' avg: ' + str(sum2 / len(team2)))


def shuffle(player_pool, team1):
    for i in range(0, 5):
        rand = random.randint(0, len(player_pool) - 1)
        team1.append(player_pool[rand])
        player_pool.pop(rand)
    return team1


connection = db.make_db_connection()

token = '7807406707:AAHTAE-i1gwrLYf2PDoBBPtWPQuEjI6sp1E'
bot = AsyncTeleBot(token)


# Handle '/start' and '/help'
@bot.message_handler(commands=['start'])
async def send_welcome(message):
    text = 'Дарова, это бот для сбора десятки, для просмотра всех доступных команд введи /help'
    await bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['help'])
async def commands_list(message):
    text = ('Список всех доступных в боте команд: \n'
            '')

    await bot.reply_to(message, text)


@bot.message_handler(commands=['register'])
async def register(message):
    args = message.text.split(' ', 1)
    args = args[1:]
    args = tuple(args[0].split(' '))

    if len(args) == 3:
        player = Player(args[0], args[1], args[2])
        try:
            db.insert_player(connection=connection, player=player, chat_id=message.chat.id)
            await bot.reply_to(message, "Пользователь создан")
        except:
            await bot.reply_to(message, "Такой пользователь уже создан")
    else:
        await bot.reply_to(message, "Что-то пошло не так, проверьте правильность введенных данных")


@bot.message_handler(commands=['participate'])
async def participate(message):
    args = message.text.split(' ', 1)
    db.participate(connection, str(message.chat.id), args[1])


@bot.message_handler(commands=['shuffle'])
async def teams_shuffle(message):
    if message.chat.id != 1345998530:
        return await bot.send_message(message.chat.id, 'Отсоси, мухомор ебаный')
    try:
        result_shuffle = str(team_shuffle())
        # await bot.reply_to(message, str(team_shuffle()))
        players = db.query_db(connection,
                              "SELECT chat_id FROM users"
                              " WHERE is_participant = TRUE;",
                              )
        for p in players:
            await bot.send_message(p['chat_id'], result_shuffle)

    except too_many_iterations:
        return await bot.reply_to(message, 'Нет подходящей комбинации игроков')
    # except too_much_exception:
    #     return await bot.reply_to(message, 'Слишко много игроков')
    except not_enough_exception:
        return await bot.reply_to(message, 'Слишко мало игроков')


@bot.message_handler(commands=['test'])
async def test(message):
    await bot.reply_to(message,f'{message.chat.id}')
    print(message.chat.id)  # 1345998530


@bot.message_handler(commands=['insert_tables'])
async def insert_tables(message):
    db.create_all_tables(connection)


@bot.message_handler(commands=['drop_tables'])
async def drop_tables(message):
    db.delete_all_tables(connection)


@bot.message_handler(commands=['clear_table'])
async def clear_table(message):
    db.clear_table(connection, str(message.chat.id))


@bot.message_handler(commands=['update_user'])
async def update_user(message):
    args = message.text.split(' ', 1)
    args = args[1:]
    args = tuple(args[0].split(' '))
    db.update_player(connection=connection,
                     name=args[0],
                     nick=args[1],
                     mmr=args[2],
                     chat_id=str(message.chat.id))


@bot.message_handler(commands=['delete_user'])
async def delete_user(message):
    db.delete_user(connection, str(message.chat.id))


@bot.message_handler(commands=['load_users'])
async def load_users(message):
    players = db.load_participants(connection)
    players_ids = db.query_db(connection,
                          "SELECT chat_id FROM users"
                          " WHERE is_participant = TRUE;",
                          )
    mes = ''
    for p in players:
        mes = mes.join(f"{p}\n")
    await bot.reply_to(message.chat.id, f'{mes}')


@bot.message_handler(content_types=['text'])
def func(message):
    if (message.text == "? Поздороваться"):
        bot.send_message(message.chat.id, text="Привеет.. Спасибо что читаешь статью!)")
    elif (message.text == "❓ Задать вопрос"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Как меня зовут?")
        btn2 = types.KeyboardButton("Что я могу?")
        back = types.KeyboardButton("Вернуться в главное меню")
        markup.add(btn1, btn2, back)
        bot.send_message(message.chat.id, text="Задай мне вопрос", reply_markup=markup)

    elif (message.text == "Как меня зовут?"):
        bot.send_message(message.chat.id, "У меня нет имени..")

    elif message.text == "Что я могу?":
        bot.send_message(message.chat.id, text="Поздороваться с читателями")

    elif (message.text == "Вернуться в главное меню"):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("? Поздороваться")
        button2 = types.KeyboardButton("❓ Задать вопрос")
        markup.add(button1, button2)
        bot.send_message(message.chat.id, text="Вы вернулись в главное меню", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, text="На такую комманду я не запрограммировал..")


asyncio.run(bot.polling())
