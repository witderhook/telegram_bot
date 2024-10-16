#импортируем библиотеку, а также все нужные данные из других файлов
from giphyUtils import get_random_gif, get_gif_by_name

if __name__ == '__main__':
    import telebot
    import threading
    from telebot import types

    from datetime import datetime
    from tg_bot.Constants import *
    from tg_bot.DataBaseUtils import *
    from tg_bot.Scheduler import *

    # Инициализируем бота
    bot = telebot.TeleBot(TOKEN)


    # Создаём отдельный поток для планировщика(функция рассылки гифок)
    thread_scheduler = threading.Thread(target=send_random_gif_at_18_00, args=(bot,))
    # Запускаем поток
    thread_scheduler.start()

    # --------------------------------------------------------
    # Handler-ы для обработки команд
    # --------------------------------------------------------

    #start - начало работы бота
    @bot.message_handler(commands=['start'])
    def start_handler(message):
        """Обработчик команды start"""
        # resize_keyboard, чтобы клавиатура сама подстраивалась под размеры
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=2, resize_keyboard=True)

        btn_help = types.KeyboardButton('/help')

        markup.add(btn_help)
        bot.send_message(message.from_user.id, f"Привет,{message.from_user.first_name}! Это чат поддержка компании.", reply_markup=markup)

    #help - получение инструкции по
    # пользованию бота (а также создание кнопок для бота)
    @bot.message_handler(commands=['help'])
    def help_handler(message):
        """Обработчик команды help"""
        # - row_width: integer (default 3)
        # row_width is used in combination with the add() function.
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=False, row_width=2, resize_keyboard=True)
        btn_hello = types.KeyboardButton('Привет')
        btn_reg = types.KeyboardButton('/registration')
        btn_info = types.KeyboardButton('/info')
        btn_comp = types.KeyboardButton('/complain')
        btn_random_gif = types.KeyboardButton('Случайная гифка')  # !!!!!!!!

        markup.row(btn_hello, btn_comp)
        markup.row(btn_reg, btn_info)
        markup.row(btn_random_gif)  # !!!!!!!!
        # reply_markup - возвращает разметку пользователю, которую мы создали
        bot.send_message(message.from_user.id, HELP, reply_markup=markup)

    #registration - регистрация в боте, здесь заносятся имя,
    # фамилия и email пользоваателя в файл clients_ifo
    @bot.message_handler(commands=['registration'])
    def registration_handler(message):
        """Обработчик команды registration"""
        if check_client_in_db(message.from_user.id):
            bot.send_message(message.from_user.id, "Вы уже зарегистрированы")
        else:
            bot.send_message(message.from_user.id, "Введите ваше имя:")
            bot.register_next_step_handler(message, name)


    #info - получить информацию о компании для дальнейшей связи(идёт ответом на сообщение)
    @bot.message_handler(commands=['info'])
    def send_company_info(message):
        company_info = "Сайт нашей компании: cOoL_CoMpAnY.ru\nНомер телефона: +79123322245"
        bot.reply_to(message, company_info)

    #subscription - сменить статус подписки (на рассылку гифок)
    @bot.message_handler(commands=['subscription'])
    def subscription_handler(message):
        """Обработчик команды subscription"""
        status = change_subscription_by_id(message.from_user.id)
        bot.send_message(message.from_user.id, f"Ваш статус подписки был изменён на: {status}")

    #find_gif - найти и отправить гифку по запросу
    @bot.message_handler(commands=['find_gif'])
    def find_gif_handler(message):
        """Обработчик команды find_gif"""
        bot.send_message(message.from_user.id, "Введите слово или словосочетание для поиска")
        bot.register_next_step_handler(message, get_find_name)


    # complain - пожаловаться на работу компании
    # (вся информация заносится в документ complaints)
    complain_next = False

    @bot.message_handler(commands=['complain'])
    def start_complain(message):
        global complain_next
        complain_next = True
        bot.reply_to(message, "Введите вашу жалобу:")


    @bot.message_handler(func=lambda message: complain_next)
    def handle_complaint(message):
        try:
            with open("complaints.txt", "a") as file:
                file.write(f"{message.chat.id}: {message.text}\n")
            bot.reply_to(message, "Жалоба успешно зарегистрирована.")
        except Exception as e:
            print(f"Ошибка при обработке жалобы: {e}")
        finally:
            global complain_next
            complain_next = False

    # --------------------------------------------------------
    # Handler-ы для обработки документов
    # --------------------------------------------------------

    #на вход бот получает документ в фрмате .txt,
    # на выходе отправляет пользователю данные документа сообщением
    @bot.message_handler(content_types=['document'])
    def documents_handler(message):
        """Обработчик текстовых документов"""
        print(f"Получен документ от {message.from_user.first_name}")
        if message.document.file_name[-3:] == "txt":
            # Получаем ссылку на файл
            file_info = bot.get_file(message.document.file_id)
            # Скачиваем файл в виде байтов
            downloaded_file = bot.download_file(file_info.file_path)
            # Для того чтобы отобразить в виде строки
            # Байты конвертируем в строку
            data_from_txt = downloaded_file.decode("utf-8")
            bot.send_message(message.from_user.id, f"Данные с документа {message.document.file_name}: \n'{data_from_txt}'")
        elif message.document.file_name[-2:] == "py":
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            data_from_txt = downloaded_file.decode("utf-8")
            bot.send_message(message.from_user.id, f"Данные с документа {message.document.file_name}: \n'{data_from_txt}'")
        else:
            bot.send_message(message.from_user.id, f"Данные с документа {message.document.file_name} получить невозможно")


    # --------------------------------------------------------
    # Handler-ы для обработки изображений
    # --------------------------------------------------------

    # Обработчик любых изображений
    # на вход бот получает любое количество изображений от пользователя,
    # на выходе отправляет последнее
    @bot.message_handler(content_types=['photo'])
    def photos_handler(message):
        """Обработчик изображений"""
        # Чтобы посмотреть тип и увидеть, что list
        print(type(message.photo))
        # Может быть несколько фото в отправлении, поэтому будем обрабатывать только последнее
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        # Отправляем теперь не текстовое сообщение, а изображение
        bot.send_photo(message.from_user.id, downloaded_file)




    # --------------------------------------------------------
    # Handler-ы для обработки любых текстовых сообщений
    # --------------------------------------------------------


    @bot.message_handler(content_types=['text'])
    def text_handler(message):
        """Обработчик текстовых сообщений"""
        text = message.text.lower()
        if text == "как дела?":
            bot.send_message(message.from_user.id, "Да потихоньку вот, а у вас?")
        elif text == "привет":
            bot.send_message(message.from_user.id, "Добрый день! Чем могу быть полезен?")
        elif text == "сколько времени?":
            now = datetime.now()
            current_time = now.strftime("%H:%M")
            bot.send_message(message.from_user.id, current_time)
        elif text == "случайная гифка":
            link = get_random_gif()
            bot.send_animation(message.from_user.id, link)
        else:
            bot.send_message(message.from_user.id, "Очень жаль, ничем не могу помочь. Попробуйте ввести другой запрос :(")

    # 3 функции для реализации регистрации пользователя
    def name(message):
        """Обработчик имени пользователя"""
        global client
        client = {"id": message.from_user.id, "name": message.text}
        bot.send_message(message.chat.id, "Введите вашу фамилию:")
        bot.register_next_step_handler(message, surname)


    def surname(message):
        """Обработчик фамилии пользователя"""
        client["surname"] = message.text
        bot.send_message(message.from_user.id, "Введите вашу почту:")
        bot.register_next_step_handler(message, email)


    def email(message):
        """Обработчик email пользователя"""
        client["email"] = message.text
        save_client_info(client)
        bot.send_message(message.from_user.id, f"Спасибо, мы сохранили ваши данные.\n {str(client)}")


    #функция для реалиизации поиска гифок
    def get_find_name(message):
        """Обработчик поиска для гифки"""
        bot.send_message(message.from_user.id, f"Вот ваша гифка:")
        link = get_gif_by_name(message.text)
        bot.send_animation(message.from_user.id, link)






    # Зацикливаем бота, чтобы он обрабатывал все запросы
    bot.polling(none_stop=True, interval=0)


