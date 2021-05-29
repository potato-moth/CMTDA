import sqlite3
from datetime import datetime

from sqlalchemy import create_engine
import sys

from PyQt5.QtGui import QIcon, QColor

import qrc_resources

import pandas as pd
import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QMenu, QToolBar, QAction, QMessageBox, QFileDialog, \
    QTextEdit, QStatusBar, QWidget, QGridLayout, QTabWidget, QVBoxLayout, QPushButton, \
    QTableView, QSplitter, QHBoxLayout, QInputDialog, QDialog, QCheckBox, QComboBox, QColorDialog, QStyleFactory
from pandasModel import PandasModel
from timeAxisItem import TimeAxisItem


class Window(QMainWindow):
    """Main Window."""
    con = sqlite3.connect('turbinist.db')

    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self._unit()
        self._createActions()
        self._connectedActions()
        self._createMenuBar()
        self._createToolBars()
        self._createStatusBar()

    def _unit(self):
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        hbox = QHBoxLayout(self.centralWidget)

        self.topleft = QTableView(self)
        date_axis = TimeAxisItem(orientation='bottom')
        self.topright = pg.PlotWidget(axisItems={'bottom': date_axis})
        self.topright.resize(500, 0)
        self.topright.setBackground('w')
        self.bottom = QTabWidget(self)
        self.bottom.setMaximumHeight(150)

        subtab1 = QWidget()
        subtab2 = QWidget()
        self.bottom.addTab(subtab1, 'SQL Query')
        subtab1.layout = QGridLayout(self)
        self.console = QTextEdit()
        self.submitBtn = QPushButton('Submit')
        self.submitBtn.clicked.connect(self.submitQuery)
        self.clearBtn = QPushButton('Clear')
        self.clearBtn.clicked.connect(self.console.clear)
        subtab1.layout.addWidget(self.console, 1, 0, 1, 8)
        subtab1.layout.addWidget(self.submitBtn, 2, 6)
        subtab1.layout.addWidget(self.clearBtn, 2, 7)
        subtab1.setLayout(subtab1.layout)
        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(self.topleft)
        splitter1.addWidget(self.topright)

        splitter2 = QSplitter(Qt.Vertical)
        splitter2.addWidget(splitter1)
        splitter2.addWidget(self.bottom)

        hbox.addWidget(splitter2)
        self.setLayout(hbox)

        self.resize(800, 600)
        self.setWindowTitle("Capstone Microturbine Data Analysis v0.1")
        self.show()

    def _createMenuBar(self):
        menuBar = self.menuBar()

        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        fileMenu.addAction(self.connectionAction)
        fileMenu.addAction(self.addAction)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exitAction)

        chartMenu = QMenu("&Chart", self)
        menuBar.addMenu(chartMenu)
        chartMenu.addAction(self.newChartAction)

        queryMenu = QMenu("&SQLQuery", self)
        menuBar.addMenu(queryMenu)
        queryMenu.addAction(self.newQueryAction)

        setMenu = QMenu("&Settings", self)
        menuBar.addMenu(setMenu)
        setMenu.addAction(self.userStyleAction)

        helpMenu = QMenu("&Help", self)
        menuBar.addMenu(helpMenu)
        helpMenu.addAction(self.helpContentAction)
        helpMenu.addAction(self.aboutAction)

    def _createToolBars(self):
        fileToolBar = QToolBar("Add SQL", self)
        fileToolBar.setMovable(False)
        fileToolBar.addAction(self.AddTB)
        chartToolBar = QToolBar("Chart", self)
        chartToolBar.setMovable(False)
        chartToolBar.addAction(self.ChartTB)
        queryToolBar = QToolBar("SQlQuery", self)
        queryToolBar.setMovable(False)
        queryToolBar.addAction(self.QueryTB)
        setToolBar = QToolBar("Settings", self)
        setToolBar.setMovable(False)
        setToolBar.addAction(self.SettingsTB)
        helpToolBar = QToolBar("Help", self)
        helpToolBar.setMovable(False)
        helpToolBar.addAction(self.HelpTB)

        self.addToolBar(Qt.LeftToolBarArea, fileToolBar)
        self.addToolBar(Qt.LeftToolBarArea, chartToolBar)
        self.addToolBar(Qt.LeftToolBarArea, queryToolBar)
        self.addToolBar(Qt.LeftToolBarArea, setToolBar)
        self.addToolBar(Qt.LeftToolBarArea, helpToolBar)

    def _createStatusBar(self):
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("Ready", 0)

    def _createActions(self):
        self.connectionAction = QAction("&Connect DB", self)
        self.addAction = QAction("&Add to DB", self)
        self.newChartAction = QAction("&New Chart", self)
        self.userStyleAction = QAction("&Style Settings", self)
        self.newQueryAction = QAction("&New Query", self)
        self.helpContentAction = QAction("&Help", self)
        self.aboutAction = QAction("About", self)
        self.exitAction = QAction("&Exit", self)
        self.exitAction.setShortcut('Ctrl+Q')
        self.AddTB = QAction(self)
        self.AddTB.setText("&Add to DB")
        self.AddTB.setIcon(QIcon(":openfile.png"))
        self.ChartTB = QAction(self)
        self.ChartTB.setText("&New chart")
        self.ChartTB.setIcon(QIcon(":newchart.png"))
        self.QueryTB = QAction(self)
        self.QueryTB.setText("&New query")
        self.QueryTB.setIcon(QIcon(":query.png"))
        self.SettingsTB = QAction(self)
        self.SettingsTB.setText("&Settings")
        self.SettingsTB.setIcon(QIcon(":settings.png"))
        self.HelpTB = QAction(self)
        self.HelpTB.setText("&Help")
        self.HelpTB.setIcon(QIcon(":help.png"))

    def _connectedActions(self):

        self.exitAction.triggered.connect(self.close)
        self.newQueryAction.triggered.connect(self.query_dialog)
        self.newChartAction.triggered.connect(self.dialog_plot)
        self.ChartTB.triggered.connect(self.dialog_plot)
        self.QueryTB.triggered.connect(self.query_dialog)
        self.AddTB.triggered.connect(self.addToSQL)
        self.connectionAction.triggered.connect(self.connectSQL)
        self.addAction.triggered.connect(self.addToSQL)
        self.userStyleAction.triggered.connect(self.style_dialog)

    def connectSQL(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '*.db')
        self.con = sqlite3.connect(f'{fname[0]}')
        cur = self.con.cursor()
        self.engine = create_engine(f'sqlite:///{fname[0]}')

    def addToSQL(self):
        fname = QFileDialog.getOpenFileName(self, 'Open file', '*.csv')
        try:
            df = pd.read_csv(fname[0], sep=',', header=6, encoding="cp1251", index_col=False)
            df.rename(columns={
                'Incident Record ': 'IncidentRecord',
                'Engine Speed (rpm)': 'EngineSpeed',
                'Main Gen Power (W)': 'MainGenPower',
                'Turbine Exit Temp (°C)': 'TurbineExitTemp',
                'Fuel Valve Command (%)': 'FuelValveCommand',
                'Fuel Inlet Pres (kPa)': 'FuelInletPres',
                'Bat SOC (%)': 'BatSOC',
                'Sec Bat SOC (%)': 'SecBatSOC',
                'Starts ': 'Starts',
                'Hours ': 'Hours',
                'Output Current Phase A (A)': 'OutCurA',
                'Output Current Phase B (A)': 'OutCurB',
                'Output Current Phase C (A)': 'OutCurC',
                'Output Current Neutral (A)': 'OutCurN',
            }, inplace=True)
            df['DateTime'] = df.apply(lambda x: '%s %s' % (x['Control Date '], x['Control Time ']), axis=1)
            df['DateTime'] = pd.to_datetime(df.DateTime, errors='coerce')
            data_list = [
                'DateTime',
                'IncidentRecord',
                'EngineSpeed',
                'MainGenPower',
                'TurbineExitTemp',
                'FuelValveCommand',
                'FuelInletPres',
                'BatSOC',
                'SecBatSOC',
                'Starts',
                'Hours',
                'OutCurA',
                'OutCurB',
                'OutCurC',
                'OutCurN'
            ]
            result_df = df[data_list]
            # Удаляем дубликаты по столбцу DateTime и перезаписываем фрейм
            result_df = result_df.drop_duplicates(subset=['DateTime'], keep='first')
            result_df.to_csv('temp.csv', index=False)

        except:
            pass

        data, ok = QInputDialog.getText(self, 'Table selection',
                                        'Enter table name:')
        if ok:
            result_df.to_sql(f'{data}', con=self.engine, if_exists='append', index=False)

    def submitQuery(self):
        text = self.console.toPlainText()
        sql = f"""{text}"""
        con = sqlite3.connect('turbinist.db')
        result_df = pd.read_sql(sql, con)
        model = PandasModel(result_df)
        self.topleft.setModel(model)

    def query_dialog(self):
        self.dialog = QDialog()
        grid = QGridLayout()
        self.combo = QComboBox()
        self.langs = {
            'IncidentRecord': 0,
            'EngineSpeed': 0,
            'MainGenPower': 0,
            'TurbineExitTemp': 0,
            'FuelValveCommand': 0,
            'FuelInletPres': 0,
            'BatSOC': 0,
            'SecBatSOC': 0,
            'Starts': 0,
            'Hours': 0,
            'OutCurA': 0,
            'OutCurB': 0,
            'OutCurC': 0,
            'OutCurN': 0
        }
        cbIncidentRecord = QCheckBox('IncidentRecord', self.dialog)
        cbIncidentRecord.stateChanged.connect(self.checkedIR)
        cbEngineSpeed = QCheckBox('EngineSpeed', self.dialog)
        cbEngineSpeed.stateChanged.connect(self.checkedES)
        cbMainGenPower = QCheckBox('MainGenPower', self.dialog)
        cbMainGenPower.stateChanged.connect(self.checkedMGP)
        cbTurbineExitTemp = QCheckBox('TurbineExitTemp', self.dialog)
        cbTurbineExitTemp.stateChanged.connect(self.checkedTET)
        cbFuelValveCommand = QCheckBox('FuelValveCommand', self.dialog)
        cbFuelValveCommand.stateChanged.connect(self.checkedFVC)
        cbFuelInletPres = QCheckBox('FuelInletPres', self.dialog)
        cbFuelInletPres.stateChanged.connect(self.checkedFIP)
        cbBatSOC = QCheckBox('BatSOC', self.dialog)
        cbBatSOC.stateChanged.connect(self.checkedBat)
        cbSecBatSOC = QCheckBox('SecBatSOC', self.dialog)
        cbSecBatSOC.stateChanged.connect(self.checkedSecBat)
        cbStarts = QCheckBox('Starts', self.dialog)
        cbStarts.stateChanged.connect(self.checkedStarts)
        cbHours = QCheckBox('Hours', self.dialog)
        cbHours.stateChanged.connect(self.checkedHours)
        cbOutCurA = QCheckBox('OutCurA', self.dialog)
        cbOutCurA.stateChanged.connect(self.checkedCurA)
        cbOutCurB = QCheckBox('OutCurB', self.dialog)
        cbOutCurB.stateChanged.connect(self.checkedCurB)
        cbOutCurC = QCheckBox('OutCurC', self.dialog)
        cbOutCurC.stateChanged.connect(self.checkedCurC)
        cbOutCurN = QCheckBox('OutCurN', self.dialog)
        cbOutCurN.stateChanged.connect(self.checkedCurN)
        submitBtn = QPushButton('Submit', self.dialog)
        self.dateEditS = QtWidgets.QDateTimeEdit(self.dialog)
        self.dateEditF = QtWidgets.QDateTimeEdit(self.dialog)
        self.dateEditS.setCalendarPopup(True)
        self.dateEditF.setCalendarPopup(True)
        self.dateEditS.setDateTime(QtCore.QDateTime.currentDateTime())
        self.dateEditF.setDateTime(QtCore.QDateTime.currentDateTime())
        lblStart = QLabel('Start: ')
        lblFinish = QLabel('Finish: ')
        grid.addWidget(cbIncidentRecord, 1, 0)
        grid.addWidget(cbEngineSpeed, 1, 1)
        grid.addWidget(cbMainGenPower, 1, 2)
        grid.addWidget(cbTurbineExitTemp, 1, 3)
        grid.addWidget(cbFuelValveCommand, 2, 0)
        grid.addWidget(cbFuelInletPres, 2, 1)
        grid.addWidget(cbBatSOC, 2, 2)
        grid.addWidget(cbSecBatSOC, 2, 3)
        grid.addWidget(cbStarts, 3, 0)
        grid.addWidget(cbHours, 3, 1)
        grid.addWidget(cbOutCurA, 3, 2)
        grid.addWidget(cbOutCurB, 3, 3)
        grid.addWidget(cbOutCurC, 4, 0)
        grid.addWidget(cbOutCurN, 4, 1)
        grid.addWidget(self.combo, 4, 2)
        self.combo.addItems(["MT125", "MT127",
                             "MT129"])
        grid.addWidget(submitBtn, 4, 3)
        grid.addWidget(lblStart, 5, 0)
        grid.addWidget(self.dateEditS, 6, 0, 1, 2)
        grid.addWidget(lblFinish, 5, 2)
        grid.addWidget(self.dateEditF, 6, 2, 1, 2)
        submitBtn.clicked.connect(self.draw_query)
        self.dateEditS.dateTimeChanged.connect(self.onDateChangedStart)
        self.dateEditF.dateTimeChanged.connect(self.onDateChangedFinish)

        self.dialog.setLayout(grid)
        self.dialog.setWindowTitle("New Query Settings")
        self.dialog.setWindowModality(Qt.NonModal)
        self.dialog.setGeometry(300, 300, 0, 0)
        self.dialog.show()

    def dialog_plot(self):
        self.col = QColor(0, 0, 0)
        self.dialog = QDialog()
        grid = QGridLayout()
        self.combo = QComboBox()
        self.langs = {
            'IncidentRecord': 0,
            'EngineSpeed': 0,
            'MainGenPower': 0,
            'TurbineExitTemp': 0,
            'FuelValveCommand': 0,
            'FuelInletPres': 0,
            'BatSOC': 0,
            'SecBatSOC': 0,
            'Starts': 0,
            'Hours': 0,
            'OutCurA': 0,
            'OutCurB': 0,
            'OutCurC': 0,
            'OutCurN': 0
        }

        cbIncidentRecord = QCheckBox('IncidentRecord', self.dialog)
        cbIncidentRecord.stateChanged.connect(self.checkedIR)
        cbEngineSpeed = QCheckBox('EngineSpeed', self.dialog)
        cbEngineSpeed.stateChanged.connect(self.checkedES)
        cbMainGenPower = QCheckBox('MainGenPower', self.dialog)
        cbMainGenPower.stateChanged.connect(self.checkedMGP)
        cbTurbineExitTemp = QCheckBox('TurbineExitTemp', self.dialog)
        cbTurbineExitTemp.stateChanged.connect(self.checkedTET)
        cbFuelValveCommand = QCheckBox('FuelValveCommand', self.dialog)
        cbFuelValveCommand.stateChanged.connect(self.checkedFVC)
        cbFuelInletPres = QCheckBox('FuelInletPres', self.dialog)
        cbFuelInletPres.stateChanged.connect(self.checkedFIP)
        cbBatSOC = QCheckBox('BatSOC', self.dialog)
        cbBatSOC.stateChanged.connect(self.checkedBat)
        cbSecBatSOC = QCheckBox('SecBatSOC', self.dialog)
        cbSecBatSOC.stateChanged.connect(self.checkedSecBat)
        cbStarts = QCheckBox('Starts', self.dialog)
        cbStarts.stateChanged.connect(self.checkedStarts)
        cbHours = QCheckBox('Hours', self.dialog)
        cbHours.stateChanged.connect(self.checkedHours)
        cbOutCurA = QCheckBox('OutCurA', self.dialog)
        cbOutCurA.stateChanged.connect(self.checkedCurA)
        cbOutCurB = QCheckBox('OutCurB', self.dialog)
        cbOutCurB.stateChanged.connect(self.checkedCurB)
        cbOutCurC = QCheckBox('OutCurC', self.dialog)
        cbOutCurC.stateChanged.connect(self.checkedCurC)
        cbOutCurN = QCheckBox('OutCurN', self.dialog)
        cbOutCurN.stateChanged.connect(self.checkedCurN)
        clearBtn = QPushButton('Clear', self.dialog)
        submitBtn = QPushButton('Draw', self.dialog)
        self.colBtn = QPushButton(self.dialog)
        self.dateEditS = QtWidgets.QDateTimeEdit(self.dialog)
        self.dateEditF = QtWidgets.QDateTimeEdit(self.dialog)
        self.dateEditS.setCalendarPopup(True)
        self.dateEditF.setCalendarPopup(True)
        self.dateEditS.setDateTime(QtCore.QDateTime.currentDateTime())
        self.dateEditF.setDateTime(QtCore.QDateTime.currentDateTime())
        lblStart = QLabel('Start: ')
        lblFinish = QLabel('Finish: ')
        grid.addWidget(cbIncidentRecord, 1, 0)
        grid.addWidget(cbEngineSpeed, 1, 1)
        grid.addWidget(cbMainGenPower, 1, 2)
        grid.addWidget(cbTurbineExitTemp, 1, 3)
        grid.addWidget(cbFuelValveCommand, 2, 0)
        grid.addWidget(cbFuelInletPres, 2, 1)
        grid.addWidget(cbBatSOC, 2, 2)
        grid.addWidget(cbSecBatSOC, 2, 3)
        grid.addWidget(cbStarts, 3, 0)
        grid.addWidget(cbHours, 3, 1)
        grid.addWidget(cbOutCurA, 3, 2)
        grid.addWidget(cbOutCurB, 3, 3)
        grid.addWidget(cbOutCurC, 4, 0)
        grid.addWidget(cbOutCurN, 4, 1)
        grid.addWidget(self.combo, 4, 2)
        grid.addWidget(self.colBtn, 4, 3)
        self.combo.addItems(["MT125", "MT127",
                             "MT129"])
        grid.addWidget(clearBtn, 5, 0, 1, 2)
        grid.addWidget(submitBtn, 5, 2, 1, 2)

        grid.addWidget(lblStart, 6, 0)
        grid.addWidget(self.dateEditS, 7, 0, 1, 2)
        grid.addWidget(lblFinish, 6, 2)
        grid.addWidget(self.dateEditF, 7, 2, 1, 2)
        self.colBtn.setStyleSheet("QPushButton {background-color: %s }"
                                  % self.col.name())
        submitBtn.clicked.connect(self.draw_plot)
        clearBtn.clicked.connect(self.topright.clear)
        self.colBtn.clicked.connect(self.setPlotColor)
        self.dateEditS.dateTimeChanged.connect(self.onDateChangedStart)
        self.dateEditF.dateTimeChanged.connect(self.onDateChangedFinish)
        self.dialog.setLayout(grid)
        self.dialog.setWindowTitle("New Plot Settings")
        self.dialog.setWindowModality(Qt.NonModal)
        self.dialog.setGeometry(300, 300, 0, 0)
        self.dialog.show()

    def style_dialog(self):
        dialog = QDialog()
        dialog_hbox = QHBoxLayout()
        styleComboBox = QComboBox(dialog)
        styleComboBox.addItems(QStyleFactory.keys())

        styleLabel = QLabel("&Style:")
        styleLabel.setBuddy(styleComboBox)

        styleComboBox.activated[str].connect(self.changeStyle)

        dialog_hbox.addWidget(styleLabel)
        dialog_hbox.addWidget(styleComboBox)

        dialog.setLayout(dialog_hbox)
        dialog.setWindowTitle("Style Settings")
        dialog.setWindowModality(Qt.ApplicationModal)
        dialog.exec_()

    def changeStyle(self, styleName):
        QApplication.setStyle(QStyleFactory.create(styleName))

    def onDateChangedStart(self, qDateTime):
        self.resS = qDateTime.toString('yyyy-MM-dd hh:mm:ss')

    def onDateChangedFinish(self, qDateTime):
        self.resF = qDateTime.toString('yyyy-MM-dd hh:mm:ss')

    def checkedIR(self, checked):
        if checked:
            self.langs['IncidentRecord'] = 1
        else:
            self.langs['IncidentRecord'] = 0

    def checkedES(self, checked):
        if checked:
            self.langs['EngineSpeed'] = 1
        else:
            self.langs['EngineSpeed'] = 0

    def checkedMGP(self, checked):
        if checked:
            self.langs['MainGenPower'] = 1
        else:
            self.langs['MainGenPower'] = 0

    def checkedTET(self, checked):
        if checked:
            self.langs['TurbineExitTemp'] = 1
        else:
            self.langs['TurbineExitTemp'] = 0

    def checkedFVC(self, checked):
        if checked:
            self.langs['FuelValveCommand'] = 1
        else:
            self.langs['FuelValveCommand'] = 0

    def checkedFIP(self, checked):
        if checked:
            self.langs['FuelInletPres'] = 1
        else:
            self.langs['FuelInletPres'] = 0

    def checkedBat(self, checked):
        if checked:
            self.langs['BatSOC'] = 1
        else:
            self.langs['BatSOC'] = 0

    def checkedSecBat(self, checked):
        if checked:
            self.langs['SecBatSOC'] = 1
        else:
            self.langs['SecBatSOC'] = 0

    def checkedStarts(self, checked):
        if checked:
            self.langs['Starts'] = 1
        else:
            self.langs['Starts'] = 0

    def checkedHours(self, checked):
        if checked:
            self.langs['Hours'] = 1
        else:
            self.langs['Hours'] = 0

    def checkedCurA(self, checked):
        if checked:
            self.langs['OutCurA'] = 1
        else:
            self.langs['OutCurA'] = 0

    def checkedCurB(self, checked):
        if checked:
            self.langs['OutCurB'] = 1
        else:
            self.langs['OutCurB'] = 0

    def checkedCurC(self, checked):
        if checked:
            self.langs['OutCurC'] = 1
        else:
            self.langs['OutCurC'] = 0

    def checkedCurN(self, checked):
        if checked:
            self.langs['OutCurN'] = 1
        else:
            self.langs['OutCurN'] = 0

    def setPlotColor(self):
        self.col = QColorDialog.getColor()
        if self.col.isValid():
            self.colBtn.setStyleSheet("QWidget { background-color: %s }"
                                      % self.col.name())

    def draw_query(self):
        checkedlangs = ', '.join([key for key in self.langs.keys()

                                  if self.langs[key] == 1])

        curr_text = self.combo.currentText()
        sql = f"""SELECT DateTime, {checkedlangs}  FROM {curr_text} WHERE DateTime 
              BETWEEN '{self.resS}' AND '{self.resF}' ORDER BY DateTime"""
        con = sqlite3.connect('turbinist.db')
        result_df = pd.read_sql(sql, con)
        model = PandasModel(result_df)
        self.topleft.setModel(model)

    def draw_plot(self):
        checkedlangs = ', '.join([key for key in self.langs.keys()

                                  if self.langs[key] == 1])

        curr_text = self.combo.currentText()
        sql = f"""SELECT DateTime,{checkedlangs} FROM {curr_text} WHERE DateTime 
              BETWEEN '{self.resS}' AND '{self.resF}' ORDER BY DateTime"""
        con = sqlite3.connect('turbinist.db')
        df = pd.read_sql(sql, con)
        res = df.columns.values.tolist()
        list_x = []
        for i in df.DateTime:
            list_x.append(datetime.strptime(i, '%Y-%m-%d %H:%M:%S.%f'))
        for i in range(1, len(res)):
            list_y = df[res[i]].to_list()
            self.topright.addLegend()
            self.topright.plot(x=[x.timestamp() for x in list_x], y=list_y, name=f'{res[i]} {curr_text}',
                               pen=f'{self.col.name()}')

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    win = Window()
    win.show()
    sys.exit(app.exec_())
