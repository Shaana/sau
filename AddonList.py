#!/usr/bin/env python

import os
import re

from Error import *
from Addon import Addon
from Reader import chomp, Reader

#TEMP

class Error_msg(object):

    def Print(self, message):
        print("Error: {0}".format(message))
        
    def ReadFile_LineError(self, file_name, line):
        print(bcolors.RED + "Error: " + bcolors.END + "Invalid line in file \'{0}\', line {1}".format(bcolors.YELLOW + file_name + bcolors.END, bcolors.YELLOW + str(line) + bcolors.END))
    
error = Error_msg()  
#End TEMP

class AddonList(object):
    #AddonList object counter
    num_lists = 0
    
    #currently it only creates a list from the home folder OR the given file
    def __init__(self, home=None, addon_list_file=None):
        try:
            if not home:
                raise AddonHomelessError()
               
        except AddonHomelessError as e:
            print(e)
        else: 
            self._num_addons = 0
            self._list_addons = []
            self._home = os.path.expanduser(home)
            
            if addon_list_file:
                self._addon_list_file = os.path.expanduser(addon_list_file)
                self.ParseAddonListFile(self.addon_list_file)
            else:
                self._addon_list_file = addon_list_file
                self.ParseHomeDir(self.home)
    
            #counter
            self.__class__.num_lists += 1
        
    def _SetNumAddons(self, num_addons):
        self._num_addons = num_addons
            
    def _SetListAddons(self, list_addons):
        try:
            if type(list_addons) != type([]):
                raise TypeError("Not a list. TODO")
        except TypeError as e:
            print(e)
        else:
            self._list_addons = list_addons
    
    def _SetAddonListFile(self, file):
        if file:
            self._addon_list_file= file
          
    def _GetHome(self):
        return self._home
            
    def _GetNumAddons(self):
        return self._num_addons
    
    def _GetListAddons(self):
        return self._list_addons
    
    def _GetAddonListFile(self):
        return self._addon_list_file
    
    home = property(_GetHome)
    num_addons = property(_GetNumAddons, _SetNumAddons)
    list_addons = property(_GetListAddons, _SetListAddons)
    addon_list_file = property(_GetAddonListFile, _SetAddonListFile)
        
    def Add(self, addon):
        """
        Add an addon object to the AddonList object.
        """
        try:
            if not (type(addon) == Addon):
                #TODO better change to AddonListAddError ?
                raise AddonTypeError()
        except AddonTypeError as e:
            print(e)
        else:
            self.list_addons.append(addon)
            self.num_addons += 1
      
    def Extend(self, addon_list):
        #TODO, its not checking for dublicates
        """
        Extend the AddonList object with either a list or another AddonList.
        Using the class method Add to add the single addons. (This Method is already checking if it's really an addon object)
        """
        try:
            #check if it's a list or tuple
            if type(addon_list) == type([]) or type(addon_list) == type(()):
                #use self.Add(addon) method to check if the entry is really an addon
                for addon in addon_list:
                    self.Add(addon)
            elif addon_list == AddonList:
                #no need to check if every list entry is an addon.
                self.list_addons.extend(AddonList.list_addons)
            else:
                raise AddonListExtendError()
        except AddonListExtendError as e:
            print(e)
        
    def Remove(self, addon):
        if addon in self.list_addons:
            self.list_addons.remove(addon)
            self.num_addons -= 1
                
    def ParseHomeDir(self, home):
        try:
            for folder in os.listdir(home):
                if os.path.isdir(folder):
                    addon = Addon(self.home, folder_name=folder)
                    self.Add(addon)
        except:
            pass
            
    def ParseAddonListFile(self, addon_list_file):
        #format expected: repo_type [whitespace] url
        list_lines = Reader.get_instance().read_config(addon_list_file)
        pattern = "^(git|svn|hg)(?:[\t ]+)(.+)$"
        cur_line = 1;
        for line in list_lines:
            match = re.match(pattern, line)
            if match:
                addon = Addon(self.home, url=match.group(2), repo_type=match.group(1))
                self.Add(addon)
            else:
                pass
                #TODO
                #error.ReadFile_LineError(addon_list_file, cur_line)
            cur_line += 1
    
    def Print(self):
        for addon in self.list_addons:
            print(addon)
    
    def Compare(self, list_addons):
        if type(list_addons) == AddonList:
            print("main")
        elif type(list_addons) == type([]):
            print("list")
        
