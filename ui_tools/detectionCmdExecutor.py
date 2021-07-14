import subprocess
import threading

from PyQt5.QtCore import pyqtSignal, QObject


class DetectionCmdExecutor(threading.Thread, QObject):
    gotFrameCount = pyqtSignal(int)
    gotFrameDetect = pyqtSignal(int)
    updateProgress = pyqtSignal(int)
    gotPeopleNum = pyqtSignal(int)
    tempReady = pyqtSignal()
    gotTempImg = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, order: str, main_win, thread_lock: threading.Lock, is_parallel: bool):
        threading.Thread.__init__(self)
        QObject.__init__(self)
        print(order)
        self.order = order
        self.win = main_win
        self.threadLock = thread_lock
        self.isParallel = is_parallel
        self.cmd = subprocess.Popen(self.order, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.detectFrame = 0
        self.peopleNum = 0
        self.frameCount = 999999

    def run(self) -> None:
        for i in iter(self.cmd.stdout.readline, 'b'):
            if not i:
                break

            msg = i.decode('utf8')
            # print(msg)

            if msg[:6] == 'detect':
                progress = int(self.detectFrame / self.frameCount * 100)
                self.detectFrame = int(msg.split(':')[1])
                print(self.getName(), "已处理帧:", self.detectFrame)
                self.threadLock.acquire()
                self.gotFrameDetect.emit(1)
                self.gotPeopleNum.emit(self.peopleNum)
                self.updateProgress.emit(progress)
                if not self.isParallel:
                    # print('single fresh')
                    self.win.label_process.setText("正在处理{}:".format(self.name))
                    self.win.progressBar_process.setValue(progress)
                self.threadLock.release()
                self.peopleNum = 0
            elif msg[:5] == 'class':
                self.peopleNum += 1
            elif msg[:11] == 'frame_count':
                self.frameCount = int(msg.split(' ')[1])
                self.gotFrameCount.emit(self.frameCount)
                print("总帧数:", self.frameCount)
            elif msg[:10] == 'temp_image':
                self.gotTempImg.emit()
            elif msg[:10] == 'temp_ready':
                self.tempReady.emit()

            if self.detectFrame == self.frameCount:
                self.finished.emit()

    def terminate(self):
        if self.is_alive():
            if self.threadLock.locked():
                self.threadLock.release()
            print(self.getName(), "命令行终止...")
            self.cmd.terminate()
