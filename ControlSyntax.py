#-*- coding:utf-8 -*- 
#向里走按钮，速度固定为500速
BUTTON_MOVE_INSIDE_SYNTAX = "01 02 00 00 00 00 01 F4 F8"
def setButtonMoveInSideSyntax(new):
    global BUTTON_MOVE_INSIDE_SYNTAX
    BUTTON_MOVE_INSIDE_SYNTAX = new

#向外走按钮，速度固定为500速
BUTTON_MOVE_OUTSIDE_SYNTAX = "01 01 00 00 00 00 01 F4 F7"
def setButtonMoveOutSideSyntax(new):
    global BUTTON_MOVE_OUTSIDE_SYNTAX
    BUTTON_MOVE_OUTSIDE_SYNTAX = new

#停止电机
BUTTON_MOVE_STOP_SYNTAX = "01 03 00 00 00 00 01 F4 F9"
def setButtonMoveStopSyntax(new):
    global BUTTON_MOVE_STOP_SYNTAX
    BUTTON_MOVE_STOP_SYNTAX = new

#查询接近传感器状态语句
SENSOR_COMM_SYNTAX = "01 03 00 00 00 08 44 0C"
def setControlSyntax(new):
    global SENSOR_COMM_SYNTAX
    SENSOR_COMM_SYNTAX = new