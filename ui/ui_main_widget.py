# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'main_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(600, 1024)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        self.image_label = QtWidgets.QLabel(Form)
        self.image_label.setGeometry(QtCore.QRect(0, 0, 400, 600))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Ignored)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.image_label.sizePolicy().hasHeightForWidth())
        self.image_label.setSizePolicy(sizePolicy)
        self.image_label.setMinimumSize(QtCore.QSize(120, 120))
        self.image_label.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.image_label.setText("")
        self.image_label.setAlignment(QtCore.Qt.AlignCenter)
        self.image_label.setObjectName("image_label")
        self.cover = QtWidgets.QWidget(Form)
        self.cover.setGeometry(QtCore.QRect(0, 0, 600, 1024))
        self.cover.setObjectName("cover")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.cover)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_time = QtWidgets.QLabel(self.cover)
        self.label_time.setMinimumSize(QtCore.QSize(0, 40))
        self.label_time.setMaximumSize(QtCore.QSize(16777215, 40))
        self.label_time.setStyleSheet("font-size:14pt; \n"
"color: rgb(85, 85, 85);\n"
"font-weight:600;")
        self.label_time.setTextFormat(QtCore.Qt.AutoText)
        self.label_time.setAlignment(QtCore.Qt.AlignCenter)
        self.label_time.setObjectName("label_time")
        self.verticalLayout.addWidget(self.label_time)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.label = QtWidgets.QLabel(self.cover)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QtCore.QSize(580, 600))
        self.label.setMaximumSize(QtCore.QSize(77777, 580))
        self.label.setScaledContents(False)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        spacerItem1 = QtWidgets.QSpacerItem(20, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)
        self.widget = QtWidgets.QWidget(self.cover)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setMinimumSize(QtCore.QSize(0, 100))
        self.widget.setMaximumSize(QtCore.QSize(16777215, 200))
        self.widget.setStyleSheet("#widget{background-color: rgba(46, 255, 0, 40);}\n"
"")
        self.widget.setObjectName("widget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setContentsMargins(20, 0, 20, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_1 = QtWidgets.QLabel(self.widget)
        self.label_1.setStyleSheet("font-size:14pt; \n"
"font-weight:600;\n"
"color:#ffffff;")
        self.label_1.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_1.setObjectName("label_1")
        self.gridLayout_2.addWidget(self.label_1, 0, 0, 1, 1)
        self.sign_name = QtWidgets.QLabel(self.widget)
        self.sign_name.setStyleSheet("font-size:14pt; \n"
"font-weight:600;\n"
"color:#0dc839;")
        self.sign_name.setTextFormat(QtCore.Qt.AutoText)
        self.sign_name.setObjectName("sign_name")
        self.gridLayout_2.addWidget(self.sign_name, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.widget)
        self.label_2.setStyleSheet("font-size:14pt; \n"
"font-weight:600;\n"
"color:#ffffff;")
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.sign_time = QtWidgets.QLabel(self.widget)
        self.sign_time.setStyleSheet("font-size:14pt; \n"
"font-weight:600;\n"
"color:#0dc839;")
        self.sign_time.setObjectName("sign_time")
        self.gridLayout_2.addWidget(self.sign_time, 1, 1, 1, 1)
        self.gridLayout_2.setColumnStretch(0, 2)
        self.gridLayout_2.setColumnStretch(1, 3)
        self.horizontalLayout.addLayout(self.gridLayout_2)
        self.label_attend_img = QtWidgets.QLabel(self.widget)
        self.label_attend_img.setMinimumSize(QtCore.QSize(100, 100))
        self.label_attend_img.setMaximumSize(QtCore.QSize(100, 100))
        self.label_attend_img.setStyleSheet("")
        self.label_attend_img.setText("")
        self.label_attend_img.setPixmap(QtGui.QPixmap("../resource/images/signin_success.png"))
        self.label_attend_img.setScaledContents(True)
        self.label_attend_img.setObjectName("label_attend_img")
        self.horizontalLayout.addWidget(self.label_attend_img)
        self.horizontalLayout.setStretch(0, 5)
        self.horizontalLayout.setStretch(1, 2)
        self.horizontalLayout_2.addLayout(self.horizontalLayout)
        self.verticalLayout.addWidget(self.widget)
        spacerItem2 = QtWidgets.QSpacerItem(20, 100, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        self.verticalLayout.addItem(spacerItem2)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_time.setText(_translate("Form", "2022-03-33 08:43:00"))
        self.label_1.setText(_translate("Form", "姓名:"))
        self.sign_name.setText(_translate("Form", "姓名"))
        self.label_2.setText(_translate("Form", "签到时间:"))
        self.sign_time.setText(_translate("Form", "签到时间"))
