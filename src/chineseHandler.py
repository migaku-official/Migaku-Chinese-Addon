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
from aqt.utils import shortcut, saveGeom, saveSplitter
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
from .miutils import miInfo, miAsk
from .characterManipulator import CharacterManipulator


class ChineseHandler():

    def __init__(self, mw, path,  db, cssJSHandler):
        self.mw = mw 
        self.cssJSHandler = cssJSHandler
        self.path = path
        self.db = db
        self.manip = CharacterManipulator(mw)
        self.hanziRange = u'[\u4e00-\u9fff\u3400-\u4DBF\U00020000-\U0002A6DF\U0002A700-\U0002B73F\U0002B740-\U0002B81F\U0002B820-\U0002CEAF\U0002CEB0-\U0002EBEF\uF900-\uFAFF\U0002F800-\U0002FA1F]'
        self.commonJS = self.getCommonJS()
        self.insertHTMLJS = self.getInsertHTMLJS()
        self.insertToFieldJS = self.getInsertToFieldJS()
        self.fetchTextJS = self.getFetchTextJS()
        self.bracketsFromSelJS = self.getBracketFromSelJs()
        self.removeBracketsJS = self.getRemoveBracketJS()
        self.config = self.getConfig()
        self.toneToNumer =  {'ˊ':'2', 'ˇ':'3', 'ˋ':'4', '˙':'5'}
     

    def refreshConfig(self):
        self.config = self.getConfig()

    def getProgressWidget(self):
        progressWidget = QWidget(None)
        layout = QVBoxLayout()
        progressWidget.setFixedSize(400, 70)
        progressWidget.setWindowModality(Qt.ApplicationModal)
        progressWidget.setWindowIcon(QIcon(join(self.path, 'icons', 'migaku.png')))
        bar = QProgressBar(progressWidget)
        bar.setFixedSize(390, 50)
        bar.move(10,10)
        per = QLabel(bar)
        per.setAlignment(Qt.AlignCenter)
        progressWidget.show()
        return progressWidget, bar;


    def massGenerate(self, og, dest,  om, rt, notes, generateWidget):
        self.mw.checkpoint('Chinese Reading Generation')
        if not miAsk('Are you sure you want to generate from the "'+ og +'" field into  the "'+ dest +'" field?.'):
            return
        generateWidget.close() 
        progWid, bar = self.getProgressWidget()   
        bar.setMinimum(0)
        bar.setMaximum(len(notes))
        val = 0;  
        for nid in notes:
            note = mw.col.getNote(nid)
            fields = mw.col.models.fieldNames(note.model())
            if og in fields and dest in fields:

                text = note[og] 
                newText = self.finalizeReadings(text,note, og, rType = rt)
                note[dest] = self.applyOM(om, note[dest], newText)
                self.addVariants(self.removeBrackets(text), note)
                self.addSimpTrad(self.removeBrackets(text), note)
                note.flush()
            val+=1;
            bar.setValue(val)
            mw.app.processEvents()
        mw.progress.finish()
        mw.reset()


    def applyOM(self, addType, dest, text): ##overwrite mode/addtype
        if text:
            if addType == 'If Empty':
                if dest == '':
                    dest = text
            elif addType == 'Add':
                if dest == '':
                    dest = text
                else:
                    dest += '<br>' + text
            else:
                dest = text    
        return dest

    def massRemove(self, field,  notes, generateWidget):
        if not miAsk('####WARNING#####\nAre you sure you want to mass remove readings from the "'+ field +'" field? Please make sure you have selected the correct field as this will remove all "[" and "]" and text in between from a field.'):
                return
        generateWidget.close() 
        progWid, bar = self.getProgressWidget()   
        bar.setMinimum(0)
        bar.setMaximum(len(notes))
        val = 0;  
        for nid in notes:
            note = mw.col.getNote(nid)
            fields = mw.col.models.fieldNames(note.model())
            if field in fields:
                text = note[field] 
                text =  self.removeBrackets(text)

                note[field] = text
                note.flush()
            val+=1;
            bar.setValue(val)
            mw.app.processEvents()
        mw.progress.finish()
        mw.reset()


    def editorText(self, editor):    
        text = editor.web.selectedText()
        if not text:
            return False
        else:
            return text

    def cleanField(self, editor):
        if self.editorText(editor):
            editor.web.eval(self.commonJS + self.bracketsFromSelJS)
        else:
            editor.web.eval(self.commonJS + self.removeBracketsJS)

    def getBracketFromSelJs(self):
        bracketsFromSel = join(self.path, "js", "bracketsFromSel.js")
        with open(bracketsFromSel, "r") as bracketsFromSelFile:
            return bracketsFromSelFile.read()

    def getRemoveBracketJS(self):    
        removeBrackets = join(self.path, "js", "removeBrackets.js")
        with open(removeBrackets, "r") as removeBracketsFile:
            return removeBracketsFile.read()

    def getFetchTextJS(self):
        fetchText = join(self.path, "js", "fetchText.js")
        with open(fetchText, "r") as fetchTextFile:
            return fetchTextFile.read()  

    def addCReadings(self, editor):
        editor.web.eval(self.commonJS + self.fetchTextJS)

    def getCommonJS(self):
        common_utils_path = join(self.path, "js", "common.js")
        with open(common_utils_path, "r") as common_utils_file:
            return common_utils_file.read()

    def getInsertHTMLJS(self):
        insertHTML = join(self.path, "js", "insertHTML.js")
        with open(insertHTML, "r", encoding="utf-8") as insertHTMLFile:
            return insertHTMLFile.read() 

    def getInsertToFieldJS(self):
        insertHTML = join(self.path, "js", "insertHTMLToField.js")
        with open(insertHTML, "r", encoding="utf-8") as insertHTMLFile:
            return insertHTMLFile.read() 

    def getReadingType(self):
        config = self.getConfig()
        return config['ReadingType']

    def getConfig(self):
        return self.mw.addonManager.getConfig(__name__)

    def getAltReadingType(self, mName, fName):
        foundArray = []
        if mName in self.cssJSHandler.wrapperDict: 
            for entries in self.cssJSHandler.wrapperDict[mName]:
                if entries[1] == fName and entries[4] != 'default':
                    return entries[4]
        return False

    def bopoToneToNumber(self, text):
        if self.config['BopomofoTonesToNumber']:
            last = text[-1:]
            if last in self.toneToNumer:
                text = text[:-1] + self.toneToNumer[last]
            else:
                text += '1'
        return text

    def finalizeReadings(self, text, field, note, editor = False, rType = False):
        if text == '':
            return
        if note:
            if not rType:
                altType = self.getAltReadingType(note.model()['name'], field)
                if altType:
                    rType = altType
                else:
                    rType = self.getReadingType()
                if rType not in ['pinyin','bopomofo','jyutping']:
                    return
            text = self.removeBrackets(text)
            finished = False
            newStr = ''
            count = 0
            while not finished:
                word = ''
                if re.search(self.hanziRange , text[count]):
                    word += text[count]
                    lookahead = 10
                    limit = count + lookahead
                    count+= 1

                    while count < len(text) and count < limit and re.search(self.hanziRange , text[count]):
                        word += text[count]
                        
                        count += 1
                    result = False
                    while not result and len(word) > 0:
                        if rType == 'jyutping':
                            result = self.db.getJyutping(word)
                        else:
                            result = self.db.getAltFayin(word)
                        if not result:
                            count -= 1
                            word = word[:-1]
            
                    if result:
                        if rType == 'jyutping':
                            results = result[0][0].split(" ")
                        else:
                            results = self.manip.separatePinyin(result[0][0]).split(" ")
                            for idx, fayin in enumerate(results):
                                if rType == 'bopomofo':
                                    results[idx] = self.bopoToneToNumber(transcriptions.pinyin_to_zhuyin(fayin))
                        newStr +=  word + '[' + ' '.join(results).lower() + ']' 
                    else:
                        newStr += text[count]
                        count += 1
                        ###importantcheck if word not found look for char pinyin or jyutping
                else:
                    newStr += text[count]
                    count += 1
                if count == len(text):
                    finished = True
            if editor:
                editor.web.eval(self.commonJS +  self.insertHTMLJS % newStr.replace('"', '\\"'))
                # note[field] = newStr
                self.addVariants(text, note, editor)
                self.addSimpTrad(text, note, editor)
            else:
                return newStr

    def fetchParsed(self, text, field, note, rType = False):
        if text == '':
            return ''
        if not rType:
            altType = self.getAltReadingType(note.model()['name'], field)
            if altType:
                rType = altType
            else:
                rType = self.getReadingType()
        if rType not in ['pinyin','bopomofo','jyutping']:
            return text
        text = self.removeBrackets(text)
        finished = False
        newStr = ''
        count = 0
        while not finished:
            word = ''
            if re.search(self.hanziRange , text[count]):
                word += text[count]
                lookahead = 10
                limit = count + lookahead
                count+= 1

                while count < len(text) and count < limit and re.search(self.hanziRange , text[count]):
                    word += text[count]
                    
                    count += 1
                result = False
                while not result and len(word) > 0:
                    if rType == 'jyutping':
                        result = self.db.getJyutping(word)
                    else:
                        result = self.db.getAltFayin(word)
                    if not result:
                        count -= 1
                        word = word[:-1]
        
                if result:
                    if rType == 'jyutping':
                        results = result[0][0].split(" ")
                    else:
                        results = self.manip.separatePinyin(result[0][0]).split(" ")
                        for idx, fayin in enumerate(results):
                            if rType == 'bopomofo':
                                results[idx] = self.bopoToneToNumber(transcriptions.pinyin_to_zhuyin(fayin))
                    newStr +=  word + '[' + ' '.join(results).lower() + ']' 
                else:
                    newStr += text[count]
                    count += 1
            else:
                newStr += text[count]
                count += 1
            if count == len(text):
                finished = True
        self.addVariants(text, note)
        self.addSimpTrad(text, note)
        return newStr
            
    def addVariants(self, text, note, editor = False):
        config = self.getConfig()
        fields = self.mw.col.models.fieldNames(note.model())
        for variant in ['SimplifiedField', 'TraditionalField']:
            varAr = config[variant].split(';')
            selFields = varAr[0].split(',')
            for selField in selFields:
                if selField.lower() == 'none':
                    continue
                if selField in fields:
                    ordinal = False
                    if editor:
                        ordinal = self.getFieldOrdinal(note, selField)
                    if variant == 'SimplifiedField':
                        text = self.db.get_simplified(self.removeBrackets(text))
                    elif variant == 'TraditionalField':
                        text = self.db.get_traditional(self.removeBrackets(text))
                    if not text:
                        return
                    if varAr[1] == 'overwrite':
                        self.addToNote(editor, note, selField, ordinal, text)
                    elif varAr[1] == 'add':
                        separator = '<br>'
                        if len(varAr) == 3:
                            separator = varAr[2]
                        if note[selField] == '' or editor:
                            self.addToNote(editor, note, selField, ordinal, note[selField] + separator.replace('<br>', '', 1) + text)
                        else:
                            self.addToNote(editor, note, selField, ordinal, note[selField] + separator + text)
                    elif varAr[1] == 'no':
                        if note[selField] == '':
                            self.addToNote(editor, note, selField, ordinal, text)

    def getSimpTradString(self, fText, varAr, text, simplified, traditional):
        sSame = False
        tSame = False
        separator = '<br>'
        if len(varAr) == 3:
            separator = varAr[2]
        if text == simplified:
            sSame = True
        if text == traditional:
            tSame = True
        if tSame and sSame:
            return ''
        if varAr[1] == 'overwrite' or varAr[1] == 'no':
            if varAr[1] == 'no' and fText != '':
                return fText
            if not sSame and not tSame:
                return simplified + separator + traditional
            elif not sSame and tSame:
                return simplified
            elif not tSame and sSame:  
                return traditional
        elif varAr[1] == 'add':
            sep2 = separator
            if fText == '':
               sep2 = sep2.replace('<br>', '', 1)
               separator = separator.replace('<br>', '', 1)
            if len(varAr) == 4:
                separator = varAr[3]
            if not sSame and not tSame:
                return fText + separator + simplified + sep2 + traditional
            elif not sSame and tSame:
                return fText + separator + simplified
            elif not tSame and sSame:  
                return fText + sep2 + traditional  

    def addSimpTrad(self, text, note, editor = False):
        config = self.getConfig()
        varAr = config['SimpTradField'].split(';')
        fields = self.mw.col.models.fieldNames(note.model())
        altFields = varAr[0].split(',')
        for altField in altFields:
            if altField.lower() == 'none':
                return
            if altField in fields:
                ordinal = False
                if editor:
                    ordinal = self.getFieldOrdinal(note, altField)
                simplified = self.db.get_simplified(self.removeBrackets(text))
                traditional = self.db.get_traditional(self.removeBrackets(text))
                newStr = ''
                self.addToNote(editor, note, altField, ordinal, self.getSimpTradString(note[altField], varAr, text, simplified, traditional))

    def getFieldOrdinal(self, note, field):
        fields = note._model["flds"]
        for f in fields:
            if field == f['name']:
                return f['ord']
        else:
            return False
        

    def addToNote(self, editor, note, field, ordinal, text):
        if ordinal is not False and editor is not False:
            editor.web.eval(self.commonJS + self.insertToFieldJS % (text.replace('"', '\\"'), str(ordinal)))
        else:
            note[field] = text

    def reloadEditor(self):
        browser = aqt.DialogManager._dialogs["Browser"][1]
        if browser:
            self.mw.progress.timer(100, browser.editor.loadNoteKeepingFocus, False)
        adder = aqt.DialogManager._dialogs["AddCards"][1]
        if adder:
            self.mw.progress.timer(100, adder.editor.loadNoteKeepingFocus, False)
        editCurrent = aqt.DialogManager._dialogs["EditCurrent"][1]
        if editCurrent:
            self.mw.progress.timer(100, editCurrent.editor.loadNoteKeepingFocus, False)


    def htmlRemove(self, text):
        pattern = r"(?:<[^<]+?>)"
        finds = re.findall(pattern, text)
        text = re.sub(r"<[^<]+?>", "--=HTML=--", text)
        return finds,text;

    def replaceHTML(self, text, matches):
        if matches:
            for match in matches:
                text = text.replace("--=HTML=--", match, 1)
        return text

    def cleanSpaces(self, text):
        return text.replace('  ', '')
        
    def removeBrackets(self, text, returnSounds = False, removeAudio = False):
        if '[' not in text and ']' not in text:
            if returnSounds:
                return text, [];
            return text
        matches, text = self.htmlRemove(text)
        if removeAudio:
            text = self.cleanSpaces(text)
            text = self.replaceHTML(text, matches)
            return re.sub(r'\[[^]]*?\]', '', text)
        else:
            pattern = r"(?:\[sound:[^\]]+?\])|(?:\[\d*\])"
            finds = re.findall(pattern, text)

            text = re.sub(r"(?:\[sound:[^\]]+?\])|(?:\[\d*\])", "-_-AUDIO-_-", text)
            text  = re.sub(r'\[[^]]*?\]', '', text)
            text = self.cleanSpaces(text)
            text = self.replaceHTML(text, matches)
            if returnSounds:
                return text, finds;
            for match in finds:
                text = text.replace("-_-AUDIO-_-", match, 1)
            return text

