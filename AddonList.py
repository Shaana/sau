#!/usr/bin/env python

__author__ = "Share"
__email__  = "shaana@student.ethz.ch"
__license__= """
Copyright (c) 2008-2012 Share <shaana@student.ethz.ch>
This file is part of sau.

sau is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

sau is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with sau.  If not, see <http://www.gnu.org/licenses/>.
"""

import os
import re

import Error
import Addon
import Reader

#TODO change num_addons to only allow certain functinos to change the value, so users cant fuck it up

#Note AddonList objects are always called addon_list, while the actual list of addons is called list_addons

class AddonList(object):
    #AddonList object counter
    num_lists = 0
    
    #currently it only creates a list from the home folder OR the given file
    def __init__(self, name=None, root=None, addon_list_config_file=None):
        """
        Every AddonList is specific to a root directory
        
        """

        try:
            if not root:
                raise Error.AddonListRootError()
            
            if not name:
                raise Error.AddonListNameError()
            
            self._root = os.path.expanduser(root)
            self.name = name
            self._num_addons = 0
            self.list_addons = []
            
            self.addon_list_config_file = addon_list_config_file
                            
            #counter
            self.__class__.num_lists += 1
            
        except (Error.AddonListRootError, Error.AddonListNameError) as e:
            print(e)
            
    def __str__(self):
        return self.name
            
    #root
    def _get_root(self):
        return self._root
    
    #name
    def _set_name(self, name):
        try:
            if type(name) != str:
                raise Error.CommonTypeError(None, type(name), str)
            
            self._name = name
            
        except Error.CommonTypeError as e:
            print(e)
    
    def _get_name(self):
        return self._name
    
    #num_addons
    def _set_num_addons(self, num_addons):
        """
        This function is only called by add_addon(), remove_addon()
        """
        try:
            if type(num_addons) != int:
                raise Error.CommonTypeError(None, type(num_addons), int)
            
            self._num_addons = num_addons
            
        except Error.CommonTypeError as e:
            print(e)
            
    def _get_num_addons(self):
        return self._num_addons
    
    #addon_list   
    def _set_list_addons(self, new_addon_list):
        try:
            if not (type(new_addon_list) == list or type(new_addon_list) == tuple):
                raise Error.CommonTypeError(None, type(new_addon_list), (list, tuple))
            
        except Error.CommonTypeError as e:
            print(e)
            
        else:
            #we want a real copy, not just a link
            self._list_addons = list(new_addon_list)
    
    def _get_list_addons(self):
        return self._list_addons
    
    
    #addon_list_config_file
    def _set_addon_list_config_file(self, file):
        try:
            if not (type(file) == str or file == None):
                raise Error.CommonTypeError(None, type(file), str)
            
            self._addon_list_config_file = file
            
        except Error.CommonTypeError as e:
            print(e)
            
    def _get_addon_list_config_file(self):
        return self._addon_list_config_file


    def add_addon(self, addon):
        """
        Add an addon object to the AddonList object.
        """
        try:
            if type(addon) != Addon.Addon:
                raise Error.CommonTypeError(None, type(addon), Addon.Addon)
            
            #maybe change to a in self.li
            for a in self.list_addons:
                if a == addon:
                    raise Error.AddonListColisionError(self, addon)
                
            
        except (Error.CommonTypeError, Error.AddonListColisionError) as e:
            print(e)
            
        else:
            self.list_addons.append(addon)
            self._num_addons += 1
            return True
    
    #TODO, allow to remove addons by url or folder
    def remove_addon(self, addon):
        try:
            if addon in self.list_addons:
                self.list_addons.remove(addon)
                self._num_addons -= 1
                return True
            else:
                raise Error.AddonListRemoveError(self, addon)
            
        except Error.AddonListRemoveError as e:
            print(e)
        
      
    def extend(self, list_addons):
        #TODO, its not checking for dublicates
        """
        Extend the AddonList object with either a list or another AddonList.
        Using the class method Add to add the single addons. (This Method is already checking if it's really an addon object)
        """
        try:
            #check if it's a list or tuple
            if type(list_addons) == list or type(list_addons) == tuple:
                #use self.add_addon(addon) method to check if the entry is really an addon and valid
                for addon in list_addons:
                    self.add_addon(addon)
                    
            elif list_addons == AddonList:
                #self.list_addons.extend(AddonList.list_addons)
                #we have to check for addon colision
                for addon in AddonList.list_addons:
                    self.add_addon(addon)
                
            else:
                raise Error.AddonListExtendError(self, list_addons)
            
        except Error.AddonListExtendError as e:
            print(e)
    
    #parse_pkgmeta_file --> take the wowace, ... and create a list out of those.
    def create_from_addon_config_file_lib_list(self):
        pass
        
    def parse_root(self):
        try:
            for folder in os.listdir(self.root):
                if os.path.isdir(folder):
                    addon = Addon(self.root, folder_name=folder)
                    self.add_addon(addon)
        except:
            pass
            
    def parse_addon_list_config_file(self):
        #TODO allow to add a protected flag in the config file
        #format expected: repo_type [whitespace] url
        list_lines = Reader.Reader.get_instance().read_config(self.addon_list_config_file)
        
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
    
    def dump_addon_list(self):
        for addon in self.list_addons:
            print(addon)
    
    def compare(self, list_addons):
        if type(list_addons) == AddonList:
            print("main")
        elif type(list_addons) == type([]):
            print("list")
            
    def compare_differece(self, addon_list_obj):
        #add every addon that is ONLY in one of the lists
        #create a new list and return it !
        return AddonList()
    
    def compare_match(self, addon_list_obj):
        #a list of addons, that are in both of the lists !
        #create a new list and return it !
        return AddonList()
    
    def execute(self):
        """
        run update or clone for every addon in the list
        """
        pass
    
    root = property(_get_root)
    name = property(_get_name, _set_name)
    num_addons = property(_get_num_addons)
    list_addons = property(_get_list_addons, _set_list_addons)
    
    addon_list_config_file = property(_get_addon_list_config_file, _set_addon_list_config_file)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
        
