import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from classplus_api import request_otp, verify_otp
from email_providers.auto_email import generate_temp_email_and_fetch_otp

ASK_EMAIL_OPTION, ASK_EMAIL_MANUAL, ASK_OTP = range(3)

user_email_map = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome! I can help you generate a Classplus token.\nSend /gettoken to begin."
    )

async def gettoken(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Choose an option:\n1. Use temporary email (auto-generated)\n2. Use your own email\n\nSend 1 or 2."
    )
    return ASK_EMAIL_OPTION

async def email_option(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = update.message.text.strip()
    user_id = update.effective_user.id

    if choice == "1":
        email = await generate_temp_email_and_fetch_otp("init")  # get temp email
        user_email_map[user_id] = email
        await update.message.reply_text(f"Your temporary email is: {email}\n\nPlease request an OTP to this email on the Classplus platform, then send /next when done.")
        return ASK_OTP

    elif choice == "2":
        await update.message.reply_text("Please enter your email address:")
        return ASK_EMAIL_MANUAL

    else:
        await update.message.reply_text("Invalid choice. Please send 1 or 2.")
        return ASK_EMAIL_OPTION

async def set_manual_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = update.message.text.strip()
    user_id = update.effective_user.id
    user_email_map[user_id] = email
    await update.message.reply_text(f"Email set to: {email}\n\nNow request OTP on this email via Classplus, then send /next when ready.")
    return ASK_OTP

async def get_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    email = user_email_map.get(user_id)
    if not email:
        await update.message.reply_text("Email not found. Please use /gettoken again.")
        return ConversationHandler.END

    await update.message.reply_text("Fetching OTP from inbox or waiting for manual OTP...")

    otp = await generate_temp_email_and_fetch_otp("fetch", email=email)

    if not otp:
        await update.message.reply_text("OTP not found in inbox. If you're using a manual email, please type your OTP now:")
        return ASK_OTP

    token = await verify_otp(email, otp)
    if token:
        await update.message.reply_text(f"✅ Token Generated Successfully:\n\n{token}")
    else:
        await update.message.reply_text("❌ Failed to verify OTP.")
    return ConversationHandler.END

async def handle_manual_otp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    email = user_email_map.get(user_id)
    otp = update.message.text.strip()

    token = await verify_otp(email, otp)
    if token:
        await update.message.reply_text(f"✅ Token Generated Successfully:\n\n{token}")
        return ConversationHandler.END
    else:
        await update.message.reply_text("❌ Invalid OTP. Please try again or restart with /gettoken")
        return ASK_OTP

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Cancelled.")
    return ConversationHandler.END

if __name__ == '__main__':
    import os
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    app = Application.builder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("gettoken", gettoken)],
        states={
            ASK_EMAIL_OPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, email_option)],
            ASK_EMAIL_MANUAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_manual_email)],
            ASK_OTP: [CommandHandler("next", get_otp), MessageHandler(filters.TEXT & ~filters.COMMAND, handle_manual_otp)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    print("Bot running...")
    app.run_polling()
