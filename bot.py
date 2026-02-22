from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, Application
from attendance import get_attendance
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("BOT_TOKEN not found in environment variables. Please check your .env file.")


async def attendance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) != 2:
        await update.message.reply_text(
            "Usage:\n/attendance <username> <password>"
        )
        return

    username = context.args[0]
    password = context.args[1]

    await update.message.reply_text("⏳ Fetching attendance... Please wait.")

    # Run blocking Selenium in thread (VERY IMPORTANT for hosting)
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        None, get_attendance, username, password
    )

    await update.message.reply_text(result)


async def post_init(application: Application):
    bot_info = await application.bot.get_me()
    print(f"🤖 Bot is running as @{bot_info.username}")


def main():
    app = ApplicationBuilder().token(TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("attendance", attendance_command))

    app.run_polling()


if __name__ == "__main__":
    main()