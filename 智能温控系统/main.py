import configparser
import re


class TemperatureControlSystem:
    def __init__(self):
        # 创建 ConfigParser 对象
        self.sensor_list = None
        self.air_condition_list = None
        self.sensor_config = {}
        self.air_condition_config = {}
        self.init_config()

    def init_config(self):
        # 读取配置文件
        config = configparser.ConfigParser()
        config.read('./conf.ini', encoding='utf-8')
        sections = config.sections()
        # 正则表达式匹配空调、温湿度配置，动态加载。
        # 空调
        air_condition_pattern = r"air-conditioning\w+"
        self.air_condition_list = [re.findall(air_condition_pattern, section)[0] for section in sections if
                                   re.findall(air_condition_pattern, section)]
        # 温湿度
        sensor_pattern = r"sensor\w+"
        self.sensor_list = [re.findall(sensor_pattern, section)[0] for section in sections if
                            re.findall(sensor_pattern, section)]
        # 组装缓存
        for sensor in self.sensor_list:
            self.sensor_config[sensor] = {
                'host': config.get(f'{sensor}', f'{sensor}.host'),
                'port': config.get(f'{sensor}', f'{sensor}.port'),
                'sensor_num': config.get(f'{sensor}', f'{sensor}.sensor_num'),
                'maximum_temperature': config.get(f'{sensor}', f'{sensor}.maximum_temperature'),
                'upload_port': config.get(f'{sensor}', f'{sensor}.upload_port')
            }
        for air_condition in self.air_condition_list:
            self.air_condition_config[air_condition] = {
                'host': config.get(f'{air_condition}', f'{air_condition}.host'),
                'port': config.get(f'{air_condition}', f'{air_condition}.port'),
                'sensor_num': config.get(f'{air_condition}', f'{air_condition}.sensor_num'),
                'target_temperature': config.get(f'{air_condition}', f'{air_condition}.target_temperature'),
                'address': config.get(f'{air_condition}', f'{air_condition}.address'),
            }


temperature_control_system = TemperatureControlSystem()

if __name__ == '__main__':
    # 程序入口
    pass
    # 读取配置信息
    # 采集和温控
    # 上报
