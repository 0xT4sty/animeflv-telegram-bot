import hashlib
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext, CallbackQueryHandler
from database import add_anime_to_follow, get_followed_animes
from anime_service import search_anime, get_anime_episodes
from logger import logger
from animeflv import AnimeFLV

async def seguir(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    anime_name = ' '.join(context.args)

    logger.info(f"[Commands] Usuario {user_id} está intentando seguir el anime '{anime_name}'")

    try:
        with AnimeFLV() as api:
            anime_list = search_anime(api, anime_name)
            if anime_list:
                add_anime_to_follow(user_id, anime_list[0]['id'])
                logger.info(f"[Commands] Usuario {user_id} ahora sigue {anime_list[0]['title']} (ID: {anime_list[0]['id']})")
                await update.message.reply_text(f"Ahora sigues {anime_list[0]['title']}!")
            else:
                logger.warning(f"No se encontró el anime '{anime_name}' para el usuario {user_id}")
                await update.message.reply_text("No se encontró el anime.")
    except Exception as e:
        logger.error(f"[Commands] Error al seguir el anime '{anime_name}' para el usuario {user_id}: {e}")
        await update.message.reply_text("Ocurrió un error al intentar seguir el anime.")

async def buscar(update: Update, context: CallbackContext):
    """Permite buscar animes por su nombre y mostrar botones para seguirlos."""
    query = ' '.join(context.args)
    
    if not query:
        await update.message.reply_text("Por favor, proporciona el nombre del anime que deseas buscar.")
        return

    logger.info(f"[Commands] Usuario {update.message.from_user.id} busca el anime '{query}'")

    try:
        with AnimeFLV() as api:
            anime_list = search_anime(api, query)
            if anime_list:
                # Crear lista de mensajes y botones
                for anime in anime_list:  # Limitar a 5 resultados
                    try:
                        buttons = [
                            [InlineKeyboardButton(f"Seguir {anime.title}", callback_data=f"seguir:{anime.id}")]
                        ]
                        reply_markup = InlineKeyboardMarkup(buttons)
                        
                        # Construir la descripción del anime
                        caption = f"🎬 *{anime.title}*\n\n"

                        if anime.synopsis:
                            caption += f"📝 *Sinopsis*: {anime.synopsis}\n\n"

                        if anime.rating:
                            caption += f"⭐️ *Rating*: {anime.rating}/5\n"

                        if anime.genres:
                            genres = ', '.join(anime.genres)
                            caption += f"🎭 *Géneros*: {genres}\n"

                        if anime.debut:
                            caption += f"📅 *Debut*: {anime.debut}\n"

                        if anime.type:
                            caption += f"📺 *Tipo*: {anime.type}\n"

                        if anime.episodes:
                            num_episodes = len(anime.episodes)
                            caption += f"🎞️ *Episodios*: {num_episodes} episodios disponibles\n"

                        # Mostrar el poster y la información del anime
                        await update.message.reply_photo(photo=anime.poster, caption=caption, reply_markup=reply_markup, parse_mode="Markdown")
                    except Exception as e:
                        logger.error(f"[Commands] Ocurrió un error con el resultado [{anime.id}]'{anime.title}': {e}")
            else:
                await update.message.reply_text(f"No se encontraron animes con el nombre '{query}'.")
    except Exception as e:
        logger.error(f"[Commands] Error buscando el anime '{query}': {e}")
        await update.message.reply_text(f"Ocurrió un error al buscar el anime '{query}'.")

async def handle_callback_query(update: Update, context: CallbackContext):
    """Manejar la acción cuando el usuario presiona un botón."""
    query = update.callback_query
    await query.answer()  # Responder la consulta del botón

    # El callback_data vendrá en formato "seguir:<anime_id>"
    action, anime_id = query.data.split(":")

    if action == "seguir":
        user_id = query.from_user.id
        logger.info(f"[Commands] Usuario {user_id} quiere seguir el anime {anime_id}")

        # Lógica para añadir el anime a la lista de seguimiento
        add_anime_to_follow(user_id, anime_id)

        # Intentar editar el mensaje si es posible
        try:
            await query.edit_message_text(f"¡Ahora sigues el anime con ID: {anime_id}!")
        except telegram.error.BadRequest as e:
            # Si no se puede editar, enviar una respuesta nueva
            if str(e) == "There is no text in the message to edit":
                await query.message.reply_text(f"¡Ahora sigues el anime con ID: {anime_id}!")
            else:
                logger.error(f"[Commands] Error editando el mensaje: {e}")

async def revisar_nuevos_episodios(context: CallbackContext):
    logger.info("[Commands] Iniciando revisión de nuevos episodios...")
    
    try:
        with AnimeFLV() as api:
            conn = sqlite3.connect('anime_followers.db')
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT user_id FROM followers")
            users = cursor.fetchall()

            for user in users:
                followed_animes = get_followed_animes(user[0])
                for anime_id, last_episode in followed_animes:
                    episodes = get_anime_episodes(api, anime_id)
                    if episodes and len(episodes) > last_episode:
                        # Notificar al usuario del nuevo episodio
                        await context.bot.send_message(chat_id=user[0], text=f"Nuevo episodio de {anime_id}: Episodio {len(episodes)}")
                        update_last_episode(user[0], anime_id, len(episodes))
                        logger.info(f"[Commands] Notificado usuario {user[0]} del nuevo episodio {len(episodes)} de {anime_id}")
            conn.close()

    except Exception as e:
        logger.error(f"[Commands] Error al revisar nuevos episodios: {e}")
