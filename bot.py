from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

class Bot():

    def __init__(self, TOKEN: str) -> None:
        self.TOKEN = TOKEN
        self.bot = ApplicationBuilder().token(TOKEN).build()
        # Добавление обработчиков при инициализации
        self.register_handlers()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        with open('Hello.txt', 'r') as file:
            welcome_message = file.read()
        await update.message.reply_text(welcome_message)

        return ConversationHandler.END
    
    async def command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        with open('Hello.txt', 'r') as file:
            a = file.readlines()
        for line in a[2:]:
            print(line)

        commands = "".join(a[2:])
        await update.message.reply_text(commands)
    
    async def distance_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            distance = float(update.message.text)
            
            if distance <=0:
                await update.message.reply_text(('Пожалуйста, введите корректное расстояние.'
                                                 'Оно не может быть отрицательным или равняться нулю.'))
                return self.DISTANCE
            
            context.user_data['distance'] = distance
            if context.user_data['state'] == 'count_consumption':
                await update.message.reply_text('Введите количество потраченного бензина в литрах, например, 10.5:')
                return self.GASOLINE
            
            elif context.user_data['state'] == 'count_money':
                await update.message.reply_text('Введите расход бензина в литрах на 100 км:')
                return self.CONSUMPTION
        
        except Exception as e:
            await update.message.reply_text(('Пожалуйста, введите корректное значение.' 
            'Это должно выть число в километрах, например "99.4" (без кавычек), означает, что вы проехали 99.4 километра.'
            'Десятичная часть должна быть отделена точкой.'))
            return self.DISTANCE
        
    async def gasoline_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            gasoline = float(update.message.text)
            if gasoline <= 0:
                await update.message.reply_text(('Пожалуйста, введите корректное значение. Оно не может быть отрицательным'
                                                 ' или равняться нулю.'))
                return self.GASOLINE
            context.user_data['gasoline'] = gasoline
            await update.message.reply_text((f"Вы проехали {context.user_data['distance']} км и "
            f"потратили {context.user_data['gasoline']} литров бензина.\nРасход бензина вашего автомобиля"
            f" равен {round(100*context.user_data['gasoline']/context.user_data['distance'] , 2)} литров/100 км."
            f"\nЧтобы вернуться к списку команд, нажмите /command.\nПриятного дня!"))
        except Exception as e:
            await update.message.reply_text(('Пожалуйста, введите корректное значение. '
            'Это должно выть число в литрах, например "12.2" (без кавычек), означает, что вы проехали 12.2 километра. '
            'Десятичная часть должна быть отделена точкой.'))
            return self.GASOLINE
        
        return ConversationHandler.END
    
    async def gasoline_cost_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        pass
        try:
            cost = float(update.message.text)
            if cost <= 0:
                await update.message.reply_text(('Пожалуйста, введите корректное значение. '
                                                'Оно не может быть отрицательным или равняться нулю.'))
                return self.COST
            context.user_data['cost'] = cost
            await update.message.reply_text((f"Вы проехали {context.user_data['distance']} км с расходом бензина "
            f"{context.user_data['consumption']} л/100км. Стоимость поездки равна"
            f" {round(cost*context.user_data['distance']*context.user_data['consumption']/100, 1)} рублей.\n"
            f"Чтобы вернуться к списку команд, нажмите /command.\n"
            f"Приятного дня!"))
        except Exception as e:
            await update.message.reply_text(('Пожалуйста, введите корректное значение. Это должно быть число в рублях,'
            ' например "40.0" (без кавычек), означает, что литр бензина стоит 40.0 рублей. Десятичная часть должна быть'
            ' отделена точкой.'))
            return self.COST
        
        return ConversationHandler.END


    async def consumption_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            consumption = float(update.message.text)
            
            if consumption <=0:
                await update.message.reply_text(('Пожалуйста, введите корректный расход бензина. Он не может быть отрицательным'
                                                ' или равняться нулю.'))
                return self.CONSUMPTION
            
            context.user_data['consumption'] = consumption
            await update.message.reply_text('Введите стоимость бензина за литр, например, 40.0:')
            return self.COST
        
        except Exception as e:
            await update.message.reply_text(('Пожалуйста, введите корректное значение. количество потраченного бензина в литрах,'
            ' например, "10.5": (без кавычек), означает, что вы автомобиль расходует 10.5 литров на 100 км пути. '
            'Десятичная часть должна быть отделена точкой.'))
            return self.CONSUMPTION
    
    async def count_consumption(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
       context.user_data['state'] = 'count_consumption'
       await update.message.reply_text('Введите расстояние, которое вы проехали, в километрах, например 100.5:')
       return self.DISTANCE
    
    async def count_money(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
       
       context.user_data['state'] = 'count_money'
       await update.message.reply_text(('Введите расстояние, которое вы проехали/собираетесь проехать, в километрах, например'
                                       ' 100.5:'))
       return self.DISTANCE
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Операция отменена.")
        return ConversationHandler.END

    DISTANCE, GASOLINE, COST, CONSUMPTION = range(4)
    
    
    def register_handlers(self):
        
        conv_handler_1 = ConversationHandler(
        entry_points=[CommandHandler('consumption', self.count_consumption)],
        states={
            self.DISTANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.distance_input)],
            self.GASOLINE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.gasoline_input)],
        },
        fallbacks=[CommandHandler("cancel", self.cancel)]
        )

        conv_handler_2 = ConversationHandler(
        entry_points=[CommandHandler('money', self.count_money)],
        states={
            self.DISTANCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.distance_input)],
            self.CONSUMPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.consumption_input)],
            self.COST: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.gasoline_cost_input)],
        },
        fallbacks=[CommandHandler("cancel", self.cancel)]
        )

        self.bot.add_handler(CommandHandler('start', self.start))
        self.bot.add_handler(CommandHandler('command', self.command))
        self.bot.add_handler(conv_handler_1)
        self.bot.add_handler(conv_handler_2)

    def run(self):
        self.bot.run_polling()
