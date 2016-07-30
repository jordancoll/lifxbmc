import traceback
import xbmc
from xbmc import Player, Monitor, LOGNOTICE, LOGERROR
from lifxlan import *

class LifxPlayer(Player):

    def __new__(cls, lights):
        obj = Player.__new__(cls)
        obj.lights = dict((light, light.color) for light in lights)
        return obj

    def onPlayBackStarted(self):
        log("playback started")
        self.darken()
        
    def onPlayBackResumed(self):
        log("playback resumed")
        self.darken()
        
    def onPlayBackStopped(self):
        log("playback stopped")
        self.restore()
        
    def onPlayBackEnded(self):
        log("playback ended")
        self.restore()
        
    def onPlayBackPaused(self):
        log("playback paused")
        self.restore()

    def darken(self):
        for light, color in self.lights.iteritems():
            curr_color = light.get_color()
            self.lights[light] = curr_color
            if light.power_level:
                light.set_color(curr_color[:2] + (10, curr_color[3]), duration=1500)
            else:
                log("light %s is OFF" % light.get_label())

    def restore(self):
        for light, color in self.lights.iteritems():
            if light.power_level:
                if color:
                    light.set_color(color, duration=1500)

def log(msg, level=LOGNOTICE):
    xbmc.log("lifxbmc - " + msg, level=level)

if __name__ == '__main__':
    monitor = Monitor()

    log("lifxbmc inited")
    
    lifx = LifxLAN()
    log("discovered lights:")
    original_powers = lifx.get_color_all_lights()
    for light, color in original_powers:
        log("light: %s - power: %s - color: %s" % (light.get_label(), light.power_level, color))
 
    try:
        player = LifxPlayer(lifx.lights)
    except Exception as e:
        log(traceback.format_exc(), level=LOGERROR)
    else:
        while not monitor.abortRequested():
            if monitor.waitForAbort(10):
                break
