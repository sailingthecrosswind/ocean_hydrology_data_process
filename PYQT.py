from PyQt5.QtCore import QDir, Qt
from PyQt5.QtCore import QModelIndex, Qt,QDate,QUrl,pyqtSignal
from PyQt5.QtGui import QStandardItemModel,QValidator,QDoubleValidator
from PyQt5.QtWidgets import QApplication, QMainWindow,QAction,QLabel,QVBoxLayout, QFormLayout,QLineEdit,QSpinBox, QTableView,QFileDialog,QTextBrowser,QLayout,QGroupBox,QHBoxLayout,QTabWidget,QPushButton,QWidget,QCheckBox,QMessageBox,QDialog,QDateTimeEdit,QComboBox,QDialogButtonBox,QErrorMessage,QDoubleSpinBox,QInputDialog
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWebKitWidgets  import QWebView
from threading import Thread
import sys,time
sys.path.append('~/tide.py')
from tide import Process_Tide

class m_window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):

        self.setWindowTitle('水文测验分析报告处理系统（三航院）')
        self.statusBar()
        self.createMenu()
        centralWidget = QWidget()

        self.shower = QWebView()
        self.allGroup = QGroupBox()
        self.mid_l_Group = QGroupBox()
        self.mid_s_Group = QGroupBox("测验概况")
        self.Tabs = QTabWidget()
        self.Generate_all_button = QPushButton("生成报告及文档")

        centralLayout =  QVBoxLayout()
        centralLayout.addWidget(self.shower,stretch=50)
        centralLayout.addWidget(self.allGroup,stretch = 1)
        centralWidget.setLayout(centralLayout)
        self.setCentralWidget(centralWidget)

        allGroupLayout = QHBoxLayout()
        allGroupLayout.addWidget(self.mid_l_Group,stretch = 3)
        allGroupLayout.addWidget(self.Tabs,stretch = 13)
        self.allGroup.setLayout(allGroupLayout)

        self.tides_contral = TideTab()
        self.Tabs.addTab(self.tides_contral,"潮位")

        mid_l_GroupLayout = QVBoxLayout()
        mid_l_GroupLayout.addWidget(self.mid_s_Group)
        mid_l_GroupLayout.addWidget(self.Generate_all_button)
        self.mid_l_Group.setLayout(mid_l_GroupLayout)

        mid_s_GroupLayout = QFormLayout()
        Project_Name = QLineEdit()
        Sea_Area = QLineEdit()
        Button_Save_Info = QPushButton("确定")
        mid_s_GroupLayout.addRow(QLabel("工程名称"), Project_Name)
        mid_s_GroupLayout.addRow(QLabel("测验海域"), Sea_Area)
        mid_s_GroupLayout.addRow(Button_Save_Info)
        self.mid_s_Group.setLayout(mid_s_GroupLayout)

    def show_msg_statusbar(self,msg):
        self.statusBar().showMessage(msg)

    def createMenu(self):
        tide_load = QAction('载入数据', self)
        tide_load.setStatusTip('从Excel文件读入潮位数据，不同站点位于不同sheet,列标题应为Tide,Time')
#        tide_load.triggered.connect(self.tide)

        generate_tide_sheet = QAction('&保存潮位报表', self)
        generate_tide_sheet.setStatusTip('保存潮位月报表')
 #       generate_tide_sheet.triggered.connect(self.save_tide)

        tide_statics = QAction('&各月潮位特征值汇总', self)
        tide_statics.setStatusTip('统计各月潮位极值,涨落潮历时等')
 #       tide_statics.triggered.connect(self.out_put_data)

        tide_harmonic_analysis = QAction('&调和分析', self)
        tide_harmonic_analysis.setStatusTip('对潮位数据进行调和分析，计算各分潮特征值')
  #      tide_harmonic_analysis.triggered.connect(self.harmonic_analysis)

        load_stream_E_N = QAction('&载入数据(格式为E-N)', self)
        load_stream_E_N.setStatusTip('对应sheet名应为‘E’,‘N’')

        load_stream_V_D = QAction('&载入数据(格式为V-D)', self)
        load_stream_V_D.setStatusTip('对应sheet名应为‘V’,‘D’')

        get_button = QAction('&去除底部干扰数据', self)
        get_button.setStatusTip('找底')

        constant_3 = QAction('&常数法（三点）', self)
        constant_6 = QAction('&常数法（六点）', self)

        power_3 = QAction('&幂函数法（三点）', self)
        power_6 = QAction('&幂函数法（六点）', self)

        stream_statics = QAction('&统计潮流特征', self)
        stream_statics.setStatusTip('统计最大涨落潮流速、涨落潮历时等特征数据并输出Excel')

        generate_stream_sheet = QAction('&生成潮流报表', self)

        menubar = self.menuBar()
        TIDE = menubar.addMenu('&潮位')
        TIDE.addAction(tide_load)

        TIDE.addAction(generate_tide_sheet)
        TIDE.addAction(tide_statics)
        TIDE.addAction(tide_harmonic_analysis)

        STREAM = menubar.addMenu('&潮流')
        LOAD_STREAM = STREAM.addMenu('&载入潮流数据')
        LOAD_STREAM.addAction(load_stream_E_N)
        LOAD_STREAM.addAction(load_stream_V_D)

        STREAM.addSeparator()

        STREAM.addAction(get_button)

        STREAM.addSeparator()

        FENCENG = STREAM.addMenu('&分层')
        FENCENG.addAction(constant_6)
        FENCENG.addAction(power_6)
        FENCENG.addSeparator()
        FENCENG.addAction(constant_3)
        FENCENG.addAction(power_3)

        STREAM.addSeparator()
        STREAM.addAction(stream_statics)
        STREAM.addAction(generate_stream_sheet)
        # 整体布局

    #def createTideTab(self):
    #    self.tideTab = QTabWidget

    def display(self,Html):
        self.shower.setHtml(Html)

class TideTab(QWidget):
    def __init__(self,parent = None):
        super(TideTab,self).__init__(parent)
        global t
        t = []

        self.tide_l_Group = QGroupBox("当前文件")
        self.tide_file_button = QPushButton("导入潮位文件")
        self.auto_Preprocess = QCheckBox("打开文件时进行预处理")
        self.if_one_sheet = QCheckBox("仅载入首个工作表")
        self.check_multifile = QCheckBox("多个文件")
        self.check_multifile.setChecked(True)
        self.check_if_null = QCheckBox("潮位补全")
        self.del_data = QPushButton("删除当前潮位数据")
        self.tide_d_Group = QGroupBox("其他")

        self.errorMessageDialog = QErrorMessage(self)
        self.errorLabel = QLabel()
        self.errorButton = QPushButton("确定")

        self.tide_file_button.clicked.connect(self.open_file)
        #self.tide_file_button.setStyleSheet("background-color: yellow,border-style: outset")

        self.del_data.clicked.connect(self.del_all_data)

        tide_l_Group_Layout = QVBoxLayout()
        tide_l_Group_Layout.addWidget(self.tide_file_button)
        tide_l_Group_Layout.addWidget(self.auto_Preprocess)
        tide_l_Group_Layout.addWidget(self.if_one_sheet)
        tide_l_Group_Layout.addWidget(self.tide_d_Group)

        self.tide_l_Group.setLayout(tide_l_Group_Layout)

        tide_d_Group_Layout = QVBoxLayout()

        tide_d_Group_Layout.addWidget(self.check_multifile)
        tide_d_Group_Layout.addWidget(self.check_if_null)
        tide_d_Group_Layout.addWidget(self.del_data)

        self.tide_d_Group.setLayout(tide_d_Group_Layout)
        self.sites_Tab = QTabWidget()

        #调试site_tab 用
        self.sites_Tab.addTab(Tide_Site_Tab(), '未载入潮位数据')

        #


        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.tide_l_Group)
        mainLayout.addWidget(self.sites_Tab,stretch=5)
        self.setLayout(mainLayout)

        self.sites_contral= {}

    def welcome_init_tab(self):
        self.init_tab = Welcome_Tab("请载入潮位数据文件")
        self.sites_Tab.addTab(self.init_tab, '未载入潮位数据')
        self.init_tab.load_file_button.clicked.connect(self.open_file)

    def open_file(self):
        options = QFileDialog.Options()
        if self.check_multifile.isChecked():
            fileName,_ = QFileDialog.getOpenFileNames(self,"选取文件", "E:",
                                           "97-03表格文档 (*.xls);;Excel文件(*.xlsx)", options=options)
        else:
            fileName, _ = QFileDialog.getOpenFileName(self, "选取文件", "E:",
                                                       "97-03表格文档 (*.xls);;Excel文件(*.xlsx)", options=options)
            fileName=[fileName]

        for f in fileName:
            t.append(Process_Tide(f,only_first_sheet = self.if_one_sheet.isChecked()))
            if self.auto_Preprocess.isChecked():
                for i in t:
                    for ii in i.sites:
                        tide_thread = Thread(target=t[-1].preprocess,kwargs={'s':ii})
                        second = 0
                        tide_thread.start()
                        while tide_thread.is_alive():
                            print("正在进行数据预处理，数据来自文件" + fileName[0] + ',处理用时' + str(second) + '秒')
                            time.sleep(0.5)
                            second += 0.5

        for i in t:
            for ii in i.sites:
                self.sites_contral.update({ii: Tide_Site_Tab()})
                self.sites_Tab.addTab(self.sites_contral[ii],ii)
                self.sites_Tab.setTabToolTip(self.sites_Tab.count()-1,i.filename)
                #self.sites_Tab.widget().setToolTip()

        if len(self.sites_contral)!=0:
            self.sites_Tab.removeTab(0)

    def del_all_data(self):
        MESSAGE = "将删除所有已载入的潮位数据，是否确定？"
        reply = QMessageBox.question(self, "删除潮位数据",
                                     MESSAGE,
                                     QMessageBox.Yes | QMessageBox.No )
        if reply == QMessageBox.Yes:
            t.clear()
            self.clear_tab()
            self.welcome_init_tab()

        else:
            pass

    def clear_tab(self):
            while self.sites_Tab.count() !=0 :
                self.sites_Tab.removeTab(0)

    def errorMessage(self,Wrong_msg):
        self.errorMessageDialog.showMessage(Wrong_msg)
        self.errorLabel.setText("确定")



class Tide_Site_Tab(QWidget):
    def __init__(self,parent = None):
        super(Tide_Site_Tab, self).__init__(parent)
        self.layout_element()

    def layout_element(self):
        self.lu_Group = QGroupBox("测点位置")
        self.ld_Group = QGroupBox("起止时间")
        self.l_Group = QGroupBox()
        self.mid_Group_out = QGroupBox("潮位数据处理")
        self.mid_Group_in = QGroupBox("调整去噪度")
        self.r_Group = QGroupBox("结果输出")
        self.r_in_Group_u = QGroupBox("调和分析")
        self.r_in_Group_d = QGroupBox("文档输出")
        self.add_Group1 = QGroupBox("施测信息")
        self.add_Group2 = QGroupBox("高程基准")
        self.add_Group = QGroupBox()

        add_Group1 = QFormLayout()
        self.Survey_man = QLineEdit()
        self.Survey_Implement = QComboBox()
        self.Survey_Implement.addItem("Tide Master")
        self.Survey_Implement.addItem("其他设备（待补充）")
        self.Survey_Implement.addItem("自定义")
        self.Survey_Implement_Series_num = QLineEdit()
        add_Group1.addRow(QLabel("测量人员"),self.Survey_man)
        add_Group1.addRow(QLabel("采用仪器"), self.Survey_Implement)
        add_Group1.addRow(QLabel("仪器编号"),self.Survey_Implement_Series_num)
        self.add_Group1.setLayout(add_Group1)

        add_Group2 = QFormLayout()
        self.Altitudinal_System1 = Altitudinal_Select()
        self.Altitudinal_System_OUT = Altitudinal_Select()
        self.Altitudinal_Add = QDoubleSpinBox()
        self.Altitudinal_Add.setRange(-100,100)
        self.Altitudinal_Add.setToolTip("单位为米")
        add_Group2.addRow(QLabel("实测数据基准面"),self.Altitudinal_System1.combobox )
        add_Group2.addRow(QLabel("输出数据基准面"), self.Altitudinal_System_OUT.combobox)
        add_Group2.addRow(QLabel("基准面高差"), self.Altitudinal_Add)
        self.add_Group2.setLayout(add_Group2)

        add_Group = QVBoxLayout()
        add_Group.addWidget(self.add_Group1)
        add_Group.addWidget(self.add_Group2)
        self.add_Group.setLayout(add_Group)

        lu_GroupLayout = QFormLayout()
        self.onlyDouble = QDoubleValidator()
        self.Longitude = QLineEdit()
        self.Latitude = QLineEdit()
        self.Longitude.setValidator(self.onlyDouble)
        self.Latitude.setValidator(self.onlyDouble)

        lu_GroupLayout.addRow(QLabel("经度"), self.Longitude)
        lu_GroupLayout.addRow(QLabel("纬度"), self.Latitude)
        self.lu_Group.setLayout(lu_GroupLayout)

        ld_GroupLayout = QFormLayout()
        self.start_time = QDateTimeEdit()
        self.end_time = QDateTimeEdit(QDate.currentDate())
        ld_GroupLayout.addRow(self.start_time)
        ld_GroupLayout.addRow(self.end_time)
        self.ld_Group.setLayout(ld_GroupLayout)

        l_Group = QVBoxLayout()
        l_Group.addWidget(self.lu_Group,stretch=3)
        l_Group.addSpacing(20)
        l_Group.addWidget(self.ld_Group,stretch=3)
        self.l_Group.setLayout(l_Group)
        #self.l_Group.setFlat()
        #self.l_Group.setStyleSheet("border:5px")

        mid_Group_out = QVBoxLayout()
        self.Show_tide_data_button = QPushButton("&潮位查看")
        self.Process_method_select = QComboBox()
        self.Process_method_select.addItem("小波分析")
        self.Process_method_select.addItem("数值平滑")
        self.confirmButton = QPushButton("数据处理")
        self.Process_threshold = QSpinBox()
        self.Process_threshold.setRange(0,20)
        mid_Group_out.addWidget(self.Show_tide_data_button,stretch=2)
        mid_Group_out.addSpacing(20)
        mid_Group_out.addWidget(self.mid_Group_in,stretch=4)
        mid_Group_in = QFormLayout()
        mid_Group_in.addRow(self.Process_method_select)
        mid_Group_in.addRow("阀值",self.Process_threshold)
        mid_Group_in.addRow(self.confirmButton)
        self.mid_Group_out.setLayout(mid_Group_out)
        self.mid_Group_in.setLayout(mid_Group_in)

        r_Group = QFormLayout()
        self.Save_Sheet_Button = QPushButton("保存潮位报表")
        self.Save_Mid_Data_Button = QPushButton("保存中间结果")
        self.Astronomical_Tide_Analysis = QPushButton("天文潮计算")
        self.Theoretical_Mininum_tidal_leval = QPushButton("计算对应理论最低潮面")
        self.Is_Output_Report = QCheckBox("输出文字报告")
        self.Is_Output_mid_Document = QCheckBox("输出分析文档")
        r_Group.addRow(self.Save_Sheet_Button,self.Save_Mid_Data_Button)
        r_Group.addRow(self.r_in_Group_u)
        r_in_Group_u = QFormLayout()
        r_in_Group_u.addRow(self.Astronomical_Tide_Analysis,self.Theoretical_Mininum_tidal_leval)
        self.r_in_Group_u.setLayout(r_in_Group_u)
        r_Group.addRow(self.r_in_Group_d)
        r_in_Group_d = QFormLayout()
        r_in_Group_d.addRow(self.Is_Output_Report)
        r_in_Group_d.addRow(self.Is_Output_mid_Document)
        self.r_in_Group_d.setLayout(r_in_Group_d)
        self.r_Group.setLayout(r_Group)

        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.l_Group,stretch=2)
        mainLayout.addWidget(self.add_Group,stretch=3)
        mainLayout.addWidget(self.mid_Group_out,stretch=2)
        mainLayout.addWidget(self.r_Group,stretch=5)
        self.setLayout(mainLayout)

    def signal_init(self):
        self.preprocess = pyqtSignal()

    def preprocess_click(self):
        self.preprocess.emit()



class Altitudinal_Select(QDialog):
            def __init__(self,parent = None):
                super(Altitudinal_Select,self).__init__(parent)
                self.combobox = QComboBox()
                self.combobox.addItem("当地理论最低潮面")
                self.combobox.addItem("平均海平面")
                self.combobox.addItem("85高程")
                self.combobox.addItem("自定义")

                self.combobox.activated.connect(self.changed)

            def changed(self,index):
                if index == 0:
                    self.select = "当地理论最低潮面"
                elif index ==1:
                    self.select = "平均海平面"
                elif index ==2:
                    self.select = "85高程"
                elif index ==3:
                    self.setText()

            def setText(self):
                #text, ok = QInputDialog.getText(self, "自定义高程系统", "自定义名称:", QLineEdit.Normal)
                text, ok = QInputDialog.getText(self, "自定义高程系统",
                                                "自定义名称:", QLineEdit.Normal, self.combobox.itemText(3))
                if ok and text != '':
                    self.select = text
                    self.combobox.addItem(text)
                    self.combobox.removeItem(3)


class Welcome_Tab(QWidget):
    def __init__(self,message):
        super(Welcome_Tab,self).__init__(parent=None)
        self.load_file_button = QPushButton(message)
        self.load_file_button.setStyleSheet("""
               QPushButton
               {
                   background-color: rgb(255, 255,255);
                   border:10px solid rgb(0, 170, 255);
               }
               """ )
        main_Layout = QFormLayout()
        main_Layout.addRow(self.load_file_button)
        self.setLayout(main_Layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = m_window()
    ex.show()
    ex.showMaximized()
    sys.exit(app.exec_())