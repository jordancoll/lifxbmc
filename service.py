import xbmc

class LifxPlayer(xbmc.Player):
    def onPlayBackStarted(self):
        pass
        
    def onPlayBackResumed(self):
        pass
        
    def onPlayBackStopped(self):
        pass
        
    def onPlayBackEnded(self):
        pass
        
    def onPlayBackPaused(self):
        pass


if __name__ == '__main__':
    monitor = xbmc.Monitor()
    player = LifxPlayer()
 
    while not monitor.abortRequested():
        if monitor.waitForAbort(10):
            break
#        bmc.log("hello addon! %s" % time.time(), level=xbmc.LOGDEBUG)