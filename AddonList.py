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
import copy

import Error
import Addon
import Reader

#Note AddonList objects are always called addon_list, while the actual list of addons is called list_addons
#TODO add unique names ? and add global class var, that stores all names with a link to the object?
     

class AddonList(object):
    
    #counter for unique names
    _num_lists = 0
    
    def __init__(self, name=None, root=None, url_config_file=None):
        """
        Every AddonList is specific to a root directory
        Currently AddonList names don't have to be unique, but it helps.
        
        @param name: AddonList name
        @type name: str
        @param root: AddonList root folder (absolute path)
        @type root: str
        @param url_config_file: file containing the urls (absolute path)
        @type url_config_file: str
        
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
            
            self.url_config_file = url_config_file
                            
            #counter
            self.__class__._num_lists += 1
            
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
    #Note: currently not used
    def _set_num_addons(self, num_addons):
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
    
    #url_config_file
    def _set_url_config_file(self, file):
        try:
            if not (type(file) == str or file == None):
                raise Error.CommonTypeError(None, type(file), str)
            
            self._url_config_file = file
            
        except Error.CommonTypeError as e:
            print(e)
            
    def _get_url_config_file(self):
        return self._url_config_file

    def add_addon(self, addon):
        """
        Add an Addon object to the AddonList object.
        
        @param addon: Addon to be added to the AddonList
        @type addon: Addon
        
        """
        try:
            if type(addon) != Addon.Addon:
                raise Error.CommonTypeError(None, type(addon), Addon.Addon)
            
            if addon in self.list_addons:
                raise Error.AddonListColisionError(self, addon)
                
        except (Error.CommonTypeError, Error.AddonListColisionError) as e:
            print(e)
            
        else:
            self.list_addons.append(addon)
            self._num_addons += 1
            return True
    
    #TODO, allow to remove addons by url or folder_name
    def remove_addon(self, addon):
        """
        Remove an Addon object from the AddonList object.
        
        @param addon: Addon to be removed from the AddonList
        @type addon: Addon
        
        """
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
        """
        Extend the AddonList object with either a list or a tuple.
        Use merge() if you want to combine two AddonList objects.
        """
        try:
            #check if it's a list or tuple
            if type(list_addons) == list or type(list_addons) == tuple:
                #use self.add_addon(addon) method to check for colision and if it's really an addon.
                for addon in list_addons:
                    self.add_addon(addon)
            else:
                raise Error.AddonListExtendError(self, list_addons)
            
        except Error.AddonListExtendError as e:
            print(e)
    
    def parse_root(self, find_url_info=True, list_protected=[]):
        """
        Creates an AddonList from all folders in the root folder.
        Ignoring addons starting with the name 'Blizzard_'.
        
        """
        try:
            try:
                for folder_name in os.listdir(self.root):
                    if os.path.isdir(os.path.join(self.root, folder_name)):
                        if not match_list_protected(folder_name, list_protected):
                            addon = Addon.Addon(self.root, folder_name=folder_name)
                            if find_url_info:
                                addon.parse_home_for_url_info()
                            self.add_addon(addon)
                
                return True
            
            except OSError as e:
                raise Error.CommonOSError(e)
            
        except Error.CommonOSError as e:
            print(e)
      
    def parse_url_config_file(self):
        """
        Creates an AddonList from all urls in the given config file.
        
        format expected: [!]repo_type [whitespace] url
        if '!' is set the addon will be protected
        
        """
        list_lines = Reader.Reader.get_instance().read_config(self.url_config_file)
        
        pattern = "^(!?)(git|svn|hg)(?:[\t ]+)(.+)$"
        
        assert list_lines != None
        cur_line = 1;
        for line in list_lines:
            match = re.match(pattern, line)
            if match:
                protected = False
                if match.group(1) == "!":
                    protected = True 
                addon = Addon.Addon(self.root, (match.group(2), match.group(3)), protected=protected)
                self.add_addon(addon)

            cur_line += 1
        
        return True
           
    #Todo add errors      
    #parse_pkgmeta_file --> take the wowace, ... and create a list out of those.
    def parse_pkgmeta_info(self, dict_info):
        """
        Creates a new addon_list from a given pkgmeta parse.
        
        @param dict_info: output of the parse_pkgmeta_file() from the Addon class
        @type dict_info: dict
        
        """
        try:
            #Note: This url_info is different (local_folder, url, tag), but no repo_type !
            list_patterns = ["^(?:.+?)://(git|svn|hg).wowace.com/wow/([A-Z0-9a-z_~.-]+).*?$",
                            "^(?:.+?)://(git|svn|hg).curseforge.net/wow/([A-Z0-9a-z_~.-]+).*$",
                            "^(?:.+?)://(git|svn|hg).wowinterface.com/([A-Z0-9a-z_~.-]+)-(?:[0-9]+).+$"]
            
            assert "externals" in dict_info
            
            if dict_info and "externals" in dict_info:
                for url_info in dict_info["externals"]:
                    for pattern in list_patterns:
                        match = re.match(pattern, url_info[1])
                        if match:
                            addon = Addon.Addon(self.root, (match.group(1), url_info[1]), match.group(2))
                            self.add_addon(addon)
                            break
                        else:
                            pass #add to list that failed for the error.
            
            return True
        
        except:
            pass
    
    #support function to dump the addons in the current list. Mostly for debugging.
    def dump_list_addons(self):
        for addon in self.list_addons:
            print(addon)
    
    def merge(self, other_list, mode=None, list_ignore=[]):
        """
        Returns a new AddonList object with the merged list
        Only AddonLists with the same root can be merged !     
        
        @param other_list: AddonList to merge
        @type other_list: AddonList
        @param mode: merge mode
        @type mode: str or int
          
        modes: 
        - standard 1
        - difference 2
        - match 3
        - unique 4 (from first given list)
        
        """
        list_valid_modes = ["standard", "difference", "match", "unique"]
        
        try:          
            if self.root != other_list.root:
                raise Error.AddonListMergeRootError(self, other_list)
            
            #For now we copy the whole list first, merge into that one and return it.
            temp_list = copy.deepcopy(self)
            
            # merge into the copy of the original list, add every addon except dublicates.
            if mode == 1 or mode == "standard": 
                for addon in other_list.list_addons: 
                    if not addon in self.list_addons:
                        temp_list.add_addon(addon)
                return temp_list
                        
            elif mode == 2 or mode == 3 or mode == 4 or mode == "difference" or mode == "match" or mode =="unique":
                #we remove every addon that is in both lists from the list temp_other.
                #and we end up with a list that only contains addons that are unique in the other_list
                
                list_match = AddonList("merge_list_" + str(self.__class__._num_lists), self.root)
                list_difference = AddonList("merge_list_" + str(self.__class__._num_lists), self.root)
                temp_other = copy.deepcopy(other_list)

                for addon in temp_list.list_addons:
                    if addon in temp_other.list_addons:
                        list_match.add_addon(addon)
                        temp_other.remove_addon(addon)
                    else:
                        list_difference.add_addon(addon)
                
                if mode == 2 or mode == "difference": 
                    return list_difference.merge(temp_other, "standard")
                elif mode == 3 or mode == "match":
                    return list_match
                elif mode == 4 or mode == "unique":
                    return list_difference               

            else:
                raise Error.AddonListMergeModeError(self, mode, list_valid_modes)
            
        except (Error.AddonListMergeRootError, Error.AddonListMergeModeError) as e:
            print(e)

    #TODO give it some love
    def enhance_addon_list(self, list_ignore=[]):
            
        try:
            list_ignore.append("libstub")
            
            temp_list = copy.deepcopy(self)
            list_cleaned = AddonList("cleaned_list", self.root)

            for addon in temp_list.list_addons:
                match = False
                for ignore in list_ignore:
                    match = re.search(ignore, addon.name, re.IGNORECASE) # ?
                    if match:
                        break
                    
                if not match:
                    addon.enhance_url_info()
                    if not addon in list_cleaned.list_addons:
                        list_cleaned.add_addon(addon)
            
            return list_cleaned
  
                
        except Exception as e:
            print(e)
            
    
    #TODO far from done ...
    def execute(self, clean_repo=False, clean_ignore=False):
        """
        run update or clone for every addon in the list
        """
        try:
            libs = AddonList("libs", self.root)
            for addon in self.list_addons:
                addon.execute()
                addon.parse_pkgmeta_file()
                temp_list = AddonList("temp", self.root)
                temp_list.parse_pkgmeta_info(addon.config_info)
                libs = libs.merge(temp_list, "standard")
                
            
            libs.name = "libs_" + self.name
            return libs
        except:
            pass
    
    
    root = property(_get_root)
    name = property(_get_name, _set_name)
    num_addons = property(_get_num_addons)
    list_addons = property(_get_list_addons, _set_list_addons)
    
    url_config_file = property(_get_url_config_file, _set_url_config_file)
    

def match_list_protected(folder_name, list_protected):
    for pattern in list_protected:
        match = re.match(pattern, folder_name)
        if match:
            return True
    
    
    
    
    
    
    
    
    
    
    
    
        
