# -*- coding: utf-8 -*-
# 
# 
import json
import sys
import math
from anki.hooks import addHook
from aqt.qt import *
from aqt.utils import openLink, tooltip
from anki.utils import isMac, isWin, isLin
from anki.lang import _
from aqt.webview import AnkiWebView
import re
import platform
from . import Pyperclip 
import os
from os.path import dirname, join
import platform
from .miutils import miInfo, miAsk
from operator import itemgetter
from aqt.theme import theme_manager


versionNumber = "ver. 1.2.1"

class MigakuSVG(QSvgWidget):
    clicked=pyqtSignal()
    def __init__(self, parent=None):
        QSvgWidget.__init__(self, parent)

    def mousePressEvent(self, ev):
        self.clicked.emit()

class MigakuLabel(QLabel):
    clicked=pyqtSignal()
    def __init__(self, parent=None):
        QLabel.__init__(self, parent)

    def mousePressEvent(self, ev):
        self.clicked.emit()

class SettingsGui(QScrollArea):
    def __init__(self, mw, path, colArray, modeler, cssJSHandler, reboot):
        super(SettingsGui, self).__init__()
        self.cssJSHandler = cssJSHandler
        self.modeler = modeler
        self.reboot = reboot
        self.readingTypes = {'Pinyin': 'Pinyin: The reading will be generated in pinyin.', 'Bopomofo': 'Bopomofo: The reading will be generated in bopomofo/zhuyin.', 'Jyutping' : 'Jyutping: The reading will be generated in jyutping.'}
        self.sides = {'Front' : 'Front: Applies the display type to the front of the card.', 'Back' :'Back: Applies the display type to the back of the card.' , 'Both' : 'Both: Applies the display type to the front and back of the card.'}
        self.displayTypes = {'Hanzi' : ['hanzi', 'Hanzi: Displays text without tone coloring or reading information.'],
'Colored Hanzi' : ['coloredhanzi', 'Colored Hanzi: Displays text with tone coloring but no reading information.'],
'Hover' : ['hover', 'Hover: Displays text without tone coloring or reading information,\nbut displays an individual word\'s reading information when it is hovered.'], 
'Colored Hover' : ['coloredhover', 'Colored Hover: Displays text without tone coloring or reading information,\nbut displays an individual word\'s tone coloring and reading information when it is hovered.'],
'Hanzi Reading' : ['hanzireading', 'Hanzi Reading: Displays text without tone coloring but with reading information.'],
'Colored Hanzi Reading' : ['coloredhanzireading', 'Colored Hanzi Reading: Displays text with tone coloring and reading information.'],
'Reading' : ['reading', 'Reading: Displays text in your chosen reading type without tone coloring.\nNote that if a word\'s reading is not available it will be displayed in hanzi.'],
'Colored Reading' : ['coloredreading', 'Colored Reading: Displays text in your chosen reading type with tone coloring.\nNote that if a word\'s reading is not available it will be displayed in hanzi.']}
        self.displayTranslation = {'hanzi' : 'Hanzi', 'coloredhanzi' : 'Colored Hanzi',
            'hover' : 'Hover', 'coloredhover' : 'Colored Hover', 
            'hanzireading' : 'Hanzi Reading', 'coloredhanzireading' : 'Colored Hanzi Reading',
            'reading' : 'Reading', 'coloredreading' : 'Colored Reading'
            }
        self.rtTranslation = {'pinyin' : 'Pinyin', 'bopomofo' : 'Bopomofo', 'jyutping' : 'Jyutping'}
        self.mw = mw
        self.sortedProfiles = False
        self.sortedNoteTypes = False
        self.selectedRow = False
        self.initializing = False
        self.changingProfile = False
        self.buttonStatus = 0
        self.config = self.getConfig()
        self.cA = self.updateCurrentProfileInfo(colArray)
        self.tabs = QTabWidget()
        self.allFields = self.getAllFields()
        # self.setMinimumSize(800, 550);
        self.setContextMenuPolicy(Qt.NoContextMenu)
        self.setWindowTitle("Migaku Chinese Settings (%s)"%versionNumber)
        self.addonPath = path
        self.setWindowIcon(QIcon(join(self.addonPath, 'icons', 'migaku.png')))
        self.selectedProfiles = []
        self.selectedAltFields = []
        self.selectedSimpFields = []
        self.selectedTradFields = []
        self.selectedGraphFields = []
        self.resetButton = QPushButton('Restore Defaults')
        self.cancelButton = QPushButton('Cancel')
        self.applyButton = QPushButton('Apply')
        self.layout = QVBoxLayout()
        self.innerWidget = QWidget()
        self.setupMainLayout()
        self.tabs.addTab(self.getOptionsTab(), "Options")
        self.tabs.addTab(self.getAFTab(), "Active Fields")
        self.tabs.addTab(self.getAboutTab(), "About")
        self.initTooltips()
        self.loadProfileCB()
        self.loadFontSize()
        self.loadProfilesList()
        self.loadDefaultReadingCB()
        self.loadBopoNumbers()
        self.loadAltSimpTradFieldsCB()
        self.loadFieldsList(1)
        self.loadFieldsList(2)
        self.loadFieldsList(3)
        self.loadHanziReadingConversion()
        self.loadColors()
        self.loadTradIcons()
        self.initActiveFieldsCB()
        self.loadAutoCSSJS()
        self.loadModelAdditions()
        self.loadActiveFields()
        self.hotkeyEsc = QShortcut(QKeySequence("Esc"), self)
        self.hotkeyEsc.activated.connect(self.hide)
        self.handleAutoCSSJS()
        self.initHandlers()
        if isWin:
            self.resize(1000, 805)
            self.innerWidget.setFixedSize(980, 790)
        else:
            self.resize(1000, 1035)
            self.innerWidget.setFixedSize(980, 1020)
        self.setWidgetResizable(True)
        self.setWidget(self.innerWidget)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setWidgetResizable(True)
        self.show()


    def resetDefaults(self):
        if miAsk('Are you sure you would like to restore the default settings? This cannot be undone.'):
            conf = self.mw.addonManager.addonConfigDefaults(dirname(__file__))
            self.mw.addonManager.writeConfig(__name__, conf)
            self.close()
            self.mw.miChineseSettings = None
            self.reboot()

    def loadFontSize(self):
        self.fontSize.setValue(self.config['FontSize'])

    def loadAutoCSSJS(self):
        self.autoCSSJS.setChecked(self.config['AutoCssJsGeneration'])

    def loadModelAdditions(self):
        self.addChina.setChecked(self.config['addSimpNote'])
        self.addTaiwan.setChecked(self.config['addTradNote'])
        self.addHK.setChecked(self.config['addCantoNote'])


    def loadTradIcons(self):
        self.tradIcons.setChecked(self.config['traditionalIcons'])

    def loadBopoNumbers(self):
        self.bopo2Number.setChecked(self.config['BopomofoTonesToNumber'])

    def loadDefaultReadingCB(self):
        for key, value in self.readingTypes.items():
            self.defaultReading.addItem(key)
            self.defaultReading.setItemData(self.defaultReading.count() - 1, value ,Qt.ToolTipRole)
        r = self.config['ReadingType']
        self.defaultReading.setCurrentText(self.rtTranslation[r])

    def loadHanziReadingConversion(self):
        hanziConTypes = {'None': 'None: No conversion.', 'Simplified' : 'Simplified: Traditional characters are converted to simplified characters.', 'Traditional' : 'Traditional: Simplified characters are converted to traditional characters.'}
        readingConTypes = {'None': 'None: No conversion.', 'Pinyin' : 'Pinyin: Bopomofo/zhuyin is converted to pinyin.', 'Bopomofo' : 'Bopomofo: Pinyin is converted to bopomofo/zhuyin.'}
        for key, value in hanziConTypes.items():
            self.hanziConversion.addItem(key)
            self.hanziConversion.setItemData(self.hanziConversion.count() - 1, value ,Qt.ToolTipRole)
        for key, value in readingConTypes.items():
            self.readingConversion.addItem(key)
            self.readingConversion.setItemData(self.readingConversion.count() - 1, value ,Qt.ToolTipRole)
        hc = self.config['hanziConversion']
        rc = self.config['readingConversion']
        self.hanziConversion.setCurrentText(hc)
        self.readingConversion.setCurrentText(rc)


    def getAllFields(self):
        fieldList = []
        for prof in self.cA:
            for name, note in self.cA[prof].items():
                for f in note['fields']:
                    if f not in fieldList:
                        fieldList.append(f)
              
        return self.ciSort(fieldList)

    def ciSort(self, l):
        return sorted(l, key=lambda s: s.lower())

    def updateCurrentProfileInfo(self, colA):
        pn = self.mw.pm.name
        noteTypes = self.mw.col.models.all()
        noteTypeDict = {}
        for note in noteTypes:
            noteTypeDict[note['name']] = {"cardTypes" : [], "fields" : []}
            for ct in note['tmpls']:
                noteTypeDict[note['name']]["cardTypes"].append(ct['name'])
            for f in note['flds']:
                noteTypeDict[note['name']]["fields"].append(f['name'])
            colA[pn] = noteTypeDict
        return colA

    def loadColors(self):
        mColors = self.config["MandarinTones12345"]
        cColors = self.config["CantoneseTones123456"]
        for idx,c in enumerate(mColors):
            name = 'm' + str(idx + 1) + 'color'
            widget = getattr(self, name)
            widget.setText(c)
            widget.setStyleSheet('color:' + c + ';')

        for idx,c in enumerate(cColors):
            name = 'c' + str(idx + 1) + 'color'
            widget = getattr(self, name)
            widget.setText(c)
            widget.setStyleSheet('color:' + c + ';')

    def getOptionsTab(self):
        self.profileCB = QComboBox()
        self.addRemProfile = QPushButton('Add')
        self.currentProfiles = QLabel('None')
        self.defaultReading = QComboBox()
        self.bopo2Number = QCheckBox()
        self.altCB = QComboBox()
        self.simpCB = QComboBox()
        self.tradCB = QComboBox()
        self.addRemAlt = QPushButton('Add')
        self.addRemSimp = QPushButton('Add')
        self.addRemTrad = QPushButton('Add')
        self.altLayout = QWidget()
        self.simpLayout = QWidget()
        self.tradLayout = QWidget()
        self.altOW = QRadioButton(self.altLayout)
        self.altIfE = QRadioButton(self.altLayout)
        self.altWithSep = QRadioButton(self.altLayout)
        self.altSep = QLineEdit()
        self.simpOW = QRadioButton(self.simpLayout)
        self.simpIfE = QRadioButton(self.simpLayout)
        self.simpWithSep = QRadioButton(self.simpLayout)
        self.simpSep = QLineEdit()
        self.tradOW = QRadioButton(self.tradLayout)
        self.tradIfE = QRadioButton(self.tradLayout)
        self.tradWithSep = QRadioButton(self.tradLayout)
        self.tradSep = QLineEdit()
        self.currentAlt = QLabel('None')
        self.currentSimp = QLabel('None')
        self.currentTrad = QLabel('None')

        self.m1color = QLineEdit()
        self.m2color = QLineEdit()
        self.m3color = QLineEdit()
        self.m4color = QLineEdit()
        self.m5color = QLineEdit()

        self.c1color = QLineEdit()
        self.c2color = QLineEdit()
        self.c3color = QLineEdit()
        self.c4color = QLineEdit()
        self.c5color = QLineEdit()
        self.c6color = QLineEdit()

        self.m1pb = QPushButton('Select Color')
        self.m2pb = QPushButton('Select Color')
        self.m3pb = QPushButton('Select Color')
        self.m4pb = QPushButton('Select Color')
        self.m5pb = QPushButton('Select Color')

        self.c1pb = QPushButton('Select Color')
        self.c2pb = QPushButton('Select Color')
        self.c3pb = QPushButton('Select Color')
        self.c4pb = QPushButton('Select Color')
        self.c5pb = QPushButton('Select Color')
        self.c6pb = QPushButton('Select Color')

        self.hanziConversion = QComboBox()
        self.readingConversion = QComboBox()
        self.tradIcons = QCheckBox()

        self.fontSize = QSpinBox()
        self.fontSize.setMinimum(1)
        self.fontSize.setMaximum(200)
        

        optionsTab = QWidget(self)
        optionsTab.setLayout(self.getOptionsLayout())
        return optionsTab

    def sizeOptionsWidgets(self):
        self.profileCB.setFixedWidth(120)
        self.addRemProfile.setFixedWidth(80)
        self.defaultReading.setFixedWidth(100)
        self.m1color.setFixedWidth(100)
        self.m2color.setFixedWidth(100)
        self.m3color.setFixedWidth(100)
        self.m4color.setFixedWidth(100)
        self.m5color.setFixedWidth(100)

        self.c1color.setFixedWidth(100)
        self.c2color.setFixedWidth(100)
        self.c3color.setFixedWidth(100)
        self.c4color.setFixedWidth(100)
        self.c5color.setFixedWidth(100)
        self.c6color.setFixedWidth(100)

        self.m1pb.setFixedWidth(100)
        self.m2pb.setFixedWidth(100)
        self.m3pb.setFixedWidth(100)
        self.m4pb.setFixedWidth(100)
        self.m5pb.setFixedWidth(100)

        self.c1pb.setFixedWidth(100)
        self.c2pb.setFixedWidth(100)
        self.c3pb.setFixedWidth(100)
        self.c4pb.setFixedWidth(100)
        self.c5pb.setFixedWidth(100)
        self.c6pb.setFixedWidth(100)
        self.fontSize.setFixedWidth(80)

    
    def getOptionsLayout(self):
        self.sizeOptionsWidgets()
        ol = QVBoxLayout() #options layout

        pgb = QGroupBox() #profile group box
        pgbv = QVBoxLayout()
        pgbt = QLabel('<b>Profiles</b>')
        pgbh = QHBoxLayout()
        pgbh.addWidget(self.profileCB)
        pgbh.addWidget(self.addRemProfile)
        pgbh.addStretch()
        pgbh2 = QHBoxLayout()
        l1 = QLabel('Current Profiles:')
        l1.setFixedWidth(100)
        pgbh2.addWidget(l1)
        pgbh2.addWidget(self.currentProfiles)
        pgbh2.addStretch()
        pgbv.addWidget(pgbt)
        pgbv.addLayout(pgbh)
        pgbv.addLayout(pgbh2)
        pgb.setLayout(pgbv)
        ol.addWidget(pgb)


        ggb = QGroupBox() #generation group box
        ggb2 = QGroupBox('Field Settings')
        ggbv = QVBoxLayout()
        ggbv2 = QVBoxLayout()
        ggbt = QLabel('<b>Generation</b>')
        ggbh = QHBoxLayout()
        ggbh.addWidget(QLabel('Default Reading Type:'))
        ggbh.addWidget(self.defaultReading)
        ggbh.addWidget(QLabel('Bopomofo Tones To Numbers:'))
        ggbh.addWidget(self.bopo2Number)
        ggbh.addStretch()


        ggbh2 =  QHBoxLayout()
        l2 = QLabel('Alternate Field:')
        l2.setFixedWidth(100)
        ggbh2.addWidget(l2)
        ggbh2.addWidget(self.altCB)
        ggbh2.addWidget(self.addRemAlt)
        ggbh2.addWidget(self.altOW)
        ggbh2.addWidget(QLabel('Overwrite'))
        ggbh2.addWidget(self.altIfE)
        ggbh2.addWidget(QLabel('If Empty'))
        ggbh2.addWidget(self.altWithSep)
        ggbh2.addWidget(QLabel('Add with Separator'))
        ggbh2.addWidget(self.altSep)
        ggbh2.addStretch()
        ggbh2.setContentsMargins(0, 0, 0, 0)
        self.altLayout.setLayout(ggbh2)

        ggbh3 = QHBoxLayout()
        ggbh3.addWidget(QLabel('Current Alternate Fields:'))
        ggbh3.addWidget(self.currentAlt)
        ggbh3.addStretch()

        ggbh4 =  QHBoxLayout()
        l3 = QLabel('Simplified Field:')
        l3.setFixedWidth(100)
        ggbh4.addWidget(l3)
        ggbh4.addWidget(self.simpCB)
        ggbh4.addWidget(self.addRemSimp)
        ggbh4.addWidget(self.simpOW)
        ggbh4.addWidget(QLabel('Overwrite'))
        ggbh4.addWidget(self.simpIfE)
        ggbh4.addWidget(QLabel('If Empty'))
        ggbh4.addWidget(self.simpWithSep)
        ggbh4.addWidget(QLabel('Add with Separator'))
        ggbh4.addWidget(self.simpSep)
        ggbh4.addStretch()
        ggbh4.setContentsMargins(0, 0, 0, 0)
        self.simpLayout.setLayout(ggbh4)

        ggbh5 = QHBoxLayout()
        ggbh5.addWidget(QLabel('Current Simplified Fields:'))
        ggbh5.addWidget(self.currentSimp)
        ggbh5.addStretch()

        ggbh6 =  QHBoxLayout()
        l4 = QLabel('Traditional Field:')
        l4.setFixedWidth(100)
        ggbh6.addWidget(l4)
        ggbh6.addWidget(self.tradCB)
        ggbh6.addWidget(self.addRemTrad)
        ggbh6.addWidget(self.tradOW)
        ggbh6.addWidget(QLabel('Overwrite'))
        ggbh6.addWidget(self.tradIfE)
        ggbh6.addWidget(QLabel('If Empty'))
        ggbh6.addWidget(self.tradWithSep)
        ggbh6.addWidget(QLabel('Add with Separator'))
        ggbh6.addWidget(self.tradSep)
        ggbh6.addStretch()
        ggbh6.setContentsMargins(0, 0, 0, 0)
        self.tradLayout.setLayout(ggbh6)


        ggbh7 = QHBoxLayout()
        ggbh7.addWidget(QLabel('Current Traditional Fields:'))
        ggbh7.addWidget(self.currentTrad)
        ggbh7.addStretch()

        
        ggbv2.addWidget(self.altLayout)
        ggbv2.addLayout(ggbh3)
        ggbv2.addWidget(self.simpLayout)
        ggbv2.addLayout(ggbh5)
        ggbv2.addWidget(self.tradLayout)
        ggbv2.addLayout(ggbh7)
        ggbv2.setSpacing(5)
        ggb2.setLayout(ggbv2)

        ggbv.addWidget(ggbt)
        ggbv.addLayout(ggbh)
        ggbv.addWidget(ggb2)
        ggb.setLayout(ggbv)
        ol.addWidget(ggb)

        cgb = QGroupBox() #colors group box
        cgbv = QVBoxLayout()
        cgbv.addWidget(QLabel('<b>Colors</b>'))
        mcgb = QGroupBox('Mandarin Tones')
        mcv = QVBoxLayout()
        mch1 = QHBoxLayout()
        mch2 = QHBoxLayout()
        ml1 = QLabel('1st:')
        ml2 = QLabel('2nd:')
        ml3 = QLabel('3rd:')
        ml4 = QLabel('4th:')
        ml5 = QLabel('Neutral:')
        ml1.setFixedWidth(25)
        ml2.setFixedWidth(45)
        ml3.setFixedWidth(25)
        ml4.setFixedWidth(25)
        ml5.setFixedWidth(45)
        mch1.addWidget(ml1)
        mch1.addWidget(self.m1color)
        mch1.addWidget(self.m1pb)

        mch1.addWidget(ml2)
        mch1.addWidget(self.m2color)
        mch1.addWidget(self.m2pb)

        mch1.addWidget(ml3)
        mch1.addWidget(self.m3color)
        mch1.addWidget(self.m3pb)
        
        mch2.addWidget(ml4)
        mch2.addWidget(self.m4color)
        mch2.addWidget(self.m4pb)
        
        mch2.addWidget(ml5)
        mch2.addWidget(self.m5color)
        mch2.addWidget(self.m5pb)
        
        mch1.addStretch()
        mch2.addStretch()
        mcv.addLayout(mch1)
        mcv.addLayout(mch2)
        mcgb.setLayout(mcv)

        ccgb = QGroupBox('Cantonese Tones')  #canto
        ccv = QVBoxLayout()
        cch1 = QHBoxLayout()
        cch2 = QHBoxLayout()
        cl1 = QLabel('1st:')
        cl2 = QLabel('2nd:')
        cl3 = QLabel('3rd:')
        cl4 = QLabel('4th:')
        cl5 = QLabel('5th:')
        cl6 = QLabel('6th:')
        cl1.setFixedWidth(25)
        cl2.setFixedWidth(45)
        cl3.setFixedWidth(25)
        cl4.setFixedWidth(25)
        cl5.setFixedWidth(45)
        cl6.setFixedWidth(25)
        cch1.addWidget(cl1)
        cch1.addWidget(self.c1color)
        cch1.addWidget(self.c1pb)

        cch1.addWidget(cl2)
        cch1.addWidget(self.c2color)
        cch1.addWidget(self.c2pb)

        cch1.addWidget(cl3)
        cch1.addWidget(self.c3color)
        cch1.addWidget(self.c3pb)

        cch2.addWidget(cl4)
        cch2.addWidget(self.c4color)
        cch2.addWidget(self.c4pb)
        
        cch2.addWidget(cl5)
        cch2.addWidget(self.c5color)
        cch2.addWidget(self.c5pb)

        cch2.addWidget(cl6)
        cch2.addWidget(self.c6color)
        cch2.addWidget(self.c6pb)
        
        cch1.addStretch()
        cch2.addStretch()
        ccv.addLayout(cch1)
        ccv.addLayout(cch2)
        ccgb.setLayout(ccv)

        cgbv.addWidget(mcgb)
        cgbv.addWidget(ccgb)
        cgb.setLayout(cgbv)
        ol.addWidget(cgb)


        bgb = QGroupBox() #profile group box
        bgbv = QVBoxLayout()
        bgbt = QLabel('<b>Behavior</b>')
        bgbh = QHBoxLayout()
        bgbh.addWidget(QLabel('Hanzi/Reading Conversion:'))
        bgbh.addWidget(self.hanziConversion)
        bgbh.addWidget(self.readingConversion)
        bgbh.addStretch()
        bgbh.addWidget(QLabel('Reading Font Size:'))
        bgbh.addWidget(self.fontSize)
        bgbh.addWidget(QLabel('%'))
        bgbh.addStretch()
        bgbh2 = QHBoxLayout()
        bgbh2.addWidget(QLabel('Traditional Icons:'))
        bgbh2.addWidget(self.tradIcons)
        bgbh2.addStretch()
        bgbv.addWidget(bgbt)
        bgbv.addLayout(bgbh)
        bgbv.addLayout(bgbh2)
        bgb.setLayout(bgbv)
        ol.addWidget(bgb)
        return ol

    def getAFTable(self):
        afTable = QTableWidget(self)
        if isWin and platform.release() == '10' and theme_manager.night_mode != True:
            afTable.setStyleSheet(
        "QHeaderView::section{"
            "border-top:0px solid #D8D8D8;"
            "border-left:0px solid #D8D8D8;"
            "border-right:1px solid #D8D8D8;"
            "border-bottom: 1px solid #D8D8D8;"
            "background-color:white;"
            "padding:4px;"
        "}"
        "QTableCornerButton::section{"
            "border-top:0px solid #D8D8D8;"
            "border-left:0px solid #D8D8D8;"
            "border-right:1px solid #D8D8D8;"
            "border-bottom: 1px solid #D8D8D8;"
            "background-color:white;"
        "}")
        afTable.setSortingEnabled(True)
        afTable.setColumnCount(8)
        afTable.setSelectionBehavior(QTableView.SelectRows);
        afTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff);
        tableHeader = afTable.horizontalHeader()
        afTable.setHorizontalHeaderLabels(['Profile', 'Note Type', 'Card Type', 'Field', 'Side', 'Display Type', 'Reading Type', ''])
        tableHeader.setSectionResizeMode(0, QHeaderView.Stretch)
        tableHeader.setSectionResizeMode(1, QHeaderView.Stretch)
        tableHeader.setSectionResizeMode(2, QHeaderView.Stretch)
        tableHeader.setSectionResizeMode(3, QHeaderView.Stretch)
        tableHeader.setSectionResizeMode(4, QHeaderView.Stretch)
        tableHeader.setSectionResizeMode(5, QHeaderView.Stretch)
        tableHeader.setSectionResizeMode(6, QHeaderView.Stretch)
        tableHeader.setSectionResizeMode(7, QHeaderView.Fixed)
        afTable.setColumnWidth(7, 40)
        afTable.setEditTriggers(QTableWidget.NoEditTriggers)
        return afTable

    def enableSep(self, sep):
        sep.setEnabled(True)

    def disableSep(self, sep):
        sep.setEnabled(False) 

    def sizeAFLayout(self):
        self.profileAF.setFixedWidth(120)
        self.noteTypeAF.setFixedWidth(120)
        self.cardTypeAF.setFixedWidth(120)
        self.fieldAF.setFixedWidth(120)
        self.sideAF.setFixedWidth(120)
        self.displayAF.setFixedWidth(120)
        self.readingAF.setFixedWidth(120)

    def getAFLayout(self):
        self.sizeAFLayout()
        afl = QVBoxLayout() #active fields layout

        afh1 = QHBoxLayout()
        afh1.addWidget(QLabel('Auto CSS & JS Generation:'))
        afh1.addWidget(self.autoCSSJS)
        afh1.addStretch()
        afh1.addWidget(QLabel('Add Migaku Note Types:'))
        afh1.addWidget(self.addChina)
        afh1.addWidget(self.addTaiwan)
        afh1.addWidget(self.addHK)
        afl.addLayout(afh1)

        afh2 = QHBoxLayout()
        afh2.addWidget(self.profileAF)
        afh2.addWidget(self.noteTypeAF)
        afh2.addWidget(self.cardTypeAF)
        afh2.addWidget(self.fieldAF)
        afh2.addWidget(self.sideAF)
        afh2.addWidget(self.displayAF)
        afh2.addWidget(self.readingAF)
        afl.addLayout(afh2)

        afh3 =QHBoxLayout()
        afh3.addStretch()
        afh3.addWidget(self.addEditAF)
        afl.addLayout(afh3)

        afl.addWidget(self.afTable)

        return afl

    def getAFTab(self):
        self.autoCSSJS = QCheckBox()
        self.addChina = QCheckBox('Chinese (CH)')
        self.addTaiwan = QCheckBox('Chinese (TW)')
        self.addHK = QCheckBox('Cantonese (HK)')
        self.profileAF = QComboBox()
        self.noteTypeAF = QComboBox()
        self.cardTypeAF = QComboBox()
        self.fieldAF = QComboBox()
        self.sideAF = QComboBox()
        self.displayAF = QComboBox()
        self.readingAF = QComboBox()
        self.addEditAF = QPushButton('Add')
        self.afTable = self.getAFTable()

        afTab = QWidget(self)
        afTab.setLayout(self.getAFLayout())
        return afTab

    def initTooltips(self):
        self.profileCB.setToolTip('These are the profiles that the add-on will be active on.\nWhen set to "All", the add-on will be active on all profiles.')
        self.addRemProfile.setToolTip('Add/Remove a profile.')
        self.defaultReading.setToolTip('This is the default reading generation that will be used when\ngenerating in a field that has not been designated as an Active Field.')
        self.bopo2Number.setToolTip('When enabled bopomofo readings will be generated with numbers\ninstead of tone marks.This makes editing incorrect tones easier because\nnumbers are easier to type then tone marks. When viewed during reviews, or previews\ntone marks will replace the numbers.')
        self.altCB.setToolTip('The fields where the alternate characters will be generated.If the target field where readings are\ngenerated has only simplified characters then traditional characters will be placed in this\nfield and vice versa. If the target contains a mix of both simplified and traditional characters then a consistent\nalternate containing only simplified and traditional characters. A variant will only be generated if it is\ndifferent than the original text.')
        self.simpCB.setToolTip('The fields where simplified characters version of the text\nwill be generated when reading generation occurs. The variant will be added\neven it it is the same as the original text.')
        self.tradCB.setToolTip('The fields where traditional characters version of the text\nwill be generated when reading generation occurs. The variant will be added\neven it it is the same as the original text.')
        self.altOW.setToolTip('The alternate variant will be generated into the selected field(s),\noverwriting their current contents.')
        self.altIfE.setToolTip('The alternate variant will be generated into the selected field(s)\nonly if they are empty.')
        self.altWithSep.setToolTip('The alternate variant will be added on to the selected field(s)\nfollowing the separator. The default separator is an html line break "<br>".')
        self.altSep.setToolTip('The separator to be used when adding the alternate variant.')
        self.simpOW.setToolTip('The simplified variant will be generated into the selected field(s),\noverwriting their current contents.')
        self.simpIfE.setToolTip('The simplified variant will be generated into the selected field(s)\nonly if they are empty.')
        self.simpWithSep.setToolTip('The simplified variant will be added on to the selected field(s)\nfollowing the separator. The default separator is an html line break "<br>".')
        self.simpSep.setToolTip('The separator to be used when adding the simplified variant.')
        self.tradOW.setToolTip('The traditional variant will be generated into the selected field(s),\noverwriting their current contents.')
        self.tradIfE.setToolTip('The traditional variant will be generated into the selected field(s)\nonly if they are empty.')
        self.tradWithSep.setToolTip('The traditional variant will be added on to the selected field(s) following\nthe separator. The default separator is an html line break "<br>".')
        self.tradSep.setToolTip('The separator to be used when adding the traditional variant.')

        self.m1pb.setToolTip('Select the color for characters in the first tone.')
        self.m2pb.setToolTip('Select the color for characters in the second tone.')
        self.m3pb.setToolTip('Select the color for characters in the third tone.')
        self.m4pb.setToolTip('Select the color for characters in the fourth tone.')
        self.m5pb.setToolTip('Select the color for characters in the fifth tone.')

        self.c1pb.setToolTip('Select the color for characters in the first tone.')
        self.c2pb.setToolTip('Select the color for characters in the second tone.')
        self.c3pb.setToolTip('Select the color for characters in the third tone.')
        self.c4pb.setToolTip('Select the color for characters in the fourth tone.')
        self.c5pb.setToolTip('Select the color for characters in the fifth tone.')
        self.c6pb.setToolTip('Select the color for characters in the sixth tone.')

        self.hanziConversion.setToolTip('Will convert characters in all notes with Active Fields to the selected type.')
        self.readingConversion.setToolTip('Will convert readings in all Active Fields from pinyin to bopomofo and vice versa.')
        self.tradIcons.setToolTip('Display the conversion icons in traditional characters instead of simplified characters.')

        self.fontSize.setToolTip('The percentage font size of readings in relation to the characters.\nThe range is from 1% to 200%.')


        self.autoCSSJS.setToolTip('Enable or disable automatic CSS and JavaScript handling.\n Disabling this option is not recommended if you are not familiar with these technologies.')
        self.addChina.setToolTip('Adds the Migaku Chinese (ZH) note type for use with pinyin readings.')
        self.addTaiwan.setToolTip('Adds the Migaku Chinese (TW) note type for use with bopomofo readings.')
        self.addHK.setToolTip('Adds the Migaku Chinese (HK) note type for use with jyutping readings.')
        self.profileAF.setToolTip("Profile: Select the profile.")
        self.noteTypeAF.setToolTip("Note Type: Select the note type.")
        self.cardTypeAF.setToolTip("Card Type: Select the card type.")
        self.fieldAF.setToolTip("Field: Select the field.")
        self.sideAF.setToolTip("Side: Select the side of the card where the display type setting will apply.")
        self.displayAF.setToolTip("Display Type: Select the display type,\nhover over a display type for fuctionality details.")
        self.readingAF.setToolTip("Reading Type: Select the reading type,\ndetermines which reading system will be used when generating readings\nfor this card type.")


        

    def initHandlers(self):
        self.m1pb.clicked.connect(lambda: self.openDialogColor(self.m1color))
        self.m2pb.clicked.connect(lambda: self.openDialogColor(self.m2color))
        self.m3pb.clicked.connect(lambda: self.openDialogColor(self.m3color))
        self.m4pb.clicked.connect(lambda: self.openDialogColor(self.m4color))
        self.m5pb.clicked.connect(lambda: self.openDialogColor(self.m5color))
        self.c1pb.clicked.connect(lambda: self.openDialogColor(self.c1color))
        self.c2pb.clicked.connect(lambda: self.openDialogColor(self.c2color))
        self.c3pb.clicked.connect(lambda: self.openDialogColor(self.c3color))
        self.c4pb.clicked.connect(lambda: self.openDialogColor(self.c4color))
        self.c5pb.clicked.connect(lambda: self.openDialogColor(self.c5color))
        self.c6pb.clicked.connect(lambda: self.openDialogColor(self.c6color))
        self.addRemProfile.clicked.connect(lambda: self.addRemoveFromList(self.profileCB.currentText(), self.addRemProfile, self.currentProfiles, self.selectedProfiles, True))
        self.profileCB.currentIndexChanged.connect(lambda: self.profAltSimpTradChange(self.profileCB.currentText(), self.addRemProfile, self.selectedProfiles))
        self.addRemAlt.clicked.connect(lambda: self.addRemoveFromList(self.altCB.currentText(), self.addRemAlt, self.currentAlt, self.selectedAltFields, True))
        self.altCB.currentIndexChanged.connect(lambda: self.profAltSimpTradChange(self.altCB.currentText(), self.addRemAlt, self.selectedAltFields))
        self.addRemSimp.clicked.connect(lambda: self.addRemoveFromList(self.simpCB.currentText(), self.addRemSimp, self.currentSimp, self.selectedSimpFields, True))
        self.simpCB.currentIndexChanged.connect(lambda: self.profAltSimpTradChange(self.simpCB.currentText(), self.addRemSimp, self.selectedSimpFields))
        self.addRemTrad.clicked.connect(lambda: self.addRemoveFromList(self.tradCB.currentText(), self.addRemTrad, self.currentTrad, self.selectedTradFields, True))
        self.tradCB.currentIndexChanged.connect(lambda: self.profAltSimpTradChange(self.tradCB.currentText(), self.addRemTrad, self.selectedTradFields))
        self.altWithSep.clicked.connect(lambda: self.enableSep(self.altSep))
        self.altOW.clicked.connect(lambda: self.disableSep(self.altSep))
        self.altIfE.clicked.connect(lambda: self.disableSep(self.altSep))
        self.simpWithSep.clicked.connect(lambda: self.enableSep(self.simpSep))
        self.simpOW.clicked.connect(lambda: self.disableSep(self.simpSep))
        self.simpIfE.clicked.connect(lambda: self.disableSep(self.simpSep))
        self.tradWithSep.clicked.connect(lambda: self.enableSep(self.tradSep))
        self.tradOW.clicked.connect(lambda: self.disableSep(self.tradSep))
        self.tradIfE.clicked.connect(lambda: self.disableSep(self.tradSep))

        self.profileAF.currentIndexChanged.connect(self.profileChange )
        self.noteTypeAF.currentIndexChanged.connect(self.noteTypeChange)
        self.cardTypeAF.currentIndexChanged.connect(self.selectionChange)
        self.fieldAF.currentIndexChanged.connect(self.selectionChange)
        self.sideAF.currentIndexChanged.connect(self.selectionChange)
        self.displayAF.currentIndexChanged.connect(self.selectionChange)
        self.readingAF.currentIndexChanged.connect(self.selectionChange)

        self.afTable.cellClicked.connect(self.loadSelectedRow)

        self.addEditAF.clicked.connect(self.performAddEdit)
        self.applyButton.clicked.connect(self.saveConfig)
        self.resetButton.clicked.connect(self.resetDefaults)
        self.cancelButton.clicked.connect(self.close)
        self.autoCSSJS.toggled.connect(self.handleAutoCSSJS)


    def handleAutoCSSJS(self):
        if self.autoCSSJS.isChecked():
            self.profileAF.setEnabled(True)
            self.noteTypeAF.setEnabled(True)
            self.cardTypeAF.setEnabled(True)
            self.fieldAF.setEnabled(True)
            self.sideAF.setEnabled(True)
            self.displayAF.setEnabled(True)
            self.addEditAF.setEnabled(True)
            self.readingAF.setEnabled(True)
            self.afTable.setEnabled(True)

        else:
            self.profileAF.setEnabled(False)
            self.noteTypeAF.setEnabled(False)
            self.cardTypeAF.setEnabled(False)
            self.fieldAF.setEnabled(False)
            self.sideAF.setEnabled(False)
            self.displayAF.setEnabled(False)
            self.addEditAF.setEnabled(False)
            self.readingAF.setEnabled(False)
            self.afTable.setEnabled(False)

    def profileChange(self):
        if self.initializing:
            return
        self.changingProfile = True
        self.noteTypeAF.clear()
        self.cardTypeAF.clear()
        self.fieldAF.clear()
        if self.profileAF.currentIndex() == 0:
            self.loadAllNotes()
        else:
            prof = self.profileAF.currentText()
            for noteType in self.ciSort(self.cA[prof]):
                    self.noteTypeAF.addItem(noteType)
                    self.noteTypeAF.setItemData(self.noteTypeAF.count() - 1, noteType + ' (Prof:' + prof + ')',Qt.ToolTipRole)
                    self.noteTypeAF.setItemData(self.noteTypeAF.count() - 1, prof + ':pN:' + noteType)
        self.loadCardTypesFields()
        self.changingProfile = False
        self.selectionChange()

    def noteTypeChange(self):
        if self.initializing:
            return
        if not self.changingProfile:
            self.cardTypeAF.clear()
            self.fieldAF.clear()
            self.loadCardTypesFields()
        self.selectionChange()

    def resetWindow(self):
        self.initializing = True
        self.buttonStatus = 0
        self.addEditAF.setText('Add')
        self.selectedRow = False
        self.clearAllAF()
        self.initActiveFieldsCB()
        self.initializing = False

    def selectionChange(self):
        if self.buttonStatus == 1:
            self.buttonStatus = 2
            self.addEditAF.setText('Save Changes')

    def performAddEdit(self):
        if self.buttonStatus == 1:
            self.resetWindow()
        else:
            profile = self.profileAF.currentText()
            nt = self.noteTypeAF.itemData(self.noteTypeAF.currentIndex()).split(':pN:')[1]
            ct = self.cardTypeAF.currentText()
            field = self.fieldAF.currentText()
            side = self.sideAF.currentText()
            dt = self.displayAF.currentText()
            rt = self.readingAF.currentText()
            if profile != '' and nt != '' and ct != '' and field != '' and side != '' and dt != '' and rt != '':
                if self.buttonStatus == 0:
                    self.addToList(profile, nt, ct, field, side, dt, rt)
                elif self.buttonStatus == 2:
                    self.editEntry(profile, nt, ct, field, side, dt, rt)

    def dupeRow(self, afList, profile, nt, ct, field, side,  dt, selRow = False):
        for i in range(afList.rowCount()):
            if selRow is not False:
                if i == selRow[0].row():
                    continue
            if (afList.item(i, 0).text() == profile or afList.item(i, 0).text() == 'All' or profile == "All") and afList.item(i, 1).text() == nt and afList.item(i, 2).text() == ct and afList.item(i, 3).text() == field and (afList.item(i, 4).text() == side or afList.item(i, 4).text() == 'Both' or side == "Both"):
                return i + 1;
        return False

    def addToList(self, profile, nt, ct, field, side, dt, rt):
        afList = self.afTable
        found = self.dupeRow(afList, profile, nt, ct, field, side, dt)
        if found:
            miInfo('This row cannot be added because row #' + str(found) + 
                ' in the Active Fields List already targets this given field and side combination. Please review that entry and try again.', level = 'err')
        else:
            afList.setSortingEnabled(False)
            rc = afList.rowCount()
            afList.setRowCount(rc + 1)
            afList.setItem(rc, 0, QTableWidgetItem(profile))
            afList.setItem(rc, 1, QTableWidgetItem(nt))
            afList.setItem(rc, 2, QTableWidgetItem(ct))
            afList.setItem(rc, 3, QTableWidgetItem(field))
            afList.setItem(rc, 4, QTableWidgetItem(side))
            afList.setItem(rc, 5, QTableWidgetItem(dt))
            afList.setItem(rc, 6, QTableWidgetItem(rt))
            deleteButton =  QPushButton("X");
            deleteButton.setFixedWidth(40)
            deleteButton.clicked.connect(self.removeRow)
            afList.setCellWidget(rc, 7, deleteButton);
            afList.setSortingEnabled(True)

    def initEditMode(self):
        self.buttonStatus = 1
        self.addEditAF.setText('Cancel')

    def editEntry(self, profile, nt, ct, field, side, dt, rt):
        afList = self.afTable
        rc = self.selectedRow
        found = self.dupeRow(afList, profile, nt, ct, field, side, dt, rc)
        if found:
            miInfo('This row cannot be edited in this manner because row #' + str(found) + 
                ' in the Active Fields List already targets this given field and side combination. Please review that entry and try again.', level = 'err')
        else:
            afList.setSortingEnabled(False)
            rc[0].setText(profile)
            rc[1].setText(nt)
            rc[2].setText(ct)
            rc[3].setText(field)
            rc[4].setText(side)
            rc[5].setText(dt)
            rc[6].setText(rt)
            afList.setSortingEnabled(True) 
        self.resetWindow()   

    def removeRow(self):
        if miAsk('Are you sure you would like to remove this entry from the active field list?'):
            self.afTable.removeRow(self.afTable.selectionModel().currentIndex().row())
            self.resetWindow()

    def loadSelectedRow(self, row, col):
        afList = self.afTable
        prof = afList.item(row, 0).text()
        nt = afList.item(row, 1).text()
        ct = afList.item(row, 2).text()
        field = afList.item(row, 3).text()
        side = afList.item(row, 4).text()
        dt = afList.item(row, 5).text()
        rt = afList.item(row, 6).text()
        if prof.lower() == 'all':
            loaded = self.unspecifiedProfileLoad( nt, ct, field, side, dt, rt)
        else:
            loaded = self.specifiedProfileLoad(prof, nt, ct, field, side, dt, rt)
        if loaded:
            self.initEditMode()
            self.selectedRow = [afList.item(row, 0), afList.item(row, 1), afList.item(row, 2), afList.item(row, 3), afList.item(row, 4), afList.item(row, 5), afList.item(row, 6)]
            

    def unspecifiedProfileLoad(self, nt, ct, field, side, dt, rt):
        self.profileAF.setCurrentIndex(0)
        if self.findFirstNoteCardFieldMatch(nt, ct, field):
            index = self.sideAF.findText(side, Qt.MatchFixedString)
            if index >= 0:
                self.sideAF.setCurrentIndex(index)
            index = self.displayAF.findText(dt, Qt.MatchFixedString)
            if index >= 0:
                self.displayAF.setCurrentIndex(index)
            index = self.readingAF.findText(rt, Qt.MatchFixedString)
            if index >= 0:
                self.readingAF.setCurrentIndex(index)
            return True
        else: 
            return False

    def findFirstNoteCardFieldMatch(self, nt, ct, field):
        for i in range(self.noteTypeAF.count()):
            if self.noteTypeAF.itemText(i).startswith(nt):
                self.noteTypeAF.setCurrentIndex(i)
                ci = self.cardTypeAF.findText(ct, Qt.MatchFixedString)
                if ci >= 0:
                    fi = self.fieldAF.findText(field, Qt.MatchFixedString)
                    if fi >= 0:
                        self.noteTypeAF.setCurrentIndex(i)
                        self.cardTypeAF.setCurrentIndex(ci)
                        self.fieldAF.setCurrentIndex(fi)
                        return True
        return False

    def specifiedProfileLoad(self, prof, nt, ct, field, side, dt, rt):
        index = self.profileAF.findText(prof, Qt.MatchFixedString)
        if index >= 0:
            self.profileAF.setCurrentIndex(index)
        index = self.noteTypeAF.findText(nt, Qt.MatchFixedString)
        if index >= 0:
            self.noteTypeAF.setCurrentIndex(index)
        index = self.cardTypeAF.findText(ct, Qt.MatchFixedString)
        if index >= 0:
            self.cardTypeAF.setCurrentIndex(index)
        index = self.fieldAF.findText(field, Qt.MatchFixedString)
        if index >= 0:
            self.fieldAF.setCurrentIndex(index)
        index = self.sideAF.findText(side, Qt.MatchFixedString)
        if index >= 0:
            self.sideAF.setCurrentIndex(index)
        index = self.displayAF.findText(dt, Qt.MatchFixedString)
        if index >= 0:
            self.displayAF.setCurrentIndex(index)
        index = self.readingAF.findText(rt, Qt.MatchFixedString)
        if index >= 0:
            self.readingAF.setCurrentIndex(index)
        return True

    def loadAltSimpTradFieldsCB(self):
        self.altCB.addItem('Clipboard')
        self.altCB.addItem('──────────────────')
        self.altCB.model().item(self.altCB.count() - 1).setEnabled(False)
        self.altCB.model().item(self.altCB.count() - 1).setTextAlignment(Qt.AlignCenter)
        self.altCB.addItems(self.allFields)
        self.simpCB.addItem('Clipboard')
        self.simpCB.addItem('──────────────────')
        self.simpCB.model().item(self.simpCB.count() - 1).setEnabled(False)
        self.simpCB.model().item(self.simpCB.count() - 1).setTextAlignment(Qt.AlignCenter)
        self.simpCB.addItems(self.allFields)
        self.tradCB.addItem('Clipboard')
        self.tradCB.addItem('──────────────────')
        self.tradCB.model().item(self.tradCB.count() - 1).setEnabled(False)
        self.tradCB.model().item(self.tradCB.count() - 1).setTextAlignment(Qt.AlignCenter)
        self.tradCB.addItems(self.allFields)

    def loadFieldsList(self, which):
        if which == 1:
            fl = self.currentAlt
            currentSelection = self.altCB.currentText()
            fs = self.config['SimpTradField']
        elif which == 2:
            fl = self.currentSimp
            currentSelection = self.simpCB.currentText()
            fs = self.config['SimplifiedField']
        else:
            fl = self.currentTrad
            currentSelection = self.tradCB.currentText()
            fs = self.config['TraditionalField']

        fieldList = fs.split(';')
        separator = False
        if len(fieldList) > 2:
            fields, addMode, separator = fieldList
        else:    
            fields, addMode = fieldList
        fields = fields.split(',')
        for idx, field in enumerate(fields):
            if field == 'clipboard':
                fields[idx] = 'Clipboard'
        if len(fields) == 1 and (fields[0].lower() == 'none' or fields[0].lower() == ''):
            fl.setText('<i>None currently selected.</i>')
        else:
            fl.setText('<i>' + ', '.join(fields) +'</i>')
        if  which == 1:
            self.selectedAltFields = fields
            if currentSelection in self.selectedAltFields:
                self.addRemAlt.setText('Remove')
        elif  which == 2:
            self.selectedSimpFields = fields
            if currentSelection in self.selectedSimpFields:
                self.addRemSimp.setText('Remove')
        else:
            self.selectedTradFields = fields
            if currentSelection in self.selectedTradFields:
                self.addRemTrad.setText('Remove')
        self.loadAddModes(addMode.lower(), separator, which)
                
    def loadAddModes(self, addMode, separator, which):
        if which == 1:
            add = self.altWithSep
            overwrite = self.altOW
            ifEmpty = self.altIfE
            sepB = self.altSep
        elif which == 2:
            add = self.simpWithSep
            overwrite = self.simpOW
            ifEmpty = self.simpIfE
            sepB = self.simpSep
        else:
            add = self.tradWithSep
            overwrite = self.tradOW
            ifEmpty = self.tradIfE
            sepB = self.tradSep
        if addMode == 'overwrite':
            overwrite.setChecked(True)
        elif addMode == 'add':
            add.setChecked(True)
        elif addMode == 'no':
            ifEmpty.setChecked(True)
        if separator:
            sepB.setText(separator)
        else:
            sepB.setText('<br>')
        if not add.isChecked():
            sepB.setEnabled(False)


    def addRemoveFromList(self, value, button, lWidget, vList, profiles = False):
        if button.text() == 'Remove':
            if value in vList:
                vList.remove(value)
                lWidget.setText('<i>'+', '.join(vList)+ '</i>')
                button.setText('Add')
                if len(vList) == 0 or (len(vList) == 1 and vList[0].lower() == 'none'):
                    lWidget.setText('<i>None currently selected.</i>')
        else:
            if profiles and value == 'All':
                vList.clear()
                vList.append('All')
                lWidget.setText('<i>All</i>')
                button.setText('Remove')
            else:
                if profiles:
                    if 'All' in vList:
                        vList.remove('All')
                if len(vList) == 1 and (vList[0].lower() == 'none' or vList[0] == ''):
                    vList.remove(vList[0])
                vList.append(value)
                lWidget.setText('<i>'+ ', '.join(vList) + '</i>')
                button.setText('Remove')

    def profAltSimpTradChange(self, value, button, vList):
        if value in vList:
            button.setText('Remove')
        else:
            button.setText('Add')


    def loadProfileCB(self):
        pcb = self.profileCB
        pcb.addItem('All')
        pcb.addItem('──────')
        pcb.model().item(pcb.count() - 1).setEnabled(False)
        pcb.model().item(pcb.count() - 1).setTextAlignment(Qt.AlignCenter)
        for prof in self.cA:
            pcb.addItem(prof)
            pcb.setItemData(pcb.count() -1, prof, Qt.ToolTipRole)

    def loadProfilesList(self):
        pl = self.currentProfiles
        profs = self.config['Profiles']
        if len(profs) == 0:
            pl.setText('<i>None currently selected.</i>')
        else:
            profl = []
            currentSelection = self.profileCB.currentText()
            for prof in  profs:
                if prof.lower() == 'all':
                    profl.append('All')
                    self.selectedProfiles = ['All']
                    if currentSelection == 'All':
                        self.addRemProfile.setText('Remove')
                        self.selectedProfiles = profl            
                        pl.setText('<i>All</i>')
                        return
                profl.append(prof)
                if currentSelection == prof:
                    self.addRemProfile.setText('Remove')
            self.selectedProfiles = profl            
            pl.setText('<i>' + ', '.join(profl) + '</i>')

    def getConfig(self):
        return self.mw.addonManager.getConfig(__name__)
    

    def saveAltSimpTradConfig(self):
        if len(self.selectedAltFields) < 1:
            altConfig = ['none']
        else:
            altConfig = [ ','.join(self.selectedAltFields)]
        if len(self.selectedSimpFields) < 1:
            simpConfig = ['none']
        else:
            simpConfig = [ ','.join(self.selectedSimpFields)]
        if len(self.selectedTradFields) < 1:
            tradConfig = ['none']
        else:
            tradConfig = [ ','.join(self.selectedTradFields)]
        if self.altWithSep.isChecked():
            altConfig.append('add')
            altConfig.append(self.altSep.text())
        elif self.altOW.isChecked():
            altConfig.append('overwrite')
        elif self.altIfE.isChecked():
            altConfig.append('no')
        if self.simpWithSep.isChecked():
            simpConfig.append('add')
            simpConfig.append(self.simpSep.text())
        elif self.simpOW.isChecked():
            simpConfig.append('overwrite')
        elif self.simpIfE.isChecked():
            simpConfig.append('no')

        if self.tradWithSep.isChecked():
            tradConfig.append('add')
            tradConfig.append(self.tradSep.text())
        elif self.tradOW.isChecked():
            tradConfig.append('overwrite')
        elif self.tradIfE.isChecked():
            tradConfig.append('no')
        return ';'.join(altConfig), ';'.join(simpConfig), ';'.join(tradConfig);

    def getColors(self,letter, maxr):
        colors = []
        for idx in range(1, maxr):
            name = letter + str(idx) + 'color'
            widget = getattr(self, name)
            colors.append(widget.text())
        return colors

    def saveActiveFields(self):
        afList = self.afTable
        afs = []
        for i in range(afList.rowCount()):
            prof = afList.item(i, 0).text()
            if prof == 'All':
                prof = 'all'
            nt = afList.item(i, 1).text()
            ct = afList.item(i, 2).text()
            field = afList.item(i, 3).text()
            side = afList.item(i, 4).text().lower()
            target = afList.item(i,  5).text()
            for key, value in self.displayTranslation.items():
                if value == target:
                    dt = key
                    break
            rt = afList.item(i,  6).text().lower()
            afs.append(';'.join([dt,prof,nt,ct,field,side,rt]))
        return afs
 

    def saveConfig(self):
        drt = self.defaultReading.currentText().lower()
        b2n = self.bopo2Number.isChecked()
        tradIcons = self.tradIcons.isChecked()
        alt, simp, trad = self.saveAltSimpTradConfig()
        mColors = self.getColors('m', 6)
        cColors = self.getColors('c', 7)
        autoCSSJS = self.autoCSSJS.isChecked()
        addChina = self.addChina.isChecked()
        addTaiwan = self.addTaiwan.isChecked()
        addHK = self.addHK.isChecked()
        hc = self.hanziConversion.currentText()
        rc = self.readingConversion.currentText()
        fontSize = self.fontSize.value()
        newConf = {"ActiveFields" : self.saveActiveFields(),  "Profiles" : self.selectedProfiles,
         "AutoCssJsGeneration" : autoCSSJS, "addSimpNote" : addChina, "addTradNote" : addTaiwan, "addCantoNote" : addHK,
         "BopomofoTonesToNumber" : b2n, "hanziConversion" : hc, "readingConversion" : rc, "ReadingType" : drt, "SimplifiedField" : simp,
         "TraditionalField" : trad, "SimpTradField" : alt,  "traditionalIcons" : tradIcons, "CantoneseTones123456": cColors, "MandarinTones12345" : mColors, "FontSize": fontSize
         }
        
        self.mw.addonManager.writeConfig(__name__, newConf)
        if addChina or addTaiwan or addHK: 
            self.modeler.addModels() 
        # self.CSSJSHandler.injectWrapperElements()  ### properly handle cssjs handling
        self.cssJSHandler.injectWrapperElements()
        self.hide()
        self.mw.MigakuChinese.refreshConfig()
        self.mw.updateMigakuChineseConfig()

    def openDialogColor(self, lineEd):
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            lineEd.setText(color.name())
            lineEd.setStyleSheet('color:' + color.name() + ';')


    def miQLabel(self, text, width):
        label = QLabel(text)
        label.setFixedHeight(30)
        label.setFixedWidth(width)
        return label

    def setupMainLayout(self):
        self.ml = QVBoxLayout()
        self.ml.addWidget(self.tabs)
        bl = QHBoxLayout()
        bl.addWidget(self.resetButton)
        bl.addStretch()
        bl.addWidget(self.cancelButton)
        bl.addWidget(self.applyButton)
        self.ml.addLayout(bl)
        self.innerWidget.setLayout(self.ml)


    def getSVGWidget(self,  name):
        widget = MigakuSVG(join(self.addonPath, 'icons', name))
        widget.setFixedSize(27,27)
        return widget

    def getAboutTab(self):
        tab_4 = QWidget()
        tab_4.setObjectName("tab_4")
        tab4vl = QVBoxLayout()
        migakuAbout = QGroupBox()
        migakuAbout.setTitle('Migaku')
        migakuAboutVL = QVBoxLayout()

        migakuAbout.setStyleSheet("QGroupBox { font-weight: bold; } ")
        migakuAboutText = QLabel("This an original Migaku add-on. Migaku seeks to be a comprehensive platform for acquiring foreign languages. The official Migaku website will be published soon!")
        migakuAboutText.setWordWrap(True);
        migakuAboutText.setOpenExternalLinks(True);
        migakuAbout.setLayout(migakuAboutVL)
        migakuAboutLinksTitle = QLabel("<b>Links<b>")
 
        migakuAboutLinksHL3 = QHBoxLayout()


        migakuInfo = QLabel("Migaku:")
        migakuInfoSite = self.getSVGWidget('migaku.svg')
        migakuInfoSite.setCursor(QCursor(Qt.PointingHandCursor))

        migakuInfoYT = self.getSVGWidget('Youtube.svg')
        migakuInfoYT.setCursor(QCursor(Qt.PointingHandCursor))

        migakuInfoTW = self.getSVGWidget('Twitter.svg')
        migakuInfoTW.setCursor(QCursor(Qt.PointingHandCursor))


        migakuPatreonIcon = self.getSVGWidget('Patreon.svg')
        migakuPatreonIcon.setCursor(QCursor(Qt.PointingHandCursor))
        migakuAboutLinksHL3.addWidget(migakuInfo)
        migakuAboutLinksHL3.addWidget(migakuInfoSite)
        migakuAboutLinksHL3.addWidget(migakuInfoYT)
        migakuAboutLinksHL3.addWidget(migakuInfoTW)
        migakuAboutLinksHL3.addWidget(migakuPatreonIcon)
        migakuAboutLinksHL3.addStretch()

        migakuAboutVL.addWidget(migakuAboutText)
        migakuAboutVL.addWidget(migakuAboutLinksTitle)
        migakuAboutVL.addLayout(migakuAboutLinksHL3)
        
        migakuContact = QGroupBox()
        migakuContact.setTitle('Contact Us')
        migakuContactVL = QVBoxLayout()
        migakuContact.setStyleSheet("QGroupBox { font-weight: bold; } ")
        migakuContactText = QLabel("If you would like to report a bug or contribute to the add-on, the best way to do so is by starting a ticket or pull request on GitHub. If you are looking for personal assistance using the add-on, check out the Migaku Patreon Discord Server.")
        migakuContactText.setWordWrap(True)

        gitHubIcon = self.getSVGWidget('Github.svg')
        gitHubIcon.setCursor(QCursor(Qt.PointingHandCursor))
        
        migakuThanks = QGroupBox()
        migakuThanks.setTitle('A Word of Thanks')
        migakuThanksVL = QVBoxLayout()
        migakuThanks.setStyleSheet("QGroupBox { font-weight: bold; } ")
        migakuThanksText = QLabel("Thanks so much to all Migaku supporters! We would not have been able to develop this add-on or any other Migaku project without your support!")
        migakuThanksText.setOpenExternalLinks(True);
        migakuThanksText.setWordWrap(True);
        migakuThanksVL.addWidget(migakuThanksText)

        migakuContactVL.addWidget(migakuContactText)
        migakuContactVL.addWidget(gitHubIcon)
        migakuContact.setLayout(migakuContactVL)
        migakuThanks.setLayout(migakuThanksVL)
        tab4vl.addWidget(migakuAbout)
        tab4vl.addWidget(migakuContact)
        tab4vl.addWidget(migakuThanks)
        tab4vl.addStretch()
        tab_4.setLayout(tab4vl)

        migakuInfoSite.clicked.connect(lambda: openLink('https://migaku.io'))
        migakuPatreonIcon.clicked.connect(lambda: openLink('https://www.patreon.com/Migaku'))
        migakuInfoYT.clicked.connect(lambda: openLink('https://www.youtube.com/channel/UCQFe3x4WAgm7joN5daMm5Ew'))
        migakuInfoTW.clicked.connect(lambda: openLink('https://twitter.com/Migaku_Yoga'))
        gitHubIcon.clicked.connect(lambda: openLink('https://github.com/migaku-official'))
        return tab_4

    def clearAllAF(self):
        self.profileAF.clear()
        self.noteTypeAF.clear()
        self.cardTypeAF.clear()
        self.fieldAF.clear()
        self.sideAF.clear()
        self.displayAF.clear()
        self.readingAF.clear()

    def initActiveFieldsCB(self):
        aP = self.profileAF
        aP.addItem('All')
        aP.addItem('──────────────────')
        aP.model().item(aP.count() - 1).setEnabled(False)
        aP.model().item(aP.count() - 1).setTextAlignment(Qt.AlignCenter)
        self.loadAllProfiles()  
        self.loadCardTypesFields()
        for key, value in self.sides.items():
            self.sideAF.addItem(key)
            self.sideAF.setItemData(self.sideAF.count() - 1, value ,Qt.ToolTipRole)
        for key, value in self.displayTypes.items():
            self.displayAF.addItem(key)
            self.displayAF.setItemData(self.displayAF.count() - 1, value[1] ,Qt.ToolTipRole)
            self.displayAF.setItemData(self.displayAF.count() - 1, value[0])
        for key, value in self.readingTypes.items():
            self.readingAF.addItem(key)
            self.readingAF.setItemData(self.readingAF.count() - 1, value ,Qt.ToolTipRole)

    def loadAllProfiles(self):
        if not self.sortedProfiles and not self.sortedNoteTypes:
            profL = []
            noteL = []
            for prof in self.cA:
                profL.append(prof)
                for noteType in self.cA[prof]:
                    noteL.append([noteType + ' (Prof:' + prof + ')', prof + ':pN:' + noteType])
            self.sortedProfiles = self.ciSort(profL)
            self.sortedNoteTypes = sorted(noteL, key=itemgetter(0))
        aP = self.profileAF
        for prof in self.sortedProfiles:
            aP.addItem(prof)
            aP.setItemData(aP.count() -1, prof, Qt.ToolTipRole)
        self.loadAllNotes()

    def loadAllNotes(self):
        for noteType in self.sortedNoteTypes:
            self.noteTypeAF.addItem(noteType[0])
            self.noteTypeAF.setItemData(self.noteTypeAF.count() - 1, noteType[0],Qt.ToolTipRole)
            self.noteTypeAF.setItemData(self.noteTypeAF.count() - 1, noteType[1])

    def loadCardTypesFields(self):
        curProf, curNote = self.noteTypeAF.itemData(self.noteTypeAF.currentIndex()).split(':pN:')     
        for cardType in self.cA[curProf][curNote]['cardTypes']:
            self.cardTypeAF.addItem(cardType)
            self.cardTypeAF.setItemData(self.cardTypeAF.count() - 1, cardType,Qt.ToolTipRole)
        for field in self.cA[curProf][curNote]['fields']:
            self.fieldAF.addItem(field)
            self.fieldAF.setItemData(self.fieldAF.count() - 1, field,Qt.ToolTipRole)
        return

    def loadActiveFields(self):
        afs = self.config['ActiveFields']
        for af in afs:
            afl = af.split(';')
            dt = afl[0].lower()
            rt = afl[6].lower()
            if dt in self.displayTranslation:
                prof = afl[1]
                if prof == 'all':
                    prof = 'All'
                self.addToList(prof, afl[2], afl[3], afl[4], afl[5][0].upper() + afl[5][1:].lower() , self.displayTranslation[dt], self.rtTranslation[rt])