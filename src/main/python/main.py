import numpy as np
from time import sleep
import json
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QApplication, QStatusBar, QMainWindow, QMessageBox, QFormLayout, QAction, qApp, QVBoxLayout,QHBoxLayout,QCheckBox, QWidget,QLabel,QPushButton,QGroupBox, QComboBox, QSpinBox,QLineEdit,QProgressBar,QFileDialog,QDialog
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import matplotlib
matplotlib.use('Qt5Agg')

#from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import os
import sys

# global variable
project_dictionary = {} # empty dictionary
import_param = []

class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)



    def import_img(self):
        global import_param
        """Long-running task."""
        for i in range(import_param[3]):
            sleep(1)
            self.progress.emit(i + 1)
        self.finished.emit()
    


class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):

        wid = QWidget(self)
        self.setCentralWidget(wid)

        

        # create the menus
        # from Project
        new_project_action = QAction('New', self)
        new_project_action.setShortcut('Ctrl+N')
        new_project_action.setStatusTip('New')
        new_project_action.triggered.connect(self.create_project)
        

        open_project_action = QAction('Open', self)
        open_project_action.setShortcut('Ctrl+O')
        open_project_action.setStatusTip('Open')
        # TO DO: create a trigger

        save_project_action = QAction('Save', self)
        save_project_action.setShortcut('Ctrl+N')
        save_project_action.setStatusTip('Save')
        # TO DO: create a trigger

        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(qApp.quit)

        # from Data
        import_img_action = QAction('Import images',self)
        import_img_action.setStatusTip('Import images')
        import_img_action.triggered.connect(self.show_dialog_import) # show a dialog box on trigger
        
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        menubar = self.menuBar()
        menubar.setNativeMenuBar(True)

        filemenu_project = menubar.addMenu('Project')
        filemenu_project.addAction(new_project_action)
        filemenu_project.addAction(open_project_action)
        filemenu_project.addAction(save_project_action)
        filemenu_project.addAction(exit_action)

        filemenu_data = menubar.addMenu('Data')
        filemenu_data.addAction(import_img_action)


        filemenu_calibrate = menubar.addMenu('Calibrate')
        define_calib_board_action = QAction("Define calibration board",self)
        start_calib_action = QAction("Start calibration",self)
        filemenu_calibrate.addAction(define_calib_board_action)
        filemenu_calibrate.addAction(start_calib_action)

        filemenu_preprocess = menubar.addMenu('Preprocess')
        correct_images_action = QAction("Correct images", self)
        adjust_contrast_action = QAction("Adjust contrast", self)
        filemenu_preprocess.addAction(correct_images_action)
        filemenu_preprocess.addAction(adjust_contrast_action)

        # Create a side layout for the controls
        side_layout = QVBoxLayout()  

        side_layout.addWidget(QLabel("Dataset"))
        self.dataset_combobox = QComboBox()
        self.dataset_combobox.setFixedHeight(30)
        side_layout.addWidget(self.dataset_combobox)

        frame_layout = QHBoxLayout()
        self.frame_num = QSpinBox()
        self.frame_num.setFixedHeight(30)
        frame_layout.addWidget(QLabel("Frame"))
        frame_layout.addWidget(self.frame_num)
        side_layout.addLayout(frame_layout)

        time_layout = QHBoxLayout()
        self.time_num = QLineEdit()
        self.time_num.setFixedHeight(30)
        time_layout.addWidget(QLabel("Time (s)"))
        time_layout.addWidget(self.time_num)
        side_layout.addLayout(time_layout)

        # Add layout bitmap (background experiment or calibration image)
        bitmap_layout = QHBoxLayout()
        self.checkbox_bitmap = QCheckBox("Show bitmap")
        
        self.button_bitmap = QPushButton(">")
        self.button_bitmap.setFixedWidth(50)

        bitmap_layout.addWidget(self.checkbox_bitmap)
        bitmap_layout.addWidget(self.button_bitmap)

        side_layout.addLayout(bitmap_layout)

        # scalar checkbox and button
        scalar_layout = QHBoxLayout()
        checkbox_scalar = QCheckBox("Show scalar")
        
        button_scalar = QPushButton(">")
        button_scalar.setFixedWidth(50)

        scalar_layout.addWidget(checkbox_scalar)
        scalar_layout.addWidget(button_scalar)

        side_layout.addLayout(scalar_layout)

        # vector checkbox and button
        vector_layout = QHBoxLayout()
        checkbox_vector = QCheckBox("Show vector")
        
        button_vector = QPushButton(">")
        button_vector.setFixedWidth(50)

        vector_layout.addWidget(checkbox_vector)
        vector_layout.addWidget(button_vector)

        side_layout.addLayout(vector_layout)
        side_layout.addStretch()
        self.progress_bar = QProgressBar()
        side_layout.addWidget(self.progress_bar)
        
        viewport_layout = QVBoxLayout()
        #label_viewport = QLabel()
        fig = MplCanvas(self)

        # Create toolbar, passing canvas as first parament, parent (self, the MainWindow) as second.
        toolbar = NavigationToolbar(fig, self)
        viewport_layout.addWidget(fig)
        viewport_layout.addWidget(toolbar)
        viewport = QGroupBox("Viewport")
        viewport.setLayout(viewport_layout)

        sidebar = QGroupBox("Controls")
        sidebar.setLayout(side_layout)
        sidebar.setFixedWidth(250)

        # Set the window's main layout

        outer_layout = QHBoxLayout()
        outer_layout.addWidget(sidebar)
        outer_layout.addWidget(viewport)

        wid.setLayout(outer_layout)

        f = open(os.path.join('c:' + os.sep, 'Users','david','Documents','Python_Scripts','FinitePIV','src','build','settings','base.json'))
        data = json.load(f)
        app_name = data['app_name']
        app_version = data['version']
        self.setWindowTitle(app_name + ': '+app_version)
        self.setGeometry(0, 0, 1200, 800)
        self.showMaximized()
        self.show()

    def create_project(self):
        global project_dictionary

        project_path=QFileDialog.getExistingDirectory(self,"Choose Directory")
        path_to_project_folder = os.path.dirname(project_path)
        project_name = os.path.basename(project_path)
        
        # create a project disctionary
        project_dictionary = {'project_name': project_name, 'project_path':path_to_project_folder}
        with open("current_project.json", "w") as fp:
            json.dump(project_dictionary , fp) 

        # update the title of the main window
        self.setWindowTitle(project_name) 

    def show_dialog_import(self):
        global project_dictionary

        if 'project_name' in project_dictionary.keys():
            self.dlg = QDialog(self)
            Title = 'Import images'
            self.dlg.setWindowTitle(Title)
            self.dlg.dlg_layout = QFormLayout()
            self.dlg.image_format_combo = QComboBox()
            self.dlg.image_format_combo.addItem('TIF')
            self.dlg.image_format_combo.addItem('DNG')

            self.dlg.image_dt_combo = QComboBox()
            for i in range(1,100):
                self.dlg.image_dt_combo.addItem(str(i))

            self.dlg.dataset_combo = QComboBox()
            self.dlg.dataset_combo.addItem('Calibration')
            self.dlg.dataset_combo.addItem('Experiment')
            self.dlg.dlg_layout.addRow('dataset', self.dlg.dataset_combo)
            self.dlg.dlg_layout.addRow('format', self.dlg.image_format_combo)
            self.dlg.dlg_layout.addRow('time increment', self.dlg.image_dt_combo)
            self.dlg.dlg_button=QPushButton('OK')
            self.dlg.dlg_button.clicked.connect(self.get_import_parameters)
            self.dlg.dlg_layout.addRow('', self.dlg.dlg_button)
            self.dlg.setLayout(self.dlg.dlg_layout)
            self.dlg.exec()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('You must define a project before importing images')
            msg.setWindowTitle("Error")
            msg.exec_()

    def get_import_parameters(self):
        global project_dictionary, import_param
        
        import_dataset = self.dlg.dataset_combo.currentText()
        import_img_format = self.dlg.image_format_combo.currentText()
        import_img_format=str(import_img_format)
        import_img_dt = int(self.dlg.image_dt_combo.currentText())

        new_dataset = {'name': import_dataset, 'image_format':import_img_format, 'dt': import_img_dt}
        i = 1
        new_dataset_name = 'dataset_'+str(i)
        while new_dataset_name in project_dictionary.keys():
            i = i+1
            new_dataset_name = 'dataset_'+str(i)
        
        # update the main window controls
        self.dataset_combobox.addItem(import_dataset)
        self.frame_num.setValue(1)
        self.time_num.setText(str(0))
        self.checkbox_bitmap.setChecked(True)
        self.dlg.close()

        # get path to images
        image_path=QFileDialog.getExistingDirectory(self,"Choose Directory")
        
        # add to dictionary together with number of images
        new_dataset['source_image_path'] = image_path
        list_images = os.listdir(image_path)
        num_images = len(list_images)
        new_dataset['number images'] = num_images

        # add dataset to dictionary and export as json
        project_dictionary[new_dataset_name] = new_dataset
        with open("current_project.json", "w") as fp:
            json.dump(project_dictionary , fp)

        # create destination folder
        destination_folder = os.path.join(project_dictionary['project_path'], project_dictionary['project_name'], new_dataset['name'])
        msg = 'creating folder: '+destination_folder
        self.statusBar.showMessage(msg,3000)
        os.mkdir(destination_folder)

        # start the import in a new worker
        # place parameters in global list for the worker
        import_param = [import_img_format, image_path, destination_folder, num_images]
        self.import_thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.import_thread)
        self.import_thread.started.connect(self.worker.import_img)
        self.worker.progress.connect(self.update_progress_bar)
        self.worker.finished.connect(self.import_thread.quit)
        self.import_thread.start()

    def update_progress_bar(self, current_val):
        global import_param
        num_images = import_param[3]
        self.progress_bar.setValue(int(100 * current_val/num_images))
        
        
        if int(100 * current_val/num_images)> 75:
            msg = 'importing images, almost there'
        else:
            msg = 'importing images' 
        
        self.statusBar.showMessage(msg,2000)



        
        
    



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())