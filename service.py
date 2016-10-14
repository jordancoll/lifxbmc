from threading import RLock
import xbmc
from xbmc import Player, Monitor, LOGNOTICE, LOGERROR, LOGWARNING
from xbmcaddon import Addon
from xbmcgui import Window, ControlLabel
from lifxlan import *

addon = Addon()

class LifxPlayer(Player):
    
    def __new__(cls, lights=[]):
        obj = Player.__new__(cls)
        obj.lights = dict((light, None) for light in lights)
        obj.lights_lock = RLock()
        
        return obj
    
    def __contains__(self, light):
        with self.lights_lock:
            return light.ip_addr in map(lambda l: l.ip_addr, self.lights)
    
    def add_light(self, light, color):
        with self.lights_lock:
            self.lights[light] = color if self.isPlayingVideo() else None
    
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
        self.restore()
        log("playback ended")
    
    def onPlayBackPaused(self):
        log("playback paused")
        self.restore()
    
    def darken(self):
        def store_old_and_dim(light, color):
            curr_color = light.get_color()
            self.lights[light] = curr_color
            dim_color = (curr_color[:2] + (int(float(addon.getSetting("dim_value")) * 65535 / 100), curr_color[3]))
            if light.power_level:
                light.set_color(dim_color, duration=int(float(addon.getSetting("change_duration")) * 1000))
        
        if self.isPlayingVideo():
            self.do_all_lights(store_old_and_dim)
    
    def restore(self):
        def do_restore(light, color):
            if light.power_level and color:
                light.set_color(color, duration=int(float(addon.getSetting("change_duration")) * 1000))
            self.lights[light] = None
        
        self.do_all_lights(do_restore)
    
    def do_all_lights(self, action):
        unresponsive = []
        with self.lights_lock:
            for light, color in self.lights.iteritems():
                try:
                    action(light, color)
                except IOError as ioe:
                    log("removing unresponsive light %s" % light.label, level=LOGWARNING)
                    unresponsive.append(light)
            for light in unresponsive:
                del self.lights[light]

def log(msg, level=LOGNOTICE):
    xbmc.log("lifxbmc - %s" % msg.replace("\0", ""), level=level) # strings returned from lights sometimes have null chars

if __name__ == '__main__':
    monitor = Monitor()
    player = LifxPlayer()
    
    log("inited")    
     
    while not monitor.abortRequested():
        if monitor.waitForAbort(10):
            break
        
        try:
            lifx = LifxLAN()
            for light, color in lifx.get_color_all_lights():
                if len(addon.getSetting("group_filter")) > 0:
                    pass
                if light not in player:
                    log("discovered new light %s" % light.get_label())
                    player.add_light(light, color)
        except Exception as e:
            log("Exception while discovering lights: %s" % e, level=LOGERROR)

