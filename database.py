import sqlite3
from logger import logger

def init_db():
    try:
        conn = sqlite3.connect('anime_followers.db')
        cursor = conn.cursor()

        # Crear tabla followers
        cursor.execute('''CREATE TABLE IF NOT EXISTS followers (
                            user_id INTEGER,
                            anime_id TEXT,
                            last_episode INTEGER
                        )''')

        # Crear tabla anime_mapping para el mapeo de short_id -> anime_id
        cursor.execute('''CREATE TABLE IF NOT EXISTS anime_mapping (
                            short_id TEXT PRIMARY KEY,
                            anime_id TEXT NOT NULL
                        )''')

        conn.commit()
        conn.close()
        logger.info("[database.py] Base de datos inicializada correctamente.")
    except Exception as e:
        logger.error(f"[database.py] Error inicializando la base de datos: {e}")

def add_anime_to_follow(user_id, anime_id):
    try:
        conn = sqlite3.connect('anime_followers.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO followers (user_id, anime_id, last_episode) VALUES (?, ?, ?)",
                       (user_id, anime_id, 0))
        conn.commit()
        conn.close()
        logger.info(f"[database.py] Anime {anime_id} añadido a la lista de seguimiento para el usuario {user_id}.")
    except Exception as e:
        logger.error(f"[database.py] Error añadiendo anime a la base de datos: {e}")

def get_followed_animes(user_id):
    try:
        conn = sqlite3.connect('anime_followers.db')
        cursor = conn.cursor()
        cursor.execute("SELECT anime_id, last_episode FROM followers WHERE user_id=?", (user_id,))
        followed_animes = cursor.fetchall()
        conn.close()
        return followed_animes
    except Exception as e:
        logger.error(f"[database.py] Error obteniendo animes seguidos para el usuario {user_id}: {e}")
        return []

def update_last_episode(user_id, anime_id, last_episode):
    try:
        conn = sqlite3.connect('anime_followers.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE followers SET last_episode=? WHERE user_id=? AND anime_id=?",
                       (last_episode, user_id, anime_id))
        conn.commit()
        conn.close()
        logger.info(f"[database.py] Actualizado el último episodio visto para el anime {anime_id} del usuario {user_id} a {last_episode}.")
    except Exception as e:
        logger.error(f"[database.py] Error actualizando último episodio para el anime {anime_id} del usuario {user_id}: {e}")

# Función para guardar el mapeo entre short_id y anime_id
def save_anime_mapping(short_id, anime_id):
    try:
        conn = sqlite3.connect('anime_followers.db')
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO anime_mapping (short_id, anime_id) VALUES (?, ?)",
                       (short_id, anime_id))
        conn.commit()
        conn.close()
        logger.info(f"[database.py] Mapeo guardado: {short_id} -> {anime_id}")
    except Exception as e:
        logger.error(f"[database.py] Error guardando el mapeo: {e}")

# Función para obtener el anime_id a partir del short_id
def get_anime_by_hash(short_id):
    try:
        conn = sqlite3.connect('anime_followers.db')
        cursor = conn.cursor()
        cursor.execute("SELECT anime_id FROM anime_mapping WHERE short_id = ?", (short_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        logger.error(f"[database.py] Error recuperando el anime para el short_id {short_id}: {e}")
        return None
