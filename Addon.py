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
import subprocess
import shutil

import Error
import Reader

#TODO add threading support for cloning, with a global class variable to keep track of the cloning instances :D
#like clone() ... do the threading and call renamed function _clone()

#TODO rework parse_pkgmeta_file()

class Addon(object):
    """
    This represents a World of Warcraft addon. This class allows to update/clone addon repositories
  
    It is recommend to embed your code into a try, except block to catch AttributeError 
    in case you assign a value to a _getter only variable.
    
    Every _get_* function return None if the variable doesn't exist.
   
    """
    #using properties, access variables via self#required for TempFolder_i.home, self.name, self.url, etc.
    #counts the number of addon instances, required for TempFolder_i
    num_addons = 0
    
    #currently supported repository types
    _supported_repository_types = ("git", "svn", "hg")
    
    #in our case always the .pkgmeta file
    _config_file = ".pkgmeta"
    _config_file_tags = ["package-as", "externals", "ignore", "move-folders", "required-dependencies", "optional-dependencies", "manual-changelog", "license-output", "tools-used", "enable-nolib-creation"]
    
    def __init__(self, root=None, url_info=None, folder_name=None, protected=False, name=None):
        """
        A valid addon requires at least the root folder and url_info tuple (repo_type, url) or 
        a root folder and an addon folder.
        
        @param root: the folder containing the addon folder(absolute path)
        @type root: str
        @param url_info: a (repo_type, url) tuple, which contains the url and
                         the corresponding repository type (currently supporting: git, svn, hg)
        @type url_info: tuple
        @param folder_name: the addon folder name
        @type folder_name: str
        @param protected: a protected addon can't be modified
        @type protected: bool
        @param name: the addon's name (just for recognition)
        @type name: str
        """
        
        #note difference between self._root and self.url_info assignments
        #in the second case the property function _set_url_info is called
        
        try:
            if not root:
                raise Error.AddonRootError()

            if (url_info) or (folder_name):
                self._root = os.path.expanduser(root)
                self.name = name                       
                self.url_info = url_info
                
                #valid folder required for cloning
                if folder_name == None:
                    self.folder_name = "TmpFolder_" + str(self.__class__.num_addons)  
                else:
                    self.folder_name = folder_name
                         
                #protected addons cannot be changed, deleted, updated, cleaned, etc.
                self.protected = protected
                            
                #config file (usually .pkgmeta file)
                #currently only changed by the parse_pkgmeta_file() function
                self._config_info = {}
                self._config_file_parsed = False
                            
                #increment counter
                self.__class__.num_addons += 1
            else:
                raise Error.AddonInitError()

        except (Error.AddonRootError , Error.AddonInitError) as e:
            print(e)

    
    def __str__(self):
        #TODO rework
        #return("name: {}; home: {}; url: {} {}; folder: {}; protected: {}".format(self.name, self.home, self.repo_type, self.url, self.folder_name, self.protected))
        return self.name
    
    
    def _remove_tree(self, file):
        """
        A little support function to delete directories/files/links.
        Deleting files is only possible within the addon root folder.
        
        returns True, if everything worked. None otherwise
        
        OSError is handled
        """
        try:
            try:
                #is it a subfolder/subfile in the addon root ?
                if file.startswith(self.root):
                    if os.path.isfile(file):
                        os.remove(file)
                    else:
                        shutil.rmtree(file)
                else:
                    raise Error.CommonRemoveTreeError(self.root, file)
                
                return True
            
            except OSError as e:
                raise Error.CommonOSError(e)
            
            except Error.CommonRemoveTreeError as e:
                print(e)
                
        except Error.CommonOSError as e:
            print(e)
        

    
    #TODO maybe add some error, that says if the repo didnt exists, or access denied, etc.. -> AddonRepository[...]Error
    #and use the subprocesss exit status
    def clone(self): #stderr=subprocess.STDOUT, stdout=subprocess.PIPE
        """Clones the given remote repository to a local folder."""
        stderr=None
        stdout=None
        try:
            try:
                #check if we even have url_info given
                if not self.url_info:
                    raise Error.AddonUrlError(self)
                
                #only prevent cloning if the addon_folder already exists and is protected!
                if os.path.exists(self.home):
                    if self.protected:
                        raise Error.AddonProtectedError(self)
                    else:
                        self._remove_tree(self.home)
                    
                if self.url_info[0] == "git":
                    subprocess.call(["git", "clone", self.url_info[1], self.home], stderr=stderr, stdout=stdout)
                elif self.url_info[0] == "svn":
                    subprocess.call(["svn", "checkout", self.url_info[1], self.home], stderr=stderr, stdout=stdout)
                elif self.url_info[0] == "hg":
                    subprocess.call(["hg", "clone", self.url_info[1], self.home], stderr=stderr, stdout=stdout)
                else:
                    #this should never every happen, since the _set_url_info is checking the repo_type already !
                    raise Error.AddonRepositoryTypeError(self, self.url_info[0], self.__class__._supported_repository_types)
                
                return True
                
            except subprocess.CalledProcessError as e:
                print(e)
                raise Error.AddonCloneError(self, "subprocess returned non zero exit status")
            
            except Error.AddonUrlError as e:
                print(e)
                raise Error.AddonCloneError(self, "no url given")
            
            except Error.AddonRepositoryTypeError as e:
                print(e)
                raise Error.AddonCloneError(self, "invalid repository type used")
            
            except Error.AddonProtectedError as e:
                print(e)
                raise Error.AddonCloneError(self, "addon folder already exists and is protected")
            
        except Error.AddonCloneError as e:
            print(e)
            
    def update(self): #stderr=subprocess.STDOUT, stdout=subprocess.PIPE
        """Updates the repository in an existing addon folder."""
        stderr=None
        stdout=None
        try:
            try:               
                try:
                    #check if its protected
                    if self.protected:
                        raise Error.AddonProtectedError(self)
                    
                    #check for the repo folder exists
                    if not os.path.exists(self.repo_folder):
                        raise Error.AddonRepositoryFolderError(self)
                    
                    #git, hg need to be in the home folder in order to work !                                        
                    os.chdir(self.home)
                    if self.url_info[0] == "git":
                        subprocess.call(["git", "pull"], stderr=stderr, stdout=stdout)
                    elif self.url_info[0] == "svn":
                        subprocess.call(["svn", "update", self.home], stderr=stderr, stdout=stdout)
                    elif self.url_info[0] == "hg":
                        subprocess.call(["hg", "pull"], stderr=stderr, stdout=stdout)
                        subprocess.call(["hg", "update"], stderr=stderr, stdout=stdout)
                    else:
                        #this should never every happen, since the _set_url_info is checking the repo_type already !
                        raise Error.AddonRepositoryTypeError(self, self.url_info[0], self.__class__._supported_repository_types)
                
                    return True
                
                except OSError as e:
                    raise Error.CommonOSError(e)
                
                except Error.AddonRepositoryFolderError as e:
                    print(e)
                    raise Error.AddonUpdateError(self, "repository folder missing")
                
                except subprocess.CalledProcessError as e:
                    print(e)
                    raise Error.AddonUpdateError(self, "subprocess returned non zero exit status")
                
                except Error.AddonRepositoryTypeError as e:
                    print(e)
                    raise Error.AddonUpdateError(self, "invalid repository type used")
                
                except Error.AddonProtectedError as e:
                    print(e)
                    raise Error.AddonUpdateError(self, "addon folder already exists and is protected")
                    
            except Error.CommonOSError as e:
                print(e)
                raise Error.AddonUpdateError(self, "an OSError occurred")
            
        except Error.AddonUpdateError as e:
            print(e)
    
    #_root
    def _get_root(self):
        return self._root
    
    #_name
    def _set_name(self, name):
        try:
            if name == None or type(name) == str:
                self._name = name
            else:
                raise Error.CommonTypeError("Addon name needs to be a string.")
            
        except Error.CommonTypeError as e:
            print(e)
        
    def _get_name(self):
        if self._name:
            return self._name
        elif self.url_info:
            return "u:" + self.url_info[1]
        elif self.folder_name:
            return "f:" +self.folder_name
        else:
            return "Unknown"
        
    #_url_info, (repo_type, url)
    def _set_url_info(self, url_info):
        try:
            if url_info == None:
                self._url_info = url_info
            #check if it's a valid tuple
            elif type(url_info) == type(()) and len(url_info) == 2:
                if url_info[0] in self.__class__._supported_repository_types:
                    self._url_info = url_info
                else:
                    raise Error.AddonRepositoryTypeError(self, url_info[0], self.__class__._supported_repository_types)
            else:
                raise Error.CommonTypeError("url_info needs to be a tuple with length two or None.")
            
        except (Error.AddonRepositoryTypeError, Error.CommonTypeError) as e:
            print(e)
        
    def _get_url_info(self):
        return self._url_info

    #_folder_name
    def _set_folder_name(self, folder_name):
        assert folder_name != None
        try:
            if type(folder_name) == str:
                self._folder_name = folder_name
            else:
                raise Error.CommonTypeError("addon folder name needs to be a string.")
            
        except Error.CommonTypeError as e:
            print(e)
        
    def _get_folder_name(self):
        return self._folder_name
    
    #'virtual' home
    def _get_home(self):
        return os.path.join(self.root, self.folder_name)
    
    #_protected
    def _get_protected(self):
        return self._protected
    
    def _set_protected(self, protected):
        try:
            if type(protected) == bool:
                self._protected = protected
            elif type(protected) == int: # or type(protected) == long: # for huge numbers
                if protected == 0:
                    self._protected = False
                else:
                    self._protected = True
            else:
                raise Error.CommonTypeError("protected needs to be True or False.")
            
        except Error.CommonTypeError as e:
            print(e)
    
    #'virtual' repo_folder
    def _get_repo_folder(self):
        return os.path.join(self.home, "." + self.url_info[0])
    
    #'virtual' toc_file
    def _get_toc_file(self):
        """
        Returns the name (without the .toc ending) of the first *.toc file found in the home folder. 
        None, if there was no *.toc file found.
        The name of this file and the folder_name have to match.
        Otherwise the World of Warcraft client won't recognize it as a valid addon.
        
        Currently a valid name only contains the following characters [A-Z0-9a-z._-]
        """
        try:
            try:
                #currently returns the first toc file found. There shouldn't be more then one anyway !
                for line in os.listdir(self.home):
                    a = re.match("^([A-Z0-9a-z._-]+).toc$", line)
                    if a:
                        return a.group(1)
                            
            except OSError as e:
                raise Error.CommonOSError(e)

        except Error.CommonOSError as e:
            print(e)

    #'virtual' config_file
    #TODO maybe make it work for more then just the .pkgmeta file, but for now that's good enough
    def _get_config_file(self):
        file = os.path.join(self.home, self.__class__._config_file)
        if os.path.exists(file) and os.path.isfile(file):
            return file
    
    #_config_info
    def _get_config_info(self):
        return self._config_info
    
    #_config_file_parsed
    def _get_config_file_parsed(self):
        return self._config_file_parsed
    
    #seams to work
    #better make this more resilient in the future, with a few proper errors
    #this only works for the .pgkmeta file (in the future we'll maybe have another function for general config files)
    def parse_pkgmeta_file(self):
        """read the .pkgmeta file and return a dict with all the information"""
        if self.config_file:
            tags = self.__class__._config_file_tags
            dict_info = {}
            list_help = []
            cur_tag = None
            
            #sub functions
            def InterpretPKG_DashReader(line):
                if line.startswith(cur_tag):
                    return
                a = re.match("^- ([A-Z0-9a-z_./-]+)", line)
                if a:
                    list_help.append(a.group(1))
            
            def InterpretPKG_ColonReader(tag_index, line):
                a = re.match("^" + tags[tag_index] + ": ([A-Z0-9a-z_./]+)", line)
                if a:
                    dict_info[tags[tag_index]] = a.group(1)
                 
            lines = Reader.Reader.get_instance().read_config(self.config_file)
            
            for line in lines:
                for tag in tags:
                    if not tag in dict_info:
                        dict_info[tag] = None
                        
                    if line.startswith(tag):
                        # if the helper list exists add it to the info dictionary
                        if len(list_help) > 0:
                            dict_info[cur_tag] = list_help
                            list_help = []
                        cur_tag = tag
                        break
            
                if cur_tag == tags[0]:
                    #package-as
                    InterpretPKG_ColonReader(0, line)
                elif cur_tag == tags[1]:
                    #externals
                    if not line.startswith(cur_tag):
                        #out: [folder, url, tag]
                        #there are multiple valid ways to config external libs
                        re_valid_externals = ["^url: ([A-Z0-9a-z_:./-]+)$","^tag: ([A-Z0-9a-z_./-]+)$","^([A-Z0-9a-z_./-]+): ([A-Z0-9a-z_:./-]+)$","^([A-Z0-9a-z_./-]+):$"] # order matters!
                        for pattern in re_valid_externals:
                            a = re.match(pattern, line)
                            if a:
                                if pattern == re_valid_externals[0]:
                                    list_help[len(list_help) - 1][1] = a.group(1)
                                elif pattern == re_valid_externals[1]:
                                    list_help[len(list_help) - 1][2] = a.group(1)
                                elif pattern == re_valid_externals[2]:
                                    list_help.append([a.group(1), a.group(2), None])
                                elif pattern == re_valid_externals[3]:
                                    list_help.append([a.group(1), None, None])
                                break                                
                elif cur_tag == tags[2]:
                    #ignore
                    InterpretPKG_DashReader(line)
                elif cur_tag == tags[3]:
                    #move-folders
                    if not line.startswith(cur_tag):
                        a = re.match("^([A-Z0-9a-z_./-]+): ([A-Z0-9a-z_./-]+)$", line)
                        if a:
                            list_help.append([a.group(1), a.group(2)])    
                elif cur_tag == tags[4]:
                    #required-dependencies
                    InterpretPKG_DashReader(line)
                elif cur_tag == tags[5]:
                    #optional-dependencies
                    InterpretPKG_DashReader(line)
                elif cur_tag == tags[6]:
                    #manual-changelog        
                    InterpretPKG_ColonReader(6, line)
                elif cur_tag == tags[7]:
                    #license-output    
                    InterpretPKG_ColonReader(7, line)
                elif cur_tag == tags[8]:
                    #tools-used
                    InterpretPKG_DashReader(line)
                elif cur_tag == tags[9]:
                    #enable-nolib-creation
                    InterpretPKG_ColonReader(9, line)
                    
            #write the last list_help
            if len(list_help) > 0:
                dict_info[cur_tag] = list_help
                list_help = []
            
            self._config_info = dict_info
            self._config_file_parsed = True
            return True
        
        else:
            #config file missing ! --> Error
            pass
        
    def clean_ignore(self, list_files):
        """
        Delete folders and files mentioned by the config file.
        
        Returns True, if every file/folder mentioned was deleted. None otherwise
        
        """
        try:
            try:
                if self.protected:
                    raise Error.AddonProtectedError(self)
                
                #keep track of files we couldn't delete
                list_not_deleted = []
                
                for file in list_files:
                    #absolute path of the file
                    absolute_file = os.path.join(self.home, file)
                    if os.path.exists(absolute_file) and self._remove_tree(absolute_file):
                        pass #good
                    else:    
                        list_not_deleted.append(file)
                
                if len(list_not_deleted) > 0:
                    raise Error.AddonCleanIgnoreError(self, list_not_deleted)
                
                return True
                
            except OSError as e:
                raise Error.CommonOSError(e)
            
            except (Error.AddonProtectedError, Error.AddonCleanIgnoreError) as e:
                print(e)
                
        except Error.CommonOSError as e:
            print(e)

    def clean_repository_folder(self):
        """
        Deletes the repository folder.
        
        Returns True, if the operation worked or the folder didn't exist in the first place.
        
        """
        try:
            if self.protected:
                raise Error.AddonProtectedError(self)

            if os.path.exists(self.repo_folder):
                #OSError handled by _remove_tree()
                if not self._remove_tree(self.repo_folder):
                    return False
             
            return True
        
        except Error.AddonProtectedError as e:
            print(e)
    
    #public attributes
    root = property(_get_root)
    url_info = property(_get_url_info, _set_url_info)
    name = property(_get_name, _set_name)
    folder_name = property(_get_folder_name, _set_folder_name)
    home = property(_get_home)  
    protected = property(_get_protected, _set_protected)
    
    repo_folder = property(_get_repo_folder)
    toc_file = property(_get_toc_file)
    
    config_file = property(_get_config_file)
    config_info = property(_get_config_info)
    config_file_parsed = property(_get_config_file_parsed)


