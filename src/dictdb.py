# -*- coding: utf-8 -*-
#


import sqlite3
import os.path

addon_path = os.path.dirname(__file__)

class DictDB:
    conn = None
    c = None

    def __init__(self):
        try:
            from aqt import mw

            db_file = os.path.join(mw.pm.addonFolder(), addon_path, "db", "chinese_dict.sqlite")
        except:
            db_file = "db/chinese_dict.sqlite"

        self.conn=sqlite3.connect(db_file)
        self.c = self.conn.cursor()

        try:
            self.c.execute("create index isimplified on cidian ( simplified );")
            self.c.execute("create unique index itraditional on cidian ( traditional, pinyin );")
            self.conn.commit()
        except:
            pass

    def pushCantonese(self, trad, simp, jyut, pinyin):
        self.c.execute('INSERT INTO cantonese (traditional, simplified, jyutping, pinyin) VALUES (?, ?, ?, ?);', (trad, simp, jyut, pinyin))
        

    def commitChanges(self):
        self.conn.commit()

    def closeConnection(self):
        self.c.close()
        self.conn.close()
        self = False

    def pushToAltDict(self, trad, simp,  pinyin):
        self.c.execute('INSERT INTO altDict (traditional, simplified, pinyin) VALUES (?, ?, ?);', (trad, simp, pinyin))


    def _get_char_pinyin(self, c):
        self.c.execute("select kMandarin from hanzi where cp = ?;", (c,) )
        try:
            (pinyin,) = self.c.fetchone()
            return pinyin
        except:
            return None
    
    def _get_word_pinyin(self, w, taiwan=False):
        self.c.execute("select pinyin, pinyin_taiwan from cidian where traditional=? or simplified=?;", (w, w))
        try:
            pinyin, taiwan_pinyin = self.c.fetchone()
            if taiwan and taiwan_pinyin is not None:  
                return taiwan_pinyin
            else:
                return pinyin
        except:
            #Not in dictionary
            return None


    def _get_char_traditional(self, c):
        """Uses Unihan to find a traditional variant"""
        self.c.execute("select kTraditionalVariant from hanzi where cp = ?;", (c,) )
        try:
            (k,) = self.c.fetchone()
            return k
        except:
            return None

    def _get_word_traditional(self, w):
        """Uses CEDICT to find a traditional variant"""
        self.c.execute("select traditional from cidian where simplified=? or traditional=?;", (w, w) )
        try:
            (k,) = self.c.fetchone()
            return k
        except:
            return None

    def get_traditional(self, w, wl=4):
        """Returns the full traditional form of a string.
        Use CEDICT wherever possible. Use Unihan to fill in.
        """

        p = self._get_word_traditional(w)
        if p:
            return p #one word, in dictionary
        if len(w)==1:
            return self._get_char_traditional(w) #single character

        #We're looking up a string that's not in the dictionary
        #We'll try each 4-character sequence in turn, then 3-sequence, then 2-sequence and if those fails, do unit lookup.
        traditional = u""
        w = w[:]
        while len(w)>0:
            word_was_found = False
            word_len = wl

            while word_len > 1:
                p = self._get_word_traditional(w[:word_len])
                if p:
                    traditional += p
                    w = w[word_len:]
                    word_was_found = True
                    break
                word_len -= 1
                
            if word_was_found == False:
                p = self._get_char_traditional(w[0])
                if p:
                    traditional += p
                else:
                    #add character directly.
                    traditional+=w[0]
                w = w[1:]
                
        return traditional.replace("U+5F8C", "").replace("U+4F75","")

    def _get_char_simplified(self, c):
        """Uses Unihan to find a simplified variant"""
        self.c.execute("select kSimplifiedVariant from hanzi where cp = ?;", (c,) )
        try:
            (k,) = self.c.fetchone()
            return k
        except:
            return None         

    def _get_word_simplified(self, w):
        """Uses CEDICT to find a traditional variant"""
        self.c.execute("select simplified from cidian where traditional=? or simplified=?;", (w, w) )
        try:
            (k,) = self.c.fetchone()
            return k
        except:
            return None

    def get_simplified(self, w, wl=4):
        """Returns the full traditional form of a string.
        Use CEDICT wherever possible. Use Unihan to fill in.
        """

        p = self._get_word_simplified(w)
        if p:
            return p #one word, in dictionary
        if len(w)==1:
            return self._get_char_simplified(w) #single character

        #We're looking up a string that's not in the dictionary
        #We'll try each 4-character sequence in turn, then 3-sequence, then 2-sequence and if those fails, do unit lookup.
        simplified = u""
        w = w[:]
        while len(w)>0:
            word_was_found = False
            word_len = wl

            while word_len > 1:
                p = self._get_word_simplified(w[:word_len])
                if p:
                    simplified += p
                    w = w[word_len:]
                    word_was_found = True
                    break
                word_len -= 1
                
            if word_was_found == False:
                p = self._get_char_simplified(w[0])
                if p:
                    simplified += p
                else:
                    #add character directly.
                    simplified+=w[0]
                w = w[1:]
                
        return simplified

    def getAllAltFayin(self):
        self.c.execute("select traditional, simplified, pinyin from altDict;")
        try:
            return self.c.fetchall()
        except:
            return False

    def getAltFayin(self, w):
        self.c.execute("select distinct pinyin from altDict where (traditional=? or simplified=?) limit 1;", (w,w))
        try:
            return self.c.fetchall()
        except:
            return False

    def getFayin(self, w):
        self.c.execute("select distinct pinyin from cidian where (traditional=? or simplified=?) limit 1;", (w,w))
        try:
            return self.c.fetchall()
        except:
            return False

    def getJyutping(self, w):
        self.c.execute("select distinct jyutping from cantonese where (traditional=? or simplified=?) limit 1;", (w,w))
        try:
            return self.c.fetchall()
        except:
            return False


        

