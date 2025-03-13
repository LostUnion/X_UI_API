#########################################################################
#  __    __         __    __  ______         ______   _______   ______  #
# /  |  /  |       /  |  /  |/      |       /      \ /       \ /      | #
# $$ |  $$ |       $$ |  $$ |$$$$$$/       /$$$$$$  |$$$$$$$  |$$$$$$/  #
# $$  \/$$/ ______ $$ |  $$ |  $$ | ______ $$ |__$$ |$$ |__$$ |  $$ |   #
#  $$  $$< /      |$$ |  $$ |  $$ |/      |$$    $$ |$$    $$/   $$ |   #
#   $$$$  \$$$$$$/ $$ |  $$ |  $$ |$$$$$$/ $$$$$$$$ |$$$$$$$/    $$ |   #
#  $$ /$$  |       $$ \__$$ | _$$ |_       $$ |  $$ |$$ |       _$$ |_  #
# $$ |  $$ |       $$    $$/ / $$   |      $$ |  $$ |$$ |      / $$   | #
# $$/   $$/         $$$$$$/  $$$$$$/       $$/   $$/ $$/       $$$$$$/  #
#########################################################################

import uuid
import time
import json
import base64
import secrets
from datetime import datetime
from abc import ABC
import urllib.parse
from pathlib import Path

import urllib3
import requests
from nacl.public import PrivateKey
from requests.exceptions import RequestException

from config import Config
from logger_settings import logger_xui as log

# Disabling the self-signed
# certificate warning.
urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)


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
        self.authenticated = self.session_up()

    # Raising the session and
    # recording cookies after
    # authorization.

    def session_up(self):
        log.info(
            "Connecting to "
            f"\"{self.x_ui_link}\""
        )

        try:
            payload = {
                "username": self.x_ui_login,
                "password": self.x_ui_password
            }

            # Authorization
            # in the x-ui panel.
            res = self.session.post(
                url=f"{self.x_ui_link}/login",
                # Skipping the verification
                # of a self-signed certificate.
                verify=False,
                # Allows you to download the
                # response in parts, reducing
                # the memory load.
                stream=True,
                # Adding parameters and settings.
                json=payload
            )

            # Checking the successful
            # response from the server.
            if res.status_code == 200:

                # Converting the binary
                # response from the server
                # to JSON format.
                j_cont = json.loads(res.content)

                # Generating a message
                # for output to the user
                # and writing to the log.
                suc = f"SUCCESS: {j_cont['success']}"
                msg = f"MESSAGE: {j_cont['msg']}"

                # A separator for visual
                # differentiation.
                sep = '-' * (len(str(suc)) + len(str(msg)))

                # Checking that success
                # from the server is True.
                if j_cont['success']:

                    log.info(
                        'Authorization was successful\n'
                        f'{sep}\n{suc}\n{msg}\n{sep}'
                    )

                    # Collecting cookie data
                    # from the session after
                    # authorization.
                    cookies = [
                        {
                            "domain": k.domain,
                            "name": k.name,
                            "path": k.path,
                            "value": k.value
                        }
                        for k in self.session.cookies
                    ]

                    # Installation of these
                    # cookies in the session
                    # for later use.
                    for cookie in cookies:
                        self.session.cookies.set(**cookie)

                    # An informational message
                    # after installing cookies.
                    log.info(
                        "Cookies have been installed"
                    )

                    return True

                else:
                    # An informational message
                    # if success was False.
                    log.error(
                        'Authorization failed\n'
                        f'{sep}\n{suc}\n{msg}\n{sep}'
                    )

                    quit()

            else:
                # Information message if
                # res.status_code != 200.
                log.error(
                    f"[{res.status_code}] - An "
                    "error occurred during "
                    "authorization"
                )

                quit()

        # Output of the location
        # and the error itself to
        # the log.
        except RequestException as err:
            log.error(
                "An error has occurred in "
                "the X_UI/session_up progr"
                f"am block: {err}"
            )

            return False

    # Downloading connection backups.
    def export_conf_backups(self):
        log.info(
            "Getting a backup of "
            "user configuration data"
        )

        try:
            # Request to receive user
            # configuration data.
            res = self.session.get(
                url=f"{self.x_ui_link}/server/getDb",
                # Skipping the verification
                # of a self-signed certificate.
                verify=False,
                # Allows you to download the
                # response in parts, reducing
                # the memory load.
                stream=True
            )

            # Checking the successful
            # response from the server.
            if res.status_code == 200:

                # Checking that any text has
                # been received from the server.
                if res.content:

                    # Naming of the backup file,
                    # with date and time in the
                    # name.
                    date = datetime.now()
                    date_now = date.strftime('%Y-%m-%d-%H-%M-%S')

                    # Getting the backup
                    # file save path.
                    folder_backups = Path(Config.X_UI_BACKUPS_PATH)

                    # Checking the existence
                    # of the backup folder.
                    if not folder_backups.is_dir():

                        # Creating a folder if
                        # it doesn't exist.
                        folder_backups.mkdir(parents=True, exist_ok=True)

                    # The absolute path of
                    # saving the backup file.
                    file_path = folder_backups / f"{date_now}_backup.db"

                    # Writing backup data to a file.
                    with open(file_path, "wb") as file:
                        # chunk_size sets the size
                        # of the data portion (8192 bytes)
                        # loaded at a time from the response.
                        for chunk in res.iter_content(chunk_size=8192):
                            file.write(chunk)

                        # Information output to the
                        # user that the data has been
                        # written to a file.
                        log.info(
                            f"[{res.status_code}] - "
                            "The backup data was "
                            "successfully written "
                            f"to the \"{file_path}\"file"
                        )

                        return True, file_path

                else:
                    # Informing the user that the
                    # request came with the status 200,
                    # but did not return anything in the
                    # response.
                    log.warning(
                        f"[{res.status_code}]"
                        " - The request was successful, "
                        "but the server returned nothing."
                    )

                    return False

            else:
                # Informing the user that an error
                # has occurred while downloading the
                # backup.
                log.error(
                    f"[{res.status_code}]"
                    " - Failed to download backup"
                )

                return False

        # Output of the location
        # and the error itself to
        # the log.
        except RequestException as err:
            log.error(
                "An error has occurred in the "
                "X_UI/export_conf_backups prog"
                f"ram block: {err}"
            )

            return False

    # Creating a table
    # for log output.
    def table_collection(self,
                         data):
        try:
            # Calculating the maximum
            # length of metrics.
            max_len_metric = max(len(str(item[0])) for item in data)

            # Calculating the maximum
            # length of values.
            max_len_value = max(len(str(item[1])) for item in data)

            # Output of titles.
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

            # Iterating through and
            # outputting values.
            for metric, value in data:
                log.info(
                    f"| {metric.ljust(max_len_metric)} |"
                    f" {str(value).ljust(max_len_value)} |"
                )

            # Final separation.
            log.info(
                f"+{'-' * (max_len_metric + 2)}"
                f"+{'-' * (max_len_value + 2)}+"
            )

            return True

        # Output of the location
        # and the error itself to
        # the log.
        except Exception as err:
            log.error(
                "An error has occurred in the "
                "X_UI/table_collection prog"
                f"ram block: {err}"
            )

            return False

    # Getting statistics for
    # the entire system.
    def get_system_status(self):
        log.info(
            "Getting statistics on the system"
        )

        try:
            # A request to receive all
            # data on the x-ui system.
            res = self.session.post(
                url=f"{self.x_ui_link}/server/status",
                # Skipping the verification
                # of a self-signed certificate.
                verify=False,
                # Allows you to download the
                # response in parts, reducing
                # the memory load.
                stream=True
            )

            # Checking the successful
            # response from the server.
            if res.status_code == 200:

                # Converting the binary
                # response from the server
                # to JSON format.
                j_cont = json.loads(res.content)

                # Generating a message
                # for output to the user
                # and writing to the log.
                suc = f"SUCCESS: {j_cont['success']}"
                msg = f"MESSAGE: {j_cont['msg']}"

                # A separator for visual
                # differentiation.
                sep = '-' * (len(str(suc)) + len(str(msg)))

                # Checking that success
                # from the server is True.
                if j_cont['success']:

                    # Getting an object from a
                    # response from the server.
                    obj_data = j_cont['obj']

                    # -- CPU DATA --

                    # ID of the processor,
                    # which can be 0 for the
                    # main core.
                    cpu_id = obj_data['cpu']

                    # The number of physical
                    # processor cores.
                    cpu_core = obj_data['cpuCores']

                    # The number of logical
                    # processor cores.
                    cpu_logic = obj_data['logicalPro']

                    # Processor frequency
                    # in megahertz.
                    cpu_speed_Mhz = obj_data['cpuSpeedMhz']

                    # The average CPU load
                    # over the last
                    # 1, 5, and 15 minutes.
                    cpu_leeds = obj_data['loads']

                    # -- RAM DATA --

                    # The current memory used.
                    ram_curr = obj_data['mem']['current']

                    # Shared memory.
                    ram_total = obj_data['mem']['total']

                    # -- SWAP DATA --

                    # Current swap usage.
                    swap_curr = obj_data['swap']['current']

                    # Shared swap memory.
                    swap_total = obj_data['swap']['total']

                    # -- HDD/SSD DATA --

                    # Current disk memory used.
                    disk_curr = obj_data['disk']['current']

                    # Shared disk memory
                    disk_total = obj_data['disk']['total']

                    # -- THE STATE OF THE XRAY SERVICE --

                    # Xray status.
                    xray_status = obj_data['xray']['state']

                    # Error messages.
                    xray_errMsg = obj_data['xray']['errorMsg']

                    # Xray version.
                    xray_version = obj_data['xray']['version']

                    # Operating time of the xray system in seconds.
                    uptime = obj_data['uptime']

                    # -- NETWORK CONNECTIONS --

                    # Number of TCP connections.
                    tcp_count = obj_data['tcpCount']

                    # Number of UDP connections.
                    udp_count = obj_data['udpCount']

                    # -- NETWORK TRAFFIC --

                    # Bytes sent at the moment.
                    netIO_up = obj_data['netIO']['up']

                    # Bytes received at the moment.
                    netIO_down = obj_data['netIO']['down']

                    # Bytes sent for all time.
                    netTraffic_sent = obj_data['netTraffic']['sent']

                    # Bytes received for all time.
                    netTraffic_recv = obj_data['netTraffic']['recv']

                    # -- PUBLIC IP ADDRESS --

                    # IPv4 Public IP Address.
                    publicIP_ipv4 = obj_data['publicIP']['ipv4']

                    # IPv6 Public IP Address.
                    publicIP_ipv6 = obj_data['publicIP']['ipv6']

                    # -- APPLICATION STATISTICS --

                    # Statistics on the usage of streams in the application.
                    app_stats_threads = obj_data['appStats']['threads']

                    # Statistics on memory usage in the application.
                    app_stats_mem = obj_data['appStats']['mem']

                    # The total running time of the application.
                    app_stats_uptime = obj_data['appStats']['uptime']

                    data = [
                        ["CPU - CPU ID", cpu_id],
                        ["CPU - Cores", cpu_core],
                        ["CPU - Logical Procs", cpu_logic],
                        ["CPU - Speed (MHz)", cpu_speed_Mhz],
                        ["CPU - Load (1, 5, 15 min)", ', '.join(
                            map(str, cpu_leeds)
                        )],

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

                    returned_data = {
                        "cpu_id": cpu_id,
                        "cpu_core": cpu_core,
                        "cpu_logic": cpu_logic,
                        "cpu_speed_Mhz": cpu_speed_Mhz,
                        "cpu_load": ', '.join(map(str, cpu_leeds)),
                        "ram_curr": ram_curr,
                        "ram_total": ram_total,
                        "swap_curr": swap_curr,
                        "swap_total": swap_total,
                        "disk_curr": disk_curr,
                        "disk_total": disk_total,
                        "xray_status": xray_status,
                        "xray_errMsg": xray_errMsg,
                        "xray_version": xray_version,
                        "uptime": uptime,
                        "tcp_count": tcp_count,
                        "udp_count": udp_count,
                        "netIO_up": netIO_up,
                        "netIO_down": netIO_down,
                        "netTraffic_sent": netTraffic_sent,
                        "netTraffic_recv": netTraffic_recv,
                        "publicIP_ipv4": publicIP_ipv4,
                        "publicIP_ipv6": publicIP_ipv6,
                        "publicIP_ipv6": publicIP_ipv6,
                        "app_stats_threads": app_stats_threads,
                        "app_stats_mem": app_stats_mem,
                        "app_stats_uptime": app_stats_uptime,
                    }

                    # Checking that the transmitted
                    # data has been generated in a
                    # table.
                    if self.table_collection(data):
                        log.info(
                            "The system statistics data "
                            "was recorded in the .log file."
                        )

                        return True, returned_data

                    # If the data has not been
                    # generated, an error occurs.
                    else:
                        log.error(
                            "An error occurred when displaying"
                            "a table with system statistics."
                        )

                        return False

                else:
                    # An informational message
                    # if success was False.
                    log.error(
                        'Collecting table failed\n'
                        f'{sep}\n{suc}\n{msg}\n{sep}'
                    )

                    return False

            else:
                # Informing the user that an
                # error occurred when receiving
                # x-ui statistics.
                log.error(
                    f"[{res.status_code}]"
                    " - Error when getting "
                    "statistics"
                )

                return False

        # Output of the location
        # and the error itself to
        # the log.
        except RequestException as err:
            log.error(
                "An error has occurred in the "
                "X_UI/get_system_status prog"
                f"ram block: {err}"
            )

            return False

    # Getting data about
    # all connections.
    def get_connections(self,
                        get_clients: bool = False):
        log.info(
            "Getting a list of connections"
        )

        try:
            # Request to receive all connections.
            res = self.session.post(
                url=f"{self.x_ui_link}/panel/inbound/list",
                # Skipping the verification
                # of a self-signed certificate.
                verify=False,
                # Allows you to download the
                # response in parts, reducing
                # the memory load.
                stream=True
            )

            # Checking the successful
            # response from the server.
            if res.status_code == 200:

                # Converting the binary
                # response from the server
                # to JSON format.
                j_cont = json.loads(res.content)

                # Generating a message
                # for output to the user
                # and writing to the log.
                suc = f"SUCCESS: {j_cont['success']}"
                msg = f"MESSAGE: {j_cont['msg']}"

                # A separator for visual
                # differentiation.
                sep = '-' * (len(str(suc)) + len(str(msg)))

                # Checking that success
                # from the server is True.
                if j_cont['success']:

                    obj_data = j_cont['obj']

                    all_connections = []
                    all_clients = []

                    # Iterating through all the values from obj.
                    for iter_obj in obj_data:

                        # Collecting all
                        # connection data.

                        # -- CONNECTION INFORMATION --

                        # Connection ID.
                        conn_id = iter_obj['id']

                        # Connection name.
                        conn_remark = iter_obj['remark']

                        # Checking whether the
                        # connection has been
                        # restarted.
                        conn_enable = iter_obj['enable']

                        # Connection port.
                        conn_port = iter_obj['port']

                        # Connection protocol.
                        conn_protocol = iter_obj['protocol']

                        conn_up = iter_obj['up']
                        conn_down = iter_obj['down']

                        # Settings is taken from obj.
                        sett_data = json.loads(iter_obj['settings'])

                        # streamSettings is taken from obj.
                        streamSett = json.loads(iter_obj['streamSettings'])

                        conn_network = streamSett['network']

                        conn_security = streamSett['security']
                        conn_externProxy = streamSett['externalProxy']

                        # realitySettings is taken from streamSettings.
                        realitySettings = streamSett['realitySettings']

                        # -
                        real_show = realitySettings['show']

                        # -
                        real_xver = realitySettings['xver']

                        # - Destination.
                        real_dest = realitySettings['dest']

                        # Which service is being disguised as.
                        real_serverNames = realitySettings['serverNames']

                        # The private connection key.
                        real_privateKey = realitySettings['privateKey']

                        # The minimum allowed number
                        # of clients per connection.
                        real_minClient = realitySettings['minClient']

                        # The maximum allowed number
                        # of clients per connection.
                        real_maxClient = realitySettings['maxClient']

                        # The maximum time interval.
                        real_maxTimediff = realitySettings['maxTimediff']

                        # Short identifiers.
                        real_shortIds = realitySettings['shortIds']

                        real_settings = realitySettings['settings']

                        real_sett_publicKey = real_settings['publicKey']

                        real_sett_fingprnt = real_settings['fingerprint']

                        real_sett_serverName = real_settings['serverName']

                        real_sett_spiderX = real_settings['spiderX']

                        clients = sett_data['clients']

                        # Client counter on activation.
                        clients_count = 0
                        for client in sett_data['clients']:
                            client['publicKey'] = real_sett_publicKey
                            client['privateKey'] = real_privateKey

                            client['type'] = conn_network
                            client['security'] = conn_security
                            client['fingerprint'] = real_sett_fingprnt
                            client['serverName'] = real_serverNames[0]
                            client['shortIds'] = real_shortIds[0]
                            client['SpiderX'] = real_sett_spiderX
                            client['Remark'] = conn_remark

                            all_clients.append(client)
                            clients_count += 1

                        data = [
                                ["Connection ID", conn_id],
                                ["Name", conn_remark],
                                ["Enable", conn_enable],
                                ["Port", conn_port],
                                ["Protocol", conn_protocol],
                                ["Up", conn_up],
                                ["Down", conn_down],
                                ["Clients", clients_count],
                                ["Network", conn_network],
                                ["Security", conn_security],
                                ["External Proxy", conn_externProxy],
                                ["Show", real_show],
                                ["Xver", real_xver],
                                ["Dest", real_dest],
                                ["Server Name", real_serverNames],
                                ["Private Key", real_privateKey],
                                ["Min Clients", real_minClient],
                                ["Max Clients", real_maxClient],
                                ["Max Timediff", real_maxTimediff],
                                ["Short Ids", real_shortIds],
                                ["Public Key", real_sett_publicKey],
                                ["Fingerprint", real_sett_fingprnt],
                                ["Server Name", real_sett_serverName],
                                ["Spider X", real_sett_spiderX]
                            ]

                        returned_data = {
                                "conn_id": conn_id,
                                "conn_remark": conn_remark,
                                "conn_enable": conn_enable,
                                "conn_port": conn_port,
                                "conn_protocol": conn_protocol,
                                "conn_up": conn_up,
                                "conn_down": conn_down,
                                "clients_count": clients_count,
                                "conn_network": conn_network,
                                "conn_security": conn_security,
                                "conn_externalProxy": conn_externProxy,
                                "real_show": real_show,
                                "real_xver": real_xver,
                                "real_dest": real_dest,
                                "real_serverNames": real_serverNames,
                                "real_privateKey": real_privateKey,
                                "real_minClient": real_minClient,
                                "real_maxClient": real_maxClient,
                                "real_maxTimediff": real_maxTimediff,
                                "real_shortIds": real_shortIds,
                                "real_sett_publicKey": real_sett_publicKey,
                                "real_sett_fingerprint": real_sett_fingprnt,
                                "real_sett_serverName": real_sett_serverName,
                                "real_sett_spiderX": real_sett_spiderX,
                                "clients": clients
                            }

                        if get_clients:
                            pass

                        else:
                            # Checking that the transmitted
                            # data has been generated in a
                            # table.
                            if self.table_collection(data):
                                pass

                            # If the data has not been
                            # generated, an error occurs.
                            else:
                                log.error(
                                    "An error occurred when "
                                    "displaying the connection table"
                                )

                            all_connections.append(returned_data)

                    if all_connections is not None:
                        return True, all_connections, all_clients

                    else:
                        log.error(
                            "Connections were not found"
                        )

                        return False
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

        # Output of the location
        # and the error itself to
        # the log.
        except RequestException as err:
            log.error(
                "An error has occurred in the "
                "X_UI/get_connections "
                f"program block: {err}"
            )

            return False

    # Getting all clients.
    def get_clients(self):
        log.info(
            "Getting all clients"
        )

        try:
            # Calling the get_connections method.
            # The result of the method call is
            # saved to the all_clients variable.
            all_clients = self.get_connections(get_clients=True)

            # The third element (index 2) is taken
            # from the received data and stored in
            # the clients variable.
            clients = all_clients[2]

            all_clients_data = []

            # Going through all the clients.
            for client in clients:
                client_comment = client['comment']
                client_email = client['email']
                client_enable = client['enable']
                client_expiryTime = client['expiryTime']
                client_flow = client['flow']
                client_limitIp = client['limitIp']
                client_id = client['id']
                client_reset = client['reset']
                client_subId = client['subId']
                client_tgId = client['tgId']
                client_totalGB = client['totalGB']
                client_publicKey = client['publicKey']
                client_privateKey = client['privateKey']
                client_type = client['type']
                client_security = client['security']
                client_fingerprint = client['fingerprint']
                client_serverName = client['serverName']
                client_shortIds = client['shortIds']
                client_spx = client['SpiderX']
                client_remark = client['Remark']

                # Replacing an empty value
                # and special characters.
                client_remark = urllib.parse.quote(client_remark, safe='')
                client_spx = urllib.parse.quote(client_spx, safe='')

                # Generating a vless link
                # with client_remark.
                if client_remark != "":
                    client_vless_link = (
                        f"vless://{client_id}@{Config.VLESS_HOST}:"
                        f"{Config.VLESS_PORT}?type={client_type}&security="
                        f"{client_security}&pkb={client_publicKey}"
                        f"&fp={client_fingerprint}&sni={client_serverName}"
                        f"&sid={client_shortIds}&spx={client_spx}"
                        f"&flow={client_flow}#{client_remark}-{client_email}"
                    ).replace(" ", "%20")

                # Generating a vless link
                # without client_remark.
                else:
                    client_vless_link = (
                        f"vless://{client_id}@{Config.VLESS_HOST}:"
                        f"{Config.VLESS_PORT}?type={client_type}&security="
                        f"{client_security}&pkb={client_publicKey}"
                        f"&fp={client_fingerprint}&sni={client_serverName}"
                        f"&sid={client_shortIds}&spx={client_spx}"
                        f"&flow={client_flow}#{client_email}"
                    ).replace(" ", "%20")

                data = [
                        ["Comment", client_comment],
                        ["Email", client_email],
                        ["Enable", client_enable],
                        ["Expiry Time", client_expiryTime],
                        ["Flow", client_flow],
                        ["Limit Ip", client_limitIp],
                        ["Client ID", client_id],
                        ["Reset", client_reset],
                        ["Sub ID", client_subId],
                        ["TG ID", client_tgId],
                        ["Total GB", client_totalGB],
                        ["Public Key", client_publicKey],
                        ["Private Key", client_privateKey],
                        ["Type", client_type],
                        ["Security", client_security],
                        ["Fingerprint", client_fingerprint],
                        ["Server Name", client_serverName],
                        ["Short Ids", client_shortIds],
                        ["Spider X", client_spx],
                        ["Remark", client_remark],
                        ["Vless Link", client_vless_link]
                    ]

                returned_data = {
                    "client_comment": client_comment,
                    "client_email": client_email,
                    "client_enable": client_enable,
                    "client_expiryTime": client_expiryTime,
                    "client_flow": client_flow,
                    "client_limitIp": client_limitIp,
                    "client_id": client_id,
                    "client_reset": client_reset,
                    "client_subId": client_subId,
                    "client_tgId": client_tgId,
                    "client_totalGB": client_totalGB,
                    "client_publicKey": client_publicKey,
                    "client_privateKey": client_privateKey,
                    "client_type": client_type,
                    "client_security": client_security,
                    "client_fingerprint": client_fingerprint,
                    "client_serverName": client_serverName,
                    "client_shortIds": client_shortIds,
                    "client_spx": client_spx,
                    "client_remark": client_remark,
                    "vless_link": client_vless_link
                }

                # Checking that the transmitted
                # data has been generated in a
                # table.
                if self.table_collection(data):
                    pass

                else:
                    log.error(
                        "An error occurred when "
                        "generating the client's "
                        "table"
                    )

                all_clients_data.append(returned_data)

            if all_clients_data:
                return True, all_clients_data

        # Output of the location
        # and the error itself to
        # the log.
        except Exception as err:
            log.error(
                "An error has occurred in the "
                "X_UI/get_clients "
                f"program block: {err}"
            )

            return False

    # Getting one client.
    def get_client(self,
                   client_id: str = None):

        log.info(
            "Getting one client"
        )

        try:
            # Getting a list of clients.
            all_clients = self.get_clients()
            clients = all_clients[1]

            client_data = []

            # Iterating through all received clients.
            for client in clients:
                if client_id is not None:
                    # Comparison of the entered id
                    # with the ID of the selected clients.
                    if client['client_id'] == str(client_id):
                        # Adding a client to the
                        # list with the appropriate id.
                        client_data.append(client)
                    else:
                        pass

                else:
                    log.error(
                        "The client_id field must"
                        "contain the client's id"
                    )

            if client_data:
                return True, client_data

            else:
                # Warning output that the id did not
                # match more than one id from all users.
                log.warning(
                    "The user with the id"
                    f"{client_id} was not found"
                )

        # Output of the location
        # and the error itself to
        # the log.
        except Exception as err:
            log.error(
                "An error has occurred in the "
                "X_UI/get_client "
                f"program block: {err}"
            )

    # Public and private key generation.
    def pr_pub_key(self):
        log.info(
            "Public and private key generation"
        )

        try:
            # Generating private key in base64 format.
            private_key = PrivateKey.generate()

            # Converting a private key to hex.
            private_hex = private_key.encode().hex()

            # Converting a public key to hex.
            public_hex = private_key.public_key.encode().hex()

            # Converting a private key to base64.
            private_b64 = base64.urlsafe_b64encode(
                bytes.fromhex(private_hex)
            ).decode().rstrip("=")

            # Converting a public key to base64.
            public_b64 = base64.urlsafe_b64encode(
                bytes.fromhex(public_hex)
            ).decode().rstrip("=")

            return private_b64, public_b64

        # Output of the location
        # and the error itself to
        # the log.
        except Exception as err:
            log.error(
                "An error has occurred in the "
                "X_UI/pr_pub_key "
                f"program block: {err}"
            )

            return False

    # Creating a new connection.
    def create_connection(self,
                          up: int = 0,
                          down: int = 0,
                          total: int = 0,
                          remark: str = "",
                          enable: bool = True,
                          expiryTime: int = 0,
                          listen: str = "",
                          protocol: str = "vless",
                          network: str = "tcp",
                          security: str = "reality",
                          externalProxy: list = [],
                          show: bool = False,
                          xver: int = 0,
                          dest: str = "google.com:443",
                          serverNames: list = ["www.google.com"],
                          fingerprint: str = "chrome",
                          serverName: str = "",
                          spiderX: str = "/",
                          acceptProxyProtocol: bool = False,
                          sniffing_enabled: bool = False,
                          destOverride: list = [
                              "http", "tls", "quic", "fakedns"
                          ],
                          metadataOnly: bool = False,
                          routeOnly: bool = False,
                          strategy: str = "always",
                          refresh: int = 5,
                          concurrency: int = 3):
        log.info(
            "Creating a new connection"
        )

        try:
            # Obtaining a private and public key.
            private_key, public_key = self.pr_pub_key()

            # Generating the client's uuid.
            client_id = str(uuid.uuid4())

            # Generating the client's subId.
            subId = base64.urlsafe_b64encode(
                uuid.uuid4().bytes
            ).decode().rstrip("=")

            # Creating 8 shortIds.
            short_ids = [
                secrets.token_hex(
                    secrets.choice(range(2, 9))
                ) for _ in range(8)
            ]

            # Checking that the keys are there.
            required_values = {
                "private_key": private_key,
                "public_key": public_key,
                "client_id": client_id,
                "sub_id": subId,
                "short_ids": short_ids
            }

            missing_values = [
                key for key, value in required_values.items() if not value
            ]

            # Checking for all values.
            if missing_values:
                log.error(
                    "Error: missing values "
                    f"{', '.join(missing_values)}"
                    )

                return False

            connections = self.get_connections()

            # The list for storing
            # ports after parsing.
            ports = []

            # Iterating through connections
            # and searching for ports.
            for connection in connections[1]:
                ports.append(int(connection['conn_port']))

            free_port = max(ports) + 1

            # Checking for a range of ports.
            if Config.PORT_RANGE_MIN <= free_port <= Config.PORT_RANGE_MAX:
                log.info(
                    f"The {free_port} port is within "
                    "the allowed port range"
                )

            else:
                log.error(
                    f"The {free_port} port is not "
                    "in the range of valid ports."
                )

                return False

            # Creating a test client.
            try:
                settings = json.dumps({
                    "clients": [
                        {
                            "id": f"{str(client_id)}",
                            "flow": "",
                            "email": f"{str(short_ids[0])}",
                            "limitIp": 0,
                            "totalGB": 0,
                            "expiryTime": 0,
                            "enable": True,
                            "tgId": "",
                            "subId": f"{str(subId)}",
                            "comment": "",
                            "reset": 0
                        }
                    ],
                    "decryption": "none",
                    "fallbacks": []
                })

            # Output of the location
            # and the error itself to
            # the log.
            except Exception as err:
                log.error(
                    "An error has occurred in the "
                    "X_UI/create_connection.clients "
                    f"program block: {err}"
                )

                return False

            try:
                streamSettings = json.dumps({
                    "network": f"{network}",
                    "security": f"{security}",
                    "externalProxy": list(externalProxy),
                    "realitySettings": {
                        "show": bool(show),
                        "xver": int(xver),
                        "dest": f"{str(dest)}",
                        "serverNames": list(serverNames),
                        "privateKey": f"{str(private_key)}",
                        "minClient": "",
                        "maxClient": "",
                        "maxTimediff": 0,
                        "shortIds": list(short_ids),
                        "settings": {
                            "publicKey": f"{str(public_key)}",
                            "fingerprint": f"{fingerprint}",
                            "serverName": f"{serverName}",
                            "spiderX": f"{spiderX}"
                        }
                    },
                    "tcpSettings": {
                        "acceptProxyProtocol": bool(acceptProxyProtocol),
                        "header": {
                            "type": "none"
                        }
                    }
                })

            # Output of the location
            # and the error itself to
            # the log.
            except Exception as err:
                log.error(
                    "An error has occurred in the "
                    "X_UI/create_connection.streamSettings "
                    f"program block: {err}"
                )

                return False

            try:
                sniffing = json.dumps({
                    "enabled": bool(sniffing_enabled),
                    "destOverride": list(destOverride),
                    "metadataOnly": bool(metadataOnly),
                    "routeOnly": bool(routeOnly)
                })

            # Output of the location
            # and the error itself to
            # the log.
            except Exception as err:
                log.error(
                    "An error has occurred in the "
                    "X_UI/create_connection.sniffing "
                    f"program block: {err}"
                )

                return False

            try:
                allocate = json.dumps({
                    "strategy": f"{str(strategy)}",
                    "refresh": int(refresh),
                    "concurrency": int(concurrency)
                })

            # Output of the location
            # and the error itself to
            # the log.
            except Exception as err:
                log.error(
                    "An error has occurred in the "
                    "X_UI/create_connection.allocate "
                    f"program block: {err}"
                )

                return False

            try:
                payload = {
                    "up": int(up),
                    "down": int(down),
                    "total": int(total),
                    "remark": f"{str(remark)}",
                    "enable": bool(enable),
                    "expiryTime": int(expiryTime),
                    "listen": f"{str(listen)}",
                    "port": int(free_port),
                    "protocol": f"{str(protocol)}",
                    "settings": settings,
                    "streamSettings": streamSettings,
                    "sniffing": sniffing,
                    "allocate": allocate
                }

            # Output of the location
            # and the error itself to
            # the log.
            except Exception as err:
                log.error(
                    "An error has occurred in the "
                    "X_UI/create_connection.payload "
                    f"program block: {err}"
                )

                return False

            # Request to add a new connection.
            res = self.session.post(
                url=f"{self.x_ui_link}/panel/inbound/add",
                # Skipping the verification
                # of a self-signed certificate.
                verify=False,
                # Allows you to download the
                # response in parts, reducing
                # the memory load.
                stream=True,
                # Adding parameters and settings.
                json=payload
            )

            # Checking the successful
            # response from the server.
            if res.status_code == 200:

                # Converting the binary
                # response from the server
                # to JSON format.
                j_cont = json.loads(res.content)

                # Generating a message
                # for output to the user
                # and writing to the log.
                suc = f"SUCCESS: {j_cont['success']}"
                msg = f"MESSAGE: {j_cont['msg']}"

                # A separator for visual
                # differentiation.
                sep = '-' * (len(str(suc)) + len(str(msg)))

                # Checking that success
                # from the server is True.
                if j_cont['success']:
                    obj_data = j_cont['obj']

                    log.info(
                        'Connection added\n'
                        f'{sep}\n{suc}\n{msg}\n{sep}'
                    )

                    return True, [obj_data['id'], obj_data['port']]

                else:
                    # An informational message
                    # if success was False.
                    log.error(
                        'Add connection failed\n'
                        f'{sep}\n{suc}\n{msg}\n{sep}'
                    )

                    return False

            else:
                # Informing the user that an error
                # occurred when adding the connection.
                log.error(
                    f"[{res.status_code}]"
                    " - Couldn't add connection"
                )

                return False

        # Output of the location
        # and the error itself to
        # the log.
        except RequestException as err:
            log.error(
                "An error has occurred in the "
                "X_UI/create_connection "
                f"program block: {err}"
            )

            return False

    # Search for connections
    # to create a user.
    def search_connection(self):
        log.info(
            "Search for connections"
        )

        try:
            connections = self.get_connections()
            min_conn = min(connections[1], key=lambda x: x['clients_count'])

            return min_conn['conn_id']

        # Output of the location
        # and the error itself to
        # the log.
        except Exception as err:
            log.error(
                "An error has occurred in the "
                "X_UI/search_connection "
                f"program block: {err}"
            )

            return False

    # Creating a new client on
    # an existing connection.
    def add_client(self,
                   connection_id: int = 0,
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

        if connection_id == 0:
            connection_id = self.search_connection()

        # Checking that expiration time
        # contains any value greater than 0,
        # then converts days to seconds,
        # otherwise it makes the client
        # indefinite.
        if expirtyTime != 0:
            rental_period = -int(expirtyTime) * 24 * 60 * 60 * 1000
        else:
            rental_period = 0

        # Registering a uuid
        # for a new client.
        user_UUID = str(uuid.uuid1())

        try:
            payload = {
                # The connection id to create
                # a user in, default 0.
                "id": connection_id,
                "settings": json.dumps({
                    "clients": [{
                        # The client ID is always different
                        # and is generated using a uuid.
                        "id": user_UUID,
                        # flow - the flow through which the
                        # client's traffic will pass, default
                        # xtls-rprx-vision.
                        "flow": flow,
                        # email can be used as the client's name,
                        # with the default value being the client's
                        # uuid.
                        "email": email if email else user_UUID,
                        # limit limits the number of connections
                        # per client, default is 0.
                        "limitIp": limit_ip,
                        # totalGB limits the number of GB and after
                        # exhaustion, the traffic will stop going,
                        # default 0.
                        "totalGB": totalGB,
                        # expiration Time - the time in days, how
                        # long the client will be up to date, default 0.
                        "expiryTime": rental_period,
                        # enable - the client is enabled or disabled,
                        # default is True.
                        "enable": enable,
                        # tgId is the client's telegram ID,
                        # default 0.
                        "tgId": str(tgId) if tgId else "",
                        # subId is an additional client id,
                        # default 0.
                        "subId": "",
                        # comment - a comment for the client,
                        # the default value is the client's uuid.
                        "comment": comment if comment else user_UUID,
                        # reset - client reset,
                        # default 0.
                        "reset": 0
                    }]
                })
            }

            # Request to add a user.
            res = self.session.post(
                url=f"{self.x_ui_link}/panel/inbound/addClient",
                # Skipping the verification
                # of a self-signed certificate.
                verify=False,
                # Allows you to download the
                # response in parts, reducing
                # the memory load.
                stream=True,
                # Adding parameters and settings.
                json=payload
            )

            # Checking the successful
            # response from the server.
            if res.status_code == 200:

                # Converting the binary response
                # from the server to JSON format.
                j_cont = json.loads(res.content)

                # Generating a message
                # for output to the user
                # and writing to the log.
                suc = f"SUCCESS: {j_cont['success']}"
                msg = f"MESSAGE: {j_cont['msg']}"

                # A separator for visual
                # differentiation.
                sep = '-' * (
                    len(str(suc)) + len(str(msg))
                )

                # Checking that success
                # from the server is True.
                if j_cont['success']:
                    log.info(
                        "New user has been added\n"
                        f"{sep}\n{suc}\n{msg}\n{sep}"
                    )

                    return True

                else:
                    # An informational message
                    # if success was False.
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

        # Output of the location
        # and the error itself to
        # the log.
        except RequestException as err:
            log.error(
                "An error has occurred in the "
                "X_UI/add_client "
                f"program block: {err}"
            )

            return False

    # Checking xray activity.
    def xray_parse_active(self):
        log.info(
            "Getting xray status"
        )

        try:
            # A request to receive all
            # data on the x-ui system.
            res = self.session.post(
                url=f"{self.x_ui_link}/server/status",
                # Skipping the verification
                # of a self-signed certificate.
                verify=False,
                # Allows you to download the
                # response in parts, reducing
                # the memory load.
                stream=True,
            )

            # Checking the successful
            # response from the server.
            if res.status_code == 200:

                # Converting the binary response
                # from the server to JSON format.
                j_cont = json.loads(res.content)

                # Checking that success
                # from the server is True.
                if j_cont['success']:

                    obj_data = j_cont['obj']

                    # Xray status
                    xray_status = obj_data['xray']['state']

                    if xray_status == "running":
                        return True, xray_status
                    else:
                        return False

            else:
                log.error(
                    f"[{res.status_code}] An error "
                    "occurred when accessing the "
                    "server"
                )

                return False

        # Output of the location
        # and the error itself to
        # the log.
        except RequestException as err:
            log.error(
                "An error has occurred in the "
                "X_UI/xray_parse_active prog"
                f"ram block: {err}"
            )

            return False

    # Stopping the xray service.
    # If the xray auto-restart setting
    # is set on the server, True will
    # return and an error will be displayed
    # because xray will restart automatically.
    def xray_stop(self):
        log.info(
            "Stoping xray services"
        )

        try:
            # Request to stop xray completely.
            res = self.session.post(
                url=f"{self.x_ui_link}/server/stopXrayService",
                # Skipping the verification
                # of a self-signed certificate.
                verify=False,
                # Allows you to download the
                # response in parts, reducing
                # the memory load.
                stream=True,
            )

            # Checking the successful
            # response from the server.
            if res.status_code == 200:

                # Converting the binary response
                # from the server to JSON format.
                j_cont = json.loads(res.content)

                # Generating a message
                # for output to the user
                # and writing to the log.
                suc = f"SUCCESS: {j_cont['success']}"
                msg = f"MESSAGE: {j_cont['msg']}"

                # A separator for visual
                # differentiation.
                sep = '-' * (
                    len(str(suc)) + len(str(msg))
                )

                # Checking that success
                # from the server is True.
                if j_cont['success']:

                    # Checking that success from
                    # the xray server is True.
                    if self.xray_result():
                        for _ in range(10):
                            time.sleep(2)
                            # Checking the activity of xray
                            # after it is stopped to determine
                            # the automatic restart.
                            xray_active = self.xray_parse_active()
                            if xray_active:
                                break

                        # Checking that it returned True.
                        if xray_active:

                            # Information output
                            # about the error.
                            log.error(
                                    "Xray not stoped\n"
                                    "A request was sent "
                                    "to stop the xray service, "
                                    "but the service restarted "
                                    "instead."
                                )

                            return False

                        # It is expected to return False.
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

        # Output of the location
        # and the error itself to
        # the log.
        except RequestException as err:
            log.error(
                "An error has occurred in the "
                "X_UI/xray_stop"
                f"program block: {err}"
            )

            return False

    # Restarting the xray service.
    def xray_restart(self):
        log.info(
            "Restart xray services"
        )

        try:
            # Request to restart xray.
            res = self.session.post(
                url=f"{self.x_ui_link}/server/restartXrayService",
                # Skipping the verification
                # of a self-signed certificate.
                verify=False,
                # Allows you to download the
                # response in parts, reducing
                # the memory load.
                stream=True,
            )

            # Checking the successful
            # response from the server.
            if res.status_code == 200:

                # Converting the binary response
                # from the server to JSON format.
                j_cont = json.loads(res.content)

                # Generating a message
                # for output to the user
                # and writing to the log.
                suc = f"SUCCESS: {j_cont['success']}"
                msg = f"MESSAGE: {j_cont['msg']}"

                # A separator for visual
                # differentiation.
                sep = '-' * (
                    len(str(suc)) + len(str(msg))
                )

                # Checking that success
                # from the server is True.
                if j_cont['success']:

                    # Checking that success from
                    # the xray server is True.
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

        # Output of the location
        # and the error itself to
        # the log.
        except RequestException as err:
            log.error(
                "An error has occurred in the "
                "X_UI/xray_restart "
                f"program block: {err}"
            )

            return False

    # Checking the xray result.
    def xray_result(self):
        log.info(
            "Getting result xray services"
        )

        try:
            # Request to get the xray
            # result after reboot or
            # shutdown.
            res = self.session.get(
                url=f"{self.x_ui_link}/panel/xray/getXrayResult",
                # Skipping the verification
                # of a self-signed certificate.
                verify=False,
                # Allows you to download the
                # response in parts, reducing
                # the memory load.
                stream=True,
            )

            # Checking the successful
            # response from the server.
            if res.status_code == 200:

                # Converting the binary response
                # from the server to JSON format.
                j_cont = json.loads(res.content)

                # Checking that success
                # from the server is True.
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

        # Output of the location
        # and the error itself to
        # the log.
        except RequestException as err:
            log.error(
                "An error has occurred in the "
                "X_UI/xray_result"
                f"program block: {err}"
            )

            return False
