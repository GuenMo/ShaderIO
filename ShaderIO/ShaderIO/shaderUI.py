# coding:utf-8

try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from shiboken import wrapInstance
except:
    from PySide2.QtGui import *
    from PySide2.QtCore import *
    from PySide2.QtWidgets import *
    from shiboken2 import wrapInstance
    
import os.path
import maya.OpenMayaUI as OpenMayaUI

import shaderUtils
reload(shaderUtils)

def getMayaWindow():
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QMainWindow)


class ShaderUI(QDialog):
    def __init__(self, parent=getMayaWindow()):
        super(ShaderUI, self).__init__(parent)
    
        # Window
        self.setWindowTitle('Shader IO')
        #self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setFixedWidth(200) 
        self.setFixedHeight(80)
        
        # Layout
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(5,5,5,5)
        mainLayout.setSpacing(5)
        mainLayout.setAlignment(Qt.AlignTop)
        
        typeLayout = QHBoxLayout()
        typeLabel  = QLabel('Type:')
        self.modRadioBttn  = QRadioButton('Model')
        self.hairRadioBttn = QRadioButton('Yeti')
        self.modRadioBttn.setChecked(True)
        self.typeBttnGrp   = QButtonGroup()
        self.typeBttnGrp.addButton(self.modRadioBttn)
        self.typeBttnGrp.addButton(self.hairRadioBttn)
        typeLayout.addWidget(typeLabel)
        typeLayout.addWidget(self.modRadioBttn)
        typeLayout.addWidget(self.hairRadioBttn)
        
        self.exportBttn = QPushButton('Export Shader')
        self.importBttn = QPushButton('Import Shader')
        
        mainLayout.addLayout(typeLayout)
        mainLayout.addWidget(self.exportBttn)
        mainLayout.addWidget(self.importBttn)
        
        self.setLayout(mainLayout)
        
        # 
        self.exportBttn.clicked.connect(self.exportShader)
        self.importBttn.clicked.connect(self.importShader)
    
    def exportShader(self):
        checked = self.typeBttnGrp.checkedButton().text()
        fileDir = QFileDialog.getSaveFileName(self, caption = 'Export Shaders', filter=('*.mb'))[0]
        if fileDir:
            if checked == 'Model':
                shaderUtils.exportShader(fileDir)
            elif checked == 'Yeti':
                shaderUtils.exportYeti(fileDir)
        else:
            return
        
    def importShader(self):
        checked = self.typeBttnGrp.checkedButton().text()
        fileDir = QFileDialog.getOpenFileName(self, caption = 'Import Shaders', filter=('*.mb'))[0]
        if fileDir:
            if os.path.exists(fileDir):
                if checked == 'Model':
                    shaderUtils.importShader(fileDir)
                elif checked == 'Yeti':
                    shaderUtils.importYeti(fileDir)
            else:
                print 'File not exist!'
        else:
            return
        
def main():
    global win
    try:
        win.close()
        win.deleteLater()
    except: 
        pass
    win = ShaderUI()
    win.show()


