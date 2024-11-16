from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from capitalize import capitalize_city_name
import pandas as pd
import logging

class Bot():

    def __init__(self, TOKEN: str, log_file :str ='bot.log') -> None:
        self.TOKEN = TOKEN
        self.bot = ApplicationBuilder().token(TOKEN).build()
        self.table = pd.read_csv('Russia_cities.csv', sep = ',')
        # Создание логгера
        self.logger_exp = logging.getLogger(self.__class__.__name__)
        self.logger_exp.setLevel(logging.INFO)
        # Создание обработчика для записи логов в файл
        file_handler = logging.FileHandler(log_file, mode='a')
        file_handler.setLevel(logging.INFO)
        # Формат лог-сообщение
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        # Добавление обработчика логов
        self.logger_exp.addHandler(file_handler)

        # Добавление обработчиков бота при инициализации
        self.register_handlers()

    def normalize_city_name(self, city_name):
        return city_name.lower().replace('ё', 'е')

    def in_conversation(state:str):
        def decorator(func):
            async def wrapper(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
                if state == 'conversation_handler':
                    if context.user_data.get('in_conv', False):
                        await update.message.reply_text('Пожалуйста, завершите предыдущее вычисление. Введите данные, которые запросил бот')
                        return ConversationHandler.END
                    else: 
                        context.user_data['in_conv'] = True
                        return await func(self, update, context)
                elif state == 'command':
                    result = await func(self, update, context)
                    if result == ConversationHandler.END:
                        context.user_data['in_conv'] = False
                    return result

            return wrapper

        return decorator
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):

        with open('Hello.txt', 'r') as file:
            welcome_message = file.read()
        await update.message.reply_text(welcome_message)

        self.logger_exp.info(f'Пользователь {update.effective_user} начал использовать бот.')

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

    @in_conversation(state='command')   
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
            self.logger_exp.info(f"Пользователь {update.effective_user} успешно воспользовался командой /consumption.")
        except Exception as e:
            await update.message.reply_text(('Пожалуйста, введите корректное значение. '
            'Это должно выть число в литрах, например "12.2" (без кавычек), означает, что вы проехали 12.2 километра. '
            'Десятичная часть должна быть отделена точкой.'))
            return self.GASOLINE
        
        return ConversationHandler.END
    
    @in_conversation(state='command')
    async def gasoline_cost_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        
        message = update.message.text

        try:
            if str(message).strip().lower() == 'дохуя':
                await update.message.reply_text(('Димас, помни, что Небесный Отец посылает испытания, чтобы укрепить нас'
                ' и помочь нам стать лучше. Все зависит от того, как мы будем принимать их. С этого момента у тебя всё'
                ' будет получаться и твоё будущее будет светлым. Вводи стоимость бензина:'))
                self.logger_exp.info(f"Пользователь {update.effective_user} успешно нашёл пасхалку.")
                return self.COST
        except Exception:
            pass

        try:
            cost = float(message)
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
            self.logger_exp.info(f"Пользователь {update.effective_user} успешно воспользовался командой /money.")
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
    
    @in_conversation(state='conversation_handler')
    async def count_consumption(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
       context.user_data['state'] = 'count_consumption'
       await update.message.reply_text('Введите расстояние, которое вы проехали, в километрах, например 100.5:')
       return self.DISTANCE
    
    @in_conversation(state='conversation_handler')
    async def count_money(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
       
       context.user_data['state'] = 'count_money'
       await update.message.reply_text(('Введите расстояние, которое вы проехали/собираетесь проехать, в километрах, например'
                                       ' 100.5:'))
       return self.DISTANCE
    
    @in_conversation(state='command')
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.message.reply_text("Операция отменена.")
        return ConversationHandler.END
    
    @in_conversation(state='conversation_handler')
    async def distance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(('В нашей базе 196 крупных российских городов.'
        ' К сожалению, это далеко не все российские города, поэтому вашего в ней может не оказаться.'))
        await update.message.reply_text("Введите город отправления:")
        return self.DEPARTURE

    @in_conversation(state='command')
    async def departure_city(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            dep_city = str(update.message.text)
            if self.normalize_city_name(dep_city) in self.table.city.values:
                context.user_data['dep_city'] = self.normalize_city_name(dep_city)
                await update.message.reply_text("Введите город прибытия:")
                return self.ARRIVAL
            else:
                await update.message.reply_text("К сожалению, такой город не найден.")
                self.logger_exp.info(f"Пользователь {update.effective_user} не нашёл город отправления {dep_city}.")
                await self.command(update, context)
                return ConversationHandler.END
        except Exception as e:
            await update.message.reply_text("Пожалуйста, введите корректное значение.")
            return self.DEPARTURE

    @in_conversation(state='command')
    async def arrival_city(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            arr_city = str(update.message.text)
            if self.normalize_city_name(arr_city) in self.table.city.values:
                context.user_data['arr_city'] = self.normalize_city_name(arr_city)
                dist = self.table[self.table.city == context.user_data['dep_city']][context.user_data['arr_city']].iloc[0]
                await update.message.reply_text((f"Расстояние между городами {capitalize_city_name(context.user_data['dep_city'])}"
                f" и {capitalize_city_name(context.user_data['arr_city'])} равно {dist} км."))
                self.logger_exp.info((f"Пользователь {update.effective_user} запросил расстояние между городами "
                                  f"{context.user_data['dep_city'].capitalize()}"
                                  f" и {context.user_data['arr_city'].capitalize()}."))
                return ConversationHandler.END
            else:
                await update.message.reply_text("К сожалению, такой город не найден.")
                self.logger_exp.info(f"Пользователь {update.effective_user} не нашёл город прибытия {arr_city}.")
                await self.command(update, context)
                return ConversationHandler.END
        except Exception as e:
            await update.message.reply_text('Пожалуйста, введите корректное значение.')
            return self.ARRIVAL

    async def user_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        message = update.message.text
        self.logger_exp.info(f"Пользователь {update.effective_user} отправил боту сообщение {message}")
        await update.message.reply_text((f'{update.effective_user.first_name}, к сожалению, я пока не могу поддержать разговор.'
                                         f' Для вывода поддерживаемых команд нажмите /command.'))

    DISTANCE, GASOLINE, COST, CONSUMPTION, DEPARTURE, ARRIVAL = range(6)

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

        conv_handler_3 = ConversationHandler(
        entry_points=[CommandHandler('distance', self.distance)],
        states={
            self.DEPARTURE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.departure_city)],
            self.ARRIVAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.arrival_city)],
        },
        fallbacks=[CommandHandler("cancel", self.cancel)]
        )

        self.bot.add_handler(conv_handler_1)
        self.bot.add_handler(conv_handler_2)
        self.bot.add_handler(conv_handler_3)
        self.bot.add_handler(CommandHandler('start', self.start))
        self.bot.add_handler(CommandHandler('command', self.command))
        self.bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.user_message))


    def run(self):
        self.bot.run_polling()
