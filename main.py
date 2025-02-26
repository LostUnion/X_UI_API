#################################################################
# █████████████████████████████████████████████████████████████ #
# █░░░░░░░░██░░░░░░░░████████████████░░░░░░██░░░░░░█░░░░░░░░░░█ #
# █░░▄▀▄▀░░██░░▄▀▄▀░░████████████████░░▄▀░░██░░▄▀░░█░░▄▀▄▀▄▀░░█ #
# █░░░░▄▀░░██░░▄▀░░░░████████████████░░▄▀░░██░░▄▀░░█░░░░▄▀░░░░█ #
# ███░░▄▀▄▀░░▄▀▄▀░░██████████████████░░▄▀░░██░░▄▀░░███░░▄▀░░███ #
# ███░░░░▄▀▄▀▄▀░░░░███░░░░░░░░░░░░░░█░░▄▀░░██░░▄▀░░███░░▄▀░░███ #
# █████░░▄▀▄▀▄▀░░█████░░▄▀▄▀▄▀▄▀▄▀░░█░░▄▀░░██░░▄▀░░███░░▄▀░░███ #
# ███░░░░▄▀▄▀▄▀░░░░███░░░░░░░░░░░░░░█░░▄▀░░██░░▄▀░░███░░▄▀░░███ #
# ███░░▄▀▄▀░░▄▀▄▀░░██████████████████░░▄▀░░██░░▄▀░░███░░▄▀░░███ #
# █░░░░▄▀░░██░░▄▀░░░░████████████████░░▄▀░░░░░░▄▀░░█░░░░▄▀░░░░█ #
# █░░▄▀▄▀░░██░░▄▀▄▀░░████████████████░░▄▀▄▀▄▀▄▀▄▀░░█░░▄▀▄▀▄▀░░█ #
# █░░░░░░░░██░░░░░░░░████████████████░░░░░░░░░░░░░░█░░░░░░░░░░█ #
# █████████████████████████████████████████████████████████████ #
# ------------------------------------------------------------- #
# ----------------------ПОДКЛЮЧЕНИЕ К X-UI--------------------- #
# conn = X_UI(                                                  #
#     x_ui_login="YOUR LOGIN",                                  #
#     x_ui_password="YOUR PASSWORD",                            #
#     x_ui_link="YOUR X-UI LINK"                                #
# )                                                             #
# conn.session_up()                                             #
# При ответе 200, сессия считается запущенной.                  #
# -------------------------УПРАВЛЕНИЕ-------------------------- #
# Получение информации о системе:                               #
# conn.get_system_status()                                      #
#                                                               #
# Получение всех подключений и пользователей.                   #
# conn.get_all_list()                                           #
#                                                               #
# Получение всех подключений и пользователей.                   #
# conn.get_all_list()                                           #
#                                                               #
# Остановка xray. / Работает если отключен перезапуск.          #
# conn.xray_stop()                                              #
#                                                               #
# Перезапуск xray.                                              #
# conn.xray_restart()                                           #
#                                                               #
# Запуск xray.                                                  #
# conn.xray_start()                                             #
#                                                               #
# Добавление пользователя.                                      #
# conn.add_client(                                              #
#       connection_id: int,               ID подключения        #
#       flow: str,                        Режим                 #
#       email: str,                       Почта или название    #
#       limit_ip: int,                    Лимит по IP           #
#       totalGB: float,                   Лимит по GB           #
#       expirtyTime: int,                 Количество дней       #
#       enable: bool,                     Включен или нет       #
#       tgId: int,                        ID Telegram           #
#       comment: str                      Комментарий           #
#     )                                                         #
# Получение ссылки vless                                        #
# conn.get_vless_link(user_id: str)      ID клиента             #
#################################################################

import os
import uuid
import time
import json
from datetime import datetime
from abc import ABC
import urllib.parse
from pathlib import Path

import urllib3
import requests
from requests.exceptions import RequestException
from dotenv import load_dotenv

from logger_settings import logger as log

# Отключение предупреждения о
# самоподписном сертефикате.
urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

# Загрузка переменных окружения
# из файла .env в os.environ.
load_dotenv()

vless_host = str(os.getenv('VLESS_HOST'))
vless_port = str(os.getenv('VLESS_PORT'))

class API_CLIENT(ABC):
    def __init__(self):
        self.session = requests.Session()

class X_UI(API_CLIENT):
    def __init__(self,
                 x_ui_login: str,
                 x_ui_password: str,
                 x_ui_link: str):
        
        super().__init__()
        self.x_ui_login = x_ui_login
        self.x_ui_password = x_ui_password
        self.x_ui_link = x_ui_link

    # Поднятие сессии и запись
    # cookies после авторизации.
    def session_up(self):
        log.info(
            f"Connecting to \"{self.x_ui_link}\""
        )

        try:
            # Авторизация в панели x-ui.
            res = self.session.post(
                url=f"{self.x_ui_link}/login",
                json={
                    "username": self.x_ui_login,
                    "password": self.x_ui_password
                },
                # Пропуск проверки
                # самоподписного сертификата.
                verify=False
            )

            # Проверка успешного
            # ответа от сервера.
            if res.status_code == 200:
                
                # Преобразование бинарного
                # ответа от сервера в JSON
                # формат.
                j_cont = json.loads(res.content)

                # Формирование сообщения
                # для вывода пользователю
                # и записи в лог.
                suc = f"SUCCESS: {j_cont['success']}"
                msg = f"MESSAGE: {j_cont['msg']}"

                # Сепаратор для визуального разграничения.
                sep = '-' * (len(str(suc)) + len(str(msg)))

                # Проверка что в success
                # от сервера True.
                if j_cont['success']:
                    log.info(
                        'Authorization was successful\n'
                        f'{sep}\n{suc}\n{msg}\n{sep}'
                    )

                    # Сбор cookies данных из
                    # сессии, после авторизации.
                    cookies = [
                        {
                            "domain": k.domain,
                            "name": k.name,
                            "path": k.path,
                            "value": k.value
                        }
                        for k in self.session.cookies
                    ]

                    # Установка данных cookies в сессию
                    # для последующего использования.
                    for cookie in cookies:
                        self.session.cookies.set(**cookie)

                    # Информационное сообщение
                    # после установки cookies.
                    log.info(
                        f"[{res.status_code}] - "
                        "Cookies have been installed"
                    )

                    return True
                
                else:
                    # Информационное сообщение
                    # если success было False.
                    log.error(
                        'Authorization failed\n'
                        f'{sep}\n{suc}\n{msg}\n{sep}'
                    )

                    return False
                
            else:
                # Информационное сообщение
                # если res.status_code != 200.
                log.error(
                    f'Status code [{res.status_code}]'
                    )

                return False
            
        except RequestException as err:
            # Вывод места и самой
            # ошибки в лог.
            log.error(
                "An error has occurred in "
                "the X_UI/session_up progr"
                f"am block: {err}"
            )

            return False

    # Скачивание бекапов подключений.
    def export_conf_backups(self):
        log.info(
            "Getting a backup of "
            "user configuration data"
        )

        try:
            # Запрос на получение
            # конфигурационных данных пользователей.
            res = self.session.get(
                url=f"{self.x_ui_link}/server/getDb",
                # Пропуск проверки
                # самоподписного сертификата.
                verify=False,
                # Позволяет загружать ответ
                # по частям, уменьшая нагрузку
                # на память.
                stream=True
            )

            # Проверка успешного
            # ответа от сервера.
            if res.status_code == 200:

                # Проверка что от сервера пришел какой-либо текст.
                if res.content:

                    # Именование бэкап файла,
                    # в названии дата и время.
                    date = datetime.now()
                    date_now = date.strftime('%Y-%m-%d-%H-%M-%S')

                    folder_backups = Path(os.getenv('BACKUPS_PATH'))

                    if not folder_backups.is_dir():
                        folder_backups.mkdir(parents=True, exist_ok=True)

                    file_path = folder_backups / f"{date_now}_backup.db"

                    # Запись данных бэкапа в файл
                    with open(file_path, "w") as file:
                        # chunk_size задает размер
                        # части данных (8192 байта),
                        # загружаемой за один раз из
                        # ответа.
                        for chunk in res.iter_content(chunk_size=8192):
                            file.write(chunk)

                        log.info(
                            f"[{res.status_code}] - "
                            "The backup data was "
                            "successfully written "
                            f"to the  \"{file_path}\"file"
                        )

                        return True

                else:
                    # Информирование пользователя
                    # что запрос пришел со статусом 200,
                    # но ничего не вернул в ответе.
                    log.error(
                        f"[{res.status_code}]"
                        " - The request was successful, "
                        "but the server returned nothing."
                    )
                    return False
            else:
                # Информирование пользователя
                # что произошла ошибка при
                # скачивании бэкапа.
                log.error(
                    f"[{res.status_code}]"
                    " - Failed to download backup"
                )

                return False

        except RequestException as err:
            # Вывод места и самой
            # ошибки в лог.
            log.error(
                "An error has occurred in the "
                "X_UI/export_conf_backups prog"
                f"ram block: {err}"
            )

            return False

    # Формирование таблицы для
    # вывода пользователю.
    def table_collection(self, data):
        try:
            # Подсчет максимальной длинны метрик.
            max_len_metric = max(len(str(item[0])) for item in data)

            # Подсчет максимальной длинны значений.
            max_len_value = max(len(str(item[1])) for item in data)

            # Вывод тайтлов.
            log.info(
                f"+{'-' * (max_len_metric + 2)}"
                f"+{'-' * (max_len_value + 2)}+"
            )

            log.info(
                f"| {'Metric'.ljust(max_len_metric)} |"
                f" {'Value'.ljust(max_len_value)} |"
            )

            log.info(
                f"+{'-' * (max_len_metric + 2)}"
                f"+{'-' * (max_len_value + 2)}+"
            )

            # Перебор и вывод значений.
            for metric, value in data:
                log.info(
                    f"| {metric.ljust(max_len_metric)} |"
                    f" {str(value).ljust(max_len_value)} |"
            )

            # Конечная сепарация.
            log.info(
                f"+{'-' * (max_len_metric + 2)}"
                f"+{'-' * (max_len_value + 2)}+"
            )

            return True

        except Exception as err:
            log.error(
                "An error has occurred in the "
                "X_UI/table_collection prog"
                f"ram block: {err}"
            )

    # Получение статистики всей системы.
    def get_system_status(self):
        log.info(
            "Getting statistics on the system"
        )

        try:
            # Запрос на получение
            # всех данных по системе x-ui.
            res = self.session.post(
                url=f"{self.x_ui_link}/server/status",
                # Пропуск проверки
                # самоподписного сертификата.
                verify=False,
                # Позволяет загружать ответ
                # по частям, уменьшая нагрузку
                # на память.
                stream=True
            )

            # Проверка успешного
            # ответа от сервера.
            if res.status_code == 200:

                # Преобразование бинарного
                # ответа от сервера в JSON
                # формат.
                j_cont = json.loads(res.content)

                # Формирование сообщения
                # для вывода пользователю
                # и записи в лог.
                suc = f"SUCCESS: {j_cont['success']}"
                msg = f"MESSAGE: {j_cont['msg']}"

                # Сепаратор для визуального разграничения.
                sep = '-' * (len(str(suc)) + len(str(msg)))

                # Проверка что в success
                # от сервера True.
                if j_cont['success']:

                    obj_data = j_cont['obj']

                    # Данные по процессору ##########################

                    # Идентификатор процессора,
                    # который может быть 0 для
                    # основного ядра.
                    cpu_id = obj_data['cpu']

                    # Количество физических
                    # ядер процессора.
                    cpu_core = obj_data['cpuCores']

                    # Количество логических
                    # процессоров.
                    cpu_logic = obj_data['logicalPro']

                    # Частота процессора в
                    # мегагерцах.
                    cpu_speed_Mhz = obj_data['cpuSpeedMhz']

                    # Средняя нагрузка на
                    # процессор за последние
                    # 1, 5 и 15 минут.
                    cpu_leeds = obj_data['loads']                          

                    # Данные по оперативной памяти ##################

                    # Текущая используемая память.
                    ram_curr = obj_data['mem']['current']

                    # Общая памятью.
                    ram_total = obj_data['mem']['total']                  

                    # Данные по подкачке ############################

                    # Текущее использование подкачки
                    swap_curr = obj_data['swap']['current']

                    # Общая память подкачки
                    swap_total = obj_data['swap']['total']

                    # Данные по диску ###############################

                    # Текущая используемая дисковая память
                    disk_curr = obj_data['disk']['current']

                    # Общая дисковая память
                    disk_total = obj_data['disk']['total']

                    # Состояние xray ################################

                    # Статус xray
                    xray_status = obj_data['xray']['state']

                    # Сообщения об ошибках
                    xray_errMsg = obj_data['xray']['errorMsg']

                    # Версия xray
                    xray_version = obj_data['xray']['version']

                    # Время работы xray системы в секундах
                    uptime = obj_data['uptime']

                    # Сетевые соединения ############################

                    # Количество TCP-соединений
                    tcp_count = obj_data['tcpCount']

                    # Количество UDP-соединений
                    udp_count = obj_data['udpCount']
                    
                    # Сетевой трафик ################################

                    # Отправлено байт в данный момент
                    netIO_up = obj_data['netIO']['up']

                    # Получено байт в данный момент
                    netIO_down = obj_data['netIO']['down']

                    # Отправлено байт за все время
                    netTraffic_sent = obj_data['netTraffic']['sent']

                    # Получено байт за все время
                    netTraffic_recv = obj_data['netTraffic']['recv']

                    # Публичный IP ##################################

                    # Публичный IP-адрес IPv4
                    publicIP_ipv4 = obj_data['publicIP']['ipv4']

                    # Публичный IP-адрес IPv6
                    publicIP_ipv6 = obj_data['publicIP']['ipv6']

                    # Статистика приложения ##########################

                    # Статистика по использованию потоков в приложении
                    app_stats_threads = obj_data['appStats']['threads']

                    # Статистика по использованию памяти в приложении
                    app_stats_mem = obj_data['appStats']['mem']

                    # Общее время работы приложения
                    app_stats_uptime = obj_data['appStats']['uptime']

                    data = [
                        ["CPU - CPU ID", cpu_id],
                        ["CPU - Cores", cpu_core],
                        ["CPU - Logical Procs", cpu_logic],
                        ["CPU - Speed (MHz)", cpu_speed_Mhz],
                        ["CPU - Load (1, 5, 15 min)",
                        ', '.join(map(str, cpu_leeds))],

                        ["RAM - Current", ram_curr],
                        ["RAM - Total", ram_total],

                        ["SWAP - Current", swap_curr],
                        ["SWAP - Total", swap_total],

                        ["DISK - Current", disk_curr],
                        ["DISK - Total", disk_total],

                        ["XRAY - Status", xray_status],
                        ["XRAY - Error Message", xray_errMsg],
                        ["XRAY - Version", xray_version],

                        ["UPTIME - Uptime (seconds)", uptime],

                        ["TCP COUNT - TCP", tcp_count],
                        ["UDP COUNT - UDP", udp_count],

                        ["TRAFFIC - Sent (current)", netIO_up],
                        ["TRAFFIC - Received (current)", netIO_down],
                        ["TRAFFIC - Sent (total)", netTraffic_sent],
                        ["TRAFFIC - Received (total)", netTraffic_recv],

                        ["IP - IPv4", publicIP_ipv4],
                        ["IP - IPv6", publicIP_ipv6],

                        ["APP STATISTIC - Threads", app_stats_threads],
                        ["APP STATISTIC - Memory", app_stats_mem],
                        ["APP STATISTIC - Uptime", app_stats_uptime]
                    ]

                    # Проверка что переданные
                    # данные сформировались в
                    # таблицу.
                    if self.table_collection(data):
                        log.info(
                            "The system statistics data "
                            "was recorded in the .log file."
                        )

                        return True

                    # Если данные не были
                    # сформированы, ошибка.
                    else:
                        log.error(
                            "An error occurred when displaying"
                            "a table with system statistics."
                        )

                        return False

                else:
                    # Информационное сообщение
                    # если success было False.
                    log.error(
                        'Collecting table failed\n'
                        f'{sep}\n{suc}\n{msg}\n{sep}'
                    )

                    return False

            else:
                # Информирование пользователя
                # что произошла ошибка при
                # получении статистики x-ui.
                log.error(
                    f"[{res.status_code}]"
                    " - Error when getting "
                    "statistics"
                )

                return False

        except RequestException as err:
            # Вывод места и самой
            # ошибки в лог.
            log.error(
                "An error has occurred in the "
                "X_UI/get_system_status prog"
                f"ram block: {err}"
            )

            return False

    # Получение данных о всех
    # подключениях и пользователях.
    def get_all_list(self):
        log.info(
            "Getting a list of connections"
        )

        try:
            # Запрос на получение
            # всех данных по подключениям
            # и пользователям.
            res = self.session.post(
                url=f"{self.x_ui_link}/panel/inbound/list",
                # Пропуск проверки
                # самоподписного сертификата.
                verify=False,
                # Позволяет загружать ответ
                # по частям, уменьшая нагрузку
                # на память.
                stream=True
            )

            # Проверка успешного
            # ответа от сервера.
            if res.status_code == 200:

                # Преобразование бинарного
                # ответа от сервера в JSON
                # формат.
                j_cont = json.loads(res.content)

                # Формирование сообщения
                # для вывода пользователю
                # и записи в лог.
                suc = f"SUCCESS: {j_cont['success']}"
                msg = f"MESSAGE: {j_cont['msg']}"

                # Сепаратор для визуального разграничения.
                sep = '-' * (
                    len(str(suc)) + len(str(msg))
                )

                # Проверка что в success
                # от сервера True.
                if j_cont['success']:

                    obj_data = j_cont['obj']

                    # Перебор всех значений из obj.
                    for iter_obj in obj_data:
                        # Сбор всех данных
                        # по подключениям.
                        try:
                            # Данные по подключению ##########################
                            conn_id = iter_obj['id']

                            # ID подключения.
                            conn_id = iter_obj['id']

                            # Наименование подключения.
                            conn_remark = iter_obj['remark']

                            # Проверка на то,
                            # запущено ли подключение.
                            conn_enable = iter_obj['enable']

                            # Порт подключения.
                            conn_port = iter_obj['port']

                            # Протокол подключения.
                            conn_protocol = iter_obj['protocol']

                            conn_up = iter_obj['up']
                            conn_down = iter_obj['down']

                            # Подсчет количества
                            # пользователей на
                            # данном подключении.
                            clientStats = len(
                                [cli for cli in iter_obj['clientStats']]
                            )

                            # Создание пары ключа и
                            # значения для формирования
                            # таблицы для вывода пользователю.
                            data_conn = [
                                ["Connection ID", conn_id],
                                ["Name", conn_remark],
                                ["Enable", conn_enable],
                                ["Port", conn_port],
                                ["Protocol", conn_protocol],
                                ["Up", conn_up],
                                ["Down", conn_down],
                                ["clientStats", clientStats]
                            ]

                            # Проверка что переданные
                            # данные сформировались в
                            # таблицу.
                            if self.table_collection(data_conn) == False:
                                log.error(
                                    "The data_conn data was "
                                    "not generated in the table"
                                )

                            else:
                                pass

                        except Exception as err:
                           log.error(
                           "An error occurred in the "
                           "X_UI/get_all_list block "
                           "iterating over values from obj."
                           f"Error: {err}"
                           )

                        
                        # Сбор всех данных
                        # по пользователям.
                        try:
                            # Преобразование бинарного
                            # ответа от сервера в JSON
                            # формат.

                            # Из obj берется settings.
                            # sett_data = iter_obj['settings']
                            sett_data = json.loads(iter_obj['settings'])

                            # Сбор клиентов на подключении.
                            clients = sett_data['clients']

                            # Информационный вывод пользователю
                            # что сейчас будут выведены все
                            # пользователи.
                            log.info(
                                    "Getting all users"
                                )
                            
                            # Перебор всех клиентов
                            # которые присутствуют
                            # в settings.
                            for client in clients:

                                # Уникальный UUID клиента.
                                user_id = client['id']

                                # Какой режим используется.
                                user_flow = client['flow']

                                # Email пользователя.
                                user_email = client['email']

                                # Лимит по IP.
                                user_limit_ip = client['limitIp']

                                # Какие ограничения по трафику.
                                user_totalGB = client['totalGB']

                                # Время истечения срока действия (0 бесконечный).
                                user_expiryTime = client['expiryTime']

                                # ID пользователя в телеграм.
                                user_tgId = client['tgId']

                                # Вспомогательный ID пользователя.
                                user_subId = client['subId']

                                # Комментарий.
                                user_comment = client['comment']    

                                # Сколько раз сбрасывались настройки пользователя
                                user_reset = client['reset']

                                # Создание пары ключа и
                                # значения для формирования
                                # таблицы для вывода пользователю.
                                user_data = [
                                    ["User ID", user_id],
                                    ["Flow", user_flow],
                                    ["Email", user_email],
                                    ["Limit IP", user_limit_ip],
                                    ["Total GB", user_totalGB],
                                    ["Expiry Time", user_expiryTime],
                                    ["TG ID", user_tgId],
                                    ["Sub ID", user_subId],
                                    ["Comment", user_comment],
                                    ["Reset", user_reset],
                                ]

                                # Проверка что переданные
                                # данные сформировались в
                                # таблицу.
                                if self.table_collection(user_data) == False:
                                    log.error(
                                        "The user_data data was "
                                        "not generated in the table"
                                    )

                                else:
                                    pass

                        except Exception as err:
                            log.error(
                                "An error occurred in the "
                                "X_UI/get_all_list block "
                                "iterating over values from "
                                "clients."
                                f"Error: {err}"
                            )

                        # Информационный вывод пользователю
                        # что сейчас будут выведены все
                        # значения из realitySettings.
                        log.info(
                            "Getting reality settings"
                        )

                        # Сбор всех данных
                        # по streamSettings.
                        try:

                            # Из obj берется streamSettings.
                            sSett_data = json.loads(
                                iter_obj['streamSettings']
                            )

                            # Из streamSettings
                            # берется realitySettings.
                            realSet = sSett_data['realitySettings']

                            show = realSet['show']

                            xver = realSet['xver']

                            # Место назначения
                            dest = realSet['dest']

                            # Под какой сервис
                            # происходит маскировка.
                            serverNames = realSet['serverNames'][0]
                            
                            # Приватный ключ
                            # подключения.
                            privateKey = realSet['privateKey']
                            
                            # Минимально допустимое
                            # количество клиентов на
                            # подключении.
                            minClient = realSet['minClient']
                            
                            # Максимально допустимое
                            # количество клиентов на
                            # подключении.
                            maxClient = realSet['maxClient']
                            
                            # Максимальный временной
                            # интервал.
                            maxTimediff = realSet['maxTimediff']

                            # Короткие идентификаторы.
                            shortIds = realSet['shortIds']
                            
                            # Публичный ключ
                            # подключения.
                            settings_publicKey = realSet['settings']['publicKey']

                            # Отпечаток подключения.
                            settings_fingerprint = realSet['settings']['fingerprint']

                            # Имя сервера.
                            settings_serverName = realSet['settings']['serverName']

                            settings_spiderX = realSet['settings']['spiderX']
                            

                            realSet_data = [
                                ["Show", show],
                                ["Xver", xver],
                                ["Dest", dest],
                                ["Servers Name", serverNames],
                                ["Private Key", privateKey],
                                ["Public Key", settings_publicKey],
                                ["Min Client", minClient],
                                ["Max Client", maxClient],
                                ["Max Timediff", maxTimediff],
                                ["Short Ids", shortIds[0]],
                                ["Finger Print", settings_fingerprint],
                                ["Server Name", settings_serverName],
                                ["Spider X", settings_spiderX]
                            ]

                            # Проверка что переданные
                            # данные сформировались в
                            # таблицу.
                            if self.table_collection(realSet_data) == False:
                                log.error(
                                    "The realSet_data data was "
                                    "not generated in the table"
                                )
                            
                            else:
                                pass

                        except Exception as err:
                            log.error(
                                "An error occurred in the "
                                "X_UI/get_all_list block "
                                "iterating over values from "
                                "realSet_data."
                                f"Error: {err}"
                            )
                else:
                    log.error(
                        "An error occurred while "
                        "receiving the list\n"
                        f"{sep}\n{suc}\n{msg}\n{sep}"
                    )

                    return False
            else:
                log.error(
                    f"[{res.status_code}] An error "
                    "occurred when accessing the "
                    "server"
                )
                
                return False
        except RequestException as err:
            log.error(
                "An error has occurred in the "
                "X_UI/get_all_list"
                f"program block: {err}"
            )

    # Проверка активности xray
    def xray_parse_active(self):
        log.info(
            "Getting xray status"
        )

        try:
            # Запрос на получение
            # всех данных по системе x-ui.
            res = self.session.post(
                url=f"{self.x_ui_link}/server/status",
                # Пропуск проверки
                # самоподписного сертификата.
                verify=False,
                # Позволяет загружать ответ
                # по частям, уменьшая нагрузку
                # на память.
                stream=True
            )

            # Проверка успешного
            # ответа от сервера.
            if res.status_code == 200:

                # Преобразование бинарного
                # ответа от сервера в JSON
                # формат.
                j_cont = json.loads(res.content)

                # Проверка что в success
                # от сервера True.
                if j_cont['success']:

                    obj_data = j_cont['obj']

                    # Статус xray
                    xray_status = obj_data['xray']['state']

                    if xray_status == "running":
                        return True
                    else:
                        return False
                             
            else:      
                log.error(
                    f"[{res.status_code}] An error "
                    "occurred when accessing the "
                    "server"
                )
                
                return False


        except RequestException as err:
            # Вывод места и самой
            # ошибки в лог.
            log.error(
                "An error has occurred in the "
                "X_UI/xray_parse_active prog"
                f"ram block: {err}"
            )

            return False

    # Проверка результата xray
    def xray_result(self):
        log.info(
            "Getting result xray services"
        )

        try:
            # Запрос на получение
            # результата xray после
            # перезагрузки или выключения.
            res = self.session.get(
                url=f"{self.x_ui_link}/panel/xray/getXrayResult",
                # Пропуск проверки
                # самоподписного сертификата.
                verify=False,
                # Позволяет загружать ответ
                # по частям, уменьшая нагрузку
                # на память.
                stream=True
            )

            # Проверка успешного
            # ответа от сервера.
            if res.status_code == 200:

                # Преобразование бинарного
                # ответа от сервера в JSON
                # формат.
                j_cont = json.loads(res.content)

                # Проверка что в success
                # от сервера True.
                if j_cont['success']:
                    return True
                else:
                    return False
                
            else:
                log.error(
                    f"[{res.status_code}] An error "
                    "occurred when accessing the "
                    "server"
                )
                
                return False

        except RequestException as err:
            log.error(
                "An error has occurred in the "
                "X_UI/xray_result"
                f"program block: {err}"
            )

    # Остановка сервиса xray.
    # Если на сервере установлена
    # настройка xray с автоматическим
    # перезапуском, верется True
    # и выведется ошибка, поскольку xray
    # автоматически перезапустится.
    def xray_stop(self):
        log.info(
            "Stoping xray services"
        )

        try:
            # Запрос на полную остановку xray.
            res = self.session.post(
                url=f"{self.x_ui_link}/server/stopXrayService",
                # Пропуск проверки
                # самоподписного сертификата.
                verify=False,
                # Позволяет загружать ответ
                # по частям, уменьшая нагрузку
                # на память.
                stream=True
            )

            # Проверка успешного
            # ответа от сервера.
            if res.status_code == 200:

                # Преобразование бинарного
                # ответа от сервера в JSON
                # формат.
                j_cont = json.loads(res.content)

                # Формирование сообщения
                # для вывода пользователю
                # и записи в лог.
                suc = f"SUCCESS: {j_cont['success']}"
                msg = f"MESSAGE: {j_cont['msg']}"

                # Сепаратор для визуального разграничения.
                sep = '-' * (
                    len(str(suc)) + len(str(msg))
                )

                # Проверка что в success
                # от сервера True.
                if j_cont['success']:
                    
                    # Проверка что в success
                    # от сервера xray True.
                    if self.xray_result():
                        for _ in range(10):
                            time.sleep(2)
                            # Проверка активности xray
                            # после его остановки для
                            # определения автоматического
                            # перезапуска.
                            xray_active = self.xray_parse_active()
                            if xray_active:
                                break
                            

                        # Проверка что вернулось True. 
                        if xray_active:

                            # Информационный
                            # вывод об ошибке.
                            log.error(
                                    "Xray not stoped\n"
                                    "A request was sent "
                                    "to stop the xray service, "
                                    "but the service restarted "
                                    "instead."
                                )

                            return False

                        # Ожидается возврат False.
                        else:
                            log.info(
                                "Xray stoped\n"
                                f"{sep}\n{suc}\n{msg}\n{sep}"
                            )

                            return True
                        
                    else:
                        log.error(
                            "xray_result returned False. "
                            "Something went wrong."
                        )

                        return False

                else:
                    log.error(
                        "The xray service has not been stopped\n"
                        f"{sep}\n{suc}\n{msg}\n{sep}"
                    )

                    return False
                
            else:
                log.error(
                    f"[{res.status_code}] An error "
                    "occurred when accessing the "
                    "server"
                )
                
                return False
                
        except RequestException as err:
            log.error(
                "An error has occurred in the "
                "X_UI/xray_stop"
                f"program block: {err}"
            )

    # Перезапуск сервиса xray.
    def xray_restart(self):
        log.info(
            "Restart xray services"
        )

        try:
            # Запрос на перезагрузку xray.
            res = self.session.post(
                url=f"{self.x_ui_link}/server/restartXrayService",
                # Пропуск проверки
                # самоподписного сертификата.
                verify=False,
                # Позволяет загружать ответ
                # по частям, уменьшая нагрузку
                # на память.
                stream=True
            )

            # Проверка успешного
            # ответа от сервера.
            if res.status_code == 200:

                # Преобразование бинарного
                # ответа от сервера в JSON
                # формат.
                j_cont = json.loads(res.content)

                # Формирование сообщения
                # для вывода пользователю
                # и записи в лог.
                suc = f"SUCCESS: {j_cont['success']}"
                msg = f"MESSAGE: {j_cont['msg']}"

                # Сепаратор для визуального разграничения.
                sep = '-' * (
                    len(str(suc)) + len(str(msg))
                )

                # Проверка что в success
                # от сервера True.
                if j_cont['success']:

                    # Проверка что в success
                    # от сервера xray True.
                    if self.xray_result():
                        log.info(
                            "The xray service has been restarted\n"
                            f"{sep}\n{suc}\n{msg}\n{sep}"
                        )

                        return True
                    
                    else:
                        log.error(
                            "xray_result returned False. "
                            "Something went wrong."
                        )

                        return False

                else:
                    log.error(
                        "The xray service has not been restarted\n"
                        f"{sep}\n{suc}\n{msg}\n{sep}"
                    )

                    return False
                
            else:
                log.error(
                    f"[{res.status_code}] An error "
                    "occurred when accessing the "
                    "server"
                )
                
                return False
                
        except RequestException as err:
            log.error(
                "An error has occurred in the "
                "X_UI/xray_restart"
                f"program block: {err}"
            )

    def xray_start(self):
        pass
    
    # Создание нового клиента
    # на существующем подключении.
    def add_client(self,
                   connection_id: int = 4,
                   flow: str = "xtls-rprx-vision",
                   email: str = None,
                   limit_ip: int = 0,
                   totalGB: float = 0,
                   expirtyTime: int = 0,
                   enable: bool = True,
                   tgId: int = 0,
                   comment: str = "new_user"):
        log.info(
            "Adding a new user"
        )

        # Проверка что expirtyTime
        # содержит какое-либо значение
        # больше 0, далее переводит дни
        # в секунды, иначе делает клиента
        # бессрочным.
        if expirtyTime != 0:
            rental_period = -int(expirtyTime) * 24 * 60 * 60 * 1000
        else:
            rental_period = 0

        # Регистрация uuid
        # для нового клиента.
        user_UUID = str(uuid.uuid1())

        try:
            payload = {
                # id подключения, в котором
                # необходимо создать пользователя,
                # default 0.
                "id": connection_id,
                "settings": json.dumps({
                    "clients": [{
                        # id клиента всегда разный и
                        # генерируется с помощью uuid.
                        "id": user_UUID,
                        # flow - поток через который
                        # будет проходить трафик клиента,
                        # default xtls-rprx-vision.
                        "flow": flow,
                        # email может использоваться как
                        # название клиента, по дефолту стоит
                        # uuid клиента.
                        "email": email if email else user_UUID,
                        # limitIp ограничивает количество
                        # подключений по одному клиенту,
                        # default 0.
                        "limitIp": limit_ip,
                        # totalGB ограничивает количество
                        # GB и после исчерпывания, трафик
                        # перестанет идти, default 0.
                        "totalGB": totalGB,
                        # expiryTime - время в днях,
                        # сколько будет актуален клиент,
                        # default 0.
                        "expiryTime": rental_period,
                        # enable - включен или выключен клиент,
                        # default True.
                        "enable": enable,
                        # tgId - id клиента в telegram,
                        # default 0.
                        "tgId": str(tgId) if tgId else "",
                        # subId - дополнительный id клиента,
                        # default 0.
                        "subId": "",
                        # comment - комментарий для клиента,
                        # по дефолту стоит uuid клиента.
                        "comment": comment if comment else user_UUID,
                        # reset - сброс клиента,
                        # default 0.
                        "reset": 0
                    }]
                })
            }

            # Запрос на добавление пользователя.
            res = self.session.post(
                url=f"{self.x_ui_link}/panel/inbound/addClient",
                # Полезная нагрузка в виде json.
                json=payload,
                # Пропуск проверки
                # самоподписного сертификата.
                verify=False,
                # Позволяет загружать ответ
                # по частям, уменьшая нагрузку
                # на память.
                stream=True
            )

            # Проверка успешного
            # ответа от сервера.
            if res.status_code == 200:

                # Преобразование бинарного
                # ответа от сервера в JSON
                # формат.
                j_cont = json.loads(res.content)

                # Формирование сообщения
                # для вывода пользователю
                # и записи в лог.
                suc = f"SUCCESS: {j_cont['success']}"
                msg = f"MESSAGE: {j_cont['msg']}"

                # Сепаратор для визуального разграничения.
                sep = '-' * (
                    len(str(suc)) + len(str(msg))
                )

                # Проверка что в success
                # от сервера True.
                if j_cont['success']:
                    log.info(
                        "New user has been added\n"
                        f"{sep}\n{suc}\n{msg}\n{sep}"
                    )

                    return True
                
                else:
                    log.error(
                        "New user has been not added\n"
                        f"{sep}\n{suc}\n{msg}\n{sep}"
                    )

                    return False
                
            else:
                log.error(
                    f"[{res.status_code}] An error "
                    "occurred when accessing the "
                    "server"
                )
                
                return False

        except RequestException as err:
            log.error(
                "An error has occurred in the "
                "X_UI/add_client"
                f"program block: {err}"
            )

    # Получение vless
    # конфигурации в виде
    # ссылки.
    def get_vless_link(self, user_id: str, config_json: bool = False):
        log.info(
            "Getting the vless "
            "configuration as a link"
        )

        try:
            # Запрос на получение
            # конфигурации vless.
            res = self.session.post(
                url=f"{self.x_ui_link}/panel/inbound/list",
                # Пропуск проверки
                # самоподписного сертификата.
                verify=False,
                # Позволяет загружать ответ
                # по частям, уменьшая нагрузку
                # на память.
                stream=True
            )

            # Проверка успешного
            # ответа от сервера.
            if res.status_code == 200:

                # Преобразование бинарного
                # ответа от сервера в JSON
                # формат.
                j_cont = json.loads(res.content)

                # Формирование сообщения
                # для вывода пользователю
                # и записи в лог.
                suc = f"SUCCESS: {j_cont['success']}"
                msg = f"MESSAGE: {j_cont['msg']}"

                # Сепаратор для визуального разграничения.
                sep = '-' * (
                    len(str(suc)) + len(str(msg))
                )

                # Проверка что в success
                # от сервера True.
                if j_cont['success']:

                    obj_data = j_cont['obj']

                    # Перебор всех значений из obj.
                    for iter_obj in obj_data:
                        # Сбор всех данных
                        # по пользователям.
                        try:
                            # Из obj берется settings.
                            # sett_data = iter_obj['settings']
                            sett_data = json.loads(iter_obj['settings'])

                            # Сбор клиентов на подключении.
                            clients = sett_data['clients']
                            # Перебор всех клиентов
                            # которые присутствуют
                            # в settings.
                            for client in clients:

                                if client['id'] == user_id:

                                    # Уникальный UUID клиента.
                                    user_id = client['id']

                                    # Какой режим используется.
                                    user_flow = client['flow']
                                
                                    # Email пользователя.
                                    user_email = client['email']
                                    user_email = urllib.parse.quote(user_email, safe='')

                                    # Из obj берется streamSettings.
                                    sSett_data = json.loads(
                                        iter_obj['streamSettings']
                                    )

                                    # Из streamSettings
                                    # берется realitySettings.
                                    realSet = sSett_data['realitySettings']

                                    # Под какой сервис
                                    # происходит маскировка.
                                    serverName = realSet['serverNames'][0]

                                    # Короткие идентификаторы.
                                    shortIds = realSet['shortIds'][0]

                                    # Публичный ключ
                                    # подключения.
                                    settings_publicKey = realSet['settings']['publicKey']

                                    # Отпечаток подключения.
                                    settings_fingerprint = realSet['settings']['fingerprint']

                                    settings_spx = realSet['settings']['spiderX']

                                    # Название подключения
                                    # (примечание).
                                    connection_remark = j_cont['obj'][0]['remark']

                                    # Замена пустого значения
                                    # и специальных символов.
                                    connection_remark = urllib.parse.quote(connection_remark, safe='')

                                    # Формирование vless ссылки
                                    # без названия подключения.

                                    type_ = "tcp"
                                    security = "reality"
                                    form_settings_spx = urllib.parse.quote(settings_spx, safe='')

                                    if connection_remark != "":
                                        vless_link = (
                                            f"vless://{user_id}@{os.getenv('VLESS_HOST')}:"
                                            f"{os.getenv('VLESS_PORT')}?type={type_}&security="
                                            f"{security}&pkb={settings_publicKey}"
                                            f"&fp={settings_fingerprint}&sni={serverName}"
                                            f"&sid={shortIds[0]}&spx={form_settings_spx}&flow={user_flow}"
                                            f"#{connection_remark}-{user_email}"
                                        )
                                    
                                    # Формирование vless ссылки
                                    # с названием подключения.
                                    else:
                                        vless_link = (
                                            f"vless://{user_id}@{os.getenv('VLESS_HOST')}:"
                                            f"{os.getenv('VLESS_PORT')}?type={type_}&security="
                                            f"{security}&pbk={settings_publicKey}"
                                            f"&fp={settings_fingerprint}&sni={serverName}"
                                            f"&sid={shortIds}&spx={form_settings_spx}&flow={user_flow}"
                                            f"#{user_email}"
                                        )

                                    vless_link = vless_link.replace(" ", "%20")

                                    log.info(
                                        f"USER ID {user_id} | VLESS LINK\n\n"
                                        f"{vless_link}"
                                    )

                                    # Проверка что
                                    # config_json True.
                                    if config_json:

                                        # Формирование JSON
                                        # объекта.
                                        config = {
                                            "inbounds": [
                                                {
                                                    "port": 10808,
                                                    "listen": "127.0.0.1",
                                                    "protocol": "socks",
                                                    "settings": {"udp": True}
                                                }
                                            ],
                                            "outbounds": [
                                                {
                                                    "protocol": "vless",
                                                    "settings": {
                                                        "vnext": [
                                                            {
                                                                "address": str(os.getenv('VLESS_HOST')),
                                                                "port": int(os.getenv('VLESS_PORT')),
                                                                "users": [
                                                                    {
                                                                        "id": str(user_id),
                                                                        "encryption": "none",
                                                                        "flow": str(user_flow)
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    },
                                                    "streamSettings": {
                                                        "network": str(type_),
                                                        "security": str(security),
                                                        "realitySettings": {
                                                            "publicKey": str(settings_publicKey),
                                                            "shortId": str(shortIds),
                                                            "fingerprint": str(settings_fingerprint),
                                                            "serverName": str(serverName),
                                                            "spiderX": settings_spx
                                                        } if security == "reality" else None
                                                    }
                                                }
                                            ]
                                        }

                                        config["outbounds"][0]["streamSettings"] = {k: v for k, v in config["outbounds"][0]["streamSettings"].items() if v}
                                        
                                        folder_json_config = Path(os.getenv('USER_JSON_CONFIGS_PATH'))

                                        # Проверка наличия папки
                                        # для хранения конфигураций
                                        # пользователей.
                                        if not folder_json_config.is_dir():
                                            folder_json_config.mkdir(parents=True, exist_ok=True)
                                            log.info(
                                                f"Folder {folder_json_config} has been created"
                                            )

                                        file_path = folder_json_config / f"{user_id}_config.json"

                                        # Запись в файл.
                                        with open(file_path, 'w') as file:
                                            json.dump(config, file, indent=4)

                                    return True
       
                        except Exception as err:
                            log.error(
                                "An error occurred in the "
                                "X_UI/get_all_list block "
                                "iterating over values from "
                                "clients. "
                                f"Error: {err}"
                            )
                else:
                    log.error(
                        "An error occurred while "
                        "receiving the list\n"
                        f"{sep}\n{suc}\n{msg}\n{sep}"
                    )

                    return False
                        
        except Exception as err:
            log.error(
                "An error occurred in the "
                "X_UI/get_vless_link block "
                "iterating over values from "
                "realSet_data. "
                f"Error: {err}"
            )
