from flask import Flask, request, jsonify, render_template, url_for, redirect
from flask_login import login_user, logout_user, UserMixin, LoginManager, login_required
from flask_sqlalchemy import SQLAlchemy
from threading import Thread, Event
from queue import Queue
import time, json
from datetime import datetime, timedelta
import modbus_tk.defines as cst
import modbus_tk.modbus_tcp as modbus_tcp
from flask_migrate import Migrate

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, Integer, SmallInteger, DECIMAL, DateTime, Float

from jsonschema import validate
from validate_params import schema
from decimal import Decimal

MYSQL_HOST = '155.69.142.189'
MYSQL_USERNAME = 'root'
MYSQL_PASSWORD = 'Modbus123!'

MODBUS_TCP_SERVER = '155.69.142.197'
MODBUS_TCP_PORT = 502

db_url = 'mysql+pymysql://{username}:{password}@{hostname}:{port}/{database}?charset=utf8'.format(
    username=MYSQL_USERNAME, password=MYSQL_PASSWORD, hostname=MYSQL_HOST, port='3306', database='modbus')

# 创建引擎
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
dbSession = Session()
Base = declarative_base(engine)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Bruh'
app.config['DEBUG'] = 'Test'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@192.168.0.130:3306/modbus'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://%s:%s@%s:3306/modbus' % (
    MYSQL_USERNAME, MYSQL_PASSWORD, MYSQL_HOST)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db)
g_queue = Queue()
g_event = Event()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.login_message = 'Please login first'
login_manager.init_app(app)


class AirConditionerModel(Base):
    __tablename__ = "air_conditioner"
    id = Column(Integer(), primary_key=True)
    # Holding Register (R/W)
    room_temperature_setpoint = Column(DECIMAL(3, 1))
    valve_ovr_flag = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Auto, 1: Override
    valve_ovr_cmd = Column(DECIMAL(4, 1))  # 0~100%
    fcu_ss_ovr_flag = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Auto, 1: Override
    fcu_ss_ovr_cmd = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Start
    fcu_speed_ovr_flag = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Auto, 1: Override
    fcu_speed_ovr_cmd = Column(SmallInteger(), nullable=False, default=0)  # 0: Stop, 1: Low, 2: Med, 3: High
    # Input Register (R)
    room_temperature_1 = Column(DECIMAL(3, 1))
    room_temperature_2 = Column(DECIMAL(3, 1))
    room_humidity_1 = Column(DECIMAL(4, 1))  # 0~100%
    room_humidity_2 = Column(DECIMAL(4, 1))  # 0~100%
    bms_local = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Local, 1: BMS
    fcu_ss_cmd = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Start
    fcu_status = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Running
    fcu_trip = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Normal, 1: TRIP
    fcu_low_speed = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Running
    fcu_med_speed = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Running
    fcu_high_speed = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Running
    off_coil_temperature = Column(DECIMAL(3, 1))
    water_leakage_status = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Norma, 1: Overflow
    chws_temperature = Column(DECIMAL(3, 1))
    chwr_temperature = Column(DECIMAL(3, 1))
    chw_flow_rate = Column(DECIMAL(6, 1))
    chw_valve_cmd = Column(DECIMAL(4, 1))  # 0~100%
    chw_valve_position = Column(DECIMAL(4, 1))  # 0~100%
    fcu_airflow_rate = Column(SmallInteger(), nullable=False, default=0)
    # Power Input Register (R)
    U = Column(DECIMAL(7, 3))
    I = Column(DECIMAL(7, 3))
    PF = Column(DECIMAL(6, 4))
    Phase_Angle = Column(DECIMAL(5, 3))
    W = Column(Integer())
    Kvar = Column(DECIMAL(6, 2))
    KWH = Column(DECIMAL(11, 2))
    time = Column(DateTime, nullable=False)


class AirConditionerLastDataModel(Base):
    __tablename__ = "air_conditioner_last_data"
    id = Column(Integer(), primary_key=True)
    # Holding Register (R/W)
    room_temperature_setpoint = Column(DECIMAL(3, 1))
    valve_ovr_flag = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Auto, 1: Override
    valve_ovr_cmd = Column(DECIMAL(4, 1))  # 0~100%
    fcu_ss_ovr_flag = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Auto, 1: Override
    fcu_ss_ovr_cmd = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Start
    fcu_speed_ovr_flag = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Auto, 1: Override
    fcu_speed_ovr_cmd = Column(SmallInteger(), nullable=False, default=0)  # 0: Stop, 1: Low, 2: Med, 3: High
    # Input Register (R)
    room_temperature_1 = Column(DECIMAL(3, 1))
    room_temperature_2 = Column(DECIMAL(3, 1))
    room_humidity_1 = Column(DECIMAL(4, 1))  # 0~100%
    room_humidity_2 = Column(DECIMAL(4, 1))  # 0~100%
    bms_local = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Local, 1: BMS
    fcu_ss_cmd = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Start
    fcu_status = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Running
    fcu_trip = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Normal, 1: TRIP
    fcu_low_speed = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Running
    fcu_med_speed = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Running
    fcu_high_speed = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Running
    off_coil_temperature = Column(DECIMAL(3, 1))
    water_leakage_status = Column(SmallInteger(), nullable=False, default=0)  # 0/1, 0: Norma, 1: Overflow
    chws_temperature = Column(DECIMAL(3, 1))
    chwr_temperature = Column(DECIMAL(3, 1))
    chw_flow_rate = Column(DECIMAL(6, 1))
    chw_valve_cmd = Column(DECIMAL(4, 1))  # 0~100%
    chw_valve_position = Column(DECIMAL(4, 1))  # 0~100%
    fcu_airflow_rate = Column(SmallInteger(), nullable=False, default=0)
    # Power Input Register (R)
    U = Column(DECIMAL(7, 3))
    I = Column(DECIMAL(7, 3))
    PF = Column(DECIMAL(6, 4))
    Phase_Angle = Column(DECIMAL(5, 3))
    W = Column(Integer())
    Kvar = Column(DECIMAL(6, 2))
    KWH = Column(DECIMAL(11, 2))
    time = Column(DateTime, nullable=False)


class AirConditioner(db.Model):
    __tablename__ = "air_conditioner"
    id = db.Column(db.Integer(), primary_key=True)
    # Holding Register (R/W)
    room_temperature_setpoint = db.Column(db.DECIMAL(3, 1))
    valve_ovr_flag = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Auto, 1: Override
    valve_ovr_cmd = db.Column(db.DECIMAL(4, 1))  # 0~100%
    fcu_ss_ovr_flag = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Auto, 1: Override
    fcu_ss_ovr_cmd = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Start
    fcu_speed_ovr_flag = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Auto, 1: Override
    fcu_speed_ovr_cmd = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0: Stop, 1: Low, 2: Med, 3: High
    # Input Register (R)
    room_temperature_1 = db.Column(db.DECIMAL(3, 1))
    room_temperature_2 = db.Column(db.DECIMAL(3, 1))
    room_humidity_1 = db.Column(db.DECIMAL(4, 1))  # 0~100%
    room_humidity_2 = db.Column(db.DECIMAL(4, 1))  # 0~100%
    bms_local = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Local, 1: BMS
    fcu_ss_cmd = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Start
    fcu_status = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Running
    fcu_trip = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Normal, 1: TRIP
    fcu_low_speed = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Running
    fcu_med_speed = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Running
    fcu_high_speed = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Running
    off_coil_temperature = db.Column(db.DECIMAL(3, 1))
    water_leakage_status = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Norma, 1: Overflow
    chws_temperature = db.Column(db.DECIMAL(3, 1))
    chwr_temperature = db.Column(db.DECIMAL(3, 1))
    chw_flow_rate = db.Column(DECIMAL(6, 1))
    chw_valve_cmd = db.Column(db.DECIMAL(4, 1))  # 0~100%
    chw_valve_position = db.Column(db.DECIMAL(4, 1))  # 0~100%
    fcu_airflow_rate = db.Column(db.SmallInteger(), nullable=False, default=0)
    # Power Input Register (R)
    U = Column(DECIMAL(7, 3))
    I = Column(DECIMAL(7, 3))
    PF = Column(DECIMAL(6, 4))
    Phase_Angle = Column(DECIMAL(5, 3))
    W = Column(Integer())
    Kvar = Column(DECIMAL(6, 2))
    KWH = Column(DECIMAL(11, 2))
    time = db.Column(db.DateTime, nullable=False)


def to_json(inst, cls):  # 自定义数据类型转换将object转换为json
    ret_dict = {}
    for i in cls.__table__.columns:  # 获取到模型对象的所有列
        # R/W Holding Register 不返回
        if i.name in ['valve_ovr_flag', 'valve_ovr_cmd', 'fcu_ss_ovr_flag', 'fcu_ss_ovr_cmd', 'fcu_speed_ovr_flag',
                      'fcu_speed_ovr_cmd', 'Kvar', 'Phase_Angle']:
            continue
        value = getattr(inst, i.name)  # 获取对象的属性值
        if isinstance(value, Decimal):
            value = float(value)
        if isinstance(value, datetime):  # 对时间进行转换
            value = value + timedelta(hours=8)
            value = value.strftime('%Y-%m-%d %H:%M:%S')
        ret_dict[i.name] = value  # 添加到字典中
    return ret_dict


class AirConditionerLastData(db.Model):
    __tablename__ = "air_conditioner_last_data"
    id = db.Column(db.Integer(), primary_key=True)
    # Holding Register (R/W)
    room_temperature_setpoint = db.Column(db.DECIMAL(3, 1))
    valve_ovr_flag = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Auto, 1: Override
    valve_ovr_cmd = db.Column(db.DECIMAL(4, 1))  # 0~100%
    fcu_ss_ovr_flag = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Auto, 1: Override
    fcu_ss_ovr_cmd = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Start
    fcu_speed_ovr_flag = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Auto, 1: Override
    fcu_speed_ovr_cmd = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0: Stop, 1: Low, 2: Med, 3: High
    # Input Register (R)
    room_temperature_1 = db.Column(db.DECIMAL(3, 1))
    room_temperature_2 = db.Column(db.DECIMAL(3, 1))
    room_humidity_1 = db.Column(db.DECIMAL(4, 1))  # 0~100%
    room_humidity_2 = db.Column(db.DECIMAL(4, 1))  # 0~100%
    bms_local = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Local, 1: BMS
    fcu_ss_cmd = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Start
    fcu_status = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Running
    fcu_trip = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Normal, 1: TRIP
    fcu_low_speed = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Running
    fcu_med_speed = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Running
    fcu_high_speed = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Stop, 1: Running
    off_coil_temperature = db.Column(db.DECIMAL(3, 1))
    water_leakage_status = db.Column(db.SmallInteger(), nullable=False, default=0)  # 0/1, 0: Norma, 1: Overflow
    chws_temperature = db.Column(db.DECIMAL(3, 1))
    chwr_temperature = db.Column(db.DECIMAL(3, 1))
    chw_flow_rate = db.Column(DECIMAL(6, 1))
    chw_valve_cmd = db.Column(db.DECIMAL(4, 1))  # 0~100%
    chw_valve_position = db.Column(db.DECIMAL(4, 1))  # 0~100%
    fcu_airflow_rate = db.Column(db.SmallInteger(), nullable=False, default=0)
    # Power Input Register (R)
    U = Column(DECIMAL(7, 3))
    I = Column(DECIMAL(7, 3))
    PF = Column(DECIMAL(6, 4))
    Phase_Angle = Column(DECIMAL(5, 3))
    W = Column(Integer())
    Kvar = Column(DECIMAL(6, 2))
    KWH = Column(DECIMAL(11, 2))
    time = db.Column(db.DateTime, nullable=False)

    @property  # 使用property获取对象的属性
    def serialize(self):
        return to_json(self, self.__class__)  # 直接返回实例对象本身和类本身


class User(UserMixin):
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return '1'


class ModbusBase(object):
    def __init__(self):
        self.host = MODBUS_TCP_SERVER
        self.port = MODBUS_TCP_PORT
        try:
            self.master = modbus_tcp.TcpMaster(host=self.host, port=self.port)
            self.master.set_timeout(3.0)
        except:
            print('not connected')

    def reconnect(self):
        try:
            self.master.open()
        except:
            print('Reconnected Failed!')


class ModbusReadThread(ModbusBase, Thread):
    def __init__(self, event):
        Thread.__init__(self)
        ModbusBase.__init__(self)
        self.event = event

    def read_registers(self):
        U = self.master.execute(100, cst.READ_HOLDING_REGISTERS, 0, 2, data_format='>f')
        I = self.master.execute(100, cst.READ_HOLDING_REGISTERS, 16, 2, data_format='>f')
        W = self.master.execute(100, cst.READ_HOLDING_REGISTERS, 30, 2, data_format='>f')
        Kvar = self.master.execute(100, cst.READ_HOLDING_REGISTERS, 38, 2, data_format='>f')
        PF = self.master.execute(100, cst.READ_HOLDING_REGISTERS, 54, 2, data_format='>f')
        Phase_Angle = self.master.execute(100, cst.READ_HOLDING_REGISTERS, 58, 2, data_format='>f')
        KWH = self.master.execute(100, cst.READ_HOLDING_REGISTERS, 506, 2, data_format='>i')
        power_registers_data = [U[0], I[0], W[0], Kvar[0], PF[0], Phase_Angle[0], KWH[0]]
        time.sleep(1)  # 延时，给切换Slave设备提供时间
        holding_registers_data = self.master.execute(101, cst.READ_HOLDING_REGISTERS, 0, 7)
        input_registers_data = self.master.execute(101, cst.READ_INPUT_REGISTERS, 0, 19)
        return holding_registers_data, input_registers_data, power_registers_data

    def __copy_item(self, new_item, original_item):
        for attr in dir(new_item):
            if not attr.startswith('_') and attr not in ['id', 'metadata']:
                setattr(new_item, attr, getattr(original_item, attr))
        return new_item

    def __save_last_data(self, item):
        last_data = dbSession.query(AirConditionerLastDataModel).first()
        if last_data is None:
            last_data = AirConditionerLastDataModel()
            last_data = self.__copy_item(last_data, item)
            dbSession.add(last_data)
            dbSession.commit()
        else:
            last_data = self.__copy_item(last_data, item)
            dbSession.commit()
        return

    def decode_data_and_save(self, holding_registers_data, input_registers_data, power_registers_data):
        item = AirConditionerModel()
        item.room_temperature_setpoint = float(holding_registers_data[0]) / 10.0
        item.valve_ovr_flag = holding_registers_data[1]
        item.valve_ovr_cmd = float(holding_registers_data[2]) / 10.0
        item.fcu_ss_ovr_flag = holding_registers_data[3]
        item.fcu_ss_ovr_cmd = holding_registers_data[4]
        item.fcu_speed_ovr_flag = holding_registers_data[5]
        item.fcu_speed_ovr_cmd = holding_registers_data[6]

        item.room_temperature_1 = float(input_registers_data[0]) / 10.0
        item.room_temperature_2 = float(input_registers_data[1]) / 10.0
        item.room_humidity_1 = float(input_registers_data[2]) / 10.0
        item.room_humidity_2 = float(input_registers_data[3]) / 10.0
        item.bms_local = input_registers_data[4]
        item.fcu_ss_cmd = input_registers_data[5]
        item.fcu_status = input_registers_data[6]
        item.fcu_trip = input_registers_data[7]
        item.fcu_low_speed = input_registers_data[8]
        item.fcu_med_speed = input_registers_data[9]
        item.fcu_high_speed = input_registers_data[10]
        item.off_coil_temperature = float(input_registers_data[11]) / 10.0
        item.water_leakage_status = input_registers_data[12]
        item.chws_temperature = float(input_registers_data[13]) / 10.0
        item.chwr_temperature = float(input_registers_data[14]) / 10.0
        item.chw_flow_rate = float(input_registers_data[15]) / 10.0
        item.chw_valve_cmd = float(input_registers_data[16]) / 10.0
        item.chw_valve_position = float(input_registers_data[17]) / 10.0
        item.fcu_airflow_rate = input_registers_data[18]

        # [U, I, W, Kvar, PF, Phase_Angle, KWH]
        item.U = power_registers_data[0]
        item.I = power_registers_data[1]
        item.W = power_registers_data[2]
        item.Kvar = power_registers_data[3]
        item.PF = power_registers_data[4]
        item.Phase_Angle = power_registers_data[5]
        item.KWH = float(power_registers_data[6]) / 100.0
        item.time = datetime.utcnow()  # + timedelta(hours=8)

        dbSession.add(item)
        dbSession.commit()
        self.__save_last_data(item)
        return

    def run(self):
        while True:
            self.event.wait(timeout=30)
            holding_registers_data = None
            input_registers_data = None
            power_registers_data = None
            try:
                holding_registers_data, input_registers_data, power_registers_data = self.read_registers()
            except:
                print('lost connection')
                time.sleep(1 * 60)
                self.reconnect()
            if holding_registers_data and input_registers_data and power_registers_data:
                self.decode_data_and_save(holding_registers_data, input_registers_data, power_registers_data)
            self.event.clear()


class ModbusWriteThread(ModbusBase, Thread):
    def __init__(self, event, queue):
        Thread.__init__(self)
        ModbusBase.__init__(self)
        self.event = event
        self.queue = queue

    def write_registers(self, data):
        room_temperature_setpoint = data.get('room_temperature_setpoint', None)
        if room_temperature_setpoint is not None:
            room_temperature_setpoint = int(room_temperature_setpoint * 10)
            self.master.execute(101, cst.WRITE_SINGLE_REGISTER, 0, output_value=room_temperature_setpoint)

        valve_ovr_flag = data.get('valve_ovr_flag', None)
        if valve_ovr_flag is not None:
            self.master.execute(101, cst.WRITE_SINGLE_REGISTER, 1, output_value=valve_ovr_flag)
            valve_ovr_cmd = data.get('valve_ovr_cmd', None)
            if valve_ovr_flag == 1 and valve_ovr_cmd is not None:
                valve_ovr_cmd = int(valve_ovr_cmd * 10)
                self.master.execute(101, cst.WRITE_SINGLE_REGISTER, 2, output_value=valve_ovr_cmd)

        fcu_ss_ovr_flag = data.get('fcu_ss_ovr_flag', None)
        if fcu_ss_ovr_flag is not None:
            self.master.execute(101, cst.WRITE_SINGLE_REGISTER, 3, output_value=fcu_ss_ovr_flag)
            fcu_ss_ovr_cmd = data.get('fcu_ss_ovr_cmd', None)
            if fcu_ss_ovr_flag == 1 and fcu_ss_ovr_cmd is not None:
                self.master.execute(101, cst.WRITE_SINGLE_REGISTER, 4, output_value=fcu_ss_ovr_cmd)

        fcu_speed_ovr_flag = data.get('fcu_speed_ovr_flag', None)
        if fcu_speed_ovr_flag is not None:
            self.master.execute(101, cst.WRITE_SINGLE_REGISTER, 5, output_value=fcu_speed_ovr_flag)
            fcu_speed_ovr_cmd = data.get('fcu_speed_ovr_cmd', None)
            if fcu_speed_ovr_flag == 1 and fcu_speed_ovr_cmd is not None:
                self.master.execute(101, cst.WRITE_SINGLE_REGISTER, 6, output_value=fcu_speed_ovr_cmd)
        return

    def run(self):
        while True:
            data = self.queue.get()
            try:
                self.write_registers(data)
                self.event.set()
                print("------------write ok")
            except:
                print('lost connection')
                self.reconnect()
            self.queue.task_done()


def set_registers(data):
    try:
        validate(instance=data, schema=schema)
    except Exception as e:
        return jsonify({"msg": "Params invalid",
                        "detail": str(e)})
    g_queue.put(data)

    time.sleep(3)
    # 返回设置的数据
    item = db.session.query(AirConditionerLastData).first()
    data = {
        "room_temperature_setpoint": float(item.room_temperature_setpoint),
        "valve_ovr_flag": item.valve_ovr_flag,
        "valve_ovr_cmd": float(item.valve_ovr_cmd),
        "fcu_ss_ovr_flag": item.fcu_ss_ovr_flag,
        "fcu_ss_ovr_cmd": item.fcu_ss_ovr_cmd,
        "fcu_speed_ovr_flag": item.fcu_speed_ovr_flag,
        "fcu_speed_ovr_cmd": item.fcu_speed_ovr_cmd
    }
    return data


@app.route('/airconditioner', methods=['GET', 'POST'])
def registers():
    if request.method == 'POST':
        data = request.data
        data = json.loads(data)
        data = set_registers(data)
        return jsonify({"msg": "OK", 'data': data})
    elif request.method == 'GET':
        data = db.session.query(AirConditionerLastData).first()
        return jsonify({'msg': 'OK', 'data': data.serialize})


@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'GET':
        registers = db.session.query(AirConditionerLastData).first()
        registers.time = registers.time + timedelta(hours=8)
        return render_template('index.html', registers=registers)
    elif request.method == 'POST':
        data = {
            "room_temperature_setpoint": float(request.form.get('room_temperature_setpoint')),
            "valve_ovr_flag": int(request.form.get('valve_ovr_flag')),
            "valve_ovr_cmd": float(request.form.get('valve_ovr_cmd')),
            "fcu_ss_ovr_flag": int(request.form.get('fcu_ss_ovr_flag')),
            "fcu_ss_ovr_cmd": int(request.form.get('fcu_ss_ovr_cmd')),
            "fcu_speed_ovr_flag": int(request.form.get('fcu_speed_ovr_flag')),
            "fcu_speed_ovr_cmd": int(request.form.get('fcu_speed_ovr_cmd'))
        }
        set_registers(data)
        return redirect(url_for('home'))


@login_manager.user_loader
def load_user(user_id):
    user = User()
    return user


@app.route('/', methods=['GET'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'Modbus123!':
            user = User()
            login_user(user)
            return redirect(url_for('home'))
        else:
            return redirect(url_for('login'))


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))


read_thread = ModbusReadThread(g_event)
read_thread.daemon = True
read_thread.start()
print("Starting ReadThread")

write_thread = ModbusWriteThread(g_event, g_queue)
write_thread.daemon = True
write_thread.start()
print("Starting WriteThread")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
