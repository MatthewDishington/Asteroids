import sqlite3

class ScoreDatabase:

    def __init__(self, database_name=None):
        if database_name is None:
            database_name = 'Asteroid.sqlite'

        self.connection = sqlite3.connect(database_name)
        self.cursor = self.connection.cursor()

    def get_cursor(self):
        return self.cursor

    def create_database(self):
        self.cursor.executescript('''

        CREATE TABLE IF NOT EXISTS User (
            id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            name   TEXT UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Score (
            id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
            user_id INTEGER,
            score INTEGER,
            score_datetime TEXT
        );

        ''')

    def get_high_scores(self):
        highscores=[]
        position=0
        self.cursor.execute('''SELECT U.name,S.score
                            FROM User U JOIN Score S ON S.user_id =U.id
                            ORDER BY S.score DESC LIMIT  10''')

        rows = self.cursor.fetchall()

        for row in rows:
            position+=1
            highscores.append((position, row[0], row[1]))

        return highscores

    def save_score(self, name, score):
        self.cursor.execute('''INSERT OR IGNORE INTO User (name)
        VALUES ( ? )''', ( name, ) )
        self.cursor.execute('SELECT id FROM User WHERE name = ? ', (name, ))
        user_id = self.cursor.fetchone()[0]

        self.cursor.execute('''INSERT OR IGNORE INTO Score (user_id, score, score_datetime)
        VALUES ( ?, ?, datetime("now"))''', (user_id,score ) )

        self.connection.commit()

    def get_rank(self, score):
        self.cursor.execute('SELECT COUNT(*) FROM Score WHERE score > ? ', (score, ))
        rank = self.cursor.fetchone()[0]
        return rank + 1