import numpy as np
import matplotlib.pyplot as plt 
import json
from fbs_runtime.application_context.PyQt5 import ApplicationContext
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, qApp
import os
import sys

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # create the menus
        # from Project
        new_project_action = QAction('New', self)
        new_project_action.setShortcut('Ctrl+N')
        new_project_action.setStatusTip('New')
        # TO DO: create a trigger

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
        import_calib_img_action = QAction('Import calibration images',self)
        import_calib_img_action.setStatusTip('Import calibration images')

        import_experiment_img_action = QAction('Import experiment images',self)
        import_experiment_img_action.setStatusTip('Import experiment images')

        self.statusBar()
        menubar = self.menuBar()
        menubar.setNativeMenuBar(True)

        filemenu_project = menubar.addMenu('Project')
        filemenu_project.addAction(new_project_action)
        filemenu_project.addAction(open_project_action)
        filemenu_project.addAction(save_project_action)
        filemenu_project.addAction(exit_action)

        filemenu_data = menubar.addMenu('Data')
        filemenu_data.addAction(import_calib_img_action)
        filemenu_data.addAction(import_experiment_img_action)

        filemenu_calibrate = menubar.addMenu('Calibrate')
        filemenu_preprocess = menubar.addMenu('Preprocess')




        f = open(os.path.join('c:' + os.sep, 'Users','david','Documents','Python_Scripts','FinitePIV','src','build','settings','base.json'))
        data = json.load(f)
        app_name = data['app_name']
        app_version = data['version']
        self.setWindowTitle(app_name + ': '+app_version)
        self.setGeometry(300, 300, 300, 200)
        self.showMaximized()
        self.show()



if __name__ == '__main__':
    '''appctxt = ApplicationContext()       # 1. Instantiate ApplicationContext
    window = QMainWindow()
    window.showMaximized()
    window.setWindowTitle("test")

    #layout = QGridLayout()
    #window.setLayout(layout)

    # create menu
    menubar = QMenuBar()
    menubar.setNativeMenuBar(menubar,True)
    file = menubar.addMenu("File")


    window.show()
    exit_code = appctxt.app.exec()      # 2. Invoke appctxt.app.exec()
    sys.exit(exit_code)'''

    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())