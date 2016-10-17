# coding:utf-8

from PySide import QtGui, QtCore
import os.path
import maya.OpenMayaUI as OpenMayaUI
from shiboken import wrapInstance

import shaderUtils
reload(shaderUtils)

def getMayaWindow():
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QtGui.QMainWindow)


class ShaderUI(QtGui.QDialog):
    def __init__(self, parent=getMayaWindow()):
        super(ShaderUI, self).__init__(parent)
    
        # Window
        self.setWindowTitle('Shader IO')
        #self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setFixedWidth(200) 
        self.setFixedHeight(80)
        
        # Layout
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.setContentsMargins(5,5,5,5)
        mainLayout.setSpacing(5)
        mainLayout.setAlignment(QtCore.Qt.AlignTop)
        
        typeLayout = QtGui.QHBoxLayout()
        typeLabel  = QtGui.QLabel('Type:')
        self.modRadioBttn  = QtGui.QRadioButton('Model')
        self.hairRadioBttn = QtGui.QRadioButton('Yeti')
        self.modRadioBttn.setChecked(True)
        self.typeBttnGrp   = QtGui.QButtonGroup()
        self.typeBttnGrp.addButton(self.modRadioBttn)
        self.typeBttnGrp.addButton(self.hairRadioBttn)
        typeLayout.addWidget(typeLabel)
        typeLayout.addWidget(self.modRadioBttn)
        typeLayout.addWidget(self.hairRadioBttn)
        
        self.exportBttn = QtGui.QPushButton('Export Shader')
        self.importBttn = QtGui.QPushButton('Import Shader')
        
        mainLayout.addLayout(typeLayout)
        mainLayout.addWidget(self.exportBttn)
        mainLayout.addWidget(self.importBttn)
        
        self.setLayout(mainLayout)
        
        # 
        self.exportBttn.clicked.connect(self.exportShader)
        self.importBttn.clicked.connect(self.importShader)
    
    def exportShader(self):
        checked = self.typeBttnGrp.checkedButton().text()
        fileDir = QtGui.QFileDialog.getSaveFileName(self, caption = 'Export Shaders', filter=('*.mb'))[0]
        if fileDir:
            if checked == 'Model':
                shaderUtils.exportShader(fileDir)
            elif checked == 'Yeti':
                shaderUtils.exportYeti(fileDir)
        else:
            return
        
    def importShader(self):
        checked = self.typeBttnGrp.checkedButton().text()
        fileDir = QtGui.QFileDialog.getOpenFileName(self, caption = 'Import Shaders', filter=('*.mb'))[0]
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


