#coding:utf-8
import modbus_tk
import modbus_tk.defines as cst
import modbus_tk.modbus_tcp as modbus_tcp

"""
Coil和Register
　　Modbus中定义的两种数据类型。Coil是位（bit）变量；Register是整型（Word，即16-bit）变量。

Modbus中，数据可以分为两大类，分别为Coil和Register，每一种数据，根据读写方式的不同，又可细分为两种（只读，读写）。
Modbus四种数据类型：
　　Discretes Input　　　　位变量　　　　只读
　　Coils　　　　　　　　　 位变量　　　　读写
　　Input Registers　　　　16-bit整型 　 只读
　　Holding Registers 　　  16-bit整型 　 读写

功能码：
# 0区	输出线圈	  可读可写布尔量	00001-09999
# 1区	输入线圈	  只读布尔量	10001-19999
# 3区	输入寄存器	只读寄存器	30001-39999
# 4区	保持寄存器	可读可写寄存器	40001-49999
设备地址 　　　　Modbus地址　　    描述 　　                功能 　　R/W
1~10000 　　    address-1       Coils（Output）       0          R/W
10001~20000   address-10001    Discrete Inputs        01        R
30001~40000   address-30001    Input Registers        04        R
40001~50000   address-40001    Holding Registers     03        R/W
"""

logger = modbus_tk.utils.create_logger("console")
if __name__ == "__main__":
    try:
        # 连接MODBUS TCP从机
        master = modbus_tcp.TcpMaster(host="155.69.142.197", port=502)
        master.set_timeout(5.0)
        logger.info("Modbus connected successful!!!")
        # # 读保持寄存器
        # demo1 = master.execute(1, cst.READ_HOLDING_REGISTERS, 0, 9)
        # print(demo1)
        #
        # # 读输入寄存器
        # logger.info(master.execute(3, cst.READ_INPUT_REGISTERS, 0, 9, output_value=1))
        # # 读线圈寄存器
        # logger.info(master.execute(2, cst.READ_COILS, 0, 8))
        # logger.info(master.execute(2, cst.WRITE_SINGLE_COIL, 1, output_value=2))
        # 读离散输入寄存器
        # logger.info(master.execute(4, cst.READ_DISCRETE_INPUTS, 0, 8))
        # 单个读写寄存器操作
        # 写寄存器地址为0的保持寄存器
        # logger.info(master.execute(1, cst.WRITE_SINGLE_REGISTER, 0, output_value=25))
        # logger.info(master.execute(1, cst.READ_HOLDING_REGISTERS, 0, 8))
        # 写寄存器地址为0的线圈寄存器，写入内容为0（位操作）
        # logger.info(master.execute(2, cst.WRITE_SINGLE_COIL, 2, output_value=1))
        # logger.info(master.execute(2, cst.READ_COILS, 2, 1))
        # # # 多个寄存器读写操作
        # # # 写寄存器起始地址为0的保持寄存器，操作寄存器个数为4
        # logger.info(master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 0, output_value=[25,26,27,28,29,30]))
        # logger.info(master.execute(1, cst.READ_HOLDING_REGISTERS, 0, 4))
        # # # 写寄存器起始地址为0的线圈寄存器
        # logger.info(master.execute(2, cst.WRITE_MULTIPLE_COILS, 0, output_value=[1,0,1,1]))
        # logger.info(master.execute(2, cst.READ_COILS, 0, 4))

        # Float 大端
        #master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 0, output_value=[3.15], data_format='>f')
        #result_float = master.execute(101, cst.READ_HOLDING_REGISTERS, 0, 20)
        holding_registers_data = master.execute(100, cst.READ_HOLDING_REGISTERS, 0, 6, data_format='>fff')
        logger.info(holding_registers_data)
        holding_registers_data = master.execute(100, cst.READ_HOLDING_REGISTERS, 16, 6, data_format='>fff')
        logger.info(holding_registers_data)
        holding_registers_data = master.execute(100, cst.READ_HOLDING_REGISTERS, 54, 2, data_format='>f')
        logger.info(holding_registers_data)
        holding_registers_data = master.execute(100, cst.READ_HOLDING_REGISTERS, 58, 6, data_format='>fff')
        logger.info(holding_registers_data)
        holding_registers_data = master.execute(100, cst.READ_HOLDING_REGISTERS, 30, 2, data_format='>f')
        logger.info(holding_registers_data)
        holding_registers_data = master.execute(100, cst.READ_HOLDING_REGISTERS, 506, 2, data_format='>i')
        logger.info(holding_registers_data)

        # Int 大端
        #master.execute(1, cst.WRITE_MULTIPLE_REGISTERS, 2, output_value=[1], data_format='>i')
        #result_float = master.execute(1, cst.READ_HOLDING_REGISTERS, 2, 2, data_format='>i')
        #logger.info(holding_registers_data)
        #logger.info(input_registers_data)

    except modbus_tk.modbus.ModbusError as e:
        logger.error("%s- Code=%d" % (e, e.get_exception_code()))
