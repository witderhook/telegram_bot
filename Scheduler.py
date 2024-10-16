from DataBaseUtils import get_subscribes_id_list
import schedule
import time

from tg_bot.giphyUtils import get_random_gif

#рассылка случайной гифки в 18:00
def send_random_gif_at_18_00(bot):
    """Планировщик для отправки сообщений по времени"""
    def send_gif():
        """Функция для отправки сообщения"""

        for client_id in get_subscribes_id_list():
            bot.send_animation(client_id, get_random_gif())

    # schedule.every(10).seconds.do(send_gif)
    schedule.every().day.at("18:00").do(send_gif)

    while True:
        schedule.run_pending()
        time.sleep(1)
