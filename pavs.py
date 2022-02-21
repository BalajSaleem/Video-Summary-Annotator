from logging import exception
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLineEdit, QComboBox, QFileDialog, QStyleFactory, QHBoxLayout, QLabel, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar, QTableWidget, QVBoxLayout, QTableWidgetItem, QHBoxLayout, QSplitter, QGroupBox, QFormLayout, QAction, QGridLayout, QShortcut
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5 import QtCore, Qt
from PyQt5.QtCore import Qt, QUrl, QDir, QTime, pyqtSlot
from PyQt5.QtGui import QKeySequence, QStandardItemModel, QFont
import csv
import sys
import cv2 as cv

audio_extensions = [".wav", ".mp3"]
video_extensions = [".avi", ".mp4", ".mkv"]

class Window(QMainWindow):

    #TODO: Pause video every 2 seconds
    #Labeler not able to play unless label asigned (0-5)
    def __init__(self):
        super().__init__()

        self.title = "Annotator for Videos"
        self.labels = [x for x in range(1,6)]
        self.est_counts = [0] * 5
        self.curr_counts = [0] * 5
        self.label_ratios = [(0.25,0.65), (0.20,0.40), (0.10,0.20), (0.05,0.10), (0.01,0.05)]
        # self.top = 100
        # self.left = 100
        # self.width = 300
        # self.height = 400
        # self.setWindowState = "Qt.WindowMaximized"
        iconName = "home.png"
        self.InitWindow()

    def InitWindow(self):
        self.setWindowTitle(self.title)
        # self.setWindowIcon(QtGui.QIcon(iconName))
        self.setWindowState(QtCore.Qt.WindowMaximized)

        self.UiComponents()

        self.show()

    def UiComponents(self):

        self.rowNo = 1
        self.colNo = 0
        self.fName = ""
        self.fName2 = ""
        self.fileNameExist = ""
        self.dropDownName = ""
        self.fps = 24
        self.lastPause = QTime(0,0,0,0)



        self.model = QStandardItemModel()

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)
        self.tableWidget = QTableWidget()
        self.tableWidget.cellClicked.connect(self.checkTableFrame)

        self.videoWidget = QVideoWidget()
        self.frameID=0


        self.insertBaseRow()

        openButton = QPushButton("Open...")
        openButton.clicked.connect(self.openFile)

        self.lbltxt1 = QLabel('End')
        self.lbltxt1.setFixedWidth(120)
        self.lbltxt2 = QLabel('Start')
        self.lbltxt2.setFixedWidth(120)
        self.lbltxt3 = QLabel('Total')
        self.lbltxt3.setFixedWidth(120)

        self.lbl_name_layout = QHBoxLayout()
        self.lbl_name_layout.addWidget(QLabel( "Labels:" ))
        self.lbl_curr_count_layout = QHBoxLayout()
        self.lbl_curr_count_layout.addWidget(QLabel( "Current:" ))
        self.lbl_est_count_layout = QHBoxLayout()
        self.lbl_est_count_layout.addWidget(QLabel( "Estimated:" ))


        for lbl in self.labels:
            wid_lbl = QLabel( str(lbl) + "s" )
            #wid_lbl.setFixedWidth(40)
            wid_lbl.setFixedHeight(15)
            self.lbl_name_layout.addWidget(wid_lbl)

        for lbl in self.curr_counts:
            wid_lbl = QLabel( str(lbl) )
            #wid_lbl.setFixedWidth(40)
            wid_lbl.setFixedHeight(15)
            self.lbl_curr_count_layout.addWidget(wid_lbl)
        
        for lbl in self.est_counts:
            wid_lbl = QLabel( str(lbl) )
            #wid_lbl.setFixedWidth(40)
            wid_lbl.setFixedHeight(15)
            self.lbl_est_count_layout.addWidget(wid_lbl)




        self.counts_lbl = QLabel('')
        self.counts_lbl.setFixedWidth(40)
        
        self.curr_counts_lbl = QLabel('Curr:')
        self.curr_counts_lbl.setFixedWidth(40)

        self.estimate_counts = QLabel('Est:')
        self.estimate_counts.setFixedWidth(40)

        self.v_box_tags = QVBoxLayout()
        self.v_box_tags.addWidget(self.counts_lbl)
        self.v_box_tags.addWidget(self.curr_counts_lbl)
        self.v_box_tags.addWidget(self.estimate_counts)
        
        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)


        self.lbl = QLabel('00:00:00')
        self.lbl.setFixedWidth(120)
        self.lbl.setUpdatesEnabled(True)

        self.mlbl = QLabel('00:00:00')
        self.mlbl.setFixedWidth(120)
        self.mlbl.setUpdatesEnabled(True)

        # self.lbl.setStyleSheet(stylesheet(self))
        
        self.elbl = QLabel('00:00:00')
        self.elbl.setFixedWidth(120)
        self.elbl.setUpdatesEnabled(True)
        # self.elbl.setStyleSheet(stylesheet(self))


        # self.nextButton = QPushButton("-->")
        # self.nextButton.clicked.connect(self.next)

        self.nextButton = QPushButton("Clear")
        self.nextButton.clicked.connect(self.clearTable)


        self.delButton = QPushButton("Delete")
        self.delButton.clicked.connect(self.delete)

        self.exportButton = QPushButton("Export")
        self.exportButton.clicked.connect(self.export)

        self.importButton = QPushButton("Import")
        self.importButton.clicked.connect(self.importCSV)

        # self.ctr = QLineEdit()
        # self.ctr.setPlaceholderText("Extra")

        self.startTime = QLineEdit()
        self.startTime.setPlaceholderText("Select Start Time")

        self.endTime = QLineEdit()
        self.endTime.setPlaceholderText("Select End Time")

        self.iLabel = QComboBox(self)
        #self.iLabel.addItem("0. Boring")
        self.iLabel.addItem("1. One")
        self.iLabel.addItem("2. Two")
        self.iLabel.addItem("3. Three")
        self.iLabel.addItem("4. Four")
        self.iLabel.addItem("5. Five")
        # self.iLabel.addItem("7. Showing")
        # self.iLabel.addItem("8. Following Instructions")
        self.iLabel.activated[str].connect(self.style_choice)


        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 100)
        self.positionSlider.sliderMoved.connect(self.setPosition)
        self.positionSlider.sliderMoved.connect(self.handleLabel)
        self.positionSlider.setSingleStep(2)
        self.positionSlider.setPageStep(20)
        self.positionSlider.setAttribute(Qt.WA_TranslucentBackground, True)

        self.errorLabel = QLabel()
        self.errorLabel.setSizePolicy(QSizePolicy.Preferred,
                QSizePolicy.Maximum)

        # Main plotBox
        plotBox = QHBoxLayout()
        vbox1 = QVBoxLayout()
        vbox2 = QVBoxLayout()
        vbox3 = QVBoxLayout()

        controlLayout = QHBoxLayout()
        controlLayout.setContentsMargins(32, 0, 32, 0)
        controlLayout.addWidget(openButton)
        controlLayout.addWidget(self.playButton)
        vbox1.addWidget(self.lbltxt1)
        vbox1.addWidget(self.lbl)
        vbox2.addWidget(self.lbltxt2)
        vbox2.addWidget(self.mlbl)
        vbox3.addWidget(self.lbltxt3)
        vbox3.addWidget(self.elbl)
        controlLayout.addLayout(vbox2)
        controlLayout.addLayout(vbox1)
        controlLayout.addLayout(vbox3)

        
        # controlLayout.addWidget(self.lbl)
        # controlLayout.addWidget(self.mlbl)
        # #controlLayout.addWidget(self.positionSlider)
        # controlLayout.addWidget(self.elbl)

        wid = QWidget(self)
        self.setCentralWidget(wid)

        # Left Layout{
        # layout.addWidget(self.videoWidget)

        layout = QVBoxLayout()
        layout.addWidget(self.videoWidget, 3)
        # layout.addLayout(self.grid_root)
        layout.addLayout(controlLayout)
        layout.addWidget(self.errorLabel)

        plotBox.addLayout(layout, 5)
        # }

   
        # Right Layout {
        inputFields = QHBoxLayout()
        inputFields.setContentsMargins(0, 0, 0, 0)


        
        feats = QHBoxLayout()
        feats.addWidget(self.nextButton)
        feats.addWidget(self.delButton)
        feats.addWidget(self.exportButton)
        feats.addWidget(self.importButton)

        layout2 = QVBoxLayout()
        layout2.addWidget(self.tableWidget,20)
        layout2.addLayout(self.lbl_name_layout, 1)
        layout2.addLayout(self.lbl_curr_count_layout,1)
        layout2.addLayout(self.lbl_est_count_layout,1)
        layout2.addLayout(feats, 2)
        # layout2.addWidget(self.nextButton)
        # }

        plotBox.addLayout(layout2, 2)

        # self.setLayout(layout)
        wid.setLayout(plotBox)

        self.shortcut = QShortcut(QKeySequence("["), self)
        self.shortcut.activated.connect(self.addStartTime)
        self.shortcut = QShortcut(QKeySequence("]"), self)
        self.shortcut.activated.connect(self.addEndTime)
        self.shortcut = QShortcut(QKeySequence("L"), self)
        self.shortcut.activated.connect(self.openFile)
        self.shortcut = QShortcut(QKeySequence("C"), self)
        self.shortcut.activated.connect(self.clearTable)
        self.shortcut = QShortcut(QKeySequence("P"), self)
        self.shortcut.activated.connect(self.next)

        self.shortcut = QShortcut(QKeySequence(Qt.Key_Right), self)
        self.shortcut.activated.connect(self.forwardSlider)
        self.shortcut = QShortcut(QKeySequence(Qt.Key_Left), self)
        self.shortcut.activated.connect(self.backSlider)
        self.shortcut = QShortcut(QKeySequence(Qt.Key_Up), self)
        self.shortcut.activated.connect(self.volumeUp)
        self.shortcut = QShortcut(QKeySequence(Qt.Key_Down), self)
        self.shortcut.activated.connect(self.volumeDown)
        self.shortcut = QShortcut(QKeySequence(Qt.ShiftModifier +  Qt.Key_Right) , self)
        self.shortcut.activated.connect(self.forwardSlider10)
        self.shortcut = QShortcut(QKeySequence(Qt.ShiftModifier +  Qt.Key_Left) , self)
        self.shortcut.activated.connect(self.backSlider10)


        self.shortcut = QShortcut(QKeySequence("1"), self)
        self.shortcut.activated.connect(lambda: self.set_label(0))
        self.shortcut = QShortcut(QKeySequence("2"), self)
        self.shortcut.activated.connect(lambda: self.set_label(1))
        self.shortcut = QShortcut(QKeySequence("3"), self)
        self.shortcut.activated.connect(lambda: self.set_label(2))
        self.shortcut = QShortcut(QKeySequence("4"), self)
        self.shortcut.activated.connect(lambda: self.set_label(3))
        self.shortcut = QShortcut(QKeySequence("5"), self)
        self.shortcut.activated.connect(lambda: self.set_label(4))

        self.mediaPlayer.setVideoOutput(self.videoWidget)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.positionChanged.connect(self.handleLabel)
        self.mediaPlayer.positionChanged.connect(self.pauseAfterTwo)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Movie",
                QDir.homePath())

        if fileName != '':
            self.fileNameExist = fileName
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)
        self.videopath = QUrl.fromLocalFile(fileName)
        self.errorLabel.setText(fileName)
        cam = cv.VideoCapture(fileName)
        self.fps = cam.get(cv.CAP_PROP_FPS)
        self.lastPause = QTime(0,0,0,0)
        print(f"* Video Loaded")
        print(f"* FPS: {self.fps}")
        self.errorLabel.setStyleSheet('color: black')

    def play(self):
        # self.is_playing_video = not self.is_playing_video
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()
            # self._play_video()
            # self.errorLabel.setText("Start: " + " -- " + " End:")

    def _play_video(self):
        if self.is_playing_video and self.video_fps:
            frame_idx = min(self.render_frame_idx+1, self.frame_count)
            print(frame_idx)

            if frame_idx == self.frame_count:
                self.on_play_video_clicked()
            else:
                self.target_frame_idx = frame_idx

    def style_choice(self, text):
        self.dropDownName = text
        QApplication.setStyle(QStyleFactory.create(text))


    def addStartTime(self):
        self.startTime.setText(self.lbl.text())

    def addEndTime(self):
        self.endTime.setText(self.lbl.text())
    
    def text_to_time(self, text):
        times = text.split(':')
        return QTime(int(times[0]),int(times[1]),int(times[2]))

    def set_label(self, index):
        if (self.mediaPlayer.state() == QMediaPlayer.PausedState):
            print(f"* Setting Label: {self.iLabel.itemText(index)}")
            self.last_entry_time = self.lbl.text().split
            row_widget = QTableWidgetItem(self.mlbl.text())
            row_widget.setFlags(QtCore.Qt.ItemIsEnabled)
            self.tableWidget.setItem(self.rowNo, self.colNo, row_widget)
            self.colNo += 1
            row_widget = QTableWidgetItem(self.lbl.text())
            row_widget.setFlags(QtCore.Qt.ItemIsEnabled)
            self.tableWidget.setItem(self.rowNo, self.colNo, row_widget)
            self.colNo += 1
            self.tableWidget.setItem(self.rowNo, self.colNo, QTableWidgetItem(str(index+1)))
            if index > 2:
                font = QFont()
                font.setBold(True)
                self.tableWidget.item(self.rowNo, self.colNo).setFont(font)
            self.curr_counts[index]+=1
            self.colNo += 1
            self.tableWidget.setItem(self.rowNo, self.colNo, QTableWidgetItem(self.iLabel.itemText(index).split(' ', 1)[1]))
            self.colNo = 0
            self.rowNo += 1
            self.updateCurrCounts()
            if (self.mediaPlayer.state() != QMediaPlayer.StoppedState):
                self.playButton.click()

    def next(self):
        self.tableWidget.setItem(self.rowNo, self.colNo, QTableWidgetItem(self.startTime.text()))
        self.colNo += 1
        self.tableWidget.setItem(self.rowNo, self.colNo, QTableWidgetItem(self.endTime.text()))
        self.colNo += 1
        self.tableWidget.setItem(self.rowNo, self.colNo, QTableWidgetItem(str(self.iLabel.currentIndex()+1)))
        self.colNo += 1
        self.tableWidget.setItem(self.rowNo, self.colNo, QTableWidgetItem(self.iLabel.currentText().split(' ', 1)[1]))
        self.colNo = 0
        self.rowNo += 1
        # print(self.ctr.text(), self.startTime.text(), self.iLabel.text(), self.rowNo, self.colNo)
        # print(self.iLabel.currentIndex())

    def nextLabel(self):
        self.iLabel.setCurrentIndex( self.iLabel.currentIndex+1 )
        self.iLabel.update()

    def lastLabel(self):
        self.iLabel.setCurrentIndex( self.iLabel.currentIndex-1 )
        self.iLabel.update()

    def delete(self):
        # print("delete")
        index_list = []
        for model_index in self.tableWidget.selectionModel().selectedRows():
            index = QtCore.QPersistentModelIndex(model_index)
            index_list.append(index)

        self.rowNo = self.rowNo - len(index_list)

        for index in index_list:
            row_lbl = int(self.tableWidget.item(index.row(), 2).text())
            self.curr_counts[row_lbl-1] -=1
            self.updateCurrCounts()
            self.tableWidget.removeRow(index.row())

    def clearTable(self):
        while self.tableWidget.rowCount() > 0:
            self.tableWidget.removeRow(0)
        self.insertBaseRow()
        self.lastPause = QTime(0,0,0,0)
        self.setPosition(0)
        self.curr_counts = [0] * 5
        #self.est_counts = [(0,0)] * 5
        self.updateCurrCounts()
        #self.updateEstCounts()
        print("Clearing")

    def export(self):
        if self.fileNameExist:
            self.fName = ((self.fileNameExist.rsplit('/', 1)[1]).rsplit('.',1))[0]
        path, _ = QFileDialog.getSaveFileName(self, 'Save File', QDir.homePath() + "/"+self.fName+".csv", "CSV Files(*.csv *.txt)")
        if path:
            with open(path, 'w') as stream:
                print("saving", path)
                writer = csv.writer(stream)
                # writer = csv.writer(stream, delimiter=self.delimit)
                for row in range(self.tableWidget.rowCount()):
                    rowdata = []
                    for column in range(self.tableWidget.columnCount()):
                        item = self.tableWidget.item(row, column)
                        if item != None and item != "":
                            rowdata.append(item.text())
                        else:
                            break
                    writer.writerow(rowdata)
        # self.isChanged = False
        # self.setCurrentFile(path)

    def importCSV(self):
        # if fName2 != "":
            # self.fName2 = ((self.fileNameExist.rsplit('/', 1)[1]).rsplit('.',1))[0]
            # path, _ = QFileDialog.getSaveFileName(self, 'Save File', QDir.homePath() + "/"+self.fName2+".csv", "CSV Files(*.csv *.txt)")
        # else:
        self.clearTable()
        path, _ = QFileDialog.getOpenFileName(self, 'Save File', QDir.homePath() , "CSV Files(*.csv *.txt)")
        print(path)
        if path:
            with open(path, 'r') as stream:
                print("loading", path)
                reader = csv.reader(stream)
                # reader = csv.reader(stream, delimiter=';', quoting=csv.QUOTE_ALL)
                # reader = csv.reader(stream, delimiter=';', quoting=csv.QUOTE_ALL)
                # for row in reader:
                for i, row in enumerate(reader):
                    if i == 0:
                        continue
                    else:
                        if(len(row) == 4):
                            st, et, li, ln = row
                            self.tableWidget.setItem(self.rowNo, self.colNo, QTableWidgetItem(st))
                            self.colNo += 1
                            self.tableWidget.setItem(self.rowNo, self.colNo, QTableWidgetItem(et))
                            self.colNo += 1
                            self.tableWidget.setItem(self.rowNo, self.colNo, QTableWidgetItem(str(li)))
                            if int(li) > 3:
                                font = QFont()
                                font.setBold(True)
                                self.tableWidget.item(self.rowNo, self.colNo).setFont(font)
                            self.curr_counts[int(li) - 1] +=1
                            self.updateCurrCounts()
                            self.colNo += 1
                            self.tableWidget.setItem(self.rowNo, self.colNo, QTableWidgetItem(ln))
                            self.rowNo += 1
                            self.colNo = 0

    def insertBaseRow(self):
        self.tableWidget.setColumnCount(4) #, Start Time, End Time, TimeStamp
        self.tableWidget.setRowCount(500)
        self.rowNo = 1
        self.colNo = 0
        self.tableWidget.setItem(0, 0, QTableWidgetItem("Start Time"))
        self.tableWidget.setItem(0, 1, QTableWidgetItem("End Time"))
        self.tableWidget.setItem(0, 2, QTableWidgetItem("Label Index"))
        self.tableWidget.setItem(0, 3, QTableWidgetItem("Labeler Name"))

    def checkTableFrame(self, row, column):
        if ((row > 0) and (column < 2)):
            # print("Row %d and Column %d was clicked" % (row, column))
            item = self.tableWidget.item(row, column)
            
            if (item != (None and "")):
                #try:
                itemFrame = item.text()
                itemFrame = itemFrame.split(":")
                frameTime = int(itemFrame[2]) + int(itemFrame[1])*60 + int(itemFrame[0])*3600
                elblFrames = self.elbl.text().split(":")
                elblFrameTime = int(elblFrames[2]) + int(elblFrames[1])*60 + int(elblFrames[0])*3600
                # print("Elbl FT ", str(elblFrameTime))
                # print("FT ", str(frameTime))
                # print(frameTime)
                self.mediaPlayer.setPosition(frameTime*1000)
                last_entry = self.tableWidget.item(self.rowNo-1, 1).text()
                self.lastPause = self.text_to_time(last_entry) 
                self.time = QTime(int(itemFrame[0]),int(itemFrame[1]),int(itemFrame[2])) 
                # print(self.time)
                # print(self.lastPause)
                # except exception as e:
                #     print(e)
                #     self.errorLabel.setText("Some Video Error - Please Recheck Video Imported!")
                #     self.errorLabel.setStyleSheet('color: red')

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)
        mtime = QTime(0,0,0,0)
        mtime = mtime.addMSecs(self.mediaPlayer.duration())
        start_time = QTime(0,0,0,0)
        total_secs = start_time.addMSecs(self.mediaPlayer.duration())
        self.total_secs = QTime(0, 0, 0).secsTo(total_secs)
        self.setEstCounts()
        self.updateEstCounts()
        print(f"* Length: {self.total_secs}s")
        self.elbl.setText(mtime.toString())
    
    def setEstCounts(self):
         for i in range(1,6):
            range_start = int( self.total_secs * self.label_ratios[i-1][0])
            range_end = int (self.total_secs * self.label_ratios[i-1][1])
            self.est_counts[i-1] = (range_start, range_end)
    
    def updateEstCounts(self):
        for i in range(len(self.est_counts)) :
            est_lbl =   self.lbl_est_count_layout.itemAt(i+1).widget()
            est_lbl.setText(str(self.est_counts[i][0]) + " - " + str(self.est_counts[i][1]))
    
    def updateCurrCounts(self):
        for i in range(len(self.est_counts)) :
            est_lbl =   self.lbl_curr_count_layout.itemAt(i+1).widget()
            est_lbl.setText(str(self.curr_counts[i]))



    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.errorLabel.setText("Error: " + self.mediaPlayer.errorString())
        self.errorLabel.setStyleSheet('color: red')

    def forwardSlider(self):
        self.mediaPlayer.setPosition(self.mediaPlayer.position() + 1*60)

    def forwardSlider10(self):
            self.mediaPlayer.setPosition(self.mediaPlayer.position() + int(self.fps) * 60)

    def backSlider(self):
        self.mediaPlayer.setPosition(self.mediaPlayer.position() - 1*60)

    def backSlider10(self):
        self.mediaPlayer.setPosition(self.mediaPlayer.position() - int(self.fps) * 60) #NOTE: CHANGE HERE

    def volumeUp(self):
        self.mediaPlayer.setVolume(self.mediaPlayer.volume() + 10)
        print("Volume: " + str(self.mediaPlayer.volume()))

    def volumeDown(self):
        self.mediaPlayer.setVolume(self.mediaPlayer.volume() - 10)
        print("Volume: " + str(self.mediaPlayer.volume()))

    # def mouseMoveEvent(self, event):
        # if event.buttons() == Qt.LeftButton:
        #     self.move(event.globalPos() \- QPoint(self.frameGeometry().width() / 2, \
        #                 self.frameGeometry().height() / 2))
        #     event.accept()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    ##################### update Label ##################################
    def handleLabel(self):
        self.lbl.clear()
        mtime = QTime(0,0,0,0)
        self.time = mtime.addSecs(self.mediaPlayer.position() // 1000)
        self.mtime = self.time.addSecs(-2)
        self.lbl.setText(self.time.toString())
        self.mlbl.setText(self.mtime.toString())

    def pauseAfterTwo(self):
        if  ( (self.time.second() % 2) == 0 ) and (self.lastPause.secsTo(self.time) >= 1):
            #print("* Pausing")
            if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
                self.playButton.click()
                self.lastPause = self.time
                #print(f"Updated Last Pause: {self.lastPause}" )
            

    def dropEvent(self, event):
        f = str(event.mimeData().urls()[0].toLocalFile())
        self.loadFilm(f)

    def clickFile(self):
        print("File Clicked")

    def clickExit(self):
        sys.exit()

App = QApplication(sys.argv)
window = Window()
sys.exit(App.exec())
