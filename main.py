import requests
import sys
import os
import json
from datetime import datetime, timedelta
import time
import threading
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QWidget, QDesktopWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal as Signal, QObject, Qt, QCoreApplication, QThread, pyqtSignal, pyqtSlot
from window import *

r = requests.get('https://content.warframe.com/dynamic/worldState.php')

js = r.json()

missions = js['SyndicateMissions']

global width
global height
width = int(100)
height = int(70)

#--SETTINGS--#

width = 100
height = 70

#------------#

CETUS_EPOCH = 1521369472.764
CETUS_LEN = 8998.87481
CETUS_LEN_DAY = CETUS_LEN * 2 / 3
global CETUS_DISPLAY 
CETUS_DISPLAY = '{:02}:{:02}'.format(int(0), int(0))

for i in missions:
	if i['Tag'] == 'CetusSyndicate':
		cetus = i
		cetus_expiry = int(cetus['Expiry']['$date']['$numberLong'])
		cetus_begin = cetus_expiry / 1000.0 - CETUS_LEN
		break


class Tester_Cetus(QObject):
	sig_positions = Signal(int)
	sig_positions2 = Signal(int)
	@pyqtSlot(int)
	def action(self, n):
		i = int(0)
		while True:
			i = i + 1
			if (i > 4):
				self.sig_positions.emit(1)
				i = 0
			self.sig_positions2.emit(1)
			time.sleep(0.1)

class Window_Cetus(QMainWindow):
	sig_requested = Signal(int)
	sig_requested2 = Signal(int)
	def __init__(self):
		super().__init__()
		self.setWindowFlag(Qt.X11BypassWindowManagerHint)
		self.setWindowFlag(Qt.FramelessWindowHint)
		self.setWindowFlag(Qt.WindowStaysOnTopHint)

		self.resize(width, height)
		vert = QDesktopWidget().screenGeometry().bottom()
		self.move(0, vert - height + 3)
		self.f = QFont("Arial", 30, QFont.Normal)

		self.label = QLabel(CETUS_DISPLAY)
		self.label.setFont(self.f)
		self.label.setGeometry(width, height, 50, 50)

		self.layout = QVBoxLayout()
		self.layout.addWidget(self.label)
		self.central_widget = QWidget()
		self.central_widget.setLayout(self.layout)
		self.setCentralWidget(self.central_widget)

		self.t = Tester_Cetus()
		self.q = QThread()
		self.t.sig_positions.connect(self.UpdateTime)
		self.sig_requested.connect(self.t.action)
		self.t.sig_positions2.connect(self.GetWindow)
		self.t.moveToThread(self.q)
		self.q.start()

		self.show()
		print("Started")

	def StartUpdates(self):
		self.sig_requested.emit(1)
		self.sig_requested2.emit(1)

	def UpdateTime(self):
		self.label.setText(CETUS_DISPLAY)
	def GetWindow(self):
		if (str(get_active_window()) == "Warframe"):
			self.setVisible(True)
		else:
			self.setVisible(False)

def Monitor_Cetus():
	while True:

		now = datetime.now().timestamp()
		xbegin = cetus_begin + int((now - cetus_begin) / CETUS_LEN) * CETUS_LEN

		global CETUS_DISPLAY

		if now < xbegin + CETUS_LEN_DAY:
			tim = datetime.utcfromtimestamp(xbegin - now + CETUS_LEN_DAY)
		else:
			tim = datetime.utcfromtimestamp(xbegin - now + CETUS_LEN)

		readable = '{:02}:{:02}'.format(int(tim.hour*60)+int(tim.minute), int(tim.second))
		if now < xbegin + CETUS_LEN_DAY:
			CETUS_DISPLAY = "☀️ " + readable
		else:
			CETUS_DISPLAY = "🌙 " + readable
		time.sleep(0.5)

if __name__ == "__main__":

	t_cetus = threading.Thread(target=Monitor_Cetus)

	t_cetus.start()

	App = QApplication(sys.argv)
	window = Window_Cetus()
	window.StartUpdates()
	sys.exit(App.exec())
