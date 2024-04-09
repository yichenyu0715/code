import configparser
import socket
import threading
import time
import collect_indicator


class UploadServer:
    def __init__(self):
        self.server = {}
        config = configparser.ConfigParser()
        config.read('./conf.ini', encoding='utf-8')
        self.ET103_host = config.get("ET103", "ET103.host")
        # 绑定第一个地址和端口号

    def start(self):
        threading.Thread(target=self.upload_data).start()
        print("开始上报数据至ET103")

    def upload_data(self):
        while True:
            try:
                for port, data in collect_indicator.collect_instance.upload_data.items():
                    if port not in self.server:
                        self.server[port] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.server[port].bind((self.ET103_host, port))
                        self.server[port].listen()
                    conn, addr = self.server[port].accept()
                    with conn:
                        print(f'{port} Connected by {addr}')
                        conn.send(data)
                        time.sleep(1)
            except Exception as e:
                print("上报数据异常", e)
            finally:
                time.sleep(1)


upload_server = UploadServer()
