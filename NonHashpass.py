from PyQt5 import QtWidgets, QtCore
from nonhashpass import Ui_mainWindow
from multiprocessing import Queue, Process
from moduleNonHashpass import hashpass
from sys import exit as sys_exit
from time import time

class nonhashpass(QtWidgets.QMainWindow):
    def __init__(self):
        start_time = time()
        hashpass('','',10_000)
        self.pbar_time = time() - start_time #For progressbar

        super(nonhashpass, self).__init__()
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)

        self.ui.label_6.hide() #int error label
        
        self.ledits = {
            self.ui.label_11: self.ui.lineEdit,
            self.ui.label_10: self.ui.lineEdit_2,
            self.ui.label_9:  self.ui.lineEdit_3,
        }
        for i in self.ledits:
            i.hide()
        
        self.ui.pushButton_2.hide() #generate another
        self.ui.pushButton_3.hide() #stop
        self.ui.label_7.hide() #in process label
        self.ui.progressBar.resize(311,25)
        self.ui.progressBar.hide() #progress bar

        self.ui.label_8.hide() #resulted password
        self.ui.lineEdit_4.hide() #resulted readonly password
        
        #make password button is pushButton
        #generate password is label_5
       
        self.ui.pushButton.clicked.connect(self.make_password_clicked)
        self.ui.pushButton_2.clicked.connect(self.erase_to_start)
        self.ui.pushButton_3.clicked.connect(self.erase_to_start)

        self.ui.pushButton.setDefault(True)
        self.ui.pushButton_2.setDefault(True)
        self.ui.pushButton_3.setDefault(True)

        for i in self.ledits.values():
            i.textChanged.connect(self.hide_with_edit)
        
        self.ui.lineEdit_3.textChanged.connect(self.check_int)
        
        self.generate_stopped = False
        self.all_is_valid = False
        self.active_daemon = None

    def hide_all_empty_errors(self):
        for i in self.ledits: i.hide()
    
    def make_password_clicked(self):
        self.hide_all_empty_errors()
        check_var = True
        for k,v in self.ledits.items():
            if not v.text():
                k.show(); check_var = False
        
        if not tuple(self.ledits.values())[2].text().isnumeric():
            check_var = False

        if not check_var:
            self.all_is_valid = False
        else:
            self.all_is_valid = True

        if self.all_is_valid:
            self.ui.pushButton.hide()
            self.ui.label_5.hide()
            self.ui.label_7.show()
            self.ui.pushButton_3.show()
            self.ui.progressBar.show()
            
            percent = int(self.ui.lineEdit_3.text()) / 10_000 * self.pbar_time / 100

            queue = Queue()
            p = Process(target=hashpass,args=(
                self.ui.lineEdit.text(),
                self.ui.lineEdit_2.text(),
                int(self.ui.lineEdit_3.text()), queue
            ))
            p.daemon = True; p.start()
            self.active_daemon = p

            for i in range(100):
                i += 1
                if self.generate_stopped:
                    break
                if not queue.qsize():
                    updated_time = time()
                    while time() - updated_time < percent:
                        if self.generate_stopped:
                            break
                        QtCore.QCoreApplication.processEvents()
                    else:
                        self.ui.progressBar.setValue(i)
                else:
                    self.ui.progressBar.setValue(100)
                    break
            
            if not self.generate_stopped:
                p.join()
                self.ui.progressBar.setValue(0)
                self.ui.label_7.hide()
                self.ui.label_8.show()
                self.ui.lineEdit_4.setText(queue.get())
                self.ui.lineEdit_4.show()
                self.ui.pushButton_2.show()
                self.ui.pushButton_3.hide()
                self.active_daemon = None
            
            self.generate_stopped = False

    def hide_with_edit(self):
        self.hide_all_empty_errors()
    
    def check_int(self):
        if self.ui.lineEdit_3.text():
            if not self.ui.lineEdit_3.text().isnumeric():
                self.ui.label_6.show(); self.all_is_valid = False
            else:
                self.ui.label_6.hide(); self.all_is_valid = True
        else:
            self.ui.label_6.hide(); self.all_is_valid = False
    
    def erase_to_start(self):
        if self.active_daemon:
            self.generate_stopped = True
            self.active_daemon.terminate()
            self.active_daemon.join()
            self.active_daemon = None

        self.ui.progressBar.setValue(0)
        self.ui.pushButton_3.hide()
        self.ui.label_7.hide()
        self.ui.progressBar.hide()
        self.ui.pushButton_2.hide()
        self.ui.label_8.hide()
        self.ui.lineEdit_4.hide()
        self.ui.label_5.show()
        self.ui.pushButton.show()

    def closeEvent(self,event):
        if self.active_daemon:
            self.active_daemon.terminate()
            self.active_daemon.join()
        
        self.close(); sys_exit()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    application = nonhashpass()
    application.show()

    sys_exit(app.exec())
