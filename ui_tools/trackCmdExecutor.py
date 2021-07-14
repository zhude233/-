import subprocess
import threading

from PyQt5.QtCore import pyqtSignal, QObject


class TrackCmdExecutor(threading.Thread, QObject):
    startedTrack = pyqtSignal()
    gotFrameCount = pyqtSignal(int)
    updateProgress = pyqtSignal(int)
    finishedTrack = pyqtSignal()
    savedVideo = pyqtSignal()

    def __init__(self, order: str, thread_lock: threading.Lock):
        super().__init__()
        print(order)
        self.order = order
        self.threadLock = thread_lock
        self.cmd = subprocess.Popen(self.order, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        self.frameCount = 999999

    def run(self) -> None:
        for i in iter(self.cmd.stdout.readline, 'b'):
            if not i:
                break

            msg = i.decode('utf8')
            # print(msg)

            if msg[0] == '[':
                if 'Processing frame' in msg:
                    self.updateProgress.emit(int(msg.split()[-1]) / self.frameCount * 100)
                    print(int(msg.split()[-1]) / self.frameCount * 100)
                elif 'Length of' in msg:
                    self.frameCount = int(msg.split()[-1])
                    self.gotFrameCount.emit(self.frameCount)
                    print(self.frameCount)
                elif 'MOT results' in msg:
                    self.finishedTrack.emit()
                    print('mot res')
                elif 'Save video' in msg:
                    self.savedVideo.emit()
                    print('saved')
                elif 'Starting tracking' in msg:
                    self.startedTrack.emit()
                    print('start')

    def terminate(self):
        if self.is_alive():
            if self.threadLock.locked():
                self.threadLock.release()
            print(self.getName(), "命令行终止...")
            self.cmd.terminate()
