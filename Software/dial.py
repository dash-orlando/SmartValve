'''
#
# Pressure Cuff Dial Gauge Window Setup
#
# Adapted by : Mohammad Odeh
# Date       : Mar. 7th, 2017
# Updated    : Jun. 1st, 2017
#
'''

from PyQt4              import QtCore, QtGui

# Get screen resolution for automatic sizing

app=QtGui.QApplication([])
screen_resolution = app.desktop().screenGeometry()
width, height = screen_resolution.width(), screen_resolution.height()

available_resolution = app.desktop().availableGeometry()    # Minuse the taskbar
w_avlbl, h_avlbl = available_resolution.width(), available_resolution.height()

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        #MainWindow.resize(500,500)
##        MainWindow.resize( width*3/4, h_avlbl )
        MainWindow.setGeometry( 0, 0, width*3/4, h_avlbl )
##        MainWindow.showFullScreen()
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")

        # Setup label (display mmHg)
        self.label = QtGui.QLabel(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setWeight(75)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)

        # Setup Dial
        self.Dial = Qwt5.QwtDial(self.centralwidget)
        self.Dial.setEnabled(False)
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setWeight(75)
        font.setBold(True)
        self.Dial.setFont(font)
        self.Dial.setOrientation(QtCore.Qt.Vertical)
        self.Dial.setProperty("visibleBackground", QtCore.QVariant(True))
        self.Dial.setLineWidth(4)
        self.Dial.setObjectName("Dial")
        self.verticalLayout.addWidget(self.Dial)

        # Setup pushbutton to pair device
        self.pushButtonPair = QtGui.QPushButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButtonPair.sizePolicy().hasHeightForWidth())
        self.pushButtonPair.setSizePolicy(sizePolicy)
        self.pushButtonPair.setMaximumSize(QtCore.QSize(190, 16777215))
        self.pushButtonPair.setObjectName("pushButtonPair")
        self.verticalLayout.addWidget(self.pushButtonPair)
        self.pushButtonPair.setEnabled(False)

        # Setup pushbutton to quit program
        self.pushButtonQuit = QtGui.QPushButton(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButtonQuit.sizePolicy().hasHeightForWidth())
        self.pushButtonQuit.setSizePolicy(sizePolicy)
        self.pushButtonQuit.setMaximumSize(QtCore.QSize(190, 16777215))
        self.pushButtonQuit.setObjectName("pushButtonQuit")
        self.verticalLayout.addWidget(self.pushButtonQuit)
        
        # Release ports and close window on shutdown
        self.pushButtonQuit.clicked.connect(MainWindow.close)

        # Add final touches
        self.retranslateUi(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)
        QtCore.QObject.connect(self.pushButtonPair, QtCore.SIGNAL("triggered()"), MainWindow.start)
        QtCore.QObject.connect(self.pushButtonQuit, QtCore.SIGNAL("triggered()"), MainWindow.close)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Schlumberger", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Revolutions", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonQuit.setText(QtGui.QApplication.translate("MainWindow", "EXIT", None, QtGui.QApplication.UnicodeUTF8))
        
from PyQt4 import Qwt5


# ==============
#   DEPRACATED
# ==============
'''
##        # Setup Labels (CSEC, PD3D, etc...)
##        self.csecLabel = QtGui.QLabel(self.centralwidget)
##        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
##        sizePolicy.setHorizontalStretch(0)
##        sizePolicy.setVerticalStretch(0)
##        sizePolicy.setHeightForWidth(self.csecLabel.sizePolicy().hasHeightForWidth())
##        self.csecLabel.setSizePolicy(sizePolicy)
##        self.csecLabel.setObjectName("csecLabel")
##        self.verticalLayout.addWidget(self.csecLabel)
##        self.csecLabel.setAlignment(QtCore.Qt.AlignCenter)
##        font = QtGui.QFont()
##        font.setPointSize(14)
##        font.setWeight(75)
##        font.setBold(False)
##        self.csecLabel.setFont(font)
##
##        # Setup "Paired" indicator
##        self.CommandLabel = QtGui.QLabel(self.centralwidget)
##        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
##        sizePolicy.setHorizontalStretch(0)
##        sizePolicy.setVerticalStretch(0)
##        sizePolicy.setHeightForWidth(self.CommandLabel.sizePolicy().hasHeightForWidth())
##        self.CommandLabel.setSizePolicy(sizePolicy)
##        font = QtGui.QFont()
##        font.setPointSize(10)
##        font.setWeight(50)
##        font.setBold(True)
##        self.CommandLabel.setFont(font)
##        self.CommandLabel.setObjectName("CommandLabel")
##        self.verticalLayout.addWidget(self.CommandLabel)
##
##        # Setup dropdown list to choose device from
##        self.rfObjectSelect = QtGui.QComboBox(self.centralwidget)
##        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
##        sizePolicy.setHorizontalStretch(0)
##        sizePolicy.setVerticalStretch(0)
##        sizePolicy.setHeightForWidth(self.rfObjectSelect.sizePolicy().hasHeightForWidth())
##        self.rfObjectSelect.setSizePolicy(sizePolicy)
##        self.rfObjectSelect.setMaximumSize(QtCore.QSize(190, 16777215))
##        self.rfObjectSelect.setObjectName("rfObjectSelect")
##        self.verticalLayout.addWidget(self.rfObjectSelect)
##
##    def retranslateUi(self, MainWindow):
##        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Sphygnomanometer", None, QtGui.QApplication.UnicodeUTF8))
##        self.label.setText(QtGui.QApplication.translate("MainWindow", "mmHg", None, QtGui.QApplication.UnicodeUTF8))
##        #self.CommandLabel.setText(QtGui.QApplication.translate("MainWindow", "Select a Device", None, QtGui.QApplication.UnicodeUTF8))
##        self.pushButtonQuit.setText(QtGui.QApplication.translate("MainWindow", "EXIT", None, QtGui.QApplication.UnicodeUTF8))
##        self.pushButtonPair.setText(QtGui.QApplication.translate("MainWindow", "Searching for stethoscope...", None, QtGui.QApplication.UnicodeUTF8))
##        #self.csecLabel.setText(QtGui.QApplication.translate("MainWindow", "CSEC\nPD3D", None, QtGui.QApplication.UnicodeUTF8))
'''
