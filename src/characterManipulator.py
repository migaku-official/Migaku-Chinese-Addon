# -*- coding: utf-8 -*-
# 
import re




class CharacterManipulator():



	def __init__(self, mw):
		self.mw = mw
		self.pinyin_re = self.pinyinReSub()                  
		self.pinyin_two_re = re.compile("(?P<one>"+self.pinyin_re+")(?P<two>"+self.pinyin_re+")", flags=re.I)

	def pinyinReSub(self):
	    inits = u"zh|sh|ch|[bpmfdtnlgkhjqxrzscwy]"
	    finals = u"i[ōóǒòo]ng|[ūúǔùu]ng|[āáǎàa]ng|[ēéěèe]ng|i[āɑ̄áɑ́ɑ́ǎɑ̌àɑ̀aāáǎàa]ng|[īíǐìi]ng|i[āáǎàa]n|u[āáǎàa]n|[ōóǒòo]ng|[ēéěèe]r|i[āáǎàa]|i[ēéěèe]|i[āáǎàa]o|i[ūúǔùu]|[īíǐìi]n|u[āáǎàa]|u[ōóǒòo]|u[āáǎàa]i|u[īíǐìi]|[ūúǔùu]n|u[ēéěèe]|ü[ēéěèe]|v[ēéěèe]|i[ōóǒòo]|[āáǎàa]i|[ēéěèe]i|[āáǎàa]o|[ōóǒòo]u|[āáǎàa]n|[ēéěèe]n|[āáǎàa]|[ēéěèe]|[ōóǒòo]|[īíǐìi]|[ūúǔùu]|[ǖǘǚǜüv]"
	    standalones = u"'[āáǎàa]ng|'[ēéěèe]ng|'[ēéěèe]r|'[āáǎàa]i|'[ēéěèe]i|'[āáǎàa]o|'[ōóǒòo]u|'[āáǎàa]n|'[ēéěèe]n|'[āáǎàa]|'[ēéěèe]|'[ōóǒòo]"
	    return "(("+inits+")("+finals+")[1-5]?|("+standalones+")[1-5]?)"

	


	def separatePinyin(self, text, force=False, cantonese=False):   
	        def clean(t):
	            'remove leading apostrophe'
	            if "'" == t[0]:
	                return t[1:]
	            return t
	        def separate_pinyin_sub(p):
	            return clean(p.group("one"))+" "+clean(p.group("two"))
	        text =  self.pinyin_two_re.sub(separate_pinyin_sub, text)
	        return text