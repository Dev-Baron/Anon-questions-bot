import aiosqlite
import structlog

logger = structlog.get_logger()

class Database:
    
    def __init__(self, db_path: str = 'database.sqlite'):
        self.db = db_path
    
    async def init_db(self):
        async with aiosqlite.connect(self.db) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    name TEXT,
                    username TEXT,
                    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )                     
            ''')
            await db.commit()
            return logger.info('DATABASE INITIALIZED')
        
    async def get_user(self, user_id):
        async with aiosqlite.connect(self.db) as db:
            cs = await db.cursor()
            await cs.execute('''SELECT * FROM users WHERE user_id = ?''', (user_id,))
            return await cs.fetchone()
        
    async def add_user(self, user_id, name, username):
        async with aiosqlite.connect(self.db) as db:
            await db.execute('''INSERT INTO users (user_id, name, username) VALUES (?, ?, ?)''', (user_id, name, username))
            await db.commit()
            return logger.info(f'NEW USER {user_id}')
        
db = Database()