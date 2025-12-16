from telegram.ext import MessageHandler, filters
from trilium_py.client import ETAPI
from trilium import Trilium
from bot import build_app, new_post
from env import (
    TRILIUM_URL,
    TRILIUM_TOKEN,
    TRILIUM_NOTE_ID,
    TG_BOT_TOKEN,
)

ea = ETAPI(TRILIUM_URL, TRILIUM_TOKEN)

trilium = Trilium(ea, TRILIUM_NOTE_ID)


def main() -> None:
    print("--- TRILIUM-SENDER-BOT INITIALIZING ---")
    ea = ETAPI(TRILIUM_URL, TRILIUM_TOKEN)
    trilium = Trilium(ea, TRILIUM_NOTE_ID)

    def handler_with_trilium(update, context):
        context.application.bot_data["trilium"] = trilium
        return new_post(update, context)

    app = build_app(
        token=TG_BOT_TOKEN,
        on_message=MessageHandler(
            (filters.TEXT | filters.CAPTION | filters.PHOTO) & ~filters.COMMAND,
            handler_with_trilium,
        ),
    )

    print("--- TRILIUM-SENDER-BOT STARTED ---")
    app.run_polling()


if __name__ == "__main__":
    main()
