#!/usr/bin/python


###############################################################################
#                                                                             #
#             hello.py: Uses TTS to greet you when you are home               #
#                                                                             #
###############################################################################
#                                                                             #
###############################################################################
#                                                                             #
#    This program is free software: you can redistribute it and/or modify     #
#    it under the terms of the GNU General Public License as published by     #
#    the Free Software Foundation, either version 3 of the License, or        #
#    (at your option) any later version.                                      #
#                                                                             #
#    This program is distributed in the hope that it will be useful,          #
#    but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#    GNU General Public License for more details.                             #
#                                                                             #
#    You should have received a copy of the GNU General Public License        #
#    along with this program. If not, see <http://www.gnu.org/licenses/>.     #
#                                                                             #
###############################################################################

__author__ = "Aaron Fordham"
__copyright__ = "Copyright 2017"
__credits__ = ["Aaron Fordham"]
__license__ = "GPL3"
__version__ = "0.0.1"
__maintainer__ = "Aaron Fordham"
__email__ = "a.fordham@iinet.net.au"
__status__ = "Development"

###############################################################################
#
# To Do
#
#
#
###############################################################################


import os
import sys
import subprocess
import time
#import bluetooth
import pygame
from time import sleep
from threading import Thread
import datetime

###############################################################################

class HelloYouThere():

    def __init__(self):

        pygame.init()
        self.speak("System operational. Beep. boop. beep. boop.")
        self.__logger__("System has started. Did you hear anything?")

        self.addr = self.loadaddr()

        #This creates a thread to detect motion
        #thread =  Thread(target = self.motion)
        #thread.start()

        self.main()

    def __logger__(self, string):
        print(string)



    def main(self):
        self.interval = 1
        self.pattern = [[1,0,1],
                        [1,0,0,1],
                        [1,0,0,0,1],
                        [1,0,0,0,0,1],
                        [1,0,0,0,0,0,1],
                        [1,0,0,0,0,0,0,1],
                        [1,0,0,0,0,0,0,0,1],
                        [1,0,0,0,0,0,0,0,0,1],
                        [1,0,0,0,0,0,0,0,0,0,1],
                        [1,0,0,0,0,0,0,0,0,0,0,1],
                        [1,0,0,0,0,0,0,0,0,0,0,0,1]]



        self.devicesConnected = 0

        self.on = 0
        while True:
            self.now = datetime.datetime.now().time()

            if (self.now.hour > 21 or self.now.hour < 9) and self.on == 1:
                self.on = 0
                self.__logger__("%d:%d Turning off." % (self.now.hour, self.now.minute))
                self.speak("Turning off. Good night household")

                for i,addr in enumerate(self.addr):
                    self.addr[i][-1] = "0"

            elif (self.now.hour < 21 and self.now.hour > 9) and self.on == 0:
                self.speak("Good morning") 
                self.__logger__("%d:%d Turning on." % (self.now.hour, self.now.minute))
                self.on = 1

            elif (self.now.hour < 21 or self.now.hour > 9):
               self.searchWifi()
            else:
                self.on = 1


    def loadaddr(self):
       addr = []
       with open("address") as f:
           temp = f.readlines()
           for line in temp:
               addr.append(line.split())
               for i, element in enumerate(addr):
                   addr[i][-2] = []
       return addr 

    @staticmethod
    def KnuthMorrisPratt(text, pattern):

        '''Yields all starting positions of copies of the pattern in the text
	Calling conventions are similar to string.find, but its arguments can be
	lists or iterators, not just strings, it returns all matches, not just
	the first one, and it does not need the whole text in memory at once.
	Whenever it yields, it will have read the text exactly up to and including
	the match that caused the yield. Modified to return True or None'''

	# allow indexing into pattern and protect against change during yield
        pattern = list(pattern)

	# build table of shift amounts
        shifts = [1] * (len(pattern) + 1)
        shift = 1
        for pos in range(len(pattern)):
            while shift <= pos and pattern[pos] != pattern[pos-shift]:
                 shift += shifts[pos-shift]
            shifts[pos+1] = shift

	# do the actual search
        startPos = 0
        matchLen = 0
        for c in text:
            while matchLen == len(pattern) or \
                matchLen >= 0 and pattern[matchLen] != c:
                startPos += shifts[matchLen]
                matchLen -= shifts[matchLen]
            matchLen += 1
            if matchLen == len(pattern):
                return True


        return []

    def searchWifi(self):
        i = 0

        for  name, addr, status, history, num  in self.addr:
            print(self.addr[i])
            p = subprocess.Popen("arp-scan -l | grep %s" % str(addr), stdout=subprocess.PIPE, shell=True)
            (output, err) = p.communicate()
            p_status = p.wait()
            if output and status == "0":

                self.devicesConnected +=1
                self.addr[i][2] = "1"
                self.addr[i][3] = [1] + history

                # Search the history for pattern, if pattern exists
                # break. Actions will only execute if seq not True.
                for pattern in self.pattern:
                    seq = self.KnuthMorrisPratt(history, pattern)
                    if seq == True:
                        self.__logger__("pattern exists")
                        break
                if not seq:
                    if num == "0":
                        self.__logger__("%s connected" % name)
                        self.action(name)
                        self.addr[i][4] = "1"

            elif output and status == "1":
                self.addr[i][3] = [1] + history

            elif not output and status == "1":
                self.__logger__("%s disconnected" % name)
                self.addr[i][3] = [0] + history
                self.addr[i][2] = "0"
                self.devicesConnected -=1

            elif not output and status == "0":
                self.addr[i][3] = [0] + history

            if len(self.addr[i][3]) > len(self.pattern[-1]):
                del(self.addr[i][3][-1])
            i+=1
            sleep(self.interval)
            #self.__logger__("%s %s %s %s" % (name, repr(addr), status, history))



    def motion(self):
        while True:

            print("Motion detected")
            sleep(2)

    def action(self, name):

        if name == "Aaron":
            self.speak("Where is my master?")
        elif name == "Susan":
            self.speak("I love you Susan")
        elif name == "Dave":
            self.speak("behave Dave")
        elif name == "Sadie":
            self.speak("Don't worry Sadie, I get migranes too on birth control")
        elif name == "Greg":
            self.speak("Greg. I want your curls")


    def speak(self, string):
        p = subprocess.Popen('gtts-cli "%s" -o YouThere.mp3' % string, stdout=subprocess.PIPE, shell=True)
        (output, err) = p.communicate()
        #p_status = p.wait() # Hangs for some reason??
        pygame.mixer.music.load("YouThere.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    def timeBasedActions(self, now):
        if now.hour == 16 and now.minute == 20:
            self.speak("The time is 4 20. Boo yeah")


if __name__ == "__main__":
    hi = HelloYouThere()


#target_name = "My Phone"
#target_address = None
#nearby_devices = bluetooth.discover_devices()

#for bdaddr in nearby_devices:
#    print("Found:", bdaddr)
#    print(bluetooth.lookup_name(bdaddr))
#    if target_name == bluetooth.lookup_name( bdaddr ):
#        target_address = bdaddr
#    

#if target_address is not None:
#    print("found target bluetooth device with address ", target_address)
#else:
#    print("could not find target bluetooth device nearby")

