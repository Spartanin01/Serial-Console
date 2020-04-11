import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QPushButton, QHBoxLayout, QLineEdit, \
    QMessageBox, QSpinBox, QComboBox, QVBoxLayout, QScrollArea, QFormLayout, QGroupBox
from PyQt5.QtCore import Qt,QTimer,pyqtSignal, QObject
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtGui import QIcon, QFont, QImage, QPixmap, QActionEvent, QColor
import serial.tools.list_ports
import serial
import time
import threading
from functools import partial

import sys

s = serial
com = "COM13"
baud = 9600
connected = False
windowCreated = False

currentNumber = 0
message = ""
currentMessage = ""

connectedText = QLabel
connectedButton = QPushButton
ComDropdown = QComboBox
TextBox = QLineEdit
layout = QtWidgets.QVBoxLayout
widget = QtWidgets.QWidget
scroll = QtWidgets.QScrollArea
comPorts = list(serial.tools.list_ports.comports())


# ATTACH;HEAD_VERTICAL
# SET;HEAD_VERTICAL;120
# DETACH;HEAD_VERTICAL


class Terminal(QWidget):
    valueChanged = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.ShowSended)
        self.timer.start(200)
        self.interface()

    def Send(self):
        global TextBox, layout, s, scroll, currentNumber
        try:
            currentNumber += 1
            s.write(str(TextBox.text()).encode())
            s.flush()
            l = QLabel(">" + str(currentNumber) + ": " + str(TextBox.text()))
            l.setStyleSheet("color: green; font: Consolas;border-width: 0px; border-style:solid")
            layout.addWidget(l)
            scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum()+1000)
        except Exception as e:
            print("Error occured when trying to send message")
            print(str(e))
            return

    def ShowSended(self):
        global TextBox, layout, s, scroll,currentNumber,message,currentMessage
        try:
            if currentMessage != message and message != "":
                currentMessage = message
                label = QLabel(">"+str(currentNumber) + ": " + str(message))
                label.setStyleSheet("color: green; font: Consolas;border-width: 0px; border-style:solid")
                currentNumber+=1
                layout.addWidget(label)
                scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum()+1000)
        except Exception as e:
            print("Error occured when trying to send message")
            print(str(e))
            return

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Return:
            self.Send()

    def interface(self, frame=QtWidgets.QFrame.Box):
        global TextBox, layout, widget, scroll
        self.resize(500, 500)
        self.setFixedSize(400, 400)

        self.move(1200, 100)
        self.setWindowTitle("Terminal")
        self.setWindowIcon(QIcon('terminal.png'))
        self.setStyleSheet("background-color: black;")
        self.setWindowFlag(QtCore.Qt.WindowCloseButtonHint, False)

        widget = QtWidgets.QWidget()
        layout = QtWidgets.QFormLayout(self)
        scroll = QtWidgets.QScrollArea()

        widget.setLayout(layout)

        scroll.setFrameShape(frame)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        scroll_layout = QtWidgets.QVBoxLayout(self)
        scroll_layout.addWidget(scroll)
        scroll_layout.setContentsMargins(0, 0, 0, 50)
        scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum()+10)
        scroll.setStyleSheet("background-color: black;")
        scroll.verticalScrollBar().setStyleSheet('background: white; color: black; border: 2px solid grey;')
        scroll.verticalScrollBar().rangeChanged.connect(lambda: scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum()))
        self.setLayout(scroll_layout)

        TextBox = QLineEdit(self)
        TextBox.move(10, 365)
        TextBox.resize(300, 25)
        TextBox.setStyleSheet("border: 1px solid white; color: white; background-color: black;")
       

        b1 = QPushButton("Send", self)
        b1.setToolTip('Use this button to send data')
        b1.setStyleSheet("border: 1px solid white; color: white; background-color: black;")
        b1.resize(70, 25)
        b1.move(320, 365)
        b1.clicked.connect(self.Send)

        self.show()


def SearchForComs():
    global comPorts, ComDropdown, windowCreated
    while True:
        if windowCreated:
            time.sleep(0.1)
            comPortsNew = list(serial.tools.list_ports.comports())
            if len(comPorts) != len(comPortsNew):
                print("change")
                print(len(comPorts))
                print(len(comPortsNew))
                comPorts = comPortsNew
                ComDropdown.clear()
                for v in comPorts:
                    ComDropdown.addItem(str(v))


class SerialConnection(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.interface()

    def PreConnect(self):
        global com, baud, ComDropdown
        try:
            com = str(ComDropdown.currentText())[:5]
            baud = str(self.BAUDlist.currentText())
            if not connected:
                Connect()
                self.window = Terminal()
                self.window.close()
                self.window.show()
            else:
                Disconnect()
        except Exception as e:
            print("Error occured when trying to connect")
            print(str(e))
            QMessageBox.warning(
                self, "Error", str(e))
            return

    def interface(self):
        global windowCreated, comPorts, connectedText, connectedButton, ComDropdown

        self.resize(415, 75)
        self.setFixedSize(415, 75)
        self.move(700, 400)
        self.setWindowTitle("Configuration")
        self.setWindowIcon(QIcon('gears.png'))

        l1 = QLabel("COM:", self)
        l1.move(15, 0)
        l2 = QLabel("BAUD:", self)
        l2.move(220, 0)
        l3 = QLabel("STATUS:", self)
        l3.setStyleSheet("font-size: 10pt;")
        l3.move(10, 50)
        connectedText = QLabel("DISCONNECTED", self)
        connectedText.setStyleSheet("font-size: 10pt; color: red;")
        connectedText.move(68, 50)

        connectedButton = QPushButton(" CONNECT  ", self)
        connectedButton.setToolTip('Use this button to connect with the board')
        connectedButton.move(330, 15)
        connectedButton.clicked.connect(self.PreConnect)

        ComDropdown = QComboBox(self)
        ComDropdown.setToolTip('Choose the right com port')
        ComDropdown.move(10, 15)
        ComDropdown.resize(200, 25)
        comPorts = list(serial.tools.list_ports.comports())
        for v in comPorts:
            ComDropdown.addItem(str(v))
        ComDropdown.setEnabled(True)

        self.BAUDlist = QComboBox(self)
        self.BAUDlist.setToolTip('Choose the right baud')
        Bauds = ["300", "1200", "2400", "4800", "9600", "19200", "38400", "57600", "74880", "115200", "230400",
                 "250000", "500000", "1000000", "2000000"]
        for v in Bauds:
            self.BAUDlist.addItem(str(v))
        self.BAUDlist.setEnabled(True)
        self.BAUDlist.move(220, 15)
        self.BAUDlist.resize(100, 25)

        self.show()
        windowCreated = True

    def end(self):
        self.window.close()
        self.close()

    def closeEvent(self, event):

        odp = QMessageBox.question(
            self, 'End Message',
            "Are you sure?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if odp == QMessageBox.Yes:
            self.window.close()
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()


def Connect():
    global s, connected, com, baud, connectedText, connectedButton,message
    s = serial.Serial(com, baud, timeout=1)
    s.close()
    s.open()
    time.sleep(1)
    message = "SOFTWARE:> Connected with " + str(com) + " at speed: " + str(baud)
    print("SOFTWARE:> Connected with " + str(com) + " at speed: " + str(baud))
    connectedText.setText("CONNECTED")
    connectedText.setStyleSheet("font-size: 10pt; color: green;")
    connectedButton.setText("DISCONNECT")
    connected = True


def Disconnect():
    global s, connected, com, connectedText,message
    try:
        s.close()
        message = "SOFTWARE:> Disconnected with " + str(com)
        print("SOFTWARE:> Disconnected with " + str(com))
        connectedText.setText("DISCONNECTED")
        connectedText.setStyleSheet("font-size: 10pt; color: red;")
        connectedButton.setText(" CONNECT  ")
        connected = False
    except:
        print("")


def Loop():
    global s, windowCreated, message
    while True:
        try:
            if connected and windowCreated:
                message = str(str(s.readline().strip().decode("ascii")).strip())
                if message != "":
                    print(message)
                    if message == "BOARD:> Input 0 switched to LOW":
                        print("1")
                    elif message == "BOARD:> Input 0 switched to HIGH":
                        print("2")
        except Exception as e:
            print(e)
            Disconnect()


def CreateConfiguration():
    import sys
    app = QApplication(sys.argv)
    app.setStyle('Windows')
    main = SerialConnection()
    main.show()
    sys.exit(app.exec_())


thread1 = threading.Thread(target=Loop)
thread1.start()

thread2 = threading.Thread(target=SearchForComs)
thread2.start()

thread3 = threading.Thread(target=CreateConfiguration)
thread3.start()
