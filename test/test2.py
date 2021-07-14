from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QSlider
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import *


class myVideoWidget(QVideoWidget):
    doubleClickedItem = pyqtSignal(str)  # 创建双击信号

    def __init__(self, parent=None):
        super(QVideoWidget, self).__init__(parent)

    def mouseDoubleClickEvent(self, QMouseEvent):  # 双击事件
        self.doubleClickedItem.emit("double clicked")


class myVideoSlider(QSlider):
    ClickedValue = pyqtSignal(int)

    def __init__(self, father):
        super().__init__(Qt.Horizontal, father)

    def mousePressEvent(self, QMouseEvent):  # 单击事件
        super().mousePressEvent(QMouseEvent)
        value = QMouseEvent.localPos().x()
        # self.setValue(int(value)/9)
        value = round(value / self.width() * self.maximum())  # 根据鼠标点击的位置和slider的长度算出百分比
        self.ClickedValue.emit(value)


class myMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(615, 404)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.wgt_video = myVideoWidget(self.centralwidget)
        self.wgt_video.setMinimumSize(QtCore.QSize(410, 200))
        self.wgt_video.setMaximumSize(QtCore.QSize(16777215, 16777215))
        palette = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Active, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(255, 255, 255))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Inactive, QtGui.QPalette.Window, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Base, brush)
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        palette.setBrush(QtGui.QPalette.Disabled, QtGui.QPalette.Window, brush)
        self.wgt_video.setPalette(palette)
        self.wgt_video.setAutoFillBackground(True)
        self.wgt_video.setObjectName("wgt_video")
        self.gridLayout.addWidget(self.wgt_video, 0, 0, 1, 1)
        self.sld_video = myVideoSlider(self.centralwidget)
        self.sld_video.setMinimumSize(QtCore.QSize(410, 0))
        self.sld_video.setMaximumSize(QtCore.QSize(16777215, 20))
        self.sld_video.setMaximum(100)
        self.sld_video.setOrientation(QtCore.Qt.Horizontal)
        self.sld_video.setObjectName("sld_video")
        self.gridLayout.addWidget(self.sld_video, 1, 0, 1, 1)
        self.lab_video = QtWidgets.QLabel(self.centralwidget)
        self.lab_video.setMaximumSize(QtCore.QSize(16777215, 50))
        self.lab_video.setObjectName("lab_video")
        self.gridLayout.addWidget(self.lab_video, 1, 1, 1, 1)
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.btn_open = QtWidgets.QPushButton(self.splitter)
        self.btn_open.setMaximumSize(QtCore.QSize(100, 25))
        self.btn_open.setObjectName("btn_open")
        self.btn_play = QtWidgets.QPushButton(self.splitter)
        self.btn_play.setMaximumSize(QtCore.QSize(100, 25))
        self.btn_play.setObjectName("btn_play")
        self.btn_stop = QtWidgets.QPushButton(self.splitter)
        self.btn_stop.setMaximumSize(QtCore.QSize(100, 25))
        self.btn_stop.setObjectName("btn_stop")
        self.sld_audio = QtWidgets.QSlider(self.splitter)
        self.sld_audio.setMinimumSize(QtCore.QSize(100, 0))
        self.sld_audio.setMaximumSize(QtCore.QSize(150, 20))
        self.sld_audio.setProperty("value", 99)
        self.sld_audio.setOrientation(QtCore.Qt.Horizontal)
        self.sld_audio.setObjectName("sld_audio")
        self.lab_audio = QtWidgets.QLabel(self.splitter)
        self.lab_audio.setObjectName("lab_audio")
        self.btn_cast = QtWidgets.QPushButton(self.splitter)
        self.btn_cast.setObjectName("btn_cast")
        self.gridLayout.addWidget(self.splitter, 2, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 615, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.lab_video.setText("0%")
        self.btn_open.setText("打开视频文件")
        self.btn_play.setText("播放")
        self.btn_stop.setText("暂停")
        self.lab_audio.setText("volume:100%")
        self.btn_cast.setText("截图")

        self.sld_video_pressed = False  # 判断当前进度条识别否被鼠标点击
        self.videoFullScreen = False  # 判断当前widget是否全屏
        self.videoFullScreenWidget = myVideoWidget()  # 创建一个全屏的widget
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.wgt_video)  # 视频播放输出的widget，就是上面定义的
        self.btn_open.clicked.connect(self.openVideoFile)  # 打开视频文件按钮
        self.btn_play.clicked.connect(self.playVideo)  # play
        self.btn_stop.clicked.connect(self.pauseVideo)  # pause
        self.btn_cast.clicked.connect(self.castVideo)  # 视频截图
        self.player.positionChanged.connect(self.changeSlide)  # change Slide
        self.videoFullScreenWidget.doubleClickedItem.connect(self.videoDoubleClicked)  # 双击响应
        self.wgt_video.doubleClickedItem.connect(self.videoDoubleClicked)  # 双击响应
        self.sld_video.setTracking(False)
        self.sld_video.sliderReleased.connect(self.releaseSlider)
        self.sld_video.sliderPressed.connect(self.pressSlider)
        self.sld_video.sliderMoved.connect(self.moveSlider)  # 进度条拖拽跳转
        self.sld_video.ClickedValue.connect(self.clickedSlider)  # 进度条点击跳转
        self.sld_audio.valueChanged.connect(self.volumeChange)  # 控制声音播放
        self.btn_cast.hide()


    def volumeChange(self, position):
        volume = round(position / self.sld_audio.maximum() * 100)
        print("vlume %f" % volume)
        self.player.setVolume(volume)
        self.lab_audio.setText("volume:" + str(volume) + "%")

    def clickedSlider(self, position):
        if self.player.duration() > 0:  # 开始播放后才允许进行跳转
            video_position = int((position / 100) * self.player.duration())
            self.player.setPosition(video_position)
            self.lab_video.setText("%.2f%%" % position)
        else:
            self.sld_video.setValue(0)

    def moveSlider(self, position):
        self.sld_video_pressed = True
        if self.player.duration() > 0:  # 开始播放后才允许进行跳转
            video_position = int((position / 100) * self.player.duration())
            self.player.setPosition(video_position)
            self.lab_video.setText("%.2f%%" % position)

    def pressSlider(self):
        self.sld_video_pressed = True
        print("pressed")

    def releaseSlider(self):
        self.sld_video_pressed = False

    def changeSlide(self, position):
        if not self.sld_video_pressed:  # 进度条被鼠标点击时不更新
            self.vidoeLength = self.player.duration() + 0.1
            self.sld_video.setValue(round((position / self.vidoeLength) * 100))
            self.lab_video.setText("%.2f%%" % ((position / self.vidoeLength) * 100))

    def openVideoFile(self):
        self.player.setMedia(QMediaContent(QFileDialog.getOpenFileUrl()[0]))  # 选取视频文件
        self.player.play()  # 播放视频
        print(self.player.availableMetaData())

    def playVideo(self):
        self.player.play()

    def pauseVideo(self):
        self.player.pause()

    def videoDoubleClicked(self, text):

        if self.player.duration() > 0:  # 开始播放后才允许进行全屏操作
            if self.videoFullScreen:
                self.player.setVideoOutput(self.wgt_video)
                self.videoFullScreenWidget.hide()
                self.videoFullScreen = False
            else:
                self.videoFullScreenWidget.show()
                self.player.setVideoOutput(self.videoFullScreenWidget)
                self.videoFullScreenWidget.setFullScreen(1)
                self.videoFullScreen = True


if __name__ == '__main__':
    app = QApplication(sys.argv)
    vieo_gui = myMainWindow()
    vieo_gui.show()
    sys.exit(app.exec_())