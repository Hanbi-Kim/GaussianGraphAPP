import sys
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QApplication,  QMessageBox, QFileDialog, QMainWindow
from PyQt5 import uic
import pandas as pd
import numpy as np
import os 
from matplotlib import pyplot as plt
from PyQt5.QtGui import QPixmap
from scipy.stats import norm 
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.metrics import r2_score
import matplotlib.patches as patches
import matplotlib.font_manager as fm
import warnings
warnings.filterwarnings("ignore")

form_class = uic.loadUiType("appUI.ui")[0]
class WindowClass(QMainWindow, form_class) :
    def __init__(self) :
        super().__init__()
        if os.path.exists('./plots.png'):
            os.remove('./plots.png')
        self.setupUi(self)
        self.df_list = []
        self.data = []
        self.times_index = 0
        self.font_list = fm.findSystemFonts(fontpaths=None, fontext='ttf')
        self.fileAddButton.clicked.connect(self.fileAddFunc)
        self.dfListWidget.itemClicked.connect(self.fileLoader)
        self.colListWidget.itemClicked.connect(self.dataloader)
        self.spinBox.setValue(12)
        self.tsButton.clicked.connect(self.tsPlot)
        self.gsButton.clicked.connect(self.gsPlot)
        self.saveButton.clicked.connect(self.save)
        self.prepare = False
        self.prepare_save = False

        for i, font_name in enumerate(sorted(self.font_list)):
            self.comboBox.addItem(font_name.split('/')[-1].split('.')[0])
            if font_name.split('/')[-1].split('.')[0].lower() == 'times new roman':
                self.times_index = i
            self.comboBox.setCurrentIndex(self.times_index )
            
    def fileAddFunc(self):
        self.dfListWidget.clear()
        self.df_list = []
        fname = QFileDialog.getExistingDirectory(self)
        if fname == '':
            pass
        else:
            for file_name in sorted(os.listdir(fname)):
                if file_name.split('.')[-1] in ['csv','xlsx','xls']:
                    if file_name.split('.')[0][0] not in ["~"," "]:
                        self.dfListWidget.addItem(file_name.split('.')[0])
                        self.df_list.append(os.path.join(fname,file_name))
    
    def fileLoader(self):
        r = self.dfListWidget.currentRow()
        if self.df_list[r].split('/')[-1].split(".")[-1] == 'csv': 
            self.df = pd.read_csv(self.df_list[r])
        elif self.df_list[r].split('/')[-1].split(".")[-1] == 'xlsx': 
            self.df = pd.read_excel(self.df_list[r])
        self.colListWidget.clear()
        for col in self.df.columns:
            self.colListWidget.addItem(col)
            
    def dataloader(self):
        self.data = self.df.iloc[:,self.colListWidget.currentRow()]
        if self.data.dtype not in ['float','int']:
            QMessageBox.about(self,'Error','분석에 활용할 데이터 타입이 정수형/실수형이 아닙니다. \n 데이터 타입을 정수형 또는 실수형으로 맞춰주세요.')
        else:
            self.prepare = True
        
    def tsPlot(self):
        
        if os.path.exists('./plots.png'):
            os.remove('./plots.png')
        if self.prepare:
            font_name = fm.FontProperties(fname=self.font_list[self.comboBox.currentIndex()]).get_name()
            plt.rcParams['font.family'] = font_name
            plt.rcParams['font.size'] = self.spinBox.value()
            plt.scatter(range(len(self.data)),self.data, color='black', label=self.yplainTextEdit.toPlainText(),facecolors='none')
            plt.ylabel(self.yplainTextEdit.toPlainText())
            if self.doubleSpinBox_4.value() or self.doubleSpinBox_5.value() != 0:
                plt.ylim([self.doubleSpinBox_4.value(),self.doubleSpinBox_5.value()])
            plt.xlabel(self.xplainTextEdit.toPlainText())
            plt.grid(True, alpha=0.3, linestyle = '--')
            plt.legend()
            if self.doubleSpinBox_2.value() or self.doubleSpinBox_3.value() != 0:
                plt.xlim([self.doubleSpinBox_2.value(),self.doubleSpinBox_3.value() ])
            plt.savefig('./plots.png')
            self.Image.setPixmap(QPixmap("./plots.png"))
            self.Image.setScaledContents(True)
            plt.clf()
            self.prepare_save = True
        else: 
            QMessageBox.about(self,'Error','데이터를 먼저 불러와주세요.')
            
    def gsPlot(self):
        if os.path.exists('./plots.png'):
            os.remove('./plots.png')
        if self.prepare:
            font_name = fm.FontProperties(fname=self.font_list[self.comboBox.currentIndex()]).get_name()
            plt.rcParams['font.family'] = font_name
            plt.rcParams['font.size'] = self.spinBox.value()
            plt.hist(self.data, density=True, color='gray', rwidth=0.8, alpha=1.0)
            plt.grid(True, alpha=0.3, linestyle = '--')
            x = np.arange(self.data.min(), self.data.max(), step=(self.data.max()-self.data.min()) / len(self.data))
            y = norm.pdf(x, loc=self.data.mean(), scale=self.data.std())
            ax = plt.plot(x, y, color='red') #1
            gr = GaussianProcessRegressor()
            gr.fit(np.array(self.data.index).reshape(-1, 1), np.array(self.data).reshape(-1, 1))
            r2 = r2_score(np.array(self.data).reshape(-1, 1), gr.predict(np.array(self.data.index).reshape(-1, 1)))
            plt.text(x=x.max() * 0.7,
                    y=y.max(), 
                    s=f"R^2={r2:.4f}\nmean={self.data.mean():.3f}\nstd={self.data.std():.4f}")
            ax = plt.gca()
            ax.add_patch(
            patches.Rectangle((x.max() * 0.65, y.max()*0.95), x.max()/2.5 , y.max() / 3.5,                     
                edgecolor = 'black',
                facecolor = 'white',
                fill=True,
                alpha=1.0,
            ))
            plt.ylabel(self.yplainTextEdit.toPlainText())
            if self.doubleSpinBox_4.value() or self.doubleSpinBox_5.value() != 0:
                plt.ylim([self.doubleSpinBox_4.value(),self.doubleSpinBox_5.value()])
            plt.xlabel(self.xplainTextEdit.toPlainText())
            if self.doubleSpinBox_2.value() or self.doubleSpinBox_3.value() != 0:
                plt.xlim([self.doubleSpinBox_2.value(),self.doubleSpinBox_3.value() ])
            plt.savefig('./plots.png')
            self.Image.setPixmap(QPixmap("./plots.png"))
            self.Image.setScaledContents(True)
            plt.clf()
            self.prepare_save = True
        else: 
            QMessageBox.about(self,'Error','데이터를 먼저 불러와주세요.')
        
    def color_picker(self):
        color = QColorDialog.getColor()
        return color
        
    def save(self):
        if self.prepare_save : 
            filePath, _ = QFileDialog.getSaveFileName(self, "Save Image", "",
                            "PNG(*.png);;JPEG(*.jpg *.jpeg);;All Files(*.*) ")
            if filePath == "":
                return
            from shutil import copyfile
            copyfile("./plots.png",filePath)
            if os.path.exists('./plots.png'):
                os.remove('./plots.png')
        else:
            QMessageBox.about(self,'Error','저장할 그래프가 없습니다. 그래프를 먼저 그려주세요.')
            
if __name__ == "__main__" :
    app = QApplication(sys.argv) 
    myWindow = WindowClass() 
    myWindow.show()
    app.exec_()
