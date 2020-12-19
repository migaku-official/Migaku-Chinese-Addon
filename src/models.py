from aqt import mw
from anki.stdmodels import models
from anki.hooks import addHook
import os
from os.path import dirname, join
from shutil import copyfile

class MIChineseModels():
    def __init__(self, mw):
        self.mw = mw
        self.modelList = self.getModelList()
        self.style ="""
.card {
 font-size: 23px;
 text-align: left;
 color: black;
 background-color: #FFFAF0;
 margin: 20px auto 20px auto;
 padding: 0 20px 0 20px;
 max-width: 600px; 
}

@font-face { font-family: simsun; src: url('_simsun.ttf'); }
@font-face { font-family: times; src: url('_times.ttf'); }

.dai {
    font-size: 40px;
    font-family: "times", "simsun";
}

.chu {
    font-size: 24px;
    font-family: "times", "simsun";
    display: inline-block;
}
        """

    def getModelList(self):
        modelList = []
        name = 'Migaku Chinese (ZH)'
        fields = ['Expression',  'Meaning', 'Traditional', 'Audio', 'Audio on Front']
        front = '''
{{^Audio on Front}}<span class="dai">{{Expression}}</span>{{/Audio on Front}}
{{#Audio on Front}}{{#Audio}}{{Audio}}{{/Audio}}{{/Audio on Front}}
{{#Audio on Front}}{{^Audio}}<span class="dai">{{Expression}}</span>{{/Audio}}{{/Audio on Front}}
        '''
        backTemplate = '''
{{#Audio on Front}}{{Audio}}<hr>{{/Audio on Front}}
<span class="dai">{{Expression}}</span>
{{^Audio on Front}}<hr>{{/Audio on Front}}
{{#Audio on Front}}<br><br>{{/Audio on Front}}
<span class="chu">{{Meaning}}</span><br><br>
<span class="chu">{{%s}}</span><br>
{{^Audio on Front}}{{Audio}}{{/Audio on Front}}
        '''
        back = backTemplate%'Traditional'
        modelList.append([name, fields, front, back])

        name = 'Migaku Chinese (TW)'
        fields = ['Expression',  'Meaning', 'Simplified', 'Audio', 'Audio on Front']
        back = back = backTemplate%'Simplified'
        modelList.append([name, fields, front, back])

        name = 'Migaku Chinese (HK)'
        modelList.append([name, fields, front, back])
        return modelList


    def addModels(self):
        config = self.mw.addonManager.getConfig(__name__)
        for model in self.modelList:
            if model[0] == 'Migaku Chinese (ZH)' and config['addSimpNote']:
                self.addModel(model)
            elif model[0] == 'Migaku Chinese (TW)' and config['addTradNote']:
                self.addModel(model)
            elif model[0] == 'Migaku Chinese (HK)' and config['addCantoNote']:
                self.addModel(model)
            

    def addModel(self, model):
        if not self.mw.col.models.byName(model[0]):
            modelManager = self.mw.col.models
            newModel = modelManager.new(model[0])
            for fieldName in model[1]:
                field = modelManager.newField(fieldName)
                modelManager.addField(newModel, field)
            template = modelManager.newTemplate('Reading')
            template['qfmt'] = model[2]
            template['afmt'] = model[3]
            newModel['css'] = self.style
            modelManager.addTemplate(newModel, template)
            modelManager.add(newModel)
            self.moveFontToMediaDir('_times.ttf')
            self.moveFontToMediaDir('_simsun.ttf')

    def moveFontToMediaDir(self, filename):
        src = join(dirname(__file__), filename)
        if os.path.exists(src): 
            path = join(mw.col.media.dir(), filename)
            if not os.path.exists(path): 
                copyfile(src, path)
            return True
        else:
            return False
    