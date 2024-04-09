import collect_indicator
from init_config import temperature_control_system
from upload_server import upload_server

if __name__ == '__main__':
    # 程序入口 main方法只会在执行时加载，因此main中不要写单例，否则别的类调用该实例为空
    # 读取配置信息
    temperature_control_system.start()
    # 采集和温控
    collect_indicator.collect_instance.start_thread()
    # 上报
    upload_server.start()
