#-*- coding:utf-8 -*- 
#接收电机字节数
RECEIVE_MOTOR_DATA_NUM = 0
def setReceiveMotorDataNum(new):
    global RECEIVE_MOTOR_DATA_NUM
    RECEIVE_MOTOR_DATA_NUM = new

#接收接近传感器字节数
RECEIVE_SENSOR_DATA_NUM = 0
def setReceiveSensorDataNum(new):
    global RECEIVE_SENSOR_DATA_NUM
    RECEIVE_SENSOR_DATA_NUM = new

#发送电机字节数
SEND_TO_MOTOR_DATA_NUM = 0
def setSendToMotorDataNum(new):
    global SEND_TO_MOTOR_DATA_NUM
    SEND_TO_MOTOR_DATA_NUM = new

#发送接近传感器字节数
SEND_TO_SENSOR_DATA_NUM = 0
def setSendToSensorDataNum(new):
    global SEND_TO_SENSOR_DATA_NUM
    SEND_TO_SENSOR_DATA_NUM = new

#外侧接近传感器状态
OUTSIDE_SENSOR_FLAG = 0
def setOutsideSensorFlag(new):
    global OUTSIDE_SENSOR_FLAG
    OUTSIDE_SENSOR_FLAG = new

#离子束外侧边缘接近传感器
BEAM_OUTER_EDGE_CLOSER_SENSOR_FLAG = 0
def setBeamOuterEdgeCloserSensorFlag(new):
    global BEAM_OUTER_EDGE_CLOSER_SENSOR_FLAG
    BEAM_OUTER_EDGE_CLOSER_SENSOR_FLAG = new

#离子束内侧边缘接近传感器
BEAM_INNER_EDGE_CLOSER_SENSOR_FLAG = 0
def setBeamInnerEdgeCloserSensorFlag(new):
    global BEAM_INNER_EDGE_CLOSER_SENSOR_FLAG
    BEAM_INNER_EDGE_CLOSER_SENSOR_FLAG = new

#内侧接近传感器状态
INSIDE_SENSOR_FLAG = 0
def setInsideSensorFlag(new):
    global INSIDE_SENSOR_FLAG
    INSIDE_SENSOR_FLAG = new

#头部进入传感器状态
HEAD_FLAG = 0
def setHeadFlag(new):
    global HEAD_FLAG
    HEAD_FLAG = new

#尾部进入传感器状态
TAIL_FLAG = 0
def setTailFlag(new):
    global TAIL_FLAG
    TAIL_FLAG = new

#穿过beam外侧传感器次数
THROUGH_BEAM_OUTER_TIMES = 0
def setThroughBeamOuterTimes(new):
    global THROUGH_BEAM_OUTER_TIMES
    THROUGH_BEAM_OUTER_TIMES = new

#穿过beam内侧传感器次数
THROUGH_BEAM_INNER_TIMES = 0
def setThroughBeamInnerTimes(new):
    global THROUGH_BEAM_INNER_TIMES
    THROUGH_BEAM_INNER_TIMES = new    

#位移台位置参数（位于1、2、3、4、5区间）
REALTIME_POSITION = 1
def setRealtimePosition(new):
    global REALTIME_POSITION
    REALTIME_POSITION = new

#位移台实时速度（根据方向有正负，向内为正，向外为负）
REALTIME_VELOCITY = 0
def setRealtimeVelocity(new):
    global REALTIME_VELOCITY
    REALTIME_VELOCITY = new

#已完成扫描循环数
COMPLETED_LOOPS = 0
def setCompletedLoops(new):
    global COMPLETED_LOOPS
    COMPLETED_LOOPS = new

#开始扫描标志，可以扫描为1
SCAN_FLAG = 0
def setScanFlag(new):
    global SCAN_FLAG
    SCAN_FLAG = new

#标志扫描移动方向,1为向外，2为向里，3为停止
SCAN_DIRECTION = 3
def setScanDirection(new):
    global SCAN_DIRECTION
    SCAN_DIRECTION = new

#复位按钮的触发标志
REPOSITION_FLAG = 0
def setRepositionFlag(new):
    global REPOSITION_FLAG
    REPOSITION_FLAG = new

#反向延迟触发标志,区分2、3、4区间
DELAY_FLAG_2 = 1
def setDelayFlag2(new):
    global DELAY_FLAG_2
    DELAY_FLAG_2 = new

DELAY_FLAG_3 = 1
def setDelayFlag3(new):
    global DELAY_FLAG_3
    DELAY_FLAG_3 = new

DELAY_FLAG_4 = 1
def setDelayFlag4(new):
    global DELAY_FLAG_4
    DELAY_FLAG_4 = new

    