import os
import platform
import threading

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox, QCheckBox
from ui.mainWindow import Ui_MainWindow
from ui.videoFrame import FileException
from ui.videoFrame import VideoFrame
from ui_tools.detectionCmdExecutor import DetectionCmdExecutor
from ui_tools.trackCmdExecutor import TrackCmdExecutor


class MainWin(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.threadLock = threading.Lock()
        self.setupUi(self)
        self.init_connect()
        self.isWindows = platform.uname().system == 'Windows'
        if self.isWindows:
            self.btn_stop.close()
        self.isSave = False
        self.isUseGPU = False
        self.isParallel = True
        self.isProcessing = False
        self.savePath = ''
        self.doubleSpinBox.setValue(0.80)
        self.refresh_slider()
        self.row = 0
        self.col = 0
        self.vfs = []
        self.model_path = self.output_path = self.infer = self.model_dir = self.output_dir = self.use_gpu = self.thread_hold = ''
        self.infer_mot = self.config = self.det_results_dir = self.video_file = self.track_output_dir = self.save_videos = ''
        self.processedCount = 0
        self.executors = []
        self.totalFrame = 0
        self.totalDetect = 0
        self.threadNum = 1
        self.modelPath = [
            'models/model1',
            'models/model2'
        ]
        self.isRefresh = False

    def init_connect(self):
        self.action_add_video.triggered.connect(self.add_video)
        self.btn_add_video.clicked.connect(self.add_video)
        self.slider_confidence.valueChanged.connect(self.refresh_spinbox)
        self.doubleSpinBox.valueChanged.connect(self.refresh_slider)
        self.btn_process_detect.clicked.connect(self.start_detect)
        self.btn_process_track.clicked.connect(self.start_track)
        self.btn_change_path.clicked.connect(self.change_path)
        self.radioButton_use_gpu.clicked.connect(self.switch_gpu_parallel)
        self.radioButton_parallel.clicked.connect(self.switch_gpu_parallel)
        self.checkBox_save.clicked.connect(self.switch_save)
        self.btn_stop.clicked.connect(self.on_btn_stop_clicked)

    def add_video(self):
        vf = VideoFrame(self)
        self.vfs.append(vf)
        frame = vf.get_frame()
        try:
            vf.load()
            self.gridLayout_2.addWidget(frame, self.row, self.col, 1, 1)
            self.col = (self.col + 1) % 2
            self.row = self.row + (1 if self.col == 0 else 0)
            self.gridLayout_2.removeWidget(self.btn_add_video)
            self.gridLayout_2.addWidget(self.btn_add_video, self.row, self.col, 1, 1)
        except FileException:
            self.vfs.pop()

    def refresh_spinbox(self):
        self.doubleSpinBox.setValue(self.slider_confidence.value() / 100)

    def refresh_slider(self):
        self.slider_confidence.setValue(self.doubleSpinBox.value() * 100)

    def start_detect(self):
        if not self._source_check():
            return
        self.isRefresh = self.btn_refresh.isChecked()
        self.isProcessing = True
        self.threadNum = self.spinBox_parallel.value()
        self.isParallel = True if (self.threadNum > 1 and len(self.vfs) > 1) else False
        self.model_path = self.modelPath[self.comboBox_model.currentIndex()]
        self.output_path = self.lineEdit_path.text()
        self.infer = ' eptry.py --infer'
        self.model_dir = ' --model_dir=' + self.model_path
        self.output_dir = '' if self.output_path == '' else (' --output_dir=' + self.output_path)
        self.use_gpu = ' --use_gpu=' + str(self.isUseGPU)
        self.thread_hold = ' --threshold=' + str(self.doubleSpinBox.value())

        for i in range(self.threadNum):
            self._start_new_detect_thread()
        self.update_ui()

    def _source_check(self):
        if len(self.vfs) < 1:
            QMessageBox.warning(self, "未添加源", "请点击左边'+'按钮添加视频源", QMessageBox.Ok, QMessageBox.Ok)
            return False
        return True

    def _start_new_detect_thread(self):
        if self.processedCount < len(self.vfs):
            vf = self.vfs[self.processedCount]
            file_name = vf.get_file_name()
            print("开始处理:", file_name)
            video_file = ' --video_file=' + vf.get_path()
            order = 'python' \
                    + self.infer + self.model_dir + video_file + self.use_gpu + self.output_dir + self.thread_hold
            executor = DetectionCmdExecutor(order, self, self.threadLock, self.isParallel)
            executor.setName(file_name)
            executor.gotFrameCount.connect(self._refresh_total_frame)
            executor.gotFrameDetect.connect(self._refresh_total_detect)
            executor.tempReady.connect(vf.enter_temp_detect_mod)
            if self.isRefresh:
                executor.gotTempImg.connect(vf.set_progressing_img)
            executor.gotPeopleNum.connect(vf.set_progressing_people_num)
            executor.updateProgress.connect(vf.set_progress_bar)
            executor.finished.connect(vf.exit_temp_detect_mod)
            executor.finished.connect(self._start_new_detect_thread)
            executor.start()
            self.executors.append(executor)
            self.processedCount += 1

    def _refresh_total_frame(self, new_count: int):
        self.totalFrame += new_count
        print("线程池中总帧数:", self.totalFrame)

    def _refresh_total_detect(self):
        self.totalDetect += 1
        if self.isParallel:
            # print('total fresh')
            names = []
            for executor in self.executors:
                names.append(executor.getName())
            self.label_process.setText("正在处理{}:".format(names))
            self.progressBar_process.setValue(self.totalDetect / self.totalFrame * 100)
            print("总已处理帧:", self.totalDetect)

    def start_track(self):
        if not self._source_check():
            return

        self.infer_mot = ' entry.py --mot'
        self.config = ' -c configs/mot/deepsort/deepsort_pcb_pyramid_r101.yml'
        self.det_results_dir = ' --det_results_dir=output/det/1/'
        self.track_output_dir = ' --output_dir=output/result/'
        self.save_videos = ' --save_videos'

        thread_lock = threading.Lock()
        self._start_new_track_thread(thread_lock)

        self.isProcessing = True
        self.update_ui()

    def _start_new_track_thread(self, thread_lock: threading.Lock):
        if self.processedCount < len(self.vfs):
            vf = self.vfs[self.processedCount]
            file_name = vf.get_file_name()
            print("开始处理:", file_name)
            video_file = ' --video_file=' + vf.get_path()[8:]
            order = ('python' +
                     self.infer_mot + self.config + self.det_results_dir + video_file + self.track_output_dir + self.save_videos)
            if os.getlogin() == 'hao':
                print("开发者运行\n" + order)
                QMessageBox.information(self, "略过", "开发者运行", QMessageBox.Ok, QMessageBox.Ok)
                return
            executor = TrackCmdExecutor(order, thread_lock)
            executor.setName(file_name)
            executor.startedTrack.connect(vf.enter_temp_track_mod)
            executor.updateProgress.connect(vf.set_progressing_text)
            executor.updateProgress.connect(vf.set_progress_bar)
            executor.gotFrameCount.connect(self._refresh_total_frame)
            executor.finishedTrack.connect(self._start_new_track_thread)
            executor.savedVideo.connect(vf.exit_temp_track_mod)
            executor.start()
            self.executors.append(executor)
            self.processedCount += 1
        else:
            self.isProcessing = False
            self.update_ui()

    def update_ui(self):
        is_processing = self.isProcessing
        self.btn_stop.setEnabled(is_processing)
        if is_processing:
            self.btn_stop.setFocus()
        self.frame_model.setEnabled(not is_processing)
        self.frame_detect.setEnabled(not is_processing)
        self.frame_track.setEnabled(not is_processing)
        self.frame_save.setEnabled(not is_processing)
        self.label_process.setText("正在处理" if is_processing else "等待处理")

    def on_btn_stop_clicked(self):
        for executor in self.executors:
            executor.terminate()
        for vf in self.vfs:
            vf.exit_temp_detect_mod()
        self.isProcessing = False
        self.executors.clear()
        self.totalDetect = 0
        self.totalFrame = 0
        self.processedCount = 0
        self.btn_stop.setEnabled(False)
        self.progressBar_process.setValue(0)
        self.update_ui()

    def change_path(self):
        path = QFileDialog.getExistingDirectory()
        self.savePath = path
        self.lineEdit_path.setText(path)

    def switch_gpu_parallel(self):
        self.isUseGPU = self.radioButton_use_gpu.isChecked()
        self.isParallel = self.radioButton_parallel.isChecked()
        self.spinBox_parallel.setEnabled(self.isParallel)

    def switch_save(self):
        self.isSave = self.checkBox_save.checkState()
        self.label_path.setEnabled(self.isSave)
        self.btn_change_path.setEnabled(self.isSave)
        self.lineEdit_path.setEnabled(self.isSave)
