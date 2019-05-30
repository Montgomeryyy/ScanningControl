# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'AboutMe.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AboutMe(object):
    def setupUi(self, AboutMe):
        AboutMe.setObjectName("AboutMe")
        AboutMe.resize(458, 303)
        self.textBrowser = QtWidgets.QTextBrowser(AboutMe)
        self.textBrowser.setGeometry(QtCore.QRect(0, 0, 461, 301))
        self.textBrowser.setStyleSheet("background-color: rgb(80, 80, 80)")
        self.textBrowser.setObjectName("textBrowser")

        self.retranslateUi(AboutMe)
        QtCore.QMetaObject.connectSlotsByName(AboutMe)

    def retranslateUi(self, AboutMe):
        _translate = QtCore.QCoreApplication.translate
        AboutMe.setWindowTitle(_translate("AboutMe", "AboutMe"))
        self.textBrowser.setHtml(_translate("AboutMe", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'SimSun\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">*****************************************</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600;\">AboutMe</span></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">Gearshift Scanning Control是一款用于变速扫描刻蚀的控制软件。</span></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">作者：王启蒙</span></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">授权联系方式：thu_wqm@qq.com</span></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">未经许可禁止拷贝及修改转载，作者保留所有权利。</span></p>\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">*****************************************</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">V1.0：实现了设计的基础功能。</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">V1.1：修复了在低分辨率屏幕上会界面显示不全的bug，使用布局管理器实现了窗口的自适应缩放。</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:10pt;\">V1.2:为了保证正反运行时触发变速时更精准的对准光栅和挡板的位置，添加了反向运行添加延时触发变速的功能。</span></p>\n"
"<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:10pt;\"><br /></p></body></html>"))

