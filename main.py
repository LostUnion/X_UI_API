import os
import uuid
import json
from datetime import datetime
from abc import ABC, abstractmethod

import urllib3
import requests
from dotenv import load_dotenv

from logger_settings import logger
from json_loads import loads_json_to_file


# Отключение предупреждения о
# самоподписном сертефикате
urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

# Загрузка переменных окружения
# из файла .env в os.environ.
load_dotenv()

x_ui_link = str(os.getenv('AUTH_LINK'))
x_ui_login = str(os.getenv('AUTH_LOGIN'))
x_ui_password = str(os.getenv('AUTH_PASSWORD'))

class API_CLIENT(ABC):
    def __init__(self):
        self.session = requests.Session()

    @abstractmethod
    def session_up():
        pass

class X_UI(API_CLIENT):
    def __init__(self):
        super().__init__()

    # Поднятие сессии и запись cookies
    # после авторизации.
    def session_up(self):
        logger.info(
            f"Connecting to \"{x_ui_link}\""
        )

        try:
            # Запрос по адресу x_ui_link+login.
            response = self.session.post(
                url=f"{x_ui_link}/login",
                json={
                    "username": x_ui_login,
                    "password": x_ui_password
                },
                verify=False
            )

            # Проверка что от сервера поступил 200.
            if response.status_code == 200:
                res_cont = json.loads(response.content)

                success = f"SUCCESS: {res_cont['success']}"
                message = f"MESSAGE: {res_cont['msg']}"
                sep = "-" * (len(str(success)) + len(str(message)))

                # Проверка что в success от сервера True.
                if res_cont['success']:
                    logger.info(
                        f"Authorization was successful\n"
                        f"{sep}\n"
                        f"{success}\n{message}\n"
                        f"{sep}"
                    )

                    # Сбор cookies данных с авторизованной сессии.
                    cookies = [
                        {
                            "domain": key.domain,
                            "name": key.name,
                            "path": key.path,
                            "value": key.value
                        }
                        for key in self.session.cookies
                    ]

                    # Установка данных cookies в сессию
                    # для последующего использования.
                    for cookie in cookies:
                        self.session.cookies.set(**cookie)

                    logger.info(
                        f"[{response.status_code}] - "
                        "Cookies have been installed"
                    )

                    return True
                
                else:
                    logger.info(
                        f"Authorization failed\n"
                        f"{sep}\n"
                        f"{success}\n{message}\n"
                        f"{sep}"
                    )

                    return False

        except requests.exceptions.RequestException as err:
            logger.error(
                "An error has occurred in the "
                "X_UI/session_up prog"
                f"ram block: {err}"
            )

            return False

    # Скачивание бекапов подключений.
    def export_conf_backups(self):
        logger.info(
            "Getting a backup of user "
            "configuration data"
        )

        try:
            # Запрос по адресу x_ui_link+/server/getDb.
            response = self.session.get(
                url=f"{x_ui_link}/server/getDb",
                verify=False,
                stream=True
            )

            # Проверка что от сервера поступил 200.
            if response.status_code == 200:

                # Проверка что от сервера пришел какой-либо текст.
                if response.text:
                    back_file_name = (
                        f"config_backups/{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}_backup.db"
                    )

                    # Запись данных бэкапа в файл
                    with open(back_file_name, "wb") as file:
                        for chunk in response.iter_content(chunk_size=8192):
                            file.write(chunk)

                    logger.info(
                        f"[{response.status_code}] - "
                        "The backup data was successfully "
                        f"written to the  \"{back_file_name}\""
                        " file"
                    )

                    return True
                
                else:
                    logger.error(
                        f"[{response.status_code}]"
                        " - The request was successful, "
                        "but the server returned nothing."
                    )
                    return False

            else:
                logger.error(
                    f"[{response.status_code}]"
                    " - Failed to download backup"
                )

                return False

        except requests.exceptions.RequestException as err:
            logger.error(
                "An error has occurred in the "
                "X_UI/export_conf_backups prog"
                f"ram block: {err}"
            )
            return False

    # Формирование таблицы для.
    def print_table(self, data):
        try:
            max_len_metric = max(len(str(item[0])) for item in data)
            max_len_value = max(len(str(item[1])) for item in data)

            logger.info(f"+{'-' * (max_len_metric + 2)}+{'-' * (max_len_value + 2)}+")
            logger.info(f"| {'Metric'.ljust(max_len_metric)} | {'Value'.ljust(max_len_value)} |")
            logger.info(f"+{'-' * (max_len_metric + 2)}+{'-' * (max_len_value + 2)}+")

            for metric, value in data:
                logger.info(f"| {metric.ljust(max_len_metric)} | {str(value).ljust(max_len_value)} |")

            logger.info(f"+{'-' * (max_len_metric + 2)}+{'-' * (max_len_value + 2)}+")

            return True
        except Exception as err:
            logger.error(
                "An error has occurred in the "
                "X_UI/print_table prog"
                f"ram block: {err}"
            )

    # Получение статистики всей системы.
    def get_system_status(self):
        logger.info(
            "Getting statistics on the system"
        )

        try:
            # Запрос по адресу x_ui_link+/server/status.
            response = self.session.post(
                url=f"{x_ui_link}/server/status",
                verify=False,
                stream=True
            )

            # Проверка что от сервера поступил 200.
            if response.status_code == 200:
                res_cont = json.loads(response.content)

                # Проверка что в success от сервера True.
                if res_cont['success']:

                    # Данные по процессору
                    state_cpu = res_cont['obj']['cpu']                                  # Идентификатор процессора, который может быть 0 для основного ядра
                    state_cpu_core = res_cont['obj']['cpuCores']                        # Количество физических ядер процессора
                    state_cpu_logic = res_cont['obj']['logicalPro']                     # Количество логических процессоров
                    state_cpu_speed_Mhz = res_cont['obj']['cpuSpeedMhz']                # Частота процессора в мегагерцах
                    state_cpu_leeds = res_cont['obj']['loads']                          # Средняя нагрузка на процессор за последние 1, 5 и 15 минут

                    # Данные по оперативке
                    state_ram_curr = res_cont['obj']['mem']['current']                  # Текущая используемая память
                    state_ram_total = res_cont['obj']['mem']['total']                   # Общая память

                    # Данные по подкачке
                    state_swap_curr = res_cont['obj']['swap']['current']                # Текущее использование подкачки   
                    state_swap_total = res_cont['obj']['swap']['total']                 # Общая память подкачки

                    # Данные по диску
                    state_disk_curr = res_cont['obj']['disk']['current']                # Текущая используемая дисковая память
                    state_disk_total = res_cont['obj']['disk']['total']                 # Общая дисковая память

                    # Состояние xray
                    state_xray_status = res_cont['obj']['xray']['state']                # Статус xray
                    state_xray_errMsg = res_cont['obj']['xray']['errorMsg']             # Сообщения об ошибках
                    state_xray_version = res_cont['obj']['xray']['version']             # Версия xray

                    # Время работы xray
                    state_uptime = res_cont['obj']['uptime']                            # Время работы системы в секундах

                    # Сетевые соединения
                    state_tcp_count = res_cont['obj']['tcpCount']                       # Количество TCP-соединений
                    state_udp_count = res_cont['obj']['udpCount']                       # Количество UDP-соединений

                    # Сетевой трафик
                    state_netIO_up = res_cont['obj']['netIO']['up']                     # Отправлено байт в данный момент
                    state_netIO_down = res_cont['obj']['netIO']['down']                 # Получено байт в данный момент
                    state_netTraffic_sent = res_cont['obj']['netTraffic']['sent']       # Отправлено байт за все время
                    state_netTraffic_recv = res_cont['obj']['netTraffic']['recv']       # Получено байт за все время

                    # Публичный IP
                    state_publicIP_ipv4 = res_cont['obj']['publicIP']['ipv4']           # Публичный IP-адрес IPv4
                    state_publicIP_ipv6 = res_cont['obj']['publicIP']['ipv6']           # Публичный IP-адрес IPv6

                    # Статистика приложения
                    state_app_stats_threads = res_cont['obj']['appStats']['threads']    # Статистика по использованию потоков в приложении
                    state_app_stats_mem = res_cont['obj']['appStats']['mem']            # Статистика по использованию памяти в приложении
                    state_app_stats_uptime = res_cont['obj']['appStats']['uptime']      # Общее время работы приложения

                    title_cpu = "CPU"
                    title_ram = "RAM"
                    title_swap = "SWAP"
                    title_disk = "DISK"
                    title_xray = "XRAY"
                    title_uptime = "UPTIME"
                    title_tcp_udp = "TCP/UDP COUNT"
                    title_network_traffic = "TRAFFIC"
                    title_ip = "IP"
                    title_app_statistic = "APP STATISTIC"

                    data = [
                        [f"{title_cpu} - CPU ID", state_cpu],
                        [f"{title_cpu} - Cores", state_cpu_core],
                        [f"{title_cpu} - Logical Procs", state_cpu_logic],
                        [f"{title_cpu} - Speed (MHz)", state_cpu_speed_Mhz],
                        [f"{title_cpu} - Load (1, 5, 15 min)", ', '.join(map(str, state_cpu_leeds))],

                        [f"{title_ram} - Current", state_ram_curr],
                        [f"{title_ram} - Total", state_ram_total],

                        [f"{title_swap} - Current", state_swap_curr],
                        [f"{title_swap} - Total", state_swap_total],

                        [f"{title_disk} - Current", state_disk_curr],
                        [f"{title_disk} - Total", state_disk_total],

                        [f"{title_xray} - Status", state_xray_status],
                        [f"{title_xray} - Error Message", state_xray_errMsg],
                        [f"{title_xray} - Version", state_xray_version],

                        [f"{title_uptime} - Uptime (seconds)", state_uptime],

                        [f"{title_tcp_udp} - TCP", state_tcp_count],
                        [f"{title_tcp_udp} - UDP", state_udp_count],

                        [f"{title_network_traffic} - Sent (current)", state_netIO_up],
                        [f"{title_network_traffic} - Received (current)", state_netIO_down],
                        [f"{title_network_traffic} - Sent (total)", state_netTraffic_sent],
                        [f"{title_network_traffic} - Received (total)", state_netTraffic_recv],

                        [f"{title_ip} - IPv4", state_publicIP_ipv4],
                        [f"{title_ip} - IPv6", state_publicIP_ipv6],

                        [f"{title_app_statistic} - Threads", state_app_stats_threads],
                        [f"{title_app_statistic} - Memory", state_app_stats_mem],
                        [f"{title_app_statistic} - Uptime", state_app_stats_uptime]
                    ]

                    if self.print_table(data):
                        logger.info(
                            "The system statistics data "
                            "was recorded in the .log file."
                        )

                        return True
                    
                    else:
                        logger.error(
                            "An error occurred when displaying"
                            "a table with system statistics."
                        )

                        return False
                    
                else:
                    logger.error(
                        f"[{response.status_code}] - "
                        "For some reason, the request failed."
                    )

        except requests.exceptions.RequestException as err:
            logger.error(
                "An error has occurred in the "
                "X_UI/get_system_status prog"
                f"ram block: {err}"
            )
            return False
    
    # Получение данных о всех
    # подключениях и пользователях.
    def get_all_list(self):
        logger.info(
            "Getting a list of connections"
        )

        try:
            # Запрос по адресу x_ui_link+/panel/inbound/list.
            response = self.session.post(
                url=f"{x_ui_link}/panel/inbound/list",
                verify=False,
                stream=True
            )

            # Проверка что от сервера поступил 200.
            if response.status_code == 200:
                res_cont = json.loads(response.content)

                # Проверка что в success от сервера True.
                if res_cont['success']:

                    # Перебор всех значений из obj.
                    for _ in res_cont['obj']:
                        try:
                            connection_id = res_cont['obj'][0]['id']                            # ID подключения
                            connection_remark = res_cont['obj'][0]['remark']                    # Название подключения
                            connection_enable = res_cont['obj'][0]['enable']                    # Запущено подключение
                            connection_port = res_cont['obj'][0]['port']                        # Порт подключения
                            connection_protocol = res_cont['obj'][0]['protocol']                # Протокол подключения

                            connection_up = res_cont['obj'][0]['up']
                            connection_down = res_cont['obj'][0]['down']

                            # Подсчет количества пользователей на данном подключении
                            clientStats = len([client for client in res_cont['obj'][0]['clientStats']])

                            data_connections = [
                                ["Connection ID", connection_id],
                                ["Name", connection_remark],
                                ["Enable", connection_enable],
                                ["Port", connection_port],
                                ["Protocol", connection_protocol],
                                ["Up", connection_up],
                                ["Down", connection_down],
                                ["clientStats", clientStats]
                            ]

                            self.print_table(data_connections)

                        except Exception as err:
                            logger.error(
                                "An error occurred in the "
                                "X_UI/get_all_list block "
                                "iterating over values from obj."
                                f"Error: {err}"
                            )

                        try:

                            parsed_settings = json.loads(res_cont['obj'][0]['settings'])

                            for _ in parsed_settings['clients']:
                                user_id = parsed_settings['clients'][0]['id']                   # Уникальный UUID клиента
                                user_flow = parsed_settings['clients'][0]['flow']               # Используется XTLS-режим
                                user_email = parsed_settings['clients'][0]['email']             # Email пользователя
                                user_limit_ip = parsed_settings['clients'][0]['limitIp']        # Лимит по IP
                                user_totalGB = parsed_settings['clients'][0]['totalGB']         # Нет ограничений по трафику
                                user_expiryTime = parsed_settings['clients'][0]['expiryTime']   # Время истечения срока действия (0 бесконечный)
                                user_tgId = parsed_settings['clients'][0]['tgId']               # ID пользователя в телеграм
                                user_subId = parsed_settings['clients'][0]['subId']             # Вспомогательный ID пользователя
                                user_comment = parsed_settings['clients'][0]['comment']         # Комментарий
                                user_reset = parsed_settings['clients'][0]['reset']             # Сколько раз сбрасывались настройки пользователя

                                logger.info(
                                    "Getting all users"
                                )
                            
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

                                self.print_table(user_data)

                        except Exception as err:
                            logger.error(
                                "An error occurred in the "
                                "X_UI/get_all_list block "
                                "iterating over values from "
                                "res_cont['obj'][0]['settings']."
                                f"Error: {err}"
                            )

                        try:
                            parsed_streamSettings = json.loads(res_cont['obj'][0]['streamSettings'])
                            realitySettings = parsed_streamSettings['realitySettings']

                            show = realitySettings['show']
                            xver = realitySettings['xver']
                            dest = realitySettings['dest']
                            serverNames_1 = realitySettings['serverNames'][0]
                            serverNames_2 = realitySettings['serverNames'][1]
                            privateKey = realitySettings['privateKey']
                            minClient = realitySettings['minClient']
                            maxClient = realitySettings['maxClient']
                            maxTimediff = realitySettings['maxTimediff']
                            shortIds = realitySettings['shortIds']
                            settings_publicKey = realitySettings['settings']['publicKey']
                            settings_fingerprint = realitySettings['settings']['fingerprint']
                            settings_serverName = realitySettings['settings']['serverName']
                            settings_spiderX = realitySettings['settings']['spiderX']


                            logger.info(
                                    "Getting reality settings"
                                )

                            data_realitySettings = [
                                ["Show", show],
                                ["Xver", xver],
                                ["Dest", dest],
                                ["Server Name 1", serverNames_1],
                                ["Server Name 2", serverNames_2],
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

                            self.print_table(data_realitySettings)
                        except Exception as err:
                            logger.error(
                                "An error occurred in the "
                                "X_UI/get_all_list block "
                                "iterating over values from "
                                "res_cont['obj'][0]['streamSettings']."
                                f"Error: {err}"
                            )

        except requests.exceptions.RequestException as err:
            logger.error(
                "An error has occurred in the "
                "X_UI/get_list"
                f"program block: {err}"
            )

    # Проверка результата xray
    def get_xray_result(self):
        logger.info(
            "Getting result xray services"
        )

        try:
            # Запрос по адресу x_ui_link+/panel/xray/getXrayResult.
            response = self.session.get(
                url=f"{x_ui_link}/panel/xray/getXrayResult",
                verify=False,
                stream=True
            )

            # Проверка что от сервера поступил 200.
            if response.status_code == 200:

                res_cont = json.loads(response.content)


                # Проверка что в success от сервера True.
                if res_cont['success']:
                    return True
                else:
                    return False

        except requests.exceptions.RequestException as err:
            logger.error(
                "An error has occurred in the "
                "X_UI/get_xray_result"
                f"program block: {err}"
            )

    # Остановка сервиса xray
    def stop_xray(self):
        logger.info(
            "Stoping xray services"
        )

        try:
            # Запрос по адресу x_ui_link+/server/stopXrayService.
            response = self.session.post(
                url=f"{x_ui_link}/server/stopXrayService",
                verify=False,
                stream=True
            )

            # Проверка что от сервера поступил 200.
            if response.status_code == 200:

                res_cont = json.loads(response.content)

                success = f"SUCCESS: {res_cont['success']}"
                message = f"MESSAGE: {res_cont['msg']}"
                sep = "-" * (len(str(success)) + len(str(message)))

                # Проверка что в success от сервера True.
                if res_cont['success']:

                    if self.get_xray_result():
                        logger.info(
                            f"The xray service has been successfully stopped!\n"
                            f"{sep}\n"
                            f"{success}\n{message}\n"
                            f"{sep}"
                        )

                        return True
                    else:
                        logger.info(
                            "Xray don't restarted!"
                        )

                        return False
                
                else:
                    logger.error(
                        f"The xray service has not been stopped\n"
                        f"{sep}\n"
                        f"{success}\n{message}\n"
                        f"{sep}"
                    )

                    return False

        except requests.exceptions.RequestException as err:
            logger.error(
                "An error has occurred in the "
                "X_UI/stop_xray"
                f"program block: {err}"
            )

    # Перезапуск сервиса xray
    def restart_xray(self):
        logger.info(
            "Restart xray services"
        )

        try:
            # Запрос по адресу x_ui_link+/server/restartXrayService.
            response = self.session.post(
                url=f"{x_ui_link}/server/restartXrayService",
                verify=False,
                stream=True
            )

            # Проверка что от сервера поступил 200.
            if response.status_code == 200:

                res_cont = json.loads(response.content)

                success = f"SUCCESS: {res_cont['success']}"
                message = f"MESSAGE: {res_cont['msg']}"
                sep = "-" * (len(str(success)) + len(str(message)))

                # Проверка что в success от сервера True.
                if res_cont['success']:
                    
                    if self.get_xray_result():
                        logger.info(
                            f"The xray service has been successfully restarted!\n"
                            f"{sep}\n"
                            f"{success}\n{message}\n"
                            f"{sep}"
                        )

                        return True
                    else:
                        logger.error(
                            "Xray don't restarted!"
                        )

                        return False
                
                else:
                    logger.error(
                        f"The xray service has not been restarted\n"
                        f"{sep}\n"
                        f"{success}\n{message}\n"
                        f"{sep}"
                    )

                    return False

        except requests.exceptions.RequestException as err:
            logger.error(
                "An error has occurred in the "
                "X_UI/restart_xray"
                f"program block: {err}"
            )

    # Получение vless конфигурации
    # в виде ссылки.
    def get_vless_link(self):
        logger.info(
            "Getting the vless "
            "configuration as a link"
        )

        try:
            # Запрос по адресу x_ui_link+/panel/inbound/list.
            response = self.session.post(
                url=f"{x_ui_link}/panel/inbound/list",
                verify=False,
                stream=True
            )

            # Проверка что от сервера поступил 200.
            if response.status_code == 200:
                res_cont = json.loads(response.content)

                # Проверка что в success от сервера True.
                if res_cont['success']:

                    # Перебор всех значений из obj.    
                    for _ in res_cont['obj']:
                        parsed_settings = json.loads(res_cont['obj'][0]['settings'])

                        try:
                            for _ in parsed_settings['clients']:
                                user_id = parsed_settings['clients'][0]['id']                   # Уникальный UUID клиента
                                user_flow = parsed_settings['clients'][0]['flow']               # Используется XTLS-режим
                                connection_remark = res_cont['obj'][0]['remark']                # Название подключения
                                user_email = parsed_settings['clients'][0]['email']             # Email пользователя

                                parsed_streamSettings = json.loads(res_cont['obj'][0]['streamSettings'])
                                realitySettings = parsed_streamSettings['realitySettings']

                                serverNames_1 = realitySettings['serverNames'][0]
                                shortIds = realitySettings['shortIds']
                                settings_publicKey = realitySettings['settings']['publicKey']
                                settings_fingerprint = realitySettings['settings']['fingerprint']

                                
                            vless_link = f"vless://{user_id}@{os.getenv('VLESS_HOST')}:{os.getenv('VLESS_PORT')}?type=tcp&security=reality&pkb={settings_publicKey}&fp={settings_fingerprint}&sni={serverNames_1}&sid={shortIds[0]}&spx=%2F&flow={user_flow}#{connection_remark}-{user_email}"
                            vless_link = vless_link.replace(" ", "%20")
                            
                            logger.info(
                                "Vless configuration\n"
                                f"{vless_link}"
                            )

                        except Exception as err:
                            logger.error(
                                "An error occurred in the "
                                "X_UI/get_all_list block "
                                "iterating over values from "
                                "res_cont['obj'][0]['settings']."
                                f"Error: {err}"
                            )

        except requests.exceptions.RequestException as err:
            logger.error(
                "An error has occurred in the "
                "X_UI/get_vless_link"
                f"program block: {err}"
            )

conn = X_UI()
conn.session_up()
# conn.get_system_status()
# conn.get_all_list()
# conn.stop_xray()
# conn.restart_xray()
# conn.get_vless_link()