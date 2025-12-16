# Trilium Sender Bot

Hi, this is just my personal bot to improve my programming skills

This repository contains a Telegram bot that sends messages and images directly into a Trilium note. It’s mainly for easy access, since I tend to open Telegram more often than Trilium when I’m on mobile

## Screenshots

_Post on Telegram channel_  |  _Result on TriliumDroid_
:-------------------------:|:-------------------------:
![](https://github.com/user-attachments/assets/d028fbd2-a668-4810-886b-0d3e27191cf2)  |  ![](https://github.com/user-attachments/assets/a97ad82f-f72f-43c0-8b32-1cabce4784f8)

## Features

* Append text and images
* Preserve clickable links
* Thread-safe Trilium writes
* Auto-delete processed Telegram messages
* Admin-only access
* Stored in a single note for easy review (this is the main advantage for me)

## Notes

Currently, it has some limitations:

* Only supports text and images; other message types are skipped
* You are required to edit the code directly to customize the note layout

## Installation

### Docker

Clone this project

```
git clone https://github.com/rainrisa/trilium-sender-bot.git
```

Copy the `.env` from `.env.example` and fill out the variables

```
cp .env.example .env # then fill out the .env
```

After that, just run

```
docker compose up -d
```

### Manual

I don't have the guide for manual installation for now, but you can view the step-by-step installation on the `Dockerfile`

## Environment Variables

* `TRILIUM_URL` (**required**) – your Trilium base URL
* `TRILIUM_TOKEN` (**required**) – your Trilium ETAPI token
* `TRILIUM_NOTE_ID` (**required**) – target note ID where content will be appended
* `TG_BOT_TOKEN` (**required**) – your Telegram bot token from BotFather
* `TG_ADMIN_IDS` (**required**) – space-separated Telegram user or channel IDs allowed to use the bot

## FAQ

**Why auto-delete processed messages?**

To keep things clean

**Why store everything in a single note?**

My main motivation is that when I find random things on mobile, I can dump them into one note for easy review. Later, when I’m on a desktop, I can organize them properly

**Other similar bots?**

[https://github.com/Nriver/trilium-bot](https://github.com/Nriver/trilium-bot) - creating or storing things in a separate note, instead of appending everything into a single note

## Support

If you find any problems using this bot, feel free to open an issue
