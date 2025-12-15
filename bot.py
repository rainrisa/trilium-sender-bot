from telegram import (
    Update,
)
from telegram.ext import ApplicationBuilder, ContextTypes
from typing import TypedDict, Callable, Literal
from pathlib import Path
from env import TG_ADMIN_IDS
import os
import uuid

DOWNLOAD_DIR = Path("./tmp")
DOWNLOAD_DIR.mkdir(exist_ok=True)

INVALID_MEDIA_GROUPS: set[str] = set()


class MsgDict(TypedDict):
    media_type: Literal["photo"]
    file_id: str
    caption: str | None
    post_id: int
    chat_id: int


async def download_photo(context: ContextTypes.DEFAULT_TYPE, file_id: str) -> str:
    bot = context.bot
    tg_file = await bot.get_file(file_id)

    unique_id = uuid.uuid4().hex
    short_name = unique_id[:7]
    path = DOWNLOAD_DIR / f"{short_name}.jpg"
    await tg_file.download_to_drive(custom_path=path)

    return str(path)


def delete_files(file_paths: list[str]):
    for path_str in file_paths:
        try:
            path = Path(path_str)
            if path.is_file():
                os.remove(path)
                print(f"Deleted temporary file: {path_str}")
        except Exception as e:
            print(f"Error deleting file {path_str}: {e}")


async def process_media_group(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    media_group_id = job.name
    chat_id = job.data[0]["chat_id"]

    if media_group_id in INVALID_MEDIA_GROUPS:
        print(
            f"[{chat_id}] [Group {media_group_id}] Skipping processing due to invalid media."
        )
        INVALID_MEDIA_GROUPS.discard(media_group_id)
        return

    print(f"[{chat_id}] [Group {media_group_id}] Processing {len(job.data)} item(s).")
    messages: list[MsgDict] = job.data
    text_parts: list[str] = []
    image_paths: list[str] = []

    for msg in messages:
        if msg["caption"]:
            text_parts.append(msg["caption"])

        path = await download_photo(context, msg["file_id"])
        image_paths.append(path)

    text = "\n".join(text_parts)

    trilium = context.application.bot_data["trilium"]
    print(f"[{chat_id}] [Group {media_group_id}] --> Starting Trilium append.")
    await trilium.append(text, image_paths)
    print(f"[{chat_id}] [Group {media_group_id}] <-- Trilium append finished.")

    delete_files(image_paths)

    bot = context.bot

    for msg in messages:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=msg["post_id"])
            print(f"Deleted message ID {msg['post_id']} from chat {chat_id}")
        except Exception as e:
            # Handle potential exceptions (e.g., bot doesn't have permission to delete)
            print(f"Error deleting message {msg['post_id']}: {e}")


async def process_single_message(message, context: ContextTypes.DEFAULT_TYPE):
    if message.text_html:
        text = message.text_html_urled
    elif message.caption_html:
        text = message.caption_html_urled
    else:
        text = ""

    image_paths: list[str] = []

    if message.photo:
        file_id = message.photo[-1].file_id
        path = await download_photo(context, file_id)
        image_paths.append(path)

    trilium = context.application.bot_data["trilium"]
    chat_id = message.chat_id
    message_id = message.message_id

    print(f"[{chat_id}] [Post {message_id}] --> Starting Trilium append.")
    await trilium.append(text, image_paths)
    print(f"[{chat_id}] [Post {message_id}] <-- Trilium append finished.")

    if image_paths:
        delete_files(image_paths)

    bot = context.bot
    try:
        await bot.delete_message(chat_id=message.chat_id, message_id=message.message_id)
        print(
            f"Deleted single message ID {message.message_id} from chat {message.chat_id}"
        )
    except Exception as e:
        print(f"Error deleting message {message.message_id}: {e}")


async def new_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    chat_id = update.effective_chat.id
    message_id = message.message_id
    media_group_id = message.media_group_id

    if chat_id not in TG_ADMIN_IDS:
        print(f"[{chat_id}] [Unauthorized] Access denied.")

        try:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Sorry you are not the admin",
            )
        except Exception:
            # Silence exception if bot cannot reply (e.g., in a channel it doesn't have permission to post)
            pass

        return

    if media_group_id and str(media_group_id) in INVALID_MEDIA_GROUPS:
        return

    # Unsupported attachment
    if message.video or message.document or message.audio or message.voice:
        unsupported_type = message.effective_attachment.__class__.__name__
        print(f"[{chat_id}] [Unsupported] Detected media type: {unsupported_type}")

        if media_group_id:
            INVALID_MEDIA_GROUPS.add(str(media_group_id))

            # cancel scheduled job if exists
            print(f"[{chat_id}] [Group {media_group_id}] Canceling scheduled job.")
            jobs = context.job_queue.get_jobs_by_name(str(media_group_id))
            for job in jobs:
                job.schedule_removal()

        return

    # Album (media group)
    if media_group_id:
        msg_dict: MsgDict = {
            "media_type": "photo",
            "file_id": message.photo[-1].file_id,
            "caption": message.caption_html,
            "post_id": message.message_id,
            "chat_id": message.chat_id,
        }

        jobs = context.job_queue.get_jobs_by_name(str(media_group_id))

        if jobs:
            jobs[0].data.append(msg_dict)
        else:
            print(
                f"[{chat_id}] [Group {media_group_id}] New group detected. Scheduling job in 3s."
            )
            context.job_queue.run_once(
                callback=process_media_group,
                when=3,
                data=[msg_dict],
                name=str(media_group_id),
            )

    # Single message
    else:
        print(f"[{chat_id}] [Post {message_id}] Processing single message.")
        await process_single_message(message, context)


def build_app(token: str, on_message: Callable):
    app = ApplicationBuilder().token(token).build()
    app.add_handler(on_message)
    return app
