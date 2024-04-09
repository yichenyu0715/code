import socket
import threading
import time

from crcmod import crcmod



class CollectIndicator:
    def __init__(self):
        self.tcp_sockets = {}
        self.upload_data = {}
        self.order = '01 03 00 00 00 02'  # 温湿度传感器查询指令

    def start_thread(self):
        from main import temperature_control_system
        for sensor_name, sensor_config in temperature_control_system.sensor_config.items():
            # 按照温湿度传感器个数，创建线程，与设备建立连接
            print(f"启动线程采集{sensor_name}传感器信息")
            threading.Thread(target=self.refresh_indicator, args=(sensor_name, sensor_config,)).start()

    def refresh_indicator(self, sensor_name, sensor_config):
        try:
            if sensor_name not in self.tcp_sockets:
                self.tcp_sockets[sensor_name] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                addr = (sensor_config.get("host"), int(sensor_config.get("port")))
                self.tcp_sockets[sensor_name].connect(addr)
                self.tcp_sockets[sensor_name].settimeout(3)
        except Exception as e:
            print(f"温湿度传感器：{sensor_name} 连接失败, {e}")
            time.sleep(5)
        while True:
            try:
                order_hex = self.order.split()
                order_bytes = bytes.fromhex(''.join(order_hex))
                self.tcp_sockets[sensor_name].send(order_bytes)
                time.sleep(1)
                # 温湿度传感器示例指令：01 03 04 01 F5 00 FD 01F5为湿度 00FD为温度 00FD转为十进制是253，当前温度是25.3℃
                data = self.tcp_sockets[sensor_name].recvfrom(1024)
                # 向ET103上报的数据
                self.upload_data[int(sensor_config.get("upload_port"))] = data
                self.parse_indicator(data, sensor_config)
            except Exception as e:
                print(f'发送温湿度传感器指令失败， {e}')
            finally:
                time.sleep(1)

    def parse_indicator(self, data, sensor_config):
        # 解析数据 如果温度过高，需要发送指令
        sensor_num = sensor_config.get("sensor_num")
        maximum_temperature = sensor_config.get("sensor_num")
        data_list = []
        for bytes_data in data[0]:
            data_list.append(hex(bytes_data)[2:].zfill(2))
        temp = float(int(''.join(data_list[-2:]), 16) / 10)
        try:
            last_temp = getattr(self, sensor_num, temp)
        except AttributeError as e:
            last_temp = ''
        if last_temp == temp:
            return
        setattr(self, sensor_num, temp)
        # 如果温度过高
        if temp > maximum_temperature:
            # 匹配对应空调
            for air_condition, config in temperature_control_system.air_condition_config.items():
                if config.get('sensor_num') == sensor_num:
                    try:
                        if air_condition not in self.tcp_sockets:
                            self.tcp_sockets[air_condition] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            addr = (config.get("host"), int(config.get("port")))
                            self.tcp_sockets[air_condition].connect(addr)
                            self.tcp_sockets[air_condition].settimeout(3)
                    except Exception as e:
                        print(f"空调：{air_condition} 连接失败, {e}")
                        time.sleep(5)
                    # 发送温度控制指令
                    order_hex = f'{config.get("address")} 10 00 00 00 04 08 00 AA 01 01 02 {hex(config.get("target_temperature")).zfill(2)} 03 04 '
                    crc16_command = bytes.fromhex(order_hex)
                    crc16_func = crcmod.predefined.Crc('modbus')
                    crc16_func.update(crc16_command)
                    crc = crc16_func.digest().hex()
                    crc_comand = crc[-2:] + ' ' + crc[:2]
                    code = order_hex + crc_comand
                    order_bytes = bytes.fromhex(''.join(order_hex))
                    self.tcp_sockets[air_condition].send(order_bytes)
                    time.sleep(1)
                    # 发送温控指令


collect_instance = CollectIndicator()