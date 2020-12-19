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


class CSSJSHandler():

    def __init__(self, mw, path):
        self.mw = mw
        self.path = path
        self.wrapperDict = False
        self.chineseParserHeader = '<!--###MIGAKU CHINESE SUPPORT JS START###\nDo Not Edit If Using Automatic CSS and JS Management-->'
        self.chineseParserFooter = '<!--###MIGAKU CHINESE SUPPORT JS ENDS###-->' 
        self.chineseCSSHeader = '/*###MIGAKU CHINESE SUPPORT CSS STARTS###\nDo Not Edit If Using Automatic CSS and JS Management*/'
        self.chineseCSSFooter = '/*###MIGAKU CHINESE SUPPORT CSS ENDS###*/'  
        self.chineseCSSPattern = '\/\*###MIGAKU CHINESE SUPPORT CSS STARTS###\nDo Not Edit If Using Automatic CSS and JS Management\*\/[^*]*?\/\*###MIGAKU CHINESE SUPPORT CSS ENDS###\*\/'
        self.hanziConverterHeader = '<!--###MIGAKU CHINESE SUPPORT CONVERTER JS START###\nDo Not Edit If Using Automatic CSS and JS Management-->'
        self.hanziConverterFooter = '<!--###MIGAKU CHINESE SUPPORT CONVERTER JS ENDS###-->'
        self.pinBopoConverterHeader = '<!--###MIGAKU PINYIN BOPOMOFO CONVERTER JS START###\nDo Not Edit If Using Automatic CSS and JS Management-->'
        self.pinBopoConverterFooter = '<!--###MIGAKU PINYIN BOPOMOFO CONVERTER JS ENDS###-->'
        self.tongwen_coreJS = self.getCoreJS()
        self.tongwen_table_ps2tJS = self.gettongwen_table_ps2tJS()
        self.tongwen_table_pt2sJS = self.gettongwen_table_pt2sJS()
        self.tongwen_table_s2tJS = self.gettongwen_table_s2tJS()
        self.tongwen_table_ss2tJS = self.gettongwen_table_ss2tJS()
        self.tongwen_table_st2sJS = self.gettongwen_table_st2sJS()
        self.tongwen_table_t2sJS = self.gettongwen_table_t2sJS()
        self.chineseParserJS = self.getCParser()
        self.toPinyinJS = self.getToPinyinJS()
        self.toBopoJS = self.getToBopoJS()

    def updateWrapperDict(self):
        self.wrapperDict, wrapperCheck = self.getWrapperDict()
    
    def getToPinyinJS(self):
        toPinyin = join(self.path, "js", "bopoToPinyin.js")
        with open(toPinyin, "r", encoding="utf-8") as toPinyinFile:
            return toPinyinFile.read()


    def getToBopoJS(self):
        toBopo = join(self.path, "js", "pinyinToBopo.js")
        with open(toBopo, "r", encoding="utf-8") as toBopoFile:
            return toBopoFile.read()

    def getCParser(self):
        chineseParser = join(self.path, "js", "chineseparser.js")
        with open(chineseParser, "r", encoding="utf-8") as chineseParserFile:
            return chineseParserFile.read() 


    def getCoreJS(self):
        tongwen_core = join(self.path, "js", "tongwen_core.js")
        with open(tongwen_core, "r", encoding="utf-8") as tongwen_coreFile:
            return tongwen_coreFile.read()

    def gettongwen_table_ps2tJS(self):
        tongwen_table_ps2t = join(self.path, "js", "tongwen_table_ps2t.js")
        with open(tongwen_table_ps2t, "r", encoding="utf-8") as tongwen_table_ps2tFile:
            return tongwen_table_ps2tFile.read()

    def gettongwen_table_pt2sJS(self):
        tongwen_table_pt2s = join(self.path, "js", "tongwen_table_pt2s.js")
        with open(tongwen_table_pt2s, "r", encoding="utf-8") as tongwen_table_pt2sFile:
            return tongwen_table_pt2sFile.read()

    def gettongwen_table_s2tJS(self):
        tongwen_table_s2t = join(self.path, "js", "tongwen_table_s2t.js")
        with open(tongwen_table_s2t, "r", encoding="utf-8") as tongwen_table_s2tFile:
            return tongwen_table_s2tFile.read()

    def gettongwen_table_ss2tJS(self):
        tongwen_table_ss2t = join(self.path, "js", "tongwen_table_ss2t.js")
        with open(tongwen_table_ss2t, "r", encoding="utf-8") as tongwen_table_ss2tFile:
            return tongwen_table_ss2tFile.read()

    def gettongwen_table_st2sJS(self):
        tongwen_table_st2s = join(self.path, "js", "tongwen_table_st2s.js")
        with open(tongwen_table_st2s, "r", encoding="utf-8") as tongwen_table_st2sFile:
            return tongwen_table_st2sFile.read()

    def gettongwen_table_t2sJS(self):
        tongwen_table_t2s = join(self.path, "js", "tongwen_table_t2s.js")
        with open(tongwen_table_t2s, "r", encoding="utf-8") as tongwen_table_t2sFile:
            return tongwen_table_t2sFile.read()

    def getConfig(self):
        return self.mw.addonManager.getConfig(__name__)

    
    def noteCardFieldExists(self, data):
        models = self.mw.col.models.all()
        error = ''
        note = False
        card = False
        field = False
        side = False
        if data[5] in ['both', 'front', 'back']:
            side = True
        for model in models:
            if model['name'] == data[2] and not note:
                note = True
                for t in model['tmpls']:
                    if t['name'] == data[3] and not card:
                        card = True
                for fld in model['flds']:
                    if fld['name'] == data[4] and not field:
                        field = True 
        if not note:
            return False, 'The "'+ data[2] +'" note type does not exist in this profile, if this note type exists in another profile consider setting its profile setting to the appropriate profile in the Active Fields settings menu.';
        
        if not card:
            error += 'The "'+ data[3] +'" card type does not exist.\n'
        if not field:
            error += 'The "'+ data[4] +'" field does not exist.\n'
        if not side:
            error += 'The last value must be "front", "back", or "both", it cannot be "' + data[5] + '"'

        if error == '':
            return True, False;
        return False, error;


    def fieldConflictCheck(self, item, array, dType):
        conflicts = []
        for value in array:
            valAr = value[0]
            valDType = value[1]
            if valAr == item:
                conflicts.append('In "'+ valDType +'": ' + ';'.join(valAr))
                conflicts.append('In "'+ dType +'": ' + ';'.join(item))
                return False, conflicts;
            elif valAr[2] == item[2] and valAr[3] == item[3] and valAr[4] == item[4] and (valAr[5]  == 'both' or item[5] == 'both'):
                conflicts.append('In "'+ valDType +'": ' + ';'.join(valAr))
                conflicts.append('In "'+ dType +'": ' + ';'.join(item))
                return False, conflicts;
        return True, True; 


    def getWrapperDict(self):
        wrapperDict = {}
        displayOptions = ['hover', 'coloredhover','hanzi','coloredhanzi','reading','coloredreading','hanzireading','coloredhanzireading']
        models = self.mw.col.models.all()
        syntaxErrors = ''
        notFoundErrors = ''
        fieldConflictErrors = ''
        displayTypeError = ''
        alreadyIncluded = []
        for item in self.config['ActiveFields']:
            dataArray = item.split(";")
            displayOption = dataArray[0]
            if (len(dataArray) != 6 and len(dataArray) != 7) or  '' in dataArray:
                syntaxErrors += '\n"' + item + '" in "' + displayOption + '"\n'
            elif displayOption.lower() not in displayOptions:
                displayTypeError += '\n"' + item + '" in "ActiveFields" has an incorrect display type of "'+ displayOption +'"\n'
            else:
                if self.mw.pm.name != dataArray[1] and 'all' != dataArray[1].lower():
                    continue
                if len(dataArray) == 7:

                    if dataArray[6].lower() not in ['pinyin','bopomofo','jyutping']:
                        syntaxErrors += '\n"' + item + '" in "ActiveFields"\nThe value "' + dataArray[6] + '" is not valid. The "ReadingType" value must be either "pinyin", "bopomofo", or "jyutping". The default value has been applied.'
                        dataArray[6] = 'default'
                else :
                    dataArray.append('default')
                if dataArray[2] != 'noteTypeName' and dataArray[3] != 'cardTypeName' and dataArray[4] != 'fieldName':
                    success, errorMsg = self.noteCardFieldExists(dataArray)
                    if success:
                        conflictFree,  conflicts = self.fieldConflictCheck(dataArray, alreadyIncluded, displayOption)
                        if conflictFree:
                            if dataArray[2] not in wrapperDict:
                                alreadyIncluded.append([dataArray, displayOption])
                                wrapperDict[dataArray[2]] = [[dataArray[3], dataArray[4], dataArray[5],displayOption, dataArray[6]]]
                            else:
                                if [dataArray[3], dataArray[4], dataArray[5],displayOption, dataArray[6]] not in wrapperDict[dataArray[2]]:
                                    alreadyIncluded.append([dataArray, displayOption])
                                    wrapperDict[dataArray[2]].append([dataArray[3], dataArray[4], dataArray[5],displayOption, dataArray[6]])
                        else:
                            fieldConflictErrors += 'A conflict was found in this field pair:\n\n' + '\n'.join(conflicts) + '\n\n'
                    else:
                            notFoundErrors += '"' + item + '" in "ActiveFields" has the following error(s):\n' + errorMsg + '\n\n'

        if syntaxErrors != '':
            miInfo('The following entries have incorrect syntax:\nPlease make sure the format is as follows:\n"displayType;profileName;noteTypeName;cardTypeName;fieldName;side(;ReadingType)".\n' + syntaxErrors, level="err")
            return (wrapperDict,False);
        if displayTypeError != '':
            miInfo('The following entries have an incorrect display type. Valid display types are "Hover", "ColoredHover", "Hanzi", "ColoredHanzi", "HanziReading", "ColoredHanziReading", "Reading", and "ColoredReading".\n' + syntaxErrors, level="err")
            return (wrapperDict,False);
        if notFoundErrors != '':
            miInfo('The following entries have incorrect values that are not found in your Anki collection. Please review these entries and fix any spelling mistakes.\n\n' + notFoundErrors, level="err")
            return (wrapperDict,False);
        if fieldConflictErrors != '':
            miInfo('You have entries that point to the same field and the same side. Please make sure that a field and side combination does not conflict.\n\n' + fieldConflictErrors, level="err")
            return (wrapperDict,False);
        return (wrapperDict, True);


    def checkProfile(self):
        if self.mw.pm.name in self.config['Profiles'] or ('all' in self.config['Profiles'] or 'All' in self.config['Profiles']):
            return True
        return False

    def injectWrapperElements(self):
        self.config = self.getConfig()
        if not self.checkProfile():
            return
        if not self.config["AutoCssJsGeneration"]:
            return
        variantCheck = self.checkVariantSyntax()
        stCheck = self.checkSimpTradSyntax()
        readingCheck = self.checkReadingType()
        self.wrapperDict, wrapperCheck = self.getWrapperDict();      
        models = self.mw.col.models.all()
        for model in models:
            if model['name'] in self.wrapperDict:
                model['css'] = self.editChineseCss(model['css'])
                for idx, t in enumerate(model['tmpls']):
                    modelDict = self.wrapperDict[model['name']]
                    t = self.injectChineseConverterToTemplate(t)
                    if self.templateInModelDict(t['name'], modelDict):
                        templateDict = self.templateFilteredDict(modelDict, t['name'])
                        t['qfmt'], t['afmt'] = self.cleanFieldWrappers(t['qfmt'], t['afmt'], model['flds'], templateDict)
                        for data in templateDict: 
                            if data[2] == 'both' or data[2] == 'front':                              
                                t['qfmt'] =  self.overwriteWrapperElement(t['qfmt'], data[1], data[3], data[4])
                                t['qfmt'] =  self.injectWrapperElement(t['qfmt'], data[1], data[3], data[4])
                                t['qfmt'] = self.editChineseJs(t['qfmt'])
                            if data[2] == 'both' or data[2] == 'back':          
                                t['afmt'] = self.overwriteWrapperElement(t['afmt'], data[1], data[3], data[4])
                                t['afmt'] = self.injectWrapperElement(t['afmt'], data[1], data[3], data[4])
                                t['afmt'] = self.editChineseJs(t['afmt'])
                    else:
                        t['qfmt'] = self.removeWrappers(t['qfmt'])
                        t['afmt'] = self.removeWrappers(t['afmt'])
                         
                        
            else:
                model['css'] = self.removeChineseCss(model['css'])
                for t in model['tmpls']:
                    t = self.removeChineseConverterFromTemplate(t)
                    t['qfmt'] = self.removeChineseJs(self.removeWrappers(t['qfmt']))
                    t['afmt'] = self.removeChineseJs(self.removeWrappers(t['afmt']))   
        self.mw.col.models.save()
        self.mw.col.models.flush()
        return variantCheck and stCheck and readingCheck and wrapperCheck 

    def fieldExists(self, field):
        models = self.mw.col.models.all()
        for model in models:
            for fld in model['flds']:
                if field == fld['name'] or field.lower() == 'none':
                    return True
        return False

    def checkVariantSyntax(self):
        syntaxErrors = ''
        for variant in ['SimplifiedField', 'TraditionalField']:
            varAr = self.config[variant].split(';')
            if len(varAr) not in [2,3] or (len(varAr) == 3 and varAr[1].lower() != 'add'):
                syntaxErrors += '\nThe "' + variant + '" configuration "'+ self.config[variant] +'" is incorrect. The syntax is invalid.'
            else:
                selFields = varAr[0].split(',')
                for selField in selFields:
                    if not self.fieldExists(selField):
                        syntaxErrors += '\nThe "' + variant + '" configuration "'+ self.config[variant] +'" is incorrect. At least one of the specified fields does not exist in your collection.'
                        break   
                if varAr[1].lower() not in ['overwrite', 'add', 'no']:
                    syntaxErrors += '\nThe "' + variant + '" configuration "'+ self.config[variant] +'" is incorrect. Please ensure that second value is either "overwrite", "add", or "no".'    
        if syntaxErrors != '':
            miInfo('Please make sure the syntax is as follows "field;type(;separator)".Remember that only when using "add" can you specify a separator value. The syntax is incorrect for the following entries:' + syntaxErrors, level="err")
            return False
        return True

    def checkSimpTradSyntax(self):
        syntaxErrors = ''
        simpTrad = self.config['SimpTradField']
        varAr = simpTrad.split(';')
        if len(varAr) not in [2,3,4] or (len(varAr) == 4 and varAr[1].lower() != 'add'):
            syntaxErrors += '\nThe "SimpTradField" configuration "'+ simpTrad +'" is incorrect. The syntax is invalid.'
        else:
            altFields = varAr[0].split(',')
            for altField in altFields:
                if not self.fieldExists(altField):
                    syntaxErrors += '\nThe "SimpTradField" configuration "'+ simpTrad +'" is incorrect. At least one of the specified fields does not exist in your collection.'    
                    break
            if varAr[1].lower() not in ['overwrite', 'add', 'no']:
                syntaxErrors += '\nThe "SimpTradField" configuration "'+ simpTrad +'" is incorrect. Please ensure that second value is either "overwrite", "add", or "no".'    
        if syntaxErrors != '':
            miInfo('Please make sure the syntax is as follows "field;type(;separator(;separator))". Remember that only when using "add" as the type can you specify 2 separator values. The syntax is incorrect for the following entries:' + syntaxErrors, level="err")
            return False
        return True

    def checkReadingType(self):
        rType = self.config['ReadingType']
        if rType not in ['pinyin','bopomofo','jyutping']:
            miInfo('The "'+ rType +'" value in the "ReadingType" configuration is incorrect. The value must be "pinyin", "bopomofo", or "jyutping".', level="err")
            return False
        return True

    def removeHanziConverterJs(self, text):
        
        return re.sub(self.hanziConverterHeader + r'.*?' + self.hanziConverterFooter, '', text)
    
    def newLineReduce(self, text):
        return re.sub(r'\n{3,}', '\n\n', text)
    
    def getHanziConverterJs(self, conversionType):
        js = '<script>const CHINESE_CONVERSION_TYPE ="' + conversionType.lower() + '";' + self.tongwen_coreJS + self.tongwen_table_ps2tJS + self.tongwen_table_pt2sJS + self.tongwen_table_s2tJS + self.tongwen_table_ss2tJS + self.tongwen_table_st2sJS + self.tongwen_table_t2sJS + '"simplified"===CHINESE_CONVERSION_TYPE?TongWen.trans2Simp(document):"traditional"===CHINESE_CONVERSION_TYPE&&TongWen.trans2Trad(document);</script>'
        return self.hanziConverterHeader + js + self.hanziConverterFooter

    def getRubyFontSize(self):
        return '.pinyin-ruby{font-size:' + str(self.config['FontSize']) + '% !important;}';

    def getChineseCss(self):
        toneColors = self.config['MandarinTones12345'];
        css = '.nightMode .unhovered-word .hanzi-ruby{color:white !important;}.unhovered-word .hanzi-ruby{color:inherit !important;}.unhovered-word .pinyin-ruby{visibility:hidden  !important;}' + self.getRubyFontSize();
        count = 1;
        for toneColor in toneColors:
            css += '.tone%s{color:%s;}.ankidroid_dark_mode .tone%s, .nightMode .tone%s{color:%s;}'%(str(count),toneColor, str(count),str(count),toneColor)
            count += 1
        toneColors = self.config['CantoneseTones123456'];
        count = 1;
        for toneColor in toneColors:
            css += '.canTone%s{color:%s;}.ankidroid_dark_mode .canTone%s, .nightMode .cantone%s{color:%s;}'%(str(count),toneColor,str(count),str(count),toneColor)
            count += 1
        return self.chineseCSSHeader + '\n' + css + '\n' + self.chineseCSSFooter


    def editChineseCss(self, css):
        pattern = self.chineseCSSPattern
        chineseCss = self.getChineseCss()
        if not css:
            return chineseCss
        match = re.search(pattern, css)
        if match:
            if match.group() != chineseCss:
                return css.replace(match.group(), chineseCss)
            else:
                return css
        else:
            return css + '\n' + chineseCss

    def templateInModelDict(self, template, modelDict):
        for entries in modelDict:
            if entries[0] == template:
                return True
        return False     

    def templateFilteredDict(self, modelDict, template):
        return list(filter(lambda data, tname = template: data[0] == tname, modelDict))

    def fieldInTemplateDict(self, field, templateDict):
        sides = []
        for entries in templateDict:
            if entries[1] == field:
                sides.append(entries[2])
        return sides   

    def removeChineseJs(self, text):
        return re.sub(self.chineseParserHeader + r'.*?' + self.chineseParserFooter, '', text)

    def cleanFieldWrappers(self, front, back, fields, templateDict):
        for field in fields:
            sides = self.fieldInTemplateDict(field['name'], templateDict)

            
            if len(sides) > 0:
                pattern = r'<div reading-type="[^>]+?" display-type="[^>]+?" class="wrapped-chinese">({{'+ field['name'] +'}})</div>'
                if 'both' not in sides or 'front' not in sides:
                    front = re.sub(pattern, '{{'+ field['name'] +'}}', front)
                    front = self.removeChineseJs(front)
                if 'both' not in sides or 'back' not in sides:
                    back = re.sub(pattern, '{{'+ field['name'] +'}}', back)
                    back = self.removeChineseJs(back)
            else:
                pattern = r'<div reading-type="[^>]+?" display-type="[^>]+?" class="wrapped-chinese">({{'+ field['name'] +'}})</div>'
                front = re.sub(pattern, '{{'+ field['name'] +'}}', front)
                back = re.sub(pattern, '{{'+ field['name'] +'}}', back)
                front = self.removeChineseJs(front)
                back = self.removeChineseJs(back)
        return front, back;


    def overwriteWrapperElement(self, text, field, dType, rType = 'default'):
        pattern = r'<div reading-type="([^>]+?)" display-type="([^>]+?)" class="wrapped-chinese">{{'+ field + r'}}</div>'
        finds = re.findall(pattern, text)

        if len(finds) > 0:
            for find in finds:
                if dType.lower() != find[1].lower() or rType.lower() != find[0].lower():
                    toReplace = '<div reading-type="'+ find[0] + '" display-type="'+ find[1] + '" class="wrapped-chinese">{{'+ field + r'}}</div>'
                    replaceWith = '<div reading-type="'+ rType +'" display-type="'+ dType +'" class="wrapped-chinese">{{'+ field + r'}}</div>'
                    text = text.replace(toReplace, replaceWith)
             
        return text

    def injectWrapperElement(self, text, field, dType, rType = 'default'):
        pattern = r'(?<!(?:class="wrapped-chinese">))({{'+ field + r'}})'
        replaceWith = '<div reading-type="'+ rType +'" display-type="'+ dType +'" class="wrapped-chinese">{{'+ field + '}}</div>'
        text = re.sub(pattern, replaceWith,text)  
        return text

    def getReadingType(self):
        return self.config['ReadingType']

    def getChineseJs(self):
        js = '<script>(function(){const CHINESE_READING_TYPE ="' + self.getReadingType() + '";' + self.chineseParserJS + '})();</script>'
        return self.chineseParserHeader + js + self.chineseParserFooter

    def editChineseJs(self, text):
        pattern = self.chineseParserHeader + r'.*?' + self.chineseParserFooter
        chineseJS = self.getChineseJs()
        if not text:
            return chineseJS
        match = re.search(pattern, text)
        if match:
            if match.group() != chineseJS:
                return self.newLineReduce(re.sub(match.group, chineseJS, text))
            else:
                return text
        else:
            return self.newLineReduce(text + '\n' + chineseJS)
        return

    def removeWrappers(self, text):
        pattern = r'<div reading-type="[^>]+?" display-type="[^>]+?" class="wrapped-chinese">({{[^}]+?}})</div>'
        text = re.sub(pattern, r'\1', text)
        return text

    def removeChineseCss(self, css):
        return re.sub(self.chineseCSSPattern, '', css)


    def injectChineseConverterToTemplate(self, t):
        hc = self.config['hanziConversion']
        rc = self.config['readingConversion']
        if hc == 'None' and rc == 'None' :
            t['qfmt'] = self.removeHanziConverterJs(t['qfmt'])
            t['afmt'] = self.removeHanziConverterJs(t['afmt'])
            t['qfmt'] = self.removePinBopoConverterJs(t['qfmt'])
            t['afmt'] = self.removePinBopoConverterJs(t['afmt']) 
        elif hc not in ['Traditional', 'Simplified'] or hc == 'None':
            t['qfmt'] = self.removeHanziConverterJs(t['qfmt'])
            t['afmt'] = self.removeHanziConverterJs(t['afmt'])
        else:
            t['qfmt'] = self.newLineReduce(self.removeHanziConverterJs(t['qfmt']) + '\n\n' + self.getHanziConverterJs(hc))
            t['afmt'] = self.newLineReduce(self.removeHanziConverterJs(t['afmt']) + '\n\n' + self.getHanziConverterJs(hc))
        if rc == 'None' or rc not in ['Pinyin', 'Bopomofo']:
            t['qfmt'] = self.removePinBopoConverterJs(t['qfmt'])
            t['afmt'] = self.removePinBopoConverterJs(t['afmt'])
        else:
            t['qfmt'] = self.applyPinBopoConverterJS(rc, t['qfmt'])
            t['afmt'] = self.applyPinBopoConverterJS(rc, t['afmt'])
        return t 
    

    def applyPinBopoConverterJS(self, rc, text):
        text = self.removePinBopoConverterJs(text)
        if self.chineseParserHeader in text:
            text = text.replace(self.chineseParserHeader, self.getPinBopoConverterJs(rc) + '\n\n' + self.chineseParserHeader)
        else:
            text = self.newLineReduce(text) + '\n\n' + self.getPinBopoConverterJs(rc)
        return text

    def getPinBopoConverterJs(self, rc):
        if rc == 'Pinyin':
            js = self.toPinyinJS
        else:
            js = self.toBopoJS
        return self.pinBopoConverterHeader + '<script>' + js + '</script>' + self.pinBopoConverterFooter


    def removePinBopoConverterJs(self, text):
        return re.sub(self.pinBopoConverterHeader + r'.*?<\/script>' + self.pinBopoConverterFooter, '', text)


    def removeChineseConverterFromTemplate(self, t):
        t['qfmt'] = self.removeHanziConverterJs(t['qfmt'])
        t['afmt'] = self.removeHanziConverterJs(t['afmt'])  
        t['qfmt'] = self.removePinBopoConverterJs(t['qfmt'])
        t['afmt'] = self.removePinBopoConverterJs(t['afmt'])
        return t  

