import os
import random
import time
import logging
from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message
)
from pymongo import MongoClient
import config

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("CobraBot")

# Initialize Pyrogram/Pyrofork Client
bot = Client(
    "Cobra_Chatbot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN
)

# Initialize MongoDB Connection (Persistent Single Client)
try:
    mongo_client = MongoClient(config.MONGO_URL, serverSelectionTimeoutMS=5000)
    # Chat learning data collection (compatible with original Word.WordDb)
    word_col = mongo_client["Word"]["WordDb"]
    # Chatbot disabled status collections (modern CobraDb with NatashaDb fallback)
    cobra_status_col = mongo_client["CobraDb"]["ChatbotStatus"]
    legacy_status_col = mongo_client["NatashaDb"]["Natasha"]
    logger.info("Connected to MongoDB successfully.")
except Exception as e:
    logger.error(f"Failed to initialize MongoDB: {e}")
    mongo_client = None
    word_col = None
    cobra_status_col = None
    legacy_status_col = None


def is_chat_disabled(chat_id: int) -> bool:
    """Check if chatbot is disabled in the specified group."""
    if cobra_status_col is not None:
        try:
            if cobra_status_col.find_one({"chat_id": chat_id}):
                return True
        except Exception as e:
            logger.error(f"Error checking cobra_status_col: {e}")
    if legacy_status_col is not None:
        try:
            if legacy_status_col.find_one({"chat_id": chat_id}):
                return True
        except Exception as e:
            logger.error(f"Error checking legacy_status_col: {e}")
    return False


def set_chat_disabled(chat_id: int, disabled: bool):
    """Enable or disable chatbot in the specified group."""
    if disabled:
        if cobra_status_col is not None:
            try:
                cobra_status_col.update_one({"chat_id": chat_id}, {"$set": {"chat_id": chat_id}}, upsert=True)
            except Exception as e:
                logger.error(f"Error saving to cobra_status_col: {e}")
        if legacy_status_col is not None:
            try:
                legacy_status_col.update_one({"chat_id": chat_id}, {"$set": {"chat_id": chat_id}}, upsert=True)
            except Exception as e:
                logger.error(f"Error saving to legacy_status_col: {e}")
    else:
        if cobra_status_col is not None:
            try:
                cobra_status_col.delete_many({"chat_id": chat_id})
            except Exception as e:
                logger.error(f"Error deleting from cobra_status_col: {e}")
        if legacy_status_col is not None:
            try:
                legacy_status_col.delete_many({"chat_id": chat_id})
            except Exception as e:
                logger.error(f"Error deleting from legacy_status_col: {e}")


async def is_admin(chat_id: int, user_id: int) -> bool:
    """Check if a user is an administrator in the chat."""
    try:
        member = await bot.get_chat_member(chat_id, user_id)
        status_str = str(getattr(member, "status", "")).lower()
        return any(adm in status_str for adm in ["administrator", "owner", "creator"])
    except Exception as e:
        logger.debug(f"is_admin check failed for {user_id} in {chat_id}: {e}")
        return False


async def send_cobra_media(message: Message, caption: str, reply_markup=None):
    """Smart media sender handling mp4 animation/video and photo with graceful fallbacks."""
    media_url = config.MEDIA_URL
    is_video_format = media_url and any(
        media_url.lower().endswith(ext) or ext in media_url.lower()
        for ext in [".mp4", ".webm", ".gif"]
    )

    if is_video_format:
        try:
            return await message.reply_animation(
                animation=media_url,
                caption=caption,
                reply_markup=reply_markup
            )
        except Exception as err:
            logger.warning(f"reply_animation failed ({err}), trying reply_video...")
            try:
                return await message.reply_video(
                    video=media_url,
                    caption=caption,
                    reply_markup=reply_markup
                )
            except Exception as err2:
                logger.warning(f"reply_video failed ({err2}), trying reply_photo...")
                try:
                    return await message.reply_photo(
                        photo=media_url,
                        caption=caption,
                        reply_markup=reply_markup
                    )
                except Exception as err3:
                    logger.error(f"All media sends failed ({err3}), sending text fallback.")
                    return await message.reply_text(
                        text=caption,
                        reply_markup=reply_markup,
                        disable_web_page_preview=True
                    )
    else:
        try:
            return await message.reply_photo(
                photo=media_url,
                caption=caption,
                reply_markup=reply_markup
            )
        except Exception as err:
            logger.error(f"reply_photo failed ({err}), sending text fallback.")
            return await message.reply_text(
                text=caption,
                reply_markup=reply_markup,
                disable_web_page_preview=True
            )


# ==============================================================================
# COMMAND HANDLERS
# ==============================================================================

@bot.on_message(filters.command(["start"], prefixes=["/", "!", "."]))
async def start_handler(client: Client, message: Message):
    try:
        me = await bot.get_me()
        busername = me.username or config.BOT_USERNAME
        first_name = message.from_user.first_name if message.from_user else "User"
        user_id = message.from_user.id if message.from_user else 0

        if message.chat.type != "private":
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("👥 sᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_GROUP),
                    InlineKeyboardButton("📣 ᴜᴘᴅᴀᴛᴇs", url=config.UPDATE_CHANNEL)
                ],
                [
                    InlineKeyboardButton("💠 ᴏᴡɴᴇʀ 💠", url=f"https://t.me/{config.OWNER_USERNAME.lstrip('@')}")
                ]
            ])
            caption = (
                f"🐍 **{config.BOT_NAME} ɪs ᴏɴʟɪɴᴇ!**\n"
                f"───────────────────\n"
                f"✨ **sᴘᴇᴄɪᴀʟ ғᴇᴀᴛᴜʀᴇs:**\n"
                f"───────────────────\n"
                f"➛ ᴛʜɪs ʙᴏᴛ ᴏʙsᴇʀᴠᴇs ɢʀᴏᴜᴘ ᴄʜᴀᴛs, ʟᴇᴀʀɴs ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ, ᴀɴᴅ ʀᴇᴘʟɪᴇs ᴡɪᴛʜ ᴛᴇxᴛs ᴀɴᴅ sᴛɪᴄᴋᴇʀs!\n"
                f"➛ ɴᴏ ᴄᴏᴍᴘʟᴇx sᴇᴛᴜᴘ ʀᴇǫᴜɪʀᴇᴅ. ᴊᴜsᴛ ᴀᴅᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴇɴᴀʙʟᴇ ɪᴛ.\n\n"
                f"💡 **ǫᴜɪᴄᴋ ᴄᴏᴍᴍᴀɴᴅs:**\n"
                f"• `/chatbot on` - ᴀᴄᴛɪᴠᴀᴛᴇ ᴄᴏʙʀᴀ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ\n"
                f"• `/chatbot off` - ᴅɪsᴀʙʟᴇ ᴄᴏʙʀᴀ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ\n"
                f"• `/help` - sᴇᴇ ᴍᴏʀᴇ ɪɴғᴏ\n"
                f"───────────────────"
            )
            await send_cobra_media(message, caption=caption, reply_markup=buttons)
        else:
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("➕ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕", url=f"https://t.me/{busername}?startgroup=true")
                ],
                [
                    InlineKeyboardButton("👥 sᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_GROUP),
                    InlineKeyboardButton("📣 ᴜᴘᴅᴀᴛᴇs", url=config.UPDATE_CHANNEL)
                ],
                [
                    InlineKeyboardButton("💠 ᴏᴡɴᴇʀ 💠", url=f"https://t.me/{config.OWNER_USERNAME.lstrip('@')}")
                ]
            ])
            caption = (
                f"🐍 ʜᴇʟʟᴏ [{first_name}](tg://user?id={user_id}),\n\n"
                f"ɪ ᴀᴍ **{config.BOT_NAME}** — ᴀɴ ᴀᴅᴠᴀɴᴄᴇᴅ ᴀɴᴅ ɪɴᴛᴇʟʟɪɢᴇɴᴛ ᴀɪ ᴄʜᴀᴛʙᴏᴛ!\n"
                f"═══════════════════════\n"
                f"➛ ɪғ ʏᴏᴜ ᴀʀᴇ ғᴇᴇʟɪɴɢ ʟᴏɴᴇʟʏ, ʏᴏᴜ ᴄᴀɴ ᴀʟᴡᴀʏs ᴄᴏᴍᴇ ᴀɴᴅ ᴄʜᴀᴛ ᴡɪᴛʜ ᴍᴇ.\n"
                f"➛ ɪ ʟᴇᴀʀɴ ɴᴇᴡ ᴡᴏʀᴅs ᴀɴᴅ sᴛɪᴄᴋᴇʀs ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ.\n"
                f"➛ ᴛʀʏ `/help` ᴛᴏ ᴋɴᴏᴡ ᴀʟʟ ᴍʏ ᴀʙɪʟɪᴛɪᴇs.\n"
                f"═══════════════════════"
            )
            await send_cobra_media(message, caption=caption, reply_markup=buttons)
    except Exception as e:
        logger.error(f"Error in start_handler: {e}")


@bot.on_message(filters.command(["help"], prefixes=["/", "!", "."]))
async def help_handler(client: Client, message: Message):
    try:
        me = await bot.get_me()
        busername = me.username or config.BOT_USERNAME
        if message.chat.type != "private":
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton(text="💬 ᴘᴍ ᴍᴇ ғᴏʀ ʜᴇʟᴘ", url=f"https://t.me/{busername}?start=help")]
            ])
            caption = "ᴄᴏɴᴛᴀᴄᴛ ᴍᴇ ɪɴ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ ғᴏʀ ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅs! 🐍"
            await send_cobra_media(message, caption=caption, reply_markup=buttons)
        else:
            caption = (
                f"🐍 **{config.BOT_NAME} — ʜᴇʟᴘ ɢᴜɪᴅᴇ**\n"
                f"─────────────────────\n"
                f"✨ **ғᴇᴀᴛᴜʀᴇs:**\n"
                f"• ᴏʙsᴇʀᴠᴇs ᴀʟʟ ɢʀᴏᴜᴘ ᴄᴏɴᴠᴇʀsᴀᴛɪᴏɴs ᴀɴᴅ sᴛᴏʀᴇs ᴅᴀᴛᴀ.\n"
                f"• ʀᴇᴘʟɪᴇs ᴛᴏ ʏᴏᴜʀ ǫᴜᴇsᴛɪᴏɴs, ᴛᴇxᴛs, ᴀɴᴅ sᴛɪᴄᴋᴇʀs sᴍᴀʀᴛʟʏ.\n"
                f"• ᴀᴜᴛᴏᴍᴀᴛɪᴄ ʟᴇᴀʀɴɪɴɢ ᴇɴɢɪɴᴇ — ɢᴇᴛs sᴍᴀʀᴛᴇʀ ᴇᴠᴇʀʏ ᴅᴀʏ!\n\n"
                f"⚙️ **ᴄᴏᴍᴍᴀɴᴅs:**\n"
                f"➛ `/chatbot on` - ᴇɴᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ (ᴀᴅᴍɪɴ ᴏɴʟʏ)\n"
                f"➛ `/chatbot off` - ᴅɪsᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ (ᴀᴅᴍɪɴ ᴏɴʟʏ)\n"
                f"➛ `/chatbot` - ᴄʜᴇᴄᴋ sᴛᴀᴛᴜs ᴀɴᴅ ɢᴜɪᴅᴇ\n"
                f"➛ `/ping` - ᴄʜᴇᴄᴋ ʙᴏᴛ ʟᴀᴛᴇɴᴄʏ & sᴘᴇᴇᴅ\n"
                f"─────────────────────"
            )
            buttons = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("➕ ᴀᴅᴅ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ➕", url=f"https://t.me/{busername}?startgroup=true")
                ],
                [
                    InlineKeyboardButton("👥 sᴜᴘᴘᴏʀᴛ", url=config.SUPPORT_GROUP),
                    InlineKeyboardButton("📣 ᴜᴘᴅᴀᴛᴇs", url=config.UPDATE_CHANNEL)
                ]
            ])
            await send_cobra_media(message, caption=caption, reply_markup=buttons)
    except Exception as e:
        logger.error(f"Error in help_handler: {e}")


@bot.on_message(filters.command(["chatbot"], prefixes=["/", "!", ".", "?", "-"]) & ~filters.private)
async def chatbot_toggle_handler(client: Client, message: Message):
    try:
        args = message.text.split()[1:] if message.text else []
        action = args[0].lower() if args else ""

        if not action:
            caption = (
                f"🐍 **ʜᴏᴡ ᴛᴏ ᴜsᴇ {config.BOT_NAME}:**\n"
                f"─────────────────────\n"
                f"• `/chatbot on` - ᴀᴄᴛɪᴠᴀᴛᴇ ᴄʜᴀᴛʙᴏᴛ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ\n"
                f"• `/chatbot off` - ᴅɪsᴀʙʟᴇ ᴄʜᴀᴛʙᴏᴛ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ\n\n"
                f"💡 *ᴛʜɪs ʙᴏᴛ ʟᴇᴀʀɴs ғʀᴏᴍ ɢʀᴏᴜᴘ ᴍᴇssᴀɢᴇs ᴀɴᴅ ʀᴇᴘʟɪᴇs ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ!*"
            )
            return await send_cobra_media(message, caption=caption)

        # Admin verification
        if message.from_user:
            user_id = message.from_user.id
            if not await is_admin(message.chat.id, user_id):
                return await message.reply_text("⚠️ **sɪʀ, ʏᴏᴜ ᴀʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ!** ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴛᴏɢɢʟᴇ ᴛʜᴇ ᴄʜᴀᴛʙᴏᴛ.")

        if action == "off":
            if is_chat_disabled(message.chat.id):
                return await message.reply_text(f"🐍 **{config.BOT_NAME} ɪs ᴀʟʀᴇᴀᴅʏ ᴅɪsᴀʙʟᴇᴅ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!**")
            set_chat_disabled(message.chat.id, True)
            return await message.reply_text(f"🚫 **{config.BOT_NAME} ʜᴀs ʙᴇᴇɴ ᴅɪsᴀʙʟᴇᴅ ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.**\nᴜsᴇ `/chatbot on` ᴛᴏ ᴇɴᴀʙʟᴇ ᴀɢᴀɪɴ.")

        elif action == "on":
            if not is_chat_disabled(message.chat.id):
                return await message.reply_text(f"🐍 **{config.BOT_NAME} ɪs ᴀʟʀᴇᴀᴅʏ ᴀᴄᴛɪᴠᴇ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ!**")
            set_chat_disabled(message.chat.id, False)
            req_user = f"[{message.from_user.first_name}](tg://user?id={message.from_user.id})" if message.from_user else "Admin"
            chat_title = message.chat.title or "this group"
            return await message.reply_text(
                f"✅ **sᴜᴄᴄᴇssғᴜʟʟʏ ᴇɴᴀʙʟᴇᴅ!**\n"
                f"🐍 **{config.BOT_NAME}** ɪs ɴᴏᴡ ᴀᴄᴛɪᴠᴇ ɪɴ **{chat_title}**!\n"
                f"👤 ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ: {req_user}"
            )
        else:
            await message.reply_text("❓ **ᴜɴᴋɴᴏᴡɴ ᴏᴘᴛɪᴏɴ!** ᴜsᴇ `/chatbot on` ᴏʀ `/chatbot off`.")
    except Exception as e:
        logger.error(f"Error in chatbot_toggle_handler: {e}")


@bot.on_message(filters.command(["ping"], prefixes=["/", "!", "."]))
async def ping_handler(client: Client, message: Message):
    start_time = time.time()
    m = await message.reply_text("🐍 **ᴘɪɴɢɪɴɢ...**")
    latency = round((time.time() - start_time) * 1000)
    await m.edit_text(f"🐍 **ᴘᴏɴɢ!**\n⚡ **ʟᴀᴛᴇɴᴄʏ:** `{latency} ms`\n🤖 **{config.BOT_NAME} ɪs ʀᴜɴɴɪɴɢ sᴍᴏᴏᴛʜʟʏ!**")


# ==============================================================================
# GROUP MESSAGE HANDLER & LEARNING ENGINE
# ==============================================================================

@bot.on_message(
    (filters.text | filters.sticker)
    & ~filters.private
    & ~filters.bot
)
async def group_chat_handler(client: Client, message: Message):
    if word_col is None:
        return

    # If chatbot is disabled in this group, ignore
    if is_chat_disabled(message.chat.id):
        return

    try:
        getme = await bot.get_me()
        bot_id = getme.id
    except Exception as e:
        logger.error(f"Error getting bot me: {e}")
        return

    # 1. CASE: Replying to another message
    if message.reply_to_message:
        replied = message.reply_to_message

        # A: Someone replied directly to the BOT -> Bot should respond!
        if replied.from_user and replied.from_user.id == bot_id:
            lookup_key = message.text if message.text else (message.sticker.file_unique_id if message.sticker else None)
            if lookup_key:
                try:
                    await bot.send_chat_action(message.chat.id, "typing")
                except Exception:
                    pass
                matches = list(word_col.find({"word": lookup_key}))
                if matches:
                    chosen = random.choice(matches)
                    resp_text = chosen.get("text")
                    is_sticker = chosen.get("check") == "sticker"
                    if is_sticker:
                        try:
                            await message.reply_sticker(resp_text)
                        except Exception as e:
                            logger.error(f"Failed to reply sticker: {e}")
                    else:
                        try:
                            await message.reply_text(resp_text)
                        except Exception as e:
                            logger.error(f"Failed to reply text: {e}")

        # B: Someone replied to another human user -> Bot LEARNS!
        elif replied.from_user and replied.from_user.id != bot_id:
            # Subcase: Replied message was TEXT
            if replied.text:
                if message.text:
                    if not word_col.find_one({"word": replied.text, "text": message.text}):
                        word_col.insert_one({"word": replied.text, "text": message.text, "check": "text"})
                elif message.sticker:
                    if not word_col.find_one({"word": replied.text, "id": message.sticker.file_unique_id}):
                        word_col.insert_one({
                            "word": replied.text,
                            "text": message.sticker.file_id,
                            "check": "sticker",
                            "id": message.sticker.file_unique_id
                        })

            # Subcase: Replied message was STICKER (Fixed bug where old code used undefined 'toggle')
            elif replied.sticker:
                sticker_uid = replied.sticker.file_unique_id
                if message.text:
                    if not word_col.find_one({"word": sticker_uid, "text": message.text}):
                        word_col.insert_one({"word": sticker_uid, "text": message.text, "check": "text"})
                elif message.sticker:
                    if not word_col.find_one({"word": sticker_uid, "id": message.sticker.file_unique_id}):
                        word_col.insert_one({
                            "word": sticker_uid,
                            "text": message.sticker.file_id,
                            "check": "sticker",
                            "id": message.sticker.file_unique_id
                        })

    # 2. CASE: Not a reply to any message (Spontaneous reply if known word)
    else:
        lookup_key = message.text if message.text else (message.sticker.file_unique_id if message.sticker else None)
        if lookup_key:
            matches = list(word_col.find({"word": lookup_key}))
            if matches:
                try:
                    await bot.send_chat_action(message.chat.id, "typing")
                except Exception:
                    pass
                chosen = random.choice(matches)
                resp_text = chosen.get("text")
                is_sticker = chosen.get("check") == "sticker"
                if is_sticker:
                    try:
                        await message.reply_sticker(resp_text)
                    except Exception as e:
                        logger.error(f"Failed to reply sticker: {e}")
                else:
                    try:
                        await message.reply_text(resp_text)
                    except Exception as e:
                        logger.error(f"Failed to reply text: {e}")


# ==============================================================================
# PRIVATE MESSAGE HANDLER
# ==============================================================================

@bot.on_message(
    (filters.text | filters.sticker)
    & filters.private
    & ~filters.bot
)
async def private_chat_handler(client: Client, message: Message):
    if word_col is None:
        return

    # Skip if message is a command
    if message.text and message.text.startswith(("/", "!", ".")):
        return

    lookup_key = message.text if message.text else (message.sticker.file_unique_id if message.sticker else None)
    if not lookup_key:
        return

    try:
        await bot.send_chat_action(message.chat.id, "typing")
    except Exception:
        pass

    matches = list(word_col.find({"word": lookup_key}))
    if matches:
        chosen = random.choice(matches)
        resp_text = chosen.get("text")
        is_sticker = chosen.get("check") == "sticker"
        if is_sticker:
            try:
                await message.reply_sticker(resp_text)
            except Exception as e:
                logger.error(f"Failed to reply sticker in private: {e}")
        else:
            try:
                await message.reply_text(resp_text)
            except Exception as e:
                logger.error(f"Failed to reply text in private: {e}")
    else:
        # Default friendly response when word is unknown
        default_replies = [
            "🐍 I haven't learned how to answer that yet! Add me to a group chat so I can learn more.",
            "Hmm, that's interesting! Tell me more or chat with me in a group.",
            "🐍 Cobra Chatbot is listening!",
            "I'm still learning new phrases every day! Try another message."
        ]
        await message.reply_text(random.choice(default_replies))


# ==============================================================================
# BOT RUNNER
# ==============================================================================

if __name__ == "__main__":
    logger.info(f"Starting {config.BOT_NAME}...")
    bot.run()
