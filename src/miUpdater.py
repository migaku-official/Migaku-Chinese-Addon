from aqt import mw
from aqt import addons
from anki.hooks import  wrap, addHook
from .miutils import miInfo
import time
from anki.httpclient import HttpClient

addonId = 498302176
dledIds = []


def shutdownDB( parent, mgr, ids, on_done, client):
    global dledIds 
    dledIds = ids
    if addonId in ids and hasattr(mw, 'MigakuChinese'):
        miInfo('Migaku Chinese\'s database will be diconnected so that the update may proceed. The add-on will not function properly until Anki is restarted after the update.')
        mw.MigakuChinese.db.closeConnection()
        mw.MigakuChinese.db = False
        time.sleep(2)
    

def restartDB(*args):
    if addonId in dledIds and hasattr(mw, 'MigakuChinese'):
        miInfo('Migaku Chinese has been updated. Migaku Chinese will not function properly until Anki is restarted. Please restart Anki to start using the new version now!')

def wrapOnDone(self, log):
    self.mgr.mw.progress.timer(50, lambda: restartDB(), False)

addons.download_addons = wrap(addons.download_addons, shutdownDB, 'before')
addons.DownloaderInstaller._download_done = wrap(addons.DownloaderInstaller._download_done, wrapOnDone)


