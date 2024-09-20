from animeflv import AnimeFLV
from logger import logger

def search_anime(api, anime_name):
    """Busca un anime y devuelve el primer resultado."""
    try:
        anime_list = api.search(anime_name)
        if not anime_list:
            logger.warning(f"[anime_service.py] No se encontró el anime: {anime_name}")
            return None
        logger.info(f"[anime_service.py] Se encontraron {len(anime_list)} resultados para '{anime_name}'.")
        return anime_list
    except Exception as e:
        logger.error(f"[anime_service.py] Error buscando el anime '{anime_name}': {e}")
        return None

def get_anime_episodes(api, anime_id):
    """Obtiene la lista de episodios de un anime."""
    try:
        episodes = api.get_episodes(anime_id)
        logger.info(f"[anime_service.py] Se encontraron {len(episodes)} episodios para el anime {anime_id}.")
        return episodes
    except Exception as e:
        logger.error(f"[anime_service.py] Error obteniendo episodios del anime (ID: {anime_id}): {e}")
        return None
