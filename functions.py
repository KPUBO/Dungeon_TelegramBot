from database import DataBase


def send_notifications(message, connection):
    players = DataBase.load_participants(connection)
