import logging
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ConversationHandler, filters
from telegram.error import TimedOut

# تنظیمات لاگ برای مشاهده خطاها و اطلاعات اجرایی
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# توکن ربات شما
TOKEN = '7620461717:AAHcimMwIkeeeMt-mDTXYpHqx31coTrcqlQ'

# حالت‌های مکالمه
CHOOSING, TO_CELSIUS, TO_FAHRENHEIT = range(3)

# تبدیل سلسیوس به فارنهایت
def celsius_to_fahrenheit(celsius):
    return (celsius * 9/5) + 32

# تبدیل فارنهایت به سلسیوس
def fahrenheit_to_celsius(fahrenheit):
    return (fahrenheit - 32) * 5/9

# منوی اصلی با دکمه‌های شیشه‌ای
async def start(update: Update, context) -> None:
    keyboard = [
        [
            InlineKeyboardButton("تبدیل به سلسیوس", callback_data='to_celsius'),
            InlineKeyboardButton("تبدیل به فارنهایت", callback_data='to_fahrenheit'),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        'سلام! به ربات تبدیل دما خوش آمدید.\n'
        'یک گزینه را انتخاب کنید:',
        reply_markup=reply_markup
    )

# هندلر برای دکمه‌های شیشه‌ای
async def button(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()

    # بررسی نوع دکمه انتخاب شده
    if query.data == 'to_celsius':
        await query.edit_message_text(text="لطفاً دمای فارنهایت را وارد کنید:")
        return TO_CELSIUS
    elif query.data == 'to_fahrenheit':
        await query.edit_message_text(text="لطفاً دمای سلسیوس را وارد کنید:")
        return TO_FAHRENHEIT

# دریافت عدد برای تبدیل به سلسیوس
async def to_celsius(update: Update, context) -> int:
    try:
        fahrenheit = float(update.message.text)
        celsius = fahrenheit_to_celsius(fahrenheit)
        await update.message.reply_text(f'{fahrenheit} درجه فارنهایت برابر است با {celsius:.2f} درجه سلسیوس.')

        await ask_another_action(update)  # سؤال برای انجام عمل دیگر

    except ValueError:
        await update.message.reply_text('لطفاً یک عدد معتبر وارد کنید.')
        return TO_CELSIUS
    return ConversationHandler.END

# دریافت عدد برای تبدیل به فارنهایت
async def to_fahrenheit(update: Update, context) -> int:
    try:
        celsius = float(update.message.text)
        fahrenheit = celsius_to_fahrenheit(celsius)
        await update.message.reply_text(f'{celsius} درجه سلسیوس برابر است با {fahrenheit:.2f} درجه فارنهایت.')

        await ask_another_action(update)  # سؤال برای انجام عمل دیگر

    except ValueError:
        await update.message.reply_text('لطفاً یک عدد معتبر وارد کنید.')
        return TO_FAHRENHEIT
    return ConversationHandler.END

# سؤال برای انجام عمل دیگر
async def ask_another_action(update: Update) -> None:
    keyboard = [
        [
            InlineKeyboardButton("بله", callback_data='yes'),
            InlineKeyboardButton("خیر", callback_data='no'),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    message = await update.message.reply_text(
        'آیا می‌خواهید عمل دیگری انجام دهید؟',
        reply_markup=reply_markup
    )

    return message  # ذخیره پیام برای ویرایش

# هندلر برای پاسخ به سؤال انجام عمل دیگر
async def another_action(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'yes':
        # ناپدید کردن پیام و نمایش مجدد منوی اصلی
        await query.edit_message_text(text="لطفاً گزینه خود را انتخاب کنید:")
        await start(query, context)  # بازگشت به منوی اصلی برای انتخاب عمل جدید
    elif query.data == 'no':
        await query.edit_message_text(text="خیلی ممنون که از ربات استفاده کردید!")

# تابعی برای مدیریت خطاها و جلوگیری از کرش کردن برنامه
async def error_handler(update: Update, context):
    logging.warning(f'Update {update} caused error: {context.error}')
    if isinstance(context.error, TimedOut):
        logging.warning('TimedOut error occurred.')

# تنظیمات و ساخت ربات
if __name__ == '__main__':
    try:
        app = ApplicationBuilder().token(TOKEN).build()

        # هندلر برای دستور /start
        app.add_handler(CommandHandler("start", start))

        # هندلر برای کلیک دکمه‌های شیشه‌ای
        app.add_handler(CallbackQueryHandler(button, pattern='^(to_celsius|to_fahrenheit)$'))

        # هندلر برای پاسخ به سؤال انجام عمل دیگر
        app.add_handler(CallbackQueryHandler(another_action, pattern='^(yes|no)$'))

        # تنظیم مکالمه
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, to_celsius))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, to_fahrenheit))

        # اضافه کردن error_handler برای مدیریت خطاها
        app.add_error_handler(error_handler)

        # شروع به کار ربات و مدیریت خطاها
        logging.info("ربات در حال اجرا است...")
        app.run_polling()

    except TimedOut:
        logging.error("ارتباط با تلگرام قطع شد. تلاش مجدد...")