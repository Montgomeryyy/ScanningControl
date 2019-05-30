#-*- coding:utf-8 -*- 
import string
import sys
import serial
import configparser
import numpy as np
import time

from PyQt5 import QtWidgets,QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import pyqtgraph as pg
import ControlSyntax
import ScanningParameters
import StatsData
from MainSerial import Ui_MainWindow
from SerialPortSet import Ui_SerialPortSet
from BeamDetection import Ui_BeamDetection
from AboutMe import Ui_AboutMe

class MainControlWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainControlWindow, self).__init__()
        self.setupUi(self)
        self.initWigetsStatus()
        self.initIcon()
        self.serMotor=serial.Serial()
        self.serSensor=serial.Serial() 
        self.init()

    #初始化图标
    def initIcon(self):
        icon = QtGui.QIcon("./Spider.png")
        self.setWindowIcon(icon)        
    
    #初始化部件状态
    def initWigetsStatus(self):
        self.velocitySpinBox_1.setValue(ScanningParameters.SCAN_VELOCITY_1)
        self.velocitySpinBox_2.setValue(ScanningParameters.SCAN_VELOCITY_2)
        self.velocitySpinBox_3.setValue(ScanningParameters.SCAN_VELOCITY_3)
        self.velocitySpinBox_4.setValue(ScanningParameters.SCAN_VELOCITY_4)
        self.velocitySpinBox_5.setValue(ScanningParameters.SCAN_VELOCITY_5)
        self.accelerationSpinBox_1.setValue(ScanningParameters.SCAN_ACCELERATION_1)
        self.accelerationSpinBox_2.setValue(ScanningParameters.SCAN_ACCELERATION_2)
        self.accelerationSpinBox_3.setValue(ScanningParameters.SCAN_ACCELERATION_3)
        self.accelerationSpinBox_4.setValue(ScanningParameters.SCAN_ACCELERATION_4)
        self.accelerationSpinBox_5.setValue(ScanningParameters.SCAN_ACCELERATION_5)

    def init(self):
        self.intervalTime = 200
        #创建速度设置曲线画布
        self.verticalLayout = QVBoxLayout(self.velocitySetCurveFrame)
        self.velocitySetCurve = pg.GraphicsLayoutWidget(self.velocitySetCurveFrame)
        self.verticalLayout.addWidget(self.velocitySetCurve)
        #初始化速度设置图
        self.p = self.velocitySetCurve.addPlot(title="变速预设曲线")
        self.p.showGrid(x=True,y=True)
        self.p.setLabel(axis="left",text="速度")
        self.p.setLabel(axis="bottom",text="区间")
        self.p.setTitle("变速预设曲线")
        self.curve1 = self.p.plot(pen=pg.mkPen("r",width=2))  #设置pen 格式
        self.generate_velocitySetCurve()

        #创建实时速度显示曲线画布
        self.verticalLayout2 = QVBoxLayout(self.realtimeVelocityCurveFrame)
        self.realtimeVelocityCurve = pg.GraphicsLayoutWidget(self.realtimeVelocityCurveFrame)
        self.verticalLayout2.addWidget(self.realtimeVelocityCurve)
        #初始化实时速度显示曲线
        self.realV = [0,]
        self.realT = [0,]
        self.p2 = self.realtimeVelocityCurve.addPlot(title="扫描速度实时检测曲线")
        self.p2.showGrid(x=True,y=True)
        self.p2.setLabel(axis="left",text="速度")
        self.p2.setLabel(axis="bottom",text="时间/s")
        self.p2.setTitle("扫描速度实时检测曲线")
        self.curve2 = self.p2.plot(pen=pg.mkPen("r",width=2))  #设置pen 格式
        self.generate_realtimeVelocityCurve()
        
        #检测速度输入框的修改
        self.velocitySpinBox_1.valueChanged.connect(self.generate_velocitySetCurve)
        self.velocitySpinBox_2.valueChanged.connect(self.generate_velocitySetCurve)
        self.velocitySpinBox_3.valueChanged.connect(self.generate_velocitySetCurve)
        self.velocitySpinBox_4.valueChanged.connect(self.generate_velocitySetCurve)
        self.velocitySpinBox_5.valueChanged.connect(self.generate_velocitySetCurve)
        
        #############按钮槽函数############
        #接近传感器状态指示灯
        self.outsideLEDColor = QColor(10,10,10)
        self.beamOuterEdgeSensorLEDColor = QColor(10,10,10)
        self.beamInnerEdgeSensorLEDColor = QColor(10,10,10)
        self.insideLEDColor = QColor(10,10,10)

        #check按钮
        self.checkButton.clicked.connect(self.initDefaultSerialPort)

        #确认参数按钮
        self.confirmParameterButton.clicked.connect(self.loadScanningParameter)
        
        #开始扫描按钮
        self.startScanButton.clicked.connect(self.startScan)

        #紧急停止扫描按钮
        self.stopScanButton.clicked.connect(self.stopScan)

        #修改参数按钮
        self.changeParameterButton.clicked.connect(self.changeScanParameters)

        #向内走按钮
        self.MoveInside.clicked.connect(self.motorMoveInside)

        #向外走按钮
        self.MoveOutside.clicked.connect(self.motorMoveOutside)

        #复位按钮
        self.MoveToOriginalLocation.clicked.connect(self.motorMoveToOriginalLocation)
        
        #停止按钮
        self.Stop.clicked.connect(self.motorMoveStop)

        ##############计时器触发函数##################
        #定时向接近传感器发送查询数据
        self.sendTimer = QTimer(self)
        self.sendTimer.start(self.intervalTime)
        self.sendTimer.timeout.connect(self.inquireSensorStatus)

        #定时接收接近传感器数据
        self.receiveTimer = QTimer(self)
        self.receiveTimer.start(self.intervalTime)
        self.receiveTimer.timeout.connect(self.receiveStatusAndExecuteScanLoops)

        ###############初始化计算已完成扫描周期、位移台位置、区分不同周期的参数############
        self.inquireTimes = 0
        self.determineCompletedLoops = [0] * 2
        self.beamOuterSensorSignal = [0] * 2
        self.beamInnerSensorSignal  = [0] * 2
        self.differentLoops = [0] * 2
        
        #计算反向延迟计数
        self.delayCount2 = 0
        self.delayCount3 = 0
        self.delayCount4 = 0

        #初始化串口参数
        self.Config = configparser.ConfigParser()
        self.Config.read('Config.ini') 
        self.serMotor.port = self.Config.get("SerialSetting","motor_port")
        self.serMotor.baudrate = self.Config.getint("SerialSetting","motor_baudrate")
        self.serMotor.bytesize = self.Config.getint("SerialSetting","motor_bytesize")
        self.serMotor.stopbits = self.Config.getint("SerialSetting","motor_stopbytes")
        self.serMotor.parity = self.Config.get("SerialSetting","motor_parity")
        self.serSensor.port = self.Config.get("SerialSetting","sensor_port")
        self.serSensor.baudrate = self.Config.getint("SerialSetting","sensor_baudrate")
        self.serSensor.bytesize = self.Config.getint("SerialSetting","sensor_bytesize")
        self.serSensor.stopbits = self.Config.getint("SerialSetting","sensor_stopbytes")
        self.serSensor.parity = self.Config.get("SerialSetting","sensor_parity")

    
    #更新速度设置图
    def generate_velocitySetCurve(self):
        ScanningParameters.SCAN_VELOCITY_1 = int(self.velocitySpinBox_1.value())
        ScanningParameters.SCAN_VELOCITY_2 = int(self.velocitySpinBox_2.value())
        ScanningParameters.SCAN_VELOCITY_3 = int(self.velocitySpinBox_3.value())
        ScanningParameters.SCAN_VELOCITY_4 = int(self.velocitySpinBox_4.value())
        ScanningParameters.SCAN_VELOCITY_5 = int(self.velocitySpinBox_5.value())
        x = [0, 1, 1, 2, 2, 3, 3, 4, 4, 5]
        y = [ScanningParameters.SCAN_VELOCITY_1, ScanningParameters.SCAN_VELOCITY_1, 
                ScanningParameters.SCAN_VELOCITY_2, ScanningParameters.SCAN_VELOCITY_2,
                ScanningParameters.SCAN_VELOCITY_3, ScanningParameters.SCAN_VELOCITY_3,
                ScanningParameters.SCAN_VELOCITY_4, ScanningParameters.SCAN_VELOCITY_4,
                ScanningParameters.SCAN_VELOCITY_5, ScanningParameters.SCAN_VELOCITY_5]
        self.curve1.setData(x, y)
    
    def generate_realtimeVelocityCurve(self):
        self.realT.append(self.realT[-1] + self.intervalTime/1000)
        self.realV.append(StatsData.REALTIME_VELOCITY)
        self.curve2.setData(self.realT, self.realV)

    #check按钮，初始化串口设置
    def initDefaultSerialPort(self):
        self.openSerialPort()
        StatsData.setCompletedLoops(0)
        StatsData.setReceiveMotorDataNum(0)
        StatsData.setReceiveSensorDataNum(0)
        StatsData.setSendToMotorDataNum(0)
        StatsData.setSendToSensorDataNum(0)     

    #打开串口和定时器
    def openSerialPort(self):
        if (self.serMotor.isOpen() == False):
            try:
                self.serMotor.open()   
            except:
                self.checkButton.setEnabled(True)
                QMessageBox.critical(self, "Port Error", "电机串口不能被打开，请检查串口配置！")
                self.serMotor.close()
                self.serSensor.close() 
        else:
            self.checkMessageTextBrowser.insertPlainText("上位机：电机串口已打开，请勿重复操作!" + '\n')
            textCursor = self.checkMessageTextBrowser.textCursor()
            textCursor.movePosition(textCursor.End)
            self.checkMessageTextBrowser.setTextCursor(textCursor)

        if (self.serSensor.isOpen() == False):
            try:
                self.serSensor.open()
            except:
                self.checkButton.setEnabled(True)
                QMessageBox.critical(self, "Port Error", "接近传感器串口不能被打开，请检查串口配置！")
                self.serMotor.close()
                self.serSensor.close()
        else:
            self.checkMessageTextBrowser.insertPlainText("上位机：接近传感器串口已打开，请勿重复操作!" + '\n')
            textCursor = self.checkMessageTextBrowser.textCursor()
            textCursor.movePosition(textCursor.End)
            self.checkMessageTextBrowser.setTextCursor(textCursor)

        #打开定时器
        if ~self.sendTimer.isActive():
            #print('sendtimer open')
            self.sendTimer.start(self.intervalTime)
        if ~self.receiveTimer.isActive():
            #print('receiveTimer open')
            self.receiveTimer.start(self.intervalTime)

        if self.serSensor.isOpen() and self.serMotor.isOpen():
            self.checkMessageTextBrowser.insertPlainText("上位机：电机和接近传感器串口已打开!" + '\n')
            textCursor = self.checkMessageTextBrowser.textCursor()
            textCursor.movePosition(textCursor.End)
            self.checkMessageTextBrowser.setTextCursor(textCursor)
            #如果两个串口均能正常打开，则开始持续查询接近传感器状态，并将CHECK按键置为不可用
            self.inquireSensorStatus()



    #关闭串口和定时器
    def closeSerialPort(self):
        self.sendTimer.stop()
        self.receiveTimer.stop()
        if (self.serMotor.isOpen() == True):
            try:
                self.serMotor.close()
            except:
                QMessageBox.critical(self, "Port Error", "无法关闭电机串口，请检查后再试！")
        else:
            self.checkMessageTextBrowser.insertPlainText("上位机：电机串口已关闭，请勿重复操作!" + '\n')
            textCursor = self.checkMessageTextBrowser.textCursor()
            textCursor.movePosition(textCursor.End)
            self.checkMessageTextBrowser.setTextCursor(textCursor)

        if (self.serSensor.isOpen() == True):
            try:
                self.serSensor.close()
            except:
                QMessageBox.critical(self, "Port Error", "无法关闭接近传感器串口，请检查后再试！")
        else:
            self.checkMessageTextBrowser.insertPlainText("上位机：电机串口已关闭，请勿重复操作!" + '\n')
            textCursor = self.checkMessageTextBrowser.textCursor()
            textCursor.movePosition(textCursor.End)
            self.checkMessageTextBrowser.setTextCursor(textCursor)

    #设置扫描周期和移动速度    
    def loadScanningParameter(self):
        velocity1 = self.velocitySpinBox_1.value()
        velocity2 = self.velocitySpinBox_2.value()
        velocity3 = self.velocitySpinBox_3.value()
        velocity4 = self.velocitySpinBox_4.value()
        velocity5 = self.velocitySpinBox_5.value()

        #读取设置的分区延迟时间
        delayTime4 = self.backwardDelay4SpinBox.value()
        delay4SendTimes = int(1000*delayTime4/self.intervalTime)

        delayTime3 = self.backwardDelay3SpinBox.value()
        delay3SendTimes = int(1000*delayTime3/self.intervalTime)

        delayTime2 = self.backwardDelay2SpinBox.value()
        delay2SendTimes = int(1000*delayTime2/self.intervalTime)

        ScanningParameters.setScanVelocity1(velocity1)
        ScanningParameters.setScanVelocity2(velocity2)
        ScanningParameters.setScanVelocity3(velocity3)
        ScanningParameters.setScanVelocity4(velocity4)
        ScanningParameters.setScanVelocity5(velocity5)

        ScanningParameters.setScanBackwardDelay4(delayTime4)
        ScanningParameters.setScanBackwardDelay4SendTimes(delay4SendTimes)
        ScanningParameters.setScanBackwardDelay3(delayTime3)
        ScanningParameters.setScanBackwardDelay3SendTimes(delay3SendTimes)
        ScanningParameters.setScanBackwardDelay2(delayTime2)
        ScanningParameters.setScanBackwardDelay2SendTimes(delay2SendTimes)

        periods = self.periodsSpinBox.value()
        ScanningParameters.setScanPeriods(periods)

        if periods and velocity1 and velocity2 and velocity3 and velocity4 and velocity5:
            pass
        else:
            QMessageBox.critical(self,"Value Error", "请输入有效的参数！")

        self.checkMessageTextBrowser.insertPlainText("上位机：设置扫描速度为 " + '\n' +"区间1："+ str(ScanningParameters.SCAN_VELOCITY_1) + '\n' +
                                                        "区间2："+ str(ScanningParameters.SCAN_VELOCITY_2) + '\n' +
                                                        "区间3："+ str(ScanningParameters.SCAN_VELOCITY_3) + '\n' +
                                                        "区间4："+ str(ScanningParameters.SCAN_VELOCITY_4) + '\n' +
                                                        "区间5："+ str(ScanningParameters.SCAN_VELOCITY_5) + '\n' +
                                                        "区间4反向延时："+ str( ScanningParameters.SCAN_BACKWARD_DELAY_4) + 's' + '\n' +
                                                        "区间4反向延时发送次数："+ str( ScanningParameters.SCAN_BACKWARD_DELAY_4_SEND_TIMES) + '次' + '\n' +
                                                        "区间3反向延时："+ str( ScanningParameters.SCAN_BACKWARD_DELAY_3) + 's' + '\n' +
                                                        "区间3反向延时发送次数："+ str( ScanningParameters.SCAN_BACKWARD_DELAY_3_SEND_TIMES) + '次' + '\n' +
                                                        "区间2反向延时："+ str( ScanningParameters.SCAN_BACKWARD_DELAY_2) + 's' + '\n' +
                                                        "区间2反向延时发送次数："+ str( ScanningParameters.SCAN_BACKWARD_DELAY_2_SEND_TIMES) + '次' + '\n' +
                                                        "上位机：设置扫描周期为 " + str(ScanningParameters.SCAN_PERIODS) + '\n')
        textCursor = self.checkMessageTextBrowser.textCursor()
        textCursor.movePosition(textCursor.End)
        self.checkMessageTextBrowser.setTextCursor(textCursor)

        
    #开使扫描按钮
    def startScan(self):
        #如果台子不在外接近传感器处，则需要先将台子复位
        if StatsData.OUTSIDE_SENSOR_FLAG != 1:
            QMessageBox.critical(self, "Position Error", "位移台未置于起始位置，请调整后再扫描！")
        else:
            if self.serMotor.isOpen():
                self.inquireTimes = 0
                self.delayCount2 = 0
                self.delayCount3 = 0
                self.delayCount4 = 0
                StatsData.setDelayFlag2(1)
                StatsData.setDelayFlag3(1)
                StatsData.setDelayFlag4(1)
                
                StatsData.setCompletedLoops(0)
                self.determineCompletedLoops = [0] * 2
                self.beamOuterSensorSignal = [0] * 2
                self.beamInnerSensorSignal  = [0] * 2
                StatsData.setScanFlag(1)
            else:
                QMessageBox.critical(self, "Port Error", "电机串口未打开，请检查后再试！")

    #紧急停止扫描按钮
    def stopScan(self):
        stopSyntax = self.calControlSyntax(1, StatsData.REALTIME_VELOCITY)
        if self.serMotor.isOpen() == True:
            self.sendControlStatements(stopSyntax, self.serMotor.port)
        self.closeSerialPort()
        self.checkMessageTextBrowser.insertPlainText("上位机：已关闭所有串口！"  + '\n')
        textCursor = self.checkMessageTextBrowser.textCursor()
        textCursor.movePosition(textCursor.End)
        self.checkMessageTextBrowser.setTextCursor(textCursor)
    
    #修改扫描参数按钮
    def changeScanParameters(self):
        periods=self.periodsSpinBox.value()
        ScanningParameters.setScanPeriods(periods)
        self.checkMessageTextBrowser.insertPlainText("上位机：重新设置扫描周期为 " + str(ScanningParameters.SCAN_PERIODS) + '\n')
        textCursor = self.checkMessageTextBrowser.textCursor()
        textCursor.movePosition(textCursor.End)
        self.checkMessageTextBrowser.setTextCursor(textCursor)

    #向里走
    def motorMoveInside(self):
        StatsData.setScanFlag(0)
        StatsData.setRealtimeVelocity(500)
        if self.serMotor.isOpen() == True:
            self.sendControlStatements(ControlSyntax.BUTTON_MOVE_INSIDE_SYNTAX, self.serMotor.port)
        else:
            self.checkMessageTextBrowser.insertPlainText("上位机：串口未打开，无法执行指令！ " + '\n')
            textCursor = self.checkMessageTextBrowser.textCursor()
            textCursor.movePosition(textCursor.End)
            self.checkMessageTextBrowser.setTextCursor(textCursor)
        
    #向外走
    def motorMoveOutside(self):
        StatsData.setScanFlag(0)
        StatsData.setRealtimeVelocity(-500)
        if self.serMotor.isOpen() == True:
            self.sendControlStatements(ControlSyntax.BUTTON_MOVE_OUTSIDE_SYNTAX, self.serMotor.port)
        else:
            self.checkMessageTextBrowser.insertPlainText("上位机：串口未打开，无法执行指令！ " + '\n')
            textCursor = self.checkMessageTextBrowser.textCursor()
            textCursor.movePosition(textCursor.End)
            self.checkMessageTextBrowser.setTextCursor(textCursor)

    #停止移动
    def motorMoveStop(self):
        StatsData.setScanFlag(0)
        StatsData.setRealtimeVelocity(0)
        if self.serMotor.isOpen() == True:
            self.sendControlStatements(ControlSyntax.BUTTON_MOVE_STOP_SYNTAX, self.serMotor.port)
        else:
            self.checkMessageTextBrowser.insertPlainText("上位机：串口未打开，无法执行指令！ " + '\n')
            textCursor = self.checkMessageTextBrowser.textCursor()
            textCursor.movePosition(textCursor.End)
            self.checkMessageTextBrowser.setTextCursor(textCursor)

    #回到起点
    def motorMoveToOriginalLocation(self):
        StatsData.setScanFlag(0)
        StatsData.setRealtimeVelocity(-500)
        StatsData.REPOSITION_FLAG = 1

    #定时发送数据查询接近传感器状态
    def inquireSensorStatus(self):
        if self.serSensor.isOpen() == True:
            self.sendControlStatements(ControlSyntax.SENSOR_COMM_SYNTAX, self.serSensor.port)

    #计算电机控制语句
    def calControlSyntax(self, button, velocity):
        #button = 0代表在扫描循环中自主调用该函数，由StatsData确认走的方向
        if button == 0:  
            #1向外走，2向里走，3停止
            scanDirection = StatsData.SCAN_DIRECTION
            if scanDirection == 1:
                strD = "01 01 "
            elif scanDirection == 2:
                strD = "01 02 "
            elif scanDirection == 3:
                strD = "01 03 "
            else:
                QMessageBox.critical(self, "Syntax Error", "电机控制语句计算错误！")
        #button = 1代表使用紧急停止按钮调用该函数，直接设置方向为停止
        elif button == 1:
            strD = "01 03 "
        else:
            QMessageBox.critical(self, "Function Error", "calMotorControl函数输入参数错误！")

        #根据移动速度计算控制语句
        scanVelocity = int(velocity)
        hexScanVelocity = hex(scanVelocity)
        strHexScanVelocity = str(hexScanVelocity[2:])
        
        lenStr = len(strHexScanVelocity)
        lenZero = 12 - lenStr
        S = "0"*lenZero+strHexScanVelocity
        listS = list(S)
        listV = list(" "*17)
        num =  0
        space = 0
        while num <= 16:
            if num % 3 != 2:
                listV[num] = listS[num-space]       
            else:
                listV[num] = " "
                space = space + 1
            num = num + 1
        strV =''.join(listV)
        strDV = strD + strV

        #计算校验位
        num2 = 0
        space2 = 0
        i = 0
        a=list("x"*9)
        b=''
        while num2 <= 22:
            if num2 % 3 == 0:
                if strDV[num2:num2+2] != "":
                    a[i] =(int(('0x' + strDV[num2:num2+2]),16))
                else:
                    a[i] = ""
                # print(a)
                i += 1
            num2 += 1    

        i = 0 
        sub = 0
        while i<=7:
            sub = a[i] + sub
            i += 1
            hexSub = hex(sub)
            # print(hexSub)
        strHexSub = str(hexSub)
        #如果strHexSub小于16，即0x1~0xf的格式，则在数据位前补一个0
        if len(strHexSub) == 3:
            strHexSub = "0" + strHexSub[-1:]
        else:
            strHexSub = strHexSub[-2:]
        calOutput = strDV.strip() + ' ' + strHexSub
        # print(calOutput)
        return calOutput

    #发送指令
    def sendControlStatements(self, sendString, CommNumber):
        input_string = sendString.strip()
        send_list = []
        while input_string != '':
            try:
                num = int(input_string[0:2], 16)
            except ValueError:
                QMessageBox.critical(self, 'wrong data', '请输入十六进制数据，以空格分开!')
                return None
            input_string = input_string[2:].strip()
            send_list.append(num)
        input_string = bytes(send_list)
        lenData = len(input_string)
        if CommNumber == self.serMotor.port:
            StatsData.setSendToMotorDataNum(StatsData.SEND_TO_MOTOR_DATA_NUM + lenData)
            num = self.serMotor.write(input_string)
            self.sendToMotorMessageTextBrowser.insertPlainText("上位机>>>电机：" + sendString + '\n')
            textCursor = self.sendToMotorMessageTextBrowser.textCursor()
            textCursor.movePosition(textCursor.End)
            self.sendToMotorMessageTextBrowser.setTextCursor(textCursor)
        elif CommNumber == self.serSensor.port:
            StatsData.setSendToSensorDataNum(StatsData.SEND_TO_SENSOR_DATA_NUM + lenData)
            num = self.serSensor.write(input_string)
            self.sendToSensorMessageTextBrowser.insertPlainText("上位机>>>接近传感器：" + sendString + '\n')
            textCursor = self.sendToSensorMessageTextBrowser.textCursor()
            textCursor.movePosition(textCursor.End)
            self.sendToSensorMessageTextBrowser.setTextCursor(textCursor)
        else:
            QMessageBox.critical(self, 'port error', 'sendControlStatements函数串口号参数错误!')

    #接收指令
    def receiveStatements(self, CommNumber):
        if CommNumber == self.serMotor.port:
            try:
                buffer = self.serMotor.inWaiting()
            except:
                self.closeSerialPort()
                return None
            if buffer > 0:
                data = self.serMotor.read(buffer)
                lenData = len(data)
                #hex显示
                showData = ''
                for i in range(0, len(data)):
                    showData = showData + '{:02X}'.format(data[i]) + ' '
                #统计接收到的字符数
                StatsData.setReceiveMotorDataNum(StatsData.RECEIVE_MOTOR_DATA_NUM + lenData)
                return showData, StatsData.RECEIVE_MOTOR_DATA_NUM
            else:
                return 0, 0

        elif CommNumber == self.serSensor.port:
            try:
                buffer = self.serSensor.inWaiting()
            except:
                self.closeSerialPort()
                return None
            if buffer > 0:
                data = self.serSensor.read(buffer)
                lenData = len(data)
                #hex显示
                showData = ''
                for i in range(0, len(data)):
                    showData = showData + '{:02X}'.format(data[i]) + ' '
                #统计接收到的字符数
                StatsData.setReceiveSensorDataNum(StatsData.RECEIVE_SENSOR_DATA_NUM + lenData)
                # print(showData)
                return showData, StatsData.RECEIVE_SENSOR_DATA_NUM
            else:
                return 0, 0
        else:
            QMessageBox.critical(self, 'port error', 'receiveStatements函数串口号参数错误!')

    #接收接近传感器状态并执行扫描循环
    def receiveStatusAndExecuteScanLoops(self):
        if (self.serMotor.isOpen() == True) and (self.serSensor.isOpen() == True):
            (sensorData,sensorDataNum) = self.receiveStatements(self.serSensor.port)
            (motorData,motorDataNum) = self.receiveStatements(self.serMotor.port)
            #如果能接收到接近传感器的信息，则开始查询传感器状态
            if sensorDataNum != 0:
                #读取接近传感器状态，外侧接近传感器接在通道0，束流外侧接近传感器接在通道1，束流内测传感器接在通道2，内测接近传感器接在通道3，并写入各传感器Flag
                rawSensorData = str(sensorData)
                raw2SensorData = rawSensorData.replace(" ",'')
                hexSensorPotential0 = "0x" + raw2SensorData[6:10]
                hexSensorPotential1 = "0x" + raw2SensorData[10:14]
                hexSensorPotential2 = "0x" + raw2SensorData[14:18]
                hexSensorPotential3 = "0x" + raw2SensorData[18:22]
                #print(hexSensorPotential0, hexSensorPotential1, hexSensorPotential2, hexSensorPotential3)
                potential0 = int(hexSensorPotential0, 16)
                potential1 = int(hexSensorPotential1, 16)
                potential2 = int(hexSensorPotential2, 16)
                potential3 = int(hexSensorPotential3, 16)
                #print(potential0, potential1, potential2, potential3)

                if potential0 <= 300:
                    StatsData.setOutsideSensorFlag(1)
                else:
                    StatsData.setOutsideSensorFlag(0)

                if potential1 <= 300:
                    StatsData.setBeamOuterEdgeCloserSensorFlag(1)
                else:
                    StatsData.setBeamOuterEdgeCloserSensorFlag(0)

                if potential2 <= 300:
                    StatsData.setBeamInnerEdgeCloserSensorFlag(1)
                else:
                    StatsData.setBeamInnerEdgeCloserSensorFlag(0)

                if potential3 <= 300:
                    StatsData.setInsideSensorFlag(1)
                else:
                    StatsData.setInsideSensorFlag(0)

                #判断查询周期
                if self.inquireTimes <= 1:
                    self.determineCompletedLoops[self.inquireTimes] = StatsData.OUTSIDE_SENSOR_FLAG
                    self.beamOuterSensorSignal[self.inquireTimes] = StatsData.BEAM_OUTER_EDGE_CLOSER_SENSOR_FLAG
                    self.beamInnerSensorSignal[self.inquireTimes] = StatsData.BEAM_INNER_EDGE_CLOSER_SENSOR_FLAG
                    self.differentLoops[self.inquireTimes] = StatsData.COMPLETED_LOOPS
                else:
                    self.determineCompletedLoops[0] = self.determineCompletedLoops[1]
                    self.determineCompletedLoops[1] = StatsData.OUTSIDE_SENSOR_FLAG

                    self.beamOuterSensorSignal[0] = self.beamOuterSensorSignal[1]
                    self.beamOuterSensorSignal[1] = StatsData.BEAM_OUTER_EDGE_CLOSER_SENSOR_FLAG

                    self.beamInnerSensorSignal[0] = self.beamInnerSensorSignal[1]
                    self.beamInnerSensorSignal[1] = StatsData.BEAM_INNER_EDGE_CLOSER_SENSOR_FLAG

                    self.differentLoops[0] = self.differentLoops[1]
                    self.differentLoops[1] = StatsData.COMPLETED_LOOPS
                
                #根据是否进入新的一个扫描周期来决定是否重置反向延迟标志
                if self.differentLoops[1] - self.differentLoops[0] == 1:
                    StatsData.setDelayFlag2(1)
                    StatsData.setDelayFlag3(1)
                    StatsData.setDelayFlag4(1)
                else:
                    pass

                if self.determineCompletedLoops[1] - self.determineCompletedLoops[0] == 1:
                    if self.inquireTimes >= 15:
                        StatsData.setCompletedLoops(StatsData.COMPLETED_LOOPS + 1)   
                    #print(self.determineCompletedLoops[1], self.determineCompletedLoops[0], StatsData.COMPLETED_LOOPS)  
                elif self.beamOuterSensorSignal[1] - self.beamOuterSensorSignal[0] == 1:
                    StatsData.setThroughBeamOuterTimes(StatsData.THROUGH_BEAM_OUTER_TIMES + 1)
                elif self.beamInnerSensorSignal[1] - self.beamInnerSensorSignal[0] == 1:
                    StatsData.setThroughBeamInnerTimes(StatsData.THROUGH_BEAM_INNER_TIMES + 1)
                else:
                    pass

                self.inquireTimes += 1
            
                #判断电机所处位置，并且已完成的扫描周期还不到设定值，则发送循环指令
                if StatsData.COMPLETED_LOOPS < ScanningParameters.SCAN_PERIODS and StatsData.SCAN_FLAG == 1:
                    if StatsData.OUTSIDE_SENSOR_FLAG == 1:      #即将正向进入区间1
                        StatsData.setRealtimePosition(1)
                        StatsData.setRealtimeVelocity(ScanningParameters.SCAN_VELOCITY_1)
                        StatsData.setScanDirection(2)
                        sendToMotorSyntax = self.calControlSyntax(0, StatsData.REALTIME_VELOCITY)
                        self.sendControlStatements(sendToMotorSyntax, self.serMotor.port)
                    if StatsData.BEAM_OUTER_EDGE_CLOSER_SENSOR_FLAG == 1:
                        if StatsData.THROUGH_BEAM_OUTER_TIMES % 4 == 1:      #即将正向进入区间2
                            StatsData.setRealtimePosition(2)
                            StatsData.setRealtimeVelocity(ScanningParameters.SCAN_VELOCITY_2)
                            sendToMotorSyntax = self.calControlSyntax(0, StatsData.REALTIME_VELOCITY)
                            self.sendControlStatements(sendToMotorSyntax, self.serMotor.port)
                        elif StatsData.THROUGH_BEAM_OUTER_TIMES % 4 == 2:    #即将正向进入区间3
                            StatsData.setRealtimePosition(3)
                            StatsData.setRealtimeVelocity(ScanningParameters.SCAN_VELOCITY_3)
                            sendToMotorSyntax = self.calControlSyntax(0, StatsData.REALTIME_VELOCITY)
                            self.sendControlStatements(sendToMotorSyntax, self.serMotor.port)
                        elif StatsData.THROUGH_BEAM_OUTER_TIMES % 4 == 3:    #即将反向进入区间2
                            #反向进入，添加延时
                            #待解决问题：每个周期反向要仅睡一次，暂定通过对比completed loops实现
                            if StatsData.DELAY_FLAG_2 == 1:
                                if self.delayCount2 < ScanningParameters.SCAN_BACKWARD_DELAY_2_SEND_TIMES:
                                    self.delayCount2 = self.delayCount2 + 1
                                    self.sendToMotorMessageTextBrowser.insertPlainText("上位机>>>电机：" + 'delay!' + '\n')
                                    textCursor = self.sendToMotorMessageTextBrowser.textCursor()
                                    textCursor.movePosition(textCursor.End)
                                    self.sendToMotorMessageTextBrowser.setTextCursor(textCursor)
                                else:
                                    self.delayCount2 = 0
                                    StatsData.setDelayFlag2(0)
                            else:
                                StatsData.setRealtimePosition(2)
                                StatsData.setRealtimeVelocity(-ScanningParameters.SCAN_VELOCITY_2)
                                sendToMotorSyntax = self.calControlSyntax(0, abs(StatsData.REALTIME_VELOCITY))
                                self.sendControlStatements(sendToMotorSyntax, self.serMotor.port)
                            print('self.delayCount2:'+str(self.delayCount2)+'StatsData.DELAY_FLAG_2:'+str(StatsData.DELAY_FLAG_2))
                        else:                                                #即将反向进入区间1
                            StatsData.setRealtimePosition(1)
                            StatsData.setRealtimeVelocity(-ScanningParameters.SCAN_VELOCITY_1)
                            sendToMotorSyntax = self.calControlSyntax(0, abs(StatsData.REALTIME_VELOCITY))
                            self.sendControlStatements(sendToMotorSyntax, self.serMotor.port)
                    if StatsData.BEAM_INNER_EDGE_CLOSER_SENSOR_FLAG == 1:
                        if  StatsData.THROUGH_BEAM_INNER_TIMES % 4 == 1:      #即将正向进入区间4
                            StatsData.setRealtimePosition(4)
                            StatsData.setRealtimeVelocity(ScanningParameters.SCAN_VELOCITY_4)
                            sendToMotorSyntax = self.calControlSyntax(0, StatsData.REALTIME_VELOCITY)
                            self.sendControlStatements(sendToMotorSyntax, self.serMotor.port)
                        elif StatsData.THROUGH_BEAM_INNER_TIMES % 4 == 2:      #即将正向进入区间5
                            StatsData.setRealtimePosition(5)
                            StatsData.setRealtimeVelocity(ScanningParameters.SCAN_VELOCITY_5)
                            sendToMotorSyntax = self.calControlSyntax(0, StatsData.REALTIME_VELOCITY)
                            self.sendControlStatements(sendToMotorSyntax, self.serMotor.port)
                        elif StatsData.THROUGH_BEAM_INNER_TIMES % 4 == 3:      #即将反向向进入区间4
                            #反向进入，添加延时
                            if StatsData.DELAY_FLAG_4 == 1:
                                if self.delayCount4 < ScanningParameters.SCAN_BACKWARD_DELAY_4_SEND_TIMES:
                                    self.delayCount4 = self.delayCount4 + 1
                                    self.sendToMotorMessageTextBrowser.insertPlainText("上位机>>>电机：" + 'delay!' + '\n')
                                    textCursor = self.sendToMotorMessageTextBrowser.textCursor()
                                    textCursor.movePosition(textCursor.End)
                                    self.sendToMotorMessageTextBrowser.setTextCursor(textCursor)
                                else:
                                    self.delayCount4 = 0
                                    StatsData.setDelayFlag4(0)
                            else:
                                StatsData.setRealtimePosition(4)
                                StatsData.setRealtimeVelocity(-ScanningParameters.SCAN_VELOCITY_4)
                                sendToMotorSyntax = self.calControlSyntax(0, abs(StatsData.REALTIME_VELOCITY))
                                self.sendControlStatements(sendToMotorSyntax, self.serMotor.port)
                            print('self.delayCount4:'+str(self.delayCount4)+'StatsData.DELAY_FLAG_4:'+str(StatsData.DELAY_FLAG_4))
                        else :                                                 #即将反向进入区间3
                            #反向进入，添加延时
                            if StatsData.DELAY_FLAG_3 == 1:
                                if self.delayCount3 < ScanningParameters.SCAN_BACKWARD_DELAY_3_SEND_TIMES:
                                    self.delayCount3 = self.delayCount3 + 1
                                    self.sendToMotorMessageTextBrowser.insertPlainText("上位机>>>电机：" + 'delay!' + '\n')
                                    textCursor = self.sendToMotorMessageTextBrowser.textCursor()
                                    textCursor.movePosition(textCursor.End)
                                    self.sendToMotorMessageTextBrowser.setTextCursor(textCursor)
                                else:
                                    self.delayCount3 = 0
                                    StatsData.setDelayFlag3(0)
                            else:
                                StatsData.setRealtimePosition(3)
                                StatsData.setRealtimeVelocity(-ScanningParameters.SCAN_VELOCITY_3)
                                sendToMotorSyntax = self.calControlSyntax(0, abs(StatsData.REALTIME_VELOCITY)) 
                                self.sendControlStatements(sendToMotorSyntax, self.serMotor.port)  
                            print('self.delayCount3:'+str(self.delayCount3)+'StatsData.DELAY_FLAG_3:'+str(StatsData.DELAY_FLAG_3))
                    if StatsData.INSIDE_SENSOR_FLAG == 1:                    #即将反向进入区间5
                        StatsData.setScanDirection(1)
                        StatsData.setRealtimePosition(5)
                        StatsData.setRealtimeVelocity(-ScanningParameters.SCAN_VELOCITY_5)
                        sendToMotorSyntax = self.calControlSyntax(0, abs(StatsData.REALTIME_VELOCITY)) 
                        self.sendControlStatements(sendToMotorSyntax, self.serMotor.port)
                elif StatsData.COMPLETED_LOOPS == ScanningParameters.SCAN_PERIODS and StatsData.SCAN_FLAG == 1:
                    StatsData.setScanDirection(3)
                    StatsData.setScanFlag(0)
                    stopSyntax = self.calControlSyntax(1, abs(StatsData.REALTIME_VELOCITY))
                    self.sendControlStatements(stopSyntax, self.serMotor.port)
                    StatsData.setRealtimeVelocity(0)
                else:
                    pass

                #更新实时速度显示曲线
                self.generate_realtimeVelocityCurve()

                #显示发送与接收字节数
                self.sensorToUserMessageBrowser.setText(str(sensorDataNum))
                self.userToSensorMessageBrowser.setText(str(StatsData.SEND_TO_SENSOR_DATA_NUM))
                self.userToMotorMessageBrowser.setText(str(StatsData.SEND_TO_MOTOR_DATA_NUM))

                #设置扫描进度条
                if ScanningParameters.SCAN_PERIODS != 0:
                    self.ScanProgressBar.setValue(StatsData.COMPLETED_LOOPS/ScanningParameters.SCAN_PERIODS*100)
                else:
                    self.ScanProgressBar.setValue(100)
                self.completeCycleNumberLcdNumber.display(StatsData.COMPLETED_LOOPS)
                
                #如果调用复位按钮，则将位移台复位
                if StatsData.REPOSITION_FLAG == 1:
                    if StatsData.OUTSIDE_SENSOR_FLAG == 0:
                        self.sendControlStatements(ControlSyntax.BUTTON_MOVE_OUTSIDE_SYNTAX, self.serMotor.port)
                    else:
                        self.sendControlStatements(ControlSyntax.BUTTON_MOVE_STOP_SYNTAX, self.serMotor.port)
                        StatsData.setRealtimeVelocity(0)
                        StatsData.setRepositionFlag(0)
                else:
                    pass

                #设置接近传感器状态灯
                self.changeSensorStatusLEDsColor(StatsData.OUTSIDE_SENSOR_FLAG, StatsData.BEAM_OUTER_EDGE_CLOSER_SENSOR_FLAG, 
                                                   StatsData.BEAM_INNER_EDGE_CLOSER_SENSOR_FLAG, StatsData.INSIDE_SENSOR_FLAG)

                #在接收框显示已接收的接近传感器信息
                self.receivedSensorMessageTextBrowser.insertPlainText("接近传感器>>>上位机：" + str(sensorData) + '\n')
                textCursor = self.receivedSensorMessageTextBrowser.textCursor()
                textCursor.movePosition(textCursor.End)
                self.receivedSensorMessageTextBrowser.setTextCursor(textCursor)
                
                #在接收框显示已收到的电机信息
                #print(str(motorDataNum))
                if motorDataNum != 0:
                    self.motorToUserMessageBrowser.setText(str(motorDataNum))
                    self.receivedMotorMessageTextBrowser.insertPlainText("电机>>>上位机：" + str(motorData) + '\n')
                else:
                    self.receivedMotorMessageTextBrowser.insertPlainText("电机未发送状态信息！" + '\n')
                textCursor = self.receivedMotorMessageTextBrowser.textCursor()
                textCursor.movePosition(textCursor.End)
                self.receivedMotorMessageTextBrowser.setTextCursor(textCursor)
            else:
                self.receivedSensorMessageTextBrowser.insertPlainText("接近传感器未发送状态信息！" + '\n')
                textCursor = self.receivedSensorMessageTextBrowser.textCursor()
                textCursor.movePosition(textCursor.End)
                self.receivedSensorMessageTextBrowser.setTextCursor(textCursor)
        else:
            pass
       
    #更改接近传感器指示灯状态
    def changeSensorStatusLEDsColor(self, outsideLEDStatus, beamOuterEdgeSensorLEDStatus, beamInnerEdgeSensorLEDStatus, insideLEDStatus):
        if outsideLEDStatus == 1:                      #外侧灯，未接触
            self.outsideLEDColor.setRed(255)
            self.outsideLEDColor.setGreen(0)
            self.outsideLEDColor.setBlue(0)
        elif outsideLEDStatus == 2:
            self.outsideLEDColor.setRed(255)
            self.outsideLEDColor.setGreen(255)
            self.outsideLEDColor.setBlue(0)
        else:     
            self.outsideLEDColor.setRed(10)
            self.outsideLEDColor.setGreen(0)
            self.outsideLEDColor.setBlue(0)
        
        if beamOuterEdgeSensorLEDStatus == 1:                      #外侧灯，未接触
            self.beamOuterEdgeSensorLEDColor.setRed(255)
            self.beamOuterEdgeSensorLEDColor.setGreen(0)
            self.beamOuterEdgeSensorLEDColor.setBlue(0)
        elif beamOuterEdgeSensorLEDStatus == 2:
            self.beamOuterEdgeSensorLEDColor.setRed(255)
            self.beamOuterEdgeSensorLEDColor.setGreen(255)
            self.beamOuterEdgeSensorLEDColor.setBlue(0)
        else:     
            self.beamOuterEdgeSensorLEDColor.setRed(10)
            self.beamOuterEdgeSensorLEDColor.setGreen(0)
            self.beamOuterEdgeSensorLEDColor.setBlue(0)

        if beamInnerEdgeSensorLEDStatus == 1:                      #外侧灯，未接触
            self.beamInnerEdgeSensorLEDColor.setRed(255)
            self.beamInnerEdgeSensorLEDColor.setGreen(0)
            self.beamInnerEdgeSensorLEDColor.setBlue(0)
        elif beamInnerEdgeSensorLEDStatus == 2:
            self.beamInnerEdgeSensorLEDColor.setRed(255)
            self.beamInnerEdgeSensorLEDColor.setGreen(255)
            self.beamInnerEdgeSensorLEDColor.setBlue(0)
        else:     
            self.beamInnerEdgeSensorLEDColor.setRed(10)
            self.beamInnerEdgeSensorLEDColor.setGreen(0)
            self.beamInnerEdgeSensorLEDColor.setBlue(0)

        if insideLEDStatus == 1:                      #内侧灯，未接触
            self.insideLEDColor.setRed(255)
            self.insideLEDColor.setGreen(0)
            self.insideLEDColor.setBlue(0)
        elif insideLEDStatus == 2:
            self.insideLEDColor.setRed(255)
            self.insideLEDColor.setGreen(255)
            self.insideLEDColor.setBlue(0)
        else :     
            self.insideLEDColor.setRed(10)
            self.insideLEDColor.setGreen(0)
            self.insideLEDColor.setBlue(0)


        self.outsideFrame.setStyleSheet("QFrame { background-color: %s }" %
            self.outsideLEDColor.name()) 
        self.outsideFrame_3.setStyleSheet("QFrame { background-color: %s }" %
            self.beamOuterEdgeSensorLEDColor.name()) 
        self.insideFrame_2.setStyleSheet("QFrame { background-color: %s }" %
            self.beamInnerEdgeSensorLEDColor.name()) 
        self.insideFrame.setStyleSheet("QFrame { background-color: %s }" %
            self.insideLEDColor.name()) 

class SerialConfigSet(QtWidgets.QMainWindow, Ui_SerialPortSet):
    def __init__(self):
        super(SerialConfigSet, self).__init__()
        self.setupUi(self)
        self.init()
        

    def init(self):
        #设置配置串口页面的选项
        Baudrate = ['9600', '14400', '19200', '38400', '57600', '115200']
        Port = ['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'COM10', 'COM11', 'COM12', 'COM13', 'COM14']
        ByteSize = ['5', '6', '7', '8']
        StopBytes = ['1', '1.5', '2']
        Parity = ['N', 'E', 'O']
        self.chooseMotorBaudratecomboBox.addItems(Baudrate)
        self.chooseMotorPortcomboBox.addItems(Port)
        self.chooseMotorByteSizecomboBox.addItems(ByteSize)
        self.chooseMotorStopBytescomboBox.addItems(StopBytes)
        self.chooseMotorParitycomboBox.addItems(Parity)
        
        self.chooseSensorBaudratecomboBox.addItems(Baudrate)
        self.chooseSensorPortcomboBox.addItems(Port)
        self.chooseSensorParitycomboBox.addItems(Parity)
        self.chooseSensorStopBytescomboBox.addItems(StopBytes)
        self.chooseSensorByteSizecomboBox.addItems(ByteSize)

        self.chooseMotorBaudratecomboBox_3.addItems(Baudrate)
        self.chooseMotorPortcomboBox_3.addItems(Port)
        self.chooseMotorByteSizecomboBox_3.addItems(ByteSize)
        self.chooseMotorStopBytescomboBox_3.addItems(StopBytes)
        self.chooseMotorParitycomboBox_3.addItems(Parity)
        #使用configparser库操作config.ini文件
        self.Config = configparser.RawConfigParser()
        self.Config.read('config.ini')

        #设置配置串口页面默认的显示，为config.ini保存的数据
        self.chooseMotorPortcomboBox.setCurrentText(self.Config.get("SerialSetting","motor_port"))
        self.chooseMotorBaudratecomboBox.setCurrentText(self.Config.get("SerialSetting","motor_baudrate"))
        self.chooseMotorByteSizecomboBox.setCurrentText(self.Config.get("SerialSetting","motor_bytesize"))
        self.chooseMotorStopBytescomboBox.setCurrentText(self.Config.get("SerialSetting","motor_stopbytes"))
        self.chooseMotorParitycomboBox.setCurrentText(self.Config.get("SerialSetting","motor_parity"))

        self.chooseSensorPortcomboBox.setCurrentText(self.Config.get("SerialSetting","sensor_port"))
        self.chooseSensorBaudratecomboBox.setCurrentText(self.Config.get("SerialSetting","sensor_baudrate"))
        self.chooseSensorByteSizecomboBox.setCurrentText(self.Config.get("SerialSetting","sensor_bytesize"))
        self.chooseSensorStopBytescomboBox.setCurrentText(self.Config.get("SerialSetting","sensor_stopbytes"))
        self.chooseSensorParitycomboBox.setCurrentText(self.Config.get("SerialSetting","sensor_parity"))

        self.chooseMotorPortcomboBox_3.setCurrentText(self.Config.get("SerialSetting","motor2_port"))
        self.chooseMotorBaudratecomboBox_3.setCurrentText(self.Config.get("SerialSetting","motor2_baudrate"))
        self.chooseMotorByteSizecomboBox_3.setCurrentText(self.Config.get("SerialSetting","motor2_bytesize"))
        self.chooseMotorStopBytescomboBox_3.setCurrentText(self.Config.get("SerialSetting","motor2_stopbytes"))
        self.chooseMotorParitycomboBox_3.setCurrentText(self.Config.get("SerialSetting","motor2_parity"))

        #点击保存后触发操作config.ini函数
        self.saveSerialConfigButton.clicked.connect(self.saveSerialConfig)

    def OPEN(self):
        self.show()

    def saveSerialConfig(self):
        self.Config.read('config.ini')
        self.Config.set('SerialSetting','motor_port',self.chooseMotorPortcomboBox.currentText())
        self.Config.set('SerialSetting','motor_bytesize',self.chooseMotorByteSizecomboBox.currentText())
        self.Config.set('SerialSetting','motor_baudrate',self.chooseMotorBaudratecomboBox.currentText())
        self.Config.set('SerialSetting','motor_stopbytes',self.chooseMotorStopBytescomboBox.currentText())
        self.Config.set('SerialSetting','motor_parity',self.chooseMotorParitycomboBox.currentText())

        self.Config.set('SerialSetting','sensor_port',self.chooseSensorPortcomboBox.currentText())
        self.Config.set('SerialSetting','sensor_bytesize',self.chooseSensorByteSizecomboBox.currentText())
        self.Config.set('SerialSetting','sensor_baudrate',self.chooseSensorBaudratecomboBox.currentText())
        self.Config.set('SerialSetting','sensor_stopbytes',self.chooseSensorStopBytescomboBox.currentText())
        self.Config.set('SerialSetting','sensor_parity',self.chooseSensorParitycomboBox.currentText())

        self.Config.set('SerialSetting','motor2_port',self.chooseMotorPortcomboBox_3.currentText())
        self.Config.set('SerialSetting','motor2_bytesize',self.chooseMotorByteSizecomboBox_3.currentText())
        self.Config.set('SerialSetting','motor2_baudrate',self.chooseMotorBaudratecomboBox_3.currentText())
        self.Config.set('SerialSetting','motor2_stopbytes',self.chooseMotorStopBytescomboBox_3.currentText())
        self.Config.set('SerialSetting','motor2_parity',self.chooseMotorParitycomboBox_3.currentText())
        with open('Config.ini','w') as configFile:
            self.Config.write(configFile)
            QMessageBox.information(self, "Config", "已修改配置文件，请关闭后重新打开软件！")

class BeamDetection(QtWidgets.QMainWindow, Ui_BeamDetection):
    def __init__(self):
        super(BeamDetection, self).__init__()
        self.setupUi(self)
        self.init()
    
    def init(self):
        pass


    def OPEN(self):
        self.show()

class AboutMe(QtWidgets.QMainWindow, Ui_AboutMe):
    def __init__(self):
        super(AboutMe, self).__init__()
        self.setupUi(self)
        self.init()
    
    def init(self):
        pass


    def OPEN(self):
        self.show()

if __name__ == "__main__":  
    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainControlWindow()
    serialFrom = SerialConfigSet()
    beamForm = BeamDetection()
    aboutForm = AboutMe()
    mainWindow.show()
    mainWindow.actionSerial.triggered.connect(serialFrom.OPEN)
    mainWindow.actionScan.triggered.connect(beamForm.OPEN)
    mainWindow.actionAboutme.triggered.connect(aboutForm.OPEN)
    sys.exit(app.exec_())
