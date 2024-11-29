import psycopg2
from psycopg2.extras import RealDictCursor

from exceptions import CreateUserException


class DataBase:

    def __init__(self, db_name, db_user, db_password, db_host, db_port):
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port

    def make_db_connection(self):
        try:
            connection = psycopg2.connect(
                database=self.db_name,
                user=self.db_user,
                password=self.db_password,
                host=self.db_host,
                port=self.db_port
            )
            return connection
        except:
            raise Exception

    @staticmethod
    def insert_player(connection, player, chat_id):
        cursor = connection.cursor()
        try:
            cursor.execute('''
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(100) NOT NULL,
                            nick VARCHAR(100) UNIQUE NOT NULL,
                            mmr INT NOT NULL,
                            chat_id VARCHAR(100) NOT NULL
                        )
                        ''')

            cursor.execute('''
                    INSERT INTO users (name, nick, mmr, chat_id)
                    VALUES (%s, %s, %s, %s)
                    ''', (player.name, player.nick, player.mmr, chat_id))
        except Exception as e:
            print(e)
            raise CreateUserException
        finally:
            connection.commit()

    @staticmethod
    def update_player(connection, name, nick, mmr, chat_id):

        cursor = connection.cursor()
        try:
            cursor.execute('''
                        UPDATE users
                        SET name = %s, nick=%s, mmr=%s
                        WHERE chat_id = %s;
                        ''', (name, nick, mmr, chat_id))
        except Exception as e:
            print(e)
            raise CreateUserException

        connection.commit()

    @staticmethod
    def create_all_tables(connection):

        cursor = connection.cursor()
        try:
            cursor.execute('''
                        CREATE TABLE IF NOT EXISTS users (
                            id SERIAL PRIMARY KEY,
                            name VARCHAR(100) NOT NULL,
                            nick VARCHAR(100) UNIQUE NOT NULL,
                            mmr INT NOT NULL,
                            chat_id VARCHAR(100),
                            is_participant BOOLEAN NOT NULL DEFAULT FALSE,
                            team_number INT
                        )
                        ''')
        except:
            raise Exception
        connection.commit()

    @staticmethod
    def delete_all_tables(connection):
        cursor = connection.cursor()
        try:
            cursor.execute('''DROP TABLE users CASCADE;''')
        except:
            raise Exception
        connection.commit()

    @staticmethod
    def clear_table(connection, chat_id):
        cursor = connection.cursor()
        try:
            cursor.execute('''DELETE FROM users
                                WHERE chat_id = %s;''', (chat_id,))
        except Exception as e:
            print(e)
            raise Exception
        connection.commit()

    @staticmethod
    def delete_user(connection, chat_id):
        cursor = connection.cursor()
        try:
            cursor.execute(('''DELETE FROM users CASCADE
            WHERE chat_id = %s'''), (chat_id,))
        except Exception as e:
            print(e)
            raise Exception
        connection.commit()

    @staticmethod
    def participate(connection, chat_id, state):
        cursor = connection.cursor()
        try:
            cursor.execute(('''UPDATE users
                        SET is_participant = %s
                        WHERE chat_id = %s'''), (str(state).upper(), chat_id))
        except Exception:
            raise Exception

        connection.commit()

    @staticmethod
    def query_db(connection, query, args=(), one=False):
        cur = connection.cursor()
        cur.execute(query, args)
        r = [dict((cur.description[i][0], value) \
                  for i, value in enumerate(row)) for row in cur.fetchall()]
        cur.connection.close()
        return (r[0] if r else None) if one else r

    @staticmethod
    def load_participants(connection):

        cursor = connection.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT name, nick, mmr FROM users"
                       " WHERE is_participant = TRUE;")

        # Получение всех данных
        rows = cursor.fetchall()

        players = []
        # Вывод данных
        for row in rows:
            player = {}
            for key in row.keys():
                player[key] = row[key]
                # player.append({f'{key}': row[key]})
            players.append(player)
        return players

    @staticmethod
    def set_team_number_to_player(connection, player, number):
        cursor = connection.cursor()
        try:
            print(player['name'], player['nick'])
            cursor.execute(('''UPDATE users
                                SET team_number = %s
                                    WHERE name = %s AND nick = %s'''), (number, player['name'], player['nick']))
        except Exception as e:
            print(e)
        finally:
            connection.commit()
