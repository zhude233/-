import os

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import *
from PyQt5.QtCore import QDateTime
from PyQt5.QtGui import QIcon, QPixmap, QGuiApplication
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QMessageBox

from ui_tools.clickUsableSlider import ClickUsableSlider
from ui.videoWin import VideoWin


class VideoFrame(QtWidgets.QFrame):
    windowModeSwitch = pyqtSignal(str)

    def __init__(self, mainWin: QMainWindow):
        super().__init__()
        self.mainWin = mainWin
        self.videoLength = 0.0
        self.isSlidePressed = False
        self.isWindowMode = False
        self.row = mainWin.row
        self.col = mainWin.col
        self.path = ''
        self.fileName = ''
        self.frame = QtWidgets.QFrame(mainWin.scrollAreaWidgetContents)
        self.frame.setFrameShape(QtWidgets.QFrame.Box)
        self.frame.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.frame.setMaximumSize(QtCore.QSize(680, 500))
        self.frame.setMinimumSize(QtCore.QSize(340, 250))
        self.grid_layout = QtWidgets.QGridLayout(self.frame)

        self.vw = QVideoWidget(self.frame)
        self.vw.setAutoFillBackground(True)
        self.vw.show()

        self.grid_layout.addWidget(self.vw, 0, 0, 1, 5)

        self.btn_switch = QtWidgets.QToolButton(self.frame)
        self.btn_switch.setIcon(QIcon(QPixmap('icons/play.png')))
        self.btn_switch.clicked.connect(self.switch)
        self.grid_layout.addWidget(self.btn_switch, 1, 0, 1, 1)

        self.slider = ClickUsableSlider(self.frame)
        self.slider.setOrientation(QtCore.Qt.Horizontal)
        self.grid_layout.addWidget(self.slider, 1, 1, 1, 1)

        self.lbl_curTime = QtWidgets.QLabel(self.frame)
        self.lbl_curTime.setText("--:--:--")
        self.grid_layout.addWidget(self.lbl_curTime, 1, 2, 1, 1)

        self.btn_cast = QtWidgets.QToolButton(self.frame)
        self.btn_cast.setIcon(QIcon(QPixmap('icons/cast.png')))
        self.btn_cast.setToolTip("保存截图")
        self.btn_cast.clicked.connect(self.cast_video)
        self.grid_layout.addWidget(self.btn_cast, 1, 3, 1, 1)

        self.btn_to_window = QtWidgets.QToolButton(self.frame)
        self.btn_to_window.setIcon(QIcon(QPixmap('icons/window.png')))
        self.btn_to_window.setToolTip("窗口模式")
        self.btn_to_window.clicked.connect(self.to_window)
        self.grid_layout.addWidget(self.btn_to_window, 1, 4, 1, 1)

        self.player = QMediaPlayer(flags=QMediaPlayer.StreamPlayback)

        self.lbl_img = QtWidgets.QLabel("正在处理...")
        self.lbl_img.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_img.setStyleSheet('background-color: rgb(0, 0, 0); color: rgb(255, 255, 255);')

        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setMaximum(100)
        self.progressBar.setMinimum(0)
        self.progressBar.setAutoFillBackground(True)

        self.lbl_people_num = QtWidgets.QLabel("当前人数:--")
        self.lbl_people_num.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_people_num.setAutoFillBackground(True)

    def load(self):
        self.player.setVideoOutput(self.vw)
        url = QFileDialog.getOpenFileUrl(self,
                                         "选取文件",
                                         QUrl('./'),
                                         "视频文件 (*.mp4 *.mkv);;所有文件 (*)")[0]
        if url.url() != '':
            self.fileName = url.fileName()
            self.path = url.url()
            self.player.setMedia(QMediaContent(url))
            self.player.durationChanged.connect(self.get_duration)
            self.player.positionChanged.connect(self.update_ui)
            self.player.mediaStatusChanged.connect(self.on_status_changed)
            self.slider.sliderPressed.connect(self.on_slider_pressed)
            self.slider.sliderMoved.connect(self.on_slider_moved)
            self.slider.sliderClicked.connect(self.on_slider_clicked)
            self.slider.sliderReleased.connect(self.on_slider_released)
            self.vw.setStatusTip(self.fileName)
            self.lbl_img.setStatusTip(self.fileName)
            self.player.play()
            self.player.pause()
        else:
            raise FileException("未选择文件")

    def set_progressing_img(self):
        output_dir = 'output/'
        if os.path.exists(output_dir):
            # img_path = os.path.join(output_dir, img_path)
            img_path = output_dir+'temp_'+self.fileName+'.jpg'
            # pix =
            self.lbl_img.setPixmap(QPixmap(img_path).scaledToWidth(self.lbl_img.width()))

    def set_progressing_text(self, percent: int):
        self.lbl_img.setText(str(percent) + '%')

    def set_progress_bar(self, value: int):
        self.progressBar.setValue(value)

    def set_progressing_people_num(self, num):
        self.lbl_people_num.setText("当前人数:{}".format(num))

    def enter_temp_detect_mod(self):
        self.grid_layout.addWidget(self.lbl_img, 0, 0, 1, 5)
        self.grid_layout.addWidget(self.progressBar, 1, 0, 1, 1)
        self.grid_layout.addWidget(self.lbl_people_num, 1, 1, 1, 2)
        self.btn_switch.hide()
        self.progressBar.show()
        self.lbl_img.show()
        self.lbl_people_num.show()

    def exit_temp_detect_mod(self):
        self.progressBar.hide()
        self.lbl_img.hide()
        self.lbl_people_num.hide()
        self.lbl_img.clear()
        self.lbl_people_num.clear()
        self.lbl_img.setText("正在处理...")
        self.btn_switch.show()

    def enter_temp_track_mod(self):
        self.grid_layout.addWidget(self.lbl_img, 0, 0, 1, 5)
        self.grid_layout.addWidget(self.progressBar, 1, 0, 1, 3)
        self.btn_switch.hide()
        self.lbl_curTime.hide()
        self.progressBar.show()
        self.lbl_img.show()

    def exit_temp_track_mod(self):
        self.btn_switch.show()
        self.progressBar.hide()
        self.lbl_img.clear()
        self.btn_switch.show()
        self.lbl_curTime.show()


    def get_path(self):
        return self.path

    def get_file_name(self):
        return self.fileName

    def get_duration(self):
        self.videoLength = self.player.duration()

    def update_ui(self):
        if self.videoLength > 0:
            if self.isSlidePressed:
                position = self.get_slider_position()
            else:
                position = self.player.position()
                self.slider.setValue(round(position / self.videoLength * 100))
            # hms = self.dateTime.fromMSecsSinceEpoch(position).toString("hh:mm:ss")
            hms = mm_to_hms(position)
            self.lbl_curTime.setText(hms)

    def on_status_changed(self):
        status = self.player.mediaStatus()
        if status == self.player.EndOfMedia:
            self.btn_switch.setIcon(QIcon(QPixmap('icons/play.png')))
        elif status == self.player.InvalidMedia:
            self.btn_switch.setIcon(QIcon(QPixmap('icons/play.png')))
            # QMessageBox.warning(self.parent(), "文件加载失败", "格式不支持或解码器错误", QMessageBox.Ok, QMessageBox.Ok)
            print("文件加载失败：格式不支持或解码器错误")

    def switch(self):
        state = self.player.state()
        if state == self.player.PlayingState:
            self.player.pause()
            self.btn_switch.setIcon(QIcon(QPixmap('icons/play.png')))
        elif state == self.player.PausedState or state == self.player.StoppedState:
            self.player.play()
            self.btn_switch.setIcon(QIcon(QPixmap('icons/pause.png')))

    def on_slider_moved(self):
        self.isSlidePressed = True
        self.set_video_position()

    def on_slider_pressed(self):
        self.isSlidePressed = True
        if self.player.state() == self.player.PlayingState:
            self.switch()

    def on_slider_released(self):
        self.isSlidePressed = False
        self.update_ui()

    def on_slider_clicked(self):
        self.isSlidePressed = True
        self.set_video_position()
        self.isSlidePressed = False

    def set_video_position(self):
        if self.videoLength > 0:
            position = self.get_slider_position()
            self.player.setPosition(position)

    def get_slider_position(self):
        return int(self.slider.value() / 100 * self.videoLength)

    def cast_video(self):
        screen = QGuiApplication.primaryScreen()
        cast_jpg = './' + QDateTime.currentDateTime().toString("yyyy-MM-dd hh-mm-ss") + '.jpg'
        screen.grabWindow(self.vw.winId()).save(cast_jpg)
        QMessageBox.information(self.parent(), "截图成功", "截图已保存到"+cast_jpg)

    def to_window(self):
        if self.isWindowMode:
            self.vw.close()
            self.mainWin.gridLayout_2.addWidget(self.frame, self.row, self.col, 1, 1)
            # self.frame.setVisible(True)
            self.isWindowMode = False
        else:
            self.vw = VideoWin(self)
            # self.vw.windowClose.connect(self.frame.setVisible(True))
            # self.frame.setParent(self.vw)
            self.vw.show()
            self.isWindowMode = True

    def get_frame(self):
        return self.frame


def mm_to_hms(ms: int):
    time = ms / 1000
    h = int(time / 3600)
    time %= 3600
    m = int(time / 60)
    time %= 60
    return str(h) + ':' + str(m) + ':' + str(int(time))


class FileException(Exception):
    def __init__(self, msg: str):
        print("文件错误：" + msg)
        # QMessageBox(QMessageBox.Warning, "文件错误", msg).exec_()
