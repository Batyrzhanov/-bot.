from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Этапы диалога для ConversationHandler
MAIN_MENU, CATEGORY_SELECTION, CREATE_TEAM, JOIN_TEAM = range(4)

# Категории для выбора
CATEGORIES = ["Спорт", "Хобби", "Хакатоны", "Образование", "Путешествия", "Волонтерство"]

# Словарь для хранения команд по категориям
teams = {
    "Спорт": [],
    "Хобби": [],
    "Хакатоны": [],
    "Образование": [],
    "Путешествия": [],
    "Волонтерство": [],
}

# Словарь для хранения информации о создателе команды
team_creators = {
    "Спорт": [],
    "Хобби": [],
    "Хакатоны": [],
    "Образование": [],
    "Путешествия": [],
    "Волонтерство": [],
}

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [["Создать команду", "Найти команду"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("Что вы хотите сделать?", reply_markup=reply_markup)
    return MAIN_MENU

# Обработчик выбора команды (Создать или Найти)
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    choice = update.message.text

    if choice == "Создать команду":
        reply_markup = ReplyKeyboardMarkup([CATEGORIES, ["Назад"]], resize_keyboard=True)
        context.user_data["action"] = "create"
        await update.message.reply_text("Выберите категорию для вашей новой команды:", reply_markup=reply_markup)
        return CATEGORY_SELECTION

    elif choice == "Найти команду":
        reply_markup = ReplyKeyboardMarkup([CATEGORIES, ["Назад"]], resize_keyboard=True)
        context.user_data["action"] = "join"
        await update.message.reply_text("Выберите категорию команды, которую хотите найти:", reply_markup=reply_markup)
        return CATEGORY_SELECTION

    else:
        await update.message.reply_text("Пожалуйста, выберите один из вариантов.")
        return MAIN_MENU

# Обработчик выбора категории
async def category_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    category = update.message.text

    if category == "Назад":
        return await start(update, context)  # Вернуться в главное меню

    if category not in CATEGORIES:
        await update.message.reply_text("Пожалуйста, выберите действительную категорию.")
        return CATEGORY_SELECTION

    # Если пользователь создаёт команду
    if context.user_data.get("action") == "create":
        await update.message.reply_text(f"Отлично! Вы создаете команду в категории '{category}'. Введите название команды:")
        context.user_data["category"] = category  # Сохраняем категорию
        return CREATE_TEAM

    # Если пользователь ищет команду
    else:
        if teams[category]:
            available_teams = "\n".join(
                f"• {team} (Создатель: {creator})" for team, creator in zip(teams[category], team_creators[category])
            )
            await update.message.reply_text(
                f"Ищем команды в категории '{category}'. Вот несколько доступных команд:\n{available_teams}\n\n"
                "Введите название команды, чтобы присоединиться."
            )
        else:
            await update.message.reply_text(f"Нет доступных команд в категории '{category}'.")
        return JOIN_TEAM

# Обработчик создания команды
async def create_team(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    team_name = update.message.text
    category = context.user_data["category"]
    creator_name = update.message.from_user.username or update.message.from_user.first_name  # Имя создателя
    teams[category].append(team_name)  # Сохраняем команду в соответствующей категории
    team_creators[category].append(creator_name)  # Сохраняем имя создателя
    await update.message.reply_text(f"Команда '{team_name}' успешно создана! Вы можете пригласить участников.")
    return await start(update, context)  # Вернуться в главное меню

# Обработчик присоединения к команде
async def join_team(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    team_name = update.message.text
    await update.message.reply_text(f"Вы успешно присоединились к команде '{team_name}'!")
    return await start(update, context)  # Вернуться в главное меню

# Команда /cancel для завершения разговора
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Диалог завершён. Возвращайтесь, когда будете готовы!")
    return ConversationHandler.END

# Основная функция для запуска бота
if __name__ == '__main__':
    app = ApplicationBuilder().token('7119487720:AAGVcs1YIdxeOACwdXwl1re5bXWA0wSVJ4Q').build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            CATEGORY_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, category_selection)],
            CREATE_TEAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, create_team)],
            JOIN_TEAM: [MessageHandler(filters.TEXT & ~filters.COMMAND, join_team)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)

    print("Бот запущен...")
    app.run_polling()
