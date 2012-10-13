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
import traceback

import Error
import Reader


#TODO add threading support for cloning, with a global class variable to keep track of the cloning instances :D
#like clone() ... do the threading and call renamed function _clone()

#TODO add a find_repo_folder function
#make smart TypeError() parameters or replace them with AddonTypeError(), so all error messages look the same
#NOTE: use a try, except block in the sau.py main function catching AttributeError, in case someone tries to assign a value to a _getter only variable
#TODO replace system errors with my own errors ! for better messages :)

#TODO add function like get_repo_folder


#OSError e.errno, e.filename, e.strerror


class Addon(object):
    """
    Represents a World of Warcraft addon with the following attributes:
        root: the folder containing this addon.
        name: the name of the addon, this can be anything and wont be used for identification
        home: root+folder_name, the main folder of the addon (Note that the home folder + *.toc file need to have the same name.
        url_info: tuple (repo_type, url), type of the repository (currently support: git,svn,hg) and the repository url to update the addon
        folder_name: the actually name of the folder of the addon
        protected: if its a protected addon, it cannot be changed (updated, deleted, cleaned, ...)
    Valid addons are:
        root, url, repo_type
        root, folder_name (the folder with an .toc file has to exist !)
    
    
    """
    #using properties, access variables via self#required for TempFolder_i.home, self.name, self.url, etc.
    #counts the number of addon instances, required for TempFolder_i
    num_addons = 0
    
    #currently supported repository types
    _supported_repository_types = ("git", "svn", "hg")
    
    #in our case always the .pkgmeta file
    _config_file = ".pkgmeta" 
    
    def __init__(self, root=None, url_info=None, folder_name=None, protected=False, name=None):
        #note difference between self._root and self.url_info assignments
        #in the second case the property function _set_url_info is called
        
        try:
            if not root:
                raise Error.AddonRootError()

            if (url_info) or (folder_name):
                self._root = os.path.expanduser(root)   #can't be changed for now
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
        """support function to delete files on the harddisk, check if the deletions happen in the root folder. 
        We dont allow to manipulte folders outside of the addon folder
        This function can remove files, links as well."""
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
            
            except OSError as e:
                raise Error.CommonOSError(e.strerror, e.filename)
            except Error.CommonRemoveTreeError as e:
                print(e)
        except Error.CommonOSError as e:
            print(e)
        

    
    #TODO maybe add some error, that says if the repo didnt exists, or access denied, etc.. -> AddonRepository[...]Error
    #and use the subprocesss exit status
    def clone(self, stderr=None, stdout=None): #stderr=subprocess.STDOUT, stdout=subprocess.PIPE
        """Clones the repo to a local folder."""
        try:
            try:
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
            except subprocess.CalledProcessError as e:
                print(e)
                raise Error.AddonCloneError(self, "subprocess returned non zero exit status")
            except Error.AddonRepositoryTypeError as e:
                print(e)
                raise Error.AddonCloneError(self, "invalid repository type used")
            except Error.AddonProtectedError as e:
                print(e)
                raise Error.AddonCloneError(self, "addon folder already exists and is protected")
        except Error.AddonCloneError as e:
            print(e)
            
    
    #TODO add protected support
    #check if adoon folder and/or repo folder exists        
    #TODO add protected support
    #something with the errors aint working at all ...
    def update(self, stderr=None, stdout=None): #stderr=subprocess.STDOUT, stdout=subprocess.PIPE
        """Updates an existing repo."""
        
        try:
            try:
                #check if its protected
                if self.protected:
                    raise Error.AddonProtectedError(self)
                
                #check for the repo folder exists
                if not os.path.exists(self.repo_folder):
                    raise Error.AddonRepositoryFolderError(self)
                
                try:
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
                
                except OSError as e:
                    raise Error.CommonOSError(e.strerror, e.filename)
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
                raise Error.AddonUpdateError(self, "an OSError occurred")
            except Error.AddonUpdateError as e:
                print(e)
            
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
                raise TypeError("TypeError=_set_name")
        except TypeError as e:
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
                #TODO add smart parameter to TypeError() - like expecting a 2er tuple in _set_url_info
                raise TypeError("TypeError=_set_url_info")
        except TypeError as e:
            print(e)
        except Error.AddonRepositoryTypeError as e:
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
                raise TypeError("TypeError=_set_folder_name")
        except TypeError as e:
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
                raise TypeError("TypeError=_set_protected")
        except TypeError as e:
            print(e)
    
    #'virtual' repo_folder
    def _get_repo_folder(self):
        return os.path.join(self.home, "." + self.url_info[0])
    
    
    #'virtual' config_file
    #TODO maybe make it work for more then just the .pkgmeta file, but for now that's good enough
    def _get_config_file(self):
        """Can also be used to check if config_file exists, if the function returns None, it doesn't"""
        file = os.path.join(self.home, self.__class__._config_file)
        if os.path.exists(file) and os.path.isfile(file):
            return file
    
    #_config_info
    def _get_config_info(self):
        return self._config_info
    
    #_config_file_parsed
    def _get_config_file_parsed(self):
        return self._config_file_parsed
    
    #this only works for the .pgkmeta file (in the future we'll maybe have another function for general config files)
    def parse_pkgmeta_file(self):
        """read the .pkgmeta file and return a dict with all the information"""
        if self.HasPkgFile():
            tags = ["package-as", "externals", "ignore", "move-folders", "required-dependencies", "optional-dependencies", "manual-changelog", "license-output", "tools-used", "enable-nolib-creation"]
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
                 
            lines = Reader.Reader.get_instance().read_config(self.GetPkgFileDir())
            
            for line in lines:
                for tag in tags:
                    if not tag in dict_info:
                        dict_info[tag] = None
                        pass
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
    
    def is_save_path(self):
        #check if the tree we want to delete is in the root dir
        pass
    
    
    #TODO rename to _get_toc_file_name ?    
    def find_toc_file(self):
        """
        Returns the name of the first .toc file found in the home folder.
        The name of this file and the folder_name have to match in order to work ( so wow detects it as a valid addon)
        """
        try:
            #currently returns the first toc file found. There shouldn't be more then one anyway !
            for line in os.listdir(self.home):
                a = re.match("^([A-Z0-9a-z._-]+).toc$", line)
                if a:
                    return a.group(1)
            raise Error.AddonMissingTocFileError(self)
        except OSError as e:
            print(e)
        except Error.AddonMissingTocFileError as e:
            print(e)
    
    #pointless, just check if the "." + url_info[0] folder exitsts in the home folder of the addon
    #pretty much replaced with _get_repo_folder()
    def find_repository_folder(self):
        """
        Returns the found repo folder, otherwise None (if there is more then one or none)
        """
        try:
            repo_folder = []
            for file in os.listdir(self.home):
                if file in [ "." + str(repo_type) for repo_type in self.__class__._supported_repository_types]:
                    if file not in repo_folder:
                        repo_folder.append(file)
            if len(repo_folder) == 1:
                return repo_folder[0]
            else:
                raise Error.AddonMultipleRepoFoldersError(self)
        except (OSError, Error.AddonMultipleRepoFoldersError) as e:
            print(e)
           
    
    
    #TODO check if it does what we want ;d
    def clean_ignore(self, list_files):
        """Delete folders and files mentioned by the .pkgmeta file"""
        if not self.protected:
            for file in list_files:
                try:
                    pass
                except IOError as e:
                    print("({})".format(e))
    
                if os.path.isfile(file):
                    os.remove(os.path.join(self.GetAddonDir(), file))
                elif os.path.exists(file):
                    #shutil.rmtree(os.path.join(self.GetAddonDir(), file))
                    pass

    #TODO check if it does what we want ;d
    def clean_repository_folder(self):
        """Deletes the repo folder. like .git or .svn"""
        if not self.protected:
            if self.HasRepoFolder() and self.GetRepoDir().startswith(self.GetHome()):
                #shutil.rmtree(self.GetRepoDir())
                pass
    
    #public attributes
    root = property(_get_root)
    url_info = property(_get_url_info, _set_url_info)
    name = property(_get_name, _set_name)
    folder_name = property(_get_folder_name, _set_folder_name)
    home = property(_get_home)  
    protected = property(_get_protected, _set_protected)
    
    repo_folder = property(_get_repo_folder)
    
    config_file = property(_get_config_file)
    config_info = property(_get_config_info)
    config_file_parsed = property(_get_config_file_parsed)




#a = Addon("/home/share/Development/AddOns/", ("git", "git://git.wowace.com/wow/pitbull4/mainline.git"))
a = Addon("/home/share/Development/AddOns/", None, "test")
#print(a.find_toc_file())
