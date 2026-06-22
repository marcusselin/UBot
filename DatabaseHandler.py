import sqlite3
from typing import Optional
import os
from dotenv import load_dotenv
import discord
import math
from pathlib import Path
from pathlib import PosixPath

env_dir = Path(__file__).resolve().parent
print(env_dir)
loaded = load_dotenv(env_dir / "conf" / "conf.env")
print(f"[INFO] [DATABASEHANDLER] Config state: {loaded}")
path = str(os.getenv("DBPATH"))
confpath = str(os.getenv("CONFIGDBPATH"))
storepath = str(os.getenv("STOREDBPATH"))
reactionrolespath = str(os.getenv("REACTIONROLESDBPATH"))
oneTokenAmount = int(os.getenv("ONETOKENAMOUNT"))

class DatabaseHandler:
    #Init
    def __init__(self, env_dir: PosixPath = env_dir, db_path: str = path, conf_path: str = confpath, store_path: str = storepath, reaction_roles_path: str = reactionrolespath):

        if db_path is None:
            db_path = os.getenv("DBPATH")
        path = db_path
        self.db_path = env_dir / db_path

        if conf_path is None:
            conf_path = os.getenv("CONFIGDBPATH")
        self.conf_path = env_dir / conf_path

        if store_path is None:
            store_path = os.getenv("STOREDBPATH")
        storepath = store_path
        self.store_path = env_dir / store_path

        if reaction_roles_path is None:
            reaction_roles_path = os.getenv("REACTIONROLESDBPATH")
        reactionrolespath = reaction_roles_path
        self.reaction_roles_path = env_dir / reaction_roles_path

        self._init_db()
    
    def _connect(self, guild: int):
        db_guild = f"{str(guild)}.db"
        #Init
        with sqlite3.connect(self.db_path / db_guild) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS amounts (
                    uid INTEGER PRIMARY KEY,
                    value INTEGER DEFAULT 0,
                    name TEXT,
                    additional INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 0
                )
            """)
            conn.commit()
        return sqlite3.connect(self.db_path / db_guild)
    
    def _conf_connect(self):
        return sqlite3.connect(self.conf_path)

    def _store_roles_connect(self, guild: int):
        db_guild = f"roles_{str(guild)}.db"
        #Init
        path = self.store_path / "roles" / db_guild
        with sqlite3.connect(path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS roles (
                    rid INTEGER PRIMARY KEY,
                    price INTEGER
                )
            """)
            conn.commit()
        return sqlite3.connect(path)
    
    def _store_levels_connect(self, guild: int):
        db_guild = f"levels_{str(guild)}.db"
        #Init
        path = self.store_path / "levels" / db_guild
        with sqlite3.connect(path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS levels (
                    amount INTEGER PRIMARY KEY,
                    price INTEGER
                )
            """)
            conn.commit()
        return sqlite3.connect(path)

    def _reaction_roles_connect(self, guild: int):
        db_guild = f"roles_{str(guild)}.db"
        #Init
        path = self.reaction_roles_path / db_guild
        with sqlite3.connect(path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reaction_roles (
                    rid INTEGER PRIMARY KEY,
                    desc TEXT
                )
            """)
            conn.commit()
        return sqlite3.connect(path)

    def _init_db(self):
        with self._conf_connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuration (
                    guild INTEGER PRIMARY KEY,
                    channel_id INTEGER,
                    rid INTEGER
                )
            """)
            conn.commit()

    def increase_additional(self, uid: int, amount: int, name: str, guild: int):
        self.ensure_exists(uid, name, guild)

        with self._connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE amounts
                SET additional = additional + ?
                WHERE uid = ?
            """, (amount, uid))
            conn.commit()
    
    def decrease_additional(self, uid: int, amount: int, name: str, guild: int):
        self.ensure_exists(uid, name, guild)

        with self._connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE amounts
                SET additional = additional - ?
                WHERE uid = ?
            """, (amount, uid))
            conn.commit()

    def ensure_exists(self, uid, name, guild: int):
        if self.get_value(guild, uid) is None:
            with self._connect(guild) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO amounts (uid, value, name, additional)
                    VALUES (?, 0, ?, 0)
                """, (uid, name))
                conn.commit()
    
    def get_additional(self, uid, guild: int):
        with self._connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT additional FROM amounts WHERE uid = ?
            """, (uid,))
            result = cursor.fetchone()
            return result[0] if result else 0

    #Set configuration
    def set_channel_id(self, guild: int, channel_id: int, rid: int):
        with self._conf_connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO configuration (guild, channel_id, rid)
                VALUES (?, ?, ?)
                ON CONFLICT(guild) DO UPDATE SET channel_id = excluded.channel_id, rid = excluded.rid
            """, (guild, channel_id, rid))
            conn.commit()

    #Get the report channel id
    def get_channel_id(self, guild: int):
        with self._conf_connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT channel_id FROM configuration WHERE guild = ?
            """, (guild,))
            result = cursor.fetchone()
            return result[0] if result else None 
    
    #Get the report channel id
    def get_role_id(self, guild: int):
        with self._conf_connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT rid FROM configuration WHERE guild = ?
            """, (guild,))
            result = cursor.fetchone()
            return result[0] if result else None 

    #Set value
    def set_value(self, uid: int, amount: int, name: str, guild: int):
        with self._connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO amounts (uid, value, name)
                VALUES (?, ?, ?)
                ON CONFLICT(uid) DO UPDATE SET value = excluded.value
            """, (uid, amount, name))
            conn.commit()
    
    #Increase value
    def increase_value(self, uid: int, name: str, guild: int):
        #Get previous one
        amount = self.get_value(guild, uid)
        if not amount:
            amount = 0

        amount = amount + 1

        with self._connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO amounts (uid, value, name)
                VALUES (?, ?, ?)
                ON CONFLICT(uid) DO UPDATE SET value = excluded.value
            """, (uid, amount, name))
            conn.commit()
    
    #Get value
    def get_value(self, guild: int, uid: int) -> Optional[int]:
        with self._connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT value FROM amounts WHERE uid = ?
            """, (uid,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    #Get all data from database
    def getalldata(self, guild: int):
        with self._connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT uid, value, name, additional FROM amounts")
            result = cursor.fetchall()

            data = None
            for user, amount, username, additional in result:
                rawtokens = amount / oneTokenAmount
                tokens = math.floor(rawtokens) + additional
                if data is None:
                    data = ""
                data += f"{username} ({user}): {amount} messages sent, {tokens} tokens\n"
            
            return data if data else None
        
    #Clear the database
    def clear_user_data(self, guild: int):
        with self._connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM amounts")
            conn.commit()
    
    #Clear store database
    def clear_store_data(self, guild: int):
        #Clear roles
        with self._store_roles_connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM roles")
            conn.commit()
        #Clear level ups
        with self._store_levels_connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM levels")
            conn.commit()

    #Clear config database
    def clear_config(self, guild: int):
        with self._conf_connect() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM configuration WHERE guild = ?", (guild,))
            conn.commit()

    #Add role to the store
    def add_role_to_store(self, rid: int, price: int, guild: int):
        with self._store_roles_connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO roles (rid, price)
                VALUES (?, ?)
                ON CONFLICT(rid) DO UPDATE SET price = excluded.price
            """, (rid, price))
            conn.commit()

    #Get roles for store
    def get_roles(self, guild: int):
        with self._store_roles_connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT rid, price FROM roles
            """)
            result = cursor.fetchall()
            return result if result else None
    
    #Get role price
    def get_role_price(self, rid: int, guild: int):
        with self._store_roles_connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT price FROM roles WHERE rid = ?
            """, (rid,))
            result = cursor.fetchone()
            return result[0] if result else None

    #Add a level up to the store
    def add_levelup_to_store(self, level: int, price: int, guild: int):
        with self._store_levels_connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO levels (amount, price)
                VALUES (?, ?)
                ON CONFLICT(amount) DO UPDATE SET price = excluded.price
            """, (level, price))
            conn.commit()
    
    #Get levelups for store
    def get_levelups(self, guild: int):
        with self._store_levels_connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT amount, price FROM levels")
            result = cursor.fetchall()
            return result if result else None
    
    #Get role price
    def get_levelup_price(self, amount: int, guild: int):
        with self._store_levels_connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT price FROM levels WHERE amount = ?
            """, (amount,))
            result = cursor.fetchone()
            return result[0] if result else None

    #Get the level of an user
    def get_level(self, uid: int, guild: int):
        with self._connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT level FROM amounts WHERE uid = ?", (uid,))
            result = cursor.fetchone()
            return result[0] if result else None
    
    #Increase level of an user
    def increase_level(self, uid: int, name: str, amount: int, guild: int):
        current = self.get_level(uid, guild)
        if current is None:
            current = 0
        
        newvalue = current + amount
        with self._connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO amounts (uid, name, level)
                VALUES (?, ?, ?)
                ON CONFLICT(uid) DO UPDATE SET level = excluded.level
            """, (uid, name, newvalue))
            conn.commit()
    
    #Set level of an user
    def set_level(self, uid: int, name: str, level: int, guild: int):
        with self._connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO amounts (uid, name, level)
                VALUES (?, ?, ?)
                ON CONFLICT(uid) DO UPDATE SET level = excluded.level
            """, (uid, name, level))
            conn.commit()
    
    #Delete role from store
    def remove_role_from_store(self, rid: int, guild: int):
        with self._store_roles_connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM roles WHERE rid = ?", (rid,))
            conn.commit()

    #Delete level from store
    def remove_level_from_store(self, amount: int, guild: int):
        with self._store_levels_connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM levels WHERE amount = ?", (amount,))
            conn.commit()

    #Get top10 highest level users
    def get_top10_levels(self, guild: int):
        with self._connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, level
                FROM amounts
                ORDER BY level DESC
                LIMIT 10
            """)
            result = cursor.fetchall()
            return result if result else None
    
    #Get top10 highest token users (doesnt actually calculate it but returns the required data)
    def get_tokens_for_leaderboard(self, guild: int):
        with self._connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, value, additional
                FROM amounts
            """)
            result = cursor.fetchall()
            return result if result else None

    # Get roles for reaction roles dropdown
    def get_reaction_roles(self, guild: int):
        with self._reaction_roles_connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT rid, desc FROM reaction_roles
            """)
            result = cursor.fetchall()
            return result if result else None

    # Get roles for reaction roles dropdown
    def has_reaction_role(self, rid: int, guild: int):
        with self._reaction_roles_connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 1 FROM reaction_roles WHERE rid = ? LIMIT 1
            """, (rid,))
            result = cursor.fetchone()
            return result is not None

    # Add new role to reaction roles
    def add_reaction_role(self, rid: int, desc: str, guild: int):
        with self._reaction_roles_connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO reaction_roles (rid, desc)
                VALUES (?, ?)
                ON CONFLICT(rid) DO UPDATE SET desc = excluded.desc
            """, (rid, desc))
            conn.commit()

    # Delete role from reaction roles
    def remove_reaction_role(self, rid: int, guild: int):
        with self._reaction_roles_connect(guild) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM reaction_roles WHERE rid = ?
            """, (rid,))
            conn.commit()