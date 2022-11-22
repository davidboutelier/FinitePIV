import numpy as np
import glob
import shutil
from time import sleep
import json
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QApplication, QDoubleSpinBox, QStatusBar, QMainWindow, QMessageBox, QFormLayout, QAction, qApp, QVBoxLayout,QHBoxLayout,QCheckBox, QWidget,QLabel,QPushButton,QGroupBox, QComboBox, QSpinBox,QLineEdit,QProgressBar,QFileDialog,QDialog
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import matplotlib
matplotlib.use('Qt5Agg')

#from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import os
import sys


import rawpy
import numpy as np
import warnings
from skimage import io, img_as_uint

# global variable
project_dictionary = {} # empty dictionary
import_param = [] # empty list for import
display_settings = {'background_colormap_index': 0, 'flip_background': False, 'background_min': 0, 'background_max': 65535,
'vector_type': 'inc', 'sum_mode': 'eul', 'vector_color_index': 0, 'vector_thickness': 1, 'vector_sampling': 1, 'vector_scaling_mode_index':0, 'vector_scale': 1}

class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def dng2tif(self, file_in):
        with rawpy.imread(file_in) as raw:
            rgb = raw.postprocess()
            # convert to gray
            gray_img = np.dot(rgb[..., :3], [0.2989, 0.5870, 0.1140])

            # stretch
            gray_img_max = np.max(gray_img.flatten())
            gray_img_min = np.min(gray_img.flatten())
            gray_img = (gray_img - gray_img_min) / (gray_img_max - gray_img_min)

            # convert to 16 bit
            warnings.filterwarnings("ignore", category=UserWarning)
            bit_16_gray_img = img_as_uint(gray_img)
        return bit_16_gray_img

    def import_img(self):
        global import_param
        
        im_format = import_param[0]
        source_path = import_param[1]
        dest_path = import_param[2]

        if im_format == 'TIF':
            file_list = sorted(glob.glob(os.path.join(source_path, '*.tif')))
            n_img = len(file_list)
            import_param[3] = n_img
            
            for i in range(n_img):
                file_in = file_list[i]
                file_out = 'IMG_'+str(i).zfill(4)+'.tif'
                shutil.copy(os.path.join(source_path, file_in), os.path.join(dest_path, file_out))
                self.progress.emit(i + 1)
            self.finished.emit()
        
        elif im_format == 'DNG':
            file_list = sorted(glob.glob(os.path.join(source_path, '*.dng')))
            n_img = len(file_list)
            print('not implemented yet')
            for i in range(n_img):
                file_in = file_list[i]
                file_out = os.path.join(dest_path, 'IMG_'+str(i).zfill(4)+'.tif')
                # convert dng to 16 bit tif
                new_img = self.dng2tif(os.path.join(source_path, file_in))

                # save new image in destination folder as tif
                io.imsave(file_out, new_img)
                self.progress.emit(i + 1)
            self.finished.emit()

        else:
            print('error image format unknown')

        

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

        mod_conf_action = QAction('\u2630',self)
        mod_conf_action.triggered.connect(self.show_config)
        menubar.addAction(mod_conf_action)

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
        self.button_bitmap.clicked.connect(self.show_dialog_background_display)

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
        button_vector.clicked.connect(self.show_dialog_vector_display)

        vector_layout.addWidget(checkbox_vector)
        vector_layout.addWidget(button_vector)
        side_layout.addLayout(vector_layout)

        side_layout.addStretch()
        self.progress_bar = QProgressBar()
        side_layout.addWidget(self.progress_bar)
        
        viewport_layout = QVBoxLayout()
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
        # TO DO: CHNAGE TO RELATIVE PATH
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

    def show_config(self):
        global project_dictionary

        self.dialog_conf = QDialog(self)
        Title = 'Configuration'
        self.dialog_conf.setWindowTitle(Title)
        self.dialog_conf.dlg_layout = QFormLayout()
        self.dialog_conf.username = QLineEdit()
        self.dialog_conf.max_cores = QSpinBox()

        if os.path.exists('conf.json'):
            with open('conf.json', 'r') as f:
                conf = json.load(f)
            self.dialog_conf.username.setText(conf['username'])
            self.dialog_conf.max_cores.setValue(conf['use_cores'])
        else:
            self.dialog_conf.username.setText(os.getlogin())
            max = os.cpu_count()
            self.dialog_conf.max_cores.setMaximum = max
            self.dialog_conf.max_cores.setMinimum = 1
            self.dialog_conf.max_cores.setValue(max)
        
        self.dialog_conf.dlg_layout.addRow('username:', self.dialog_conf.username)
        self.dialog_conf.dlg_layout.addRow('use cores:', self.dialog_conf.max_cores)
        
        self.dialog_conf.OK_button = QPushButton('Apply')
        self.dialog_conf.OK_button.clicked.connect(self.dialog_conf_OK)
        self.dialog_conf.dlg_layout.addRow(' ', self.dialog_conf.OK_button)
        self.dialog_conf.setLayout(self.dialog_conf.dlg_layout)
        self.dialog_conf.exec()
            
    def dialog_conf_OK(self):
        'saves the values of the configuration into the project dictionary and the json file'
        global project_dictionary
        project_dictionary['username'] = self.dialog_conf.username.text()
        project_dictionary['use_cores'] = self.dialog_conf.max_cores.value()

        if os.path.exists('conf.json'):
            print('file exists')
            with open('conf.json', 'r') as f:
                conf = json.load(f)
            conf['username'] = project_dictionary['username'] 
            conf['use_cores'] = project_dictionary['use_cores']
            with open('conf.json', 'w') as f:
                f.write(json.dumps(conf))

        else:
            conf = {'username': project_dictionary['username'], 'use_cores': project_dictionary['use_cores']}
            with open('conf.json', 'w') as f:
                f.write(json.dumps(conf))

        self.dialog_conf.close()

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
        new_dataset['dt'] = import_img_dt

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
        self.import_worker = Worker()
        self.import_worker.moveToThread(self.import_thread)
        self.import_thread.started.connect(self.import_worker.import_img)
        self.import_worker.progress.connect(self.update_import_progress_bar)
        self.import_worker.finished.connect(self.import_thread.quit)
        self.import_thread.start()

    def update_import_progress_bar(self, current_val):
        global import_param
        num_images = import_param[3]
        self.progress_bar.setValue(int(100 * current_val/num_images))
        
        
        if int(100 * current_val/num_images)> 75:
            msg = 'importing images, almost there'
        else:
            msg = 'importing images' 
        
        self.statusBar.showMessage(msg,2000)

    def show_dialog_background_display(self):
        global project_dictionary, display_settings

        self.dialog_background = QDialog(self)
        Title = 'Background'
        self.dialog_background.setWindowTitle(Title)
        self.dialog_background.dlg_layout = QFormLayout()
        self.dialog_background.colormap_combo = QComboBox()
        self.dialog_background.colormap_combo.addItem('Greys')
        self.dialog_background.colormap_combo.addItem('viridis')
        self.dialog_background.colormap_combo.setCurrentIndex(display_settings['background_colormap_index'])

        self.dialog_background.dlg_layout.addRow('colormap: ', self.dialog_background.colormap_combo)
        self.dialog_background.flip_colormap_checkbox = QCheckBox('flip colormap')
        self.dialog_background.flip_colormap_checkbox.setChecked(display_settings['flip_background'])
        self.dialog_background.dlg_layout.addRow(self.dialog_background.flip_colormap_checkbox)
        self.dialog_background.min_value = QLineEdit()
        self.dialog_background.min_value.setText(str(display_settings['background_min']))
        self.dialog_background.max_value = QLineEdit()
        self.dialog_background.max_value.setText(str(display_settings['background_max']))
        self.dialog_background.dlg_layout.addRow('min value: ',self.dialog_background.min_value)
        self.dialog_background.dlg_layout.addRow('max value: ',self.dialog_background.max_value)

        self.dialog_background.dlg_button=QPushButton('OK')
        #self.dialog_background.dlg_button.clicked.connect(self.get_import_parameters)
        self.dialog_background.dlg_layout.addRow(self.dialog_background.dlg_button)
        self.dialog_background.setLayout(self.dialog_background.dlg_layout)
        self.dialog_background.exec()

    def show_dialog_vector_display(self):
        global project_dictionary, display_settings

        self.dialog_vector = QDialog(self)
        

        if display_settings['vector_type'] == 'inc':    # this condition allows creating another window if the data is cumulative
            Title = 'Vectors'
            self.dialog_vector.setWindowTitle(Title)
            self.dialog_vector.dlg_layout = QFormLayout()
            self.dialog_vector.color_combo = QComboBox()
            self.dialog_vector.color_combo.addItem('white')
            self.dialog_vector.color_combo.addItem('black')
            self.dialog_vector.color_combo.addItem('red')
            self.dialog_vector.color_combo.addItem('blue')
            self.dialog_vector.color_combo.addItem('green')
            self.dialog_vector.color_combo.addItem('yellow')
            self.dialog_vector.color_combo.addItem('magenta')
            self.dialog_vector.color_combo.addItem('cyan')
            self.dialog_vector.color_combo.setCurrentIndex(display_settings['vector_color_index'])
            self.dialog_vector.dlg_layout.addRow('color: ', self.dialog_vector.color_combo)

            self.dialog_vector.thickness_spinbox = QDoubleSpinBox()
            self.dialog_vector.thickness_spinbox.setRange(0.1,2)
            self.dialog_vector.thickness_spinbox.setSingleStep(0.1)
            self.dialog_vector.thickness_spinbox.setValue(display_settings['vector_thickness'])
            self.dialog_vector.dlg_layout.addRow('thickness: ', self.dialog_vector.thickness_spinbox)

            self.dialog_vector.sampling_spinbox = QSpinBox()
            self.dialog_vector.sampling_spinbox.setMinimum(1)
            self.dialog_vector.sampling_spinbox.setMaximum(10)
            self.dialog_vector.sampling_spinbox.setValue(display_settings['vector_sampling'])
            self.dialog_vector.dlg_layout.addRow('sampling: ', self.dialog_vector.sampling_spinbox)

            self.dialog_vector.scaling_mode_combobox = QComboBox()
            self.dialog_vector.scaling_mode_combobox.addItem('max')
            self.dialog_vector.scaling_mode_combobox.addItem('mean')
            self.dialog_vector.scaling_mode_combobox.addItem('median')
            self.dialog_vector.scaling_mode_combobox.addItem('manual')
            self.dialog_vector.scaling_mode_combobox.setCurrentIndex(display_settings['vector_scaling_mode_index'])
            self.dialog_vector.dlg_layout.addRow('scaling mode: ', self.dialog_vector.scaling_mode_combobox)

            self.dialog_vector_scale_edit = QLineEdit()
            self.dialog_vector_scale_edit.setText(str(display_settings['vector_scale']))
            self.dialog_vector.dlg_layout.addRow('scale: ', self.dialog_vector_scale_edit)

            self.dialog_vector.dlg_button=QPushButton('OK')
            #self.dialog_background.dlg_button.clicked.connect(self.get_import_parameters)
            self.dialog_vector.dlg_layout.addRow(self.dialog_vector.dlg_button)

            self.dialog_vector.setLayout(self.dialog_vector.dlg_layout)
        self.dialog_vector.exec()

    def save_vector_display_settings(self):
        global display_settings

###########################

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())