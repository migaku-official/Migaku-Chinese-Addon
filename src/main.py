# -*- coding: utf-8 -*-
# 
from os.path import dirname, join, basename, exists, join
import sys, os, platform, re, subprocess, aqt.utils
from anki.utils import stripHTML, isWin, isMac
from . import Pyperclip 
import re

import unicodedata
import urllib.parse
from shutil import copyfile
from anki.hooks import addHook, wrap, runHook, runFilter
from aqt.utils import shortcut, saveGeom, saveSplitter, showInfo, askUser
import aqt.editor
import json
from aqt import mw
from aqt.qt import *
from . import dictdb
sys.path.append(join(dirname(__file__), 'lib'))
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import time
from urllib.request import Request, urlopen
from .misettings import SettingsGui
from .miutils import miInfo, miAsk
import requests
from aqt.main import AnkiQt
from dragonmapper import transcriptions
from anki import Collection
from .models import MIChineseModels
from .chineseHandler import ChineseHandler
from .cssJSHandler import CSSJSHandler


def getConfig():
    return mw.addonManager.getConfig(__name__)

def updateMigakuChineseConfig():
    mw.MigakuChineseConfig = getConfig()

chineseModeler = MIChineseModels(mw)
addHook("profileLoaded", chineseModeler.addModels)
mw.miChineseSettings = False
db = dictdb.DictDB()
addonPath = dirname(__file__)
autoCssJs = CSSJSHandler(mw,addonPath)
mw.MigakuChinese = ChineseHandler(mw,addonPath, db, autoCssJs)
mw.MigakuChineseConfig = getConfig()
mw.updateMigakuChineseConfig = updateMigakuChineseConfig
# addHook("profileLoaded", autoCssJs.loadWrapperDict)
addHook("profileLoaded", autoCssJs.injectWrapperElements)
addHook("profileLoaded", autoCssJs.updateWrapperDict)

requests.packages.urllib3.disable_warnings()

currentNote = False 
currentField = False
currentKey = False
wrapperDict = False
colArray = False

def loadCollectionArray(self = None, b = None):
    global colArray
    colArray = {}
    loadAllProfileInformation()

def loadAllProfileInformation():
    global colArray
    for prof in mw.pm.profiles():
        cpath = join(mw.pm.base, prof,  'collection.anki2')
        try:
            tempCol = Collection(cpath)
            noteTypes = tempCol.models.all()
            tempCol.close()
            tempCol = None
            noteTypeDict = {}
            for note in noteTypes:
                noteTypeDict[note['name']] = {"cardTypes" : [], "fields" : []}
                for ct in note['tmpls']:
                    noteTypeDict[note['name']]["cardTypes"].append(ct['name'])
                for f in note['flds']:
                    noteTypeDict[note['name']]["fields"].append(f['name'])
            colArray[prof] = noteTypeDict
        except:
            miInfo('<b>Warning:</b><br>One of your profiles could not be loaded. This usually happens if you\'ve just created a new profile and are opening it for the first time.The issue should be fixed after restarting Anki.If it persists, then your profile is corrupted in some way.\n\nYou can fix this corruption by exporting your collection, importing it into a new profile, and then deleting your previous profile. <b>', level='wrn')


AnkiQt.loadProfile = wrap(AnkiQt.loadProfile, loadCollectionArray, 'before')


def openChineseSettings():
    if not mw.miChineseSettings:
        mw.miChineseSettings = SettingsGui(mw, addonPath, colArray, chineseModeler, autoCssJs, openChineseSettings)
    mw.miChineseSettings.show()
    if mw.miChineseSettings.windowState() == Qt.WindowMinimized:
            # Window is minimised. Restore it.
           mw.miChineseSettings.setWindowState(Qt.WindowNoState)
    mw.miChineseSettings.setFocus()
    mw.miChineseSettings.activateWindow()


def setupGuiMenu():
    addMenu = False
    if not hasattr(mw, 'MigakuMainMenu'):
        mw.MigakuMainMenu = QMenu('Migaku',  mw)
        addMenu = True
    if not hasattr(mw, 'MigakuMenuSettings'):
        mw.MigakuMenuSettings = []
    if not hasattr(mw, 'MigakuMenuActions'):
        mw.MigakuMenuActions = []
    
    setting = QAction("Chinese Settings", mw)
    setting.triggered.connect(openChineseSettings)
    mw.MigakuMenuSettings.append(setting)

    mw.MigakuMainMenu.clear()
    for act in mw.MigakuMenuSettings:
        mw.MigakuMainMenu.addAction(act)
    mw.MigakuMainMenu.addSeparator()
    for act in mw.MigakuMenuActions:
        mw.MigakuMainMenu.addAction(act)

    if addMenu:
        mw.form.menubar.insertMenu(mw.form.menuHelp.menuAction(), mw.MigakuMainMenu)

setupGuiMenu()


def setupButtons(righttopbtns, editor):
  if not checkProfile():
        return righttopbtns
  editor._links["removeFormatting"] = lambda editor: mw.MigakuChinese.cleanField(editor)
  if mw.MigakuChineseConfig['traditionalIcons'] :
    duPath = os.path.join(addonPath, "icons", "tradDu.svg")
    shanPath = os.path.join(addonPath, "icons", "tradShan.svg")
  else:
    duPath = os.path.join(addonPath, "icons", "simpDu.svg")
    shanPath = os.path.join(addonPath, "icons", "simpShan.svg")

  righttopbtns.insert(0, editor._addButton(
                icon=shanPath,
                cmd='removeFormatting',
                tip="Hotkey: F10",
                id=u"删"
            ))
  editor._links["addCReadings"] = lambda editor: mw.MigakuChinese.addCReadings(editor)
  righttopbtns.insert(0, editor._addButton(
                icon=duPath,
                cmd='addCReadings',
                tip="Hotkey: F9",
                id=u"读"
            ))
  return righttopbtns

def shortcutCheck(x, key):
    if x == key:
        return False
    else:
        return True

def setupShortcuts(shortcuts, editor):
    if not checkProfile():
        return shortcuts
    # config = getConfig()
    pitchData = []
    pitchData.append({ "hotkey": "F10", "name" : 'extra', 'function' : lambda  editor=editor: mw.MigakuChinese.cleanField(editor)})
    pitchData.append({ "hotkey": "F9", "name" : 'extra', 'function' : lambda  editor=editor: mw.MigakuChinese.addCReadings(editor)})
    newKeys = shortcuts;
    for pitch in pitchData:
        newKeys = list(filter(lambda x: shortcutCheck(x[0], pitch['hotkey']), newKeys))
        newKeys += [(pitch['hotkey'] , pitch['function'])]
    shortcuts.clear()
    shortcuts += newKeys
    return 


def onRegenerate(browser):
    import anki.find
    notes = browser.selectedNotes()
    if notes:
        fields = anki.find.fieldNamesForNotes(mw.col, notes)
        generateWidget = QDialog(None, Qt.Window)
        layout = QHBoxLayout()
        og = QLabel('Origin:')
        cb = QComboBox()
        cb.addItems(fields)
        dest = QLabel('Destination:')
        destCB = QComboBox()
        destCB.addItems(fields)
        om = QLabel('Output Mode:')
        omCB = QComboBox()
        omCB.addItems(['Add', 'Overwrite', 'If Empty'])
        rt = QLabel('Reading Type:')
        rtCB = QComboBox()
        rtCB.addItems(['Pinyin','Bopomofo','Jyutping'])
        b4 =  QPushButton('Add Readings')
        b4.clicked.connect(lambda: mw.MigakuChinese.massGenerate(cb.currentText(), destCB.currentText(), omCB.currentText(), rtCB.currentText().lower(),  notes, generateWidget))##add in the vars
        b5 =  QPushButton('Remove Readings')
        b5.clicked.connect(lambda: mw.MigakuChinese.massRemove(cb.currentText(), notes, generateWidget))
        layout.addWidget(og)
        layout.addWidget(cb)
        layout.addWidget(dest)
        layout.addWidget(destCB)
        layout.addWidget(om)
        layout.addWidget(omCB)
        layout.addWidget(rt)
        layout.addWidget(rtCB)
        layout.addWidget(b4)
        layout.addWidget(b5)
        generateWidget.setWindowTitle("Generate Chinese Readings")
        generateWidget.setWindowIcon(QIcon(join(addonPath, 'icons', 'migaku.png')))
        generateWidget.setLayout(layout)
        generateWidget.exec_()
    else:
        miInfo('Please select some cards before attempting to mass generate.')

def setupMenu(browser):
    if not checkProfile():
        return
    a = QAction("Generate Chinese Readings", browser)
    a.triggered.connect(lambda: onRegenerate(browser))
    browser.form.menuEdit.addSeparator()
    browser.form.menuEdit.addAction(a)

current_path = os.path.abspath('.')
parent_path = os.path.dirname(current_path)
sys.path.append(parent_path)


def checkProfile():
    config = mw.MigakuChineseConfig
    if mw.pm.name in config['Profiles'] or ('all' in config['Profiles'] or 'All' in config['Profiles']):
        return True
    return False

def supportAccept(self):
    if self.addon != os.path.basename(addonPath):
        ogAccept(self)
    txt = self.form.editor.toPlainText()
    try:
        new_conf = json.loads(txt)
    except Exception as e:
        showInfo(_("Invalid configuration: ") + repr(e))
        return

    if not isinstance(new_conf, dict):
        showInfo(_("Invalid configuration: top level object must be a map"))
        return

    if new_conf != self.conf:
        self.mgr.writeConfig(self.addon, new_conf)
        # does the add-on define an action to be fired?
        act = self.mgr.configUpdatedAction(self.addon)
        if act:
            act(new_conf)
        if not autoCssJs.injectWrapperElements():
            return

    saveGeom(self, "addonconf")
    saveSplitter(self.form.splitter, "addonconf")
    self.hide()

ogAccept = aqt.addons.ConfigEditor.accept 
aqt.addons.ConfigEditor.accept = supportAccept
    
addHook("browser.setupMenus", setupMenu)
addHook("setupEditorButtons", setupButtons)
addHook("setupEditorShortcuts", setupShortcuts)

def getFieldName(fieldId, note):
    fields = mw.col.models.fieldNames(note.model())
    field = fields[int(fieldId)]
    return field;


def bridgeReroute(self, cmd):
    global currentKey
    if checkProfile():
        if cmd.startswith('textToCReading'):
            splitList = cmd.split(':||:||:')
            if self.note.id == int(splitList[3]):
                field = getFieldName(splitList[2], self.note)
                mw.MigakuChinese.finalizeReadings(splitList[1], field, self.note, self)
            return
    if not cmd.startswith('textToCReading'):     
        ogReroute(self, cmd)

ogReroute = aqt.editor.Editor.onBridgeCmd 
aqt.editor.Editor.onBridgeCmd = bridgeReroute