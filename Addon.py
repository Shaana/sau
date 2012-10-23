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
import sys
#import threading

import Error
import Reader
import Message

#TODO add threading support for cloning, with a global class variable to keep track of the cloning instances :D

#TODO rework parse_pkgmeta_file()
#TODO add os.path.userexpand() to urls, files, etc.
#TODO check if its an absolute path, does the url start with a '/' ?


class Addon(object):
    """
    This represents a World of Warcraft addon. This class allows to update/clone addon repositories
  
    It is recommend to embed your code into a try, except block to catch AttributeError 
    in case you assign a value to a _getter only variable.
    
    Every _get_* function return None if the variable doesn't exist.
   
    """
    
    _message = Message.Message("Addon", True)
    
    #TODO yet to be implemented
    _enable_clone_threading = False
    _enable_update_threading = False
    
    #counter for unique TmpFolder names
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
        
        #raise: Error.AddonRootError , Error.AddonInitError
        """
        
        #note difference between self._root and self.url_info assignments
        #in the second case the property function _set_url_info is called
        
        try:
            if not root:
                raise Error.AddonRootError()

            if (url_info) or (folder_name):
                #TODO check if its an absolute path, does the url start with a '/' ?
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
        return self.name + ": " + str(self.protected)
    
    #TODO add ignore case when comparing urls ! (and repo_type)
    def __eq__(self, other):
        """
        Addons are considered the same if the repot_type and url are the same. (tailing '/' are stripped for comparison)
        If not two url_infos are given, we use the both folder_names and compare them.
        
        It's only possible to compare two Addon objects.
        
        Note: If we both url_infos and both folder_names are given, we only use the url_info to compare them and ignore the folder_names.
        
        @param other: another addon object to compare to
        @type other: Addon
        """
        #basic variables to compare  
        repo_type_1 = None
        repo_type_2 = None
        url_1 = None
        url_2 = None
        folder_name_1 = self.folder_name
        folder_name_2 = other.folder_name
          
        if self.url_info:
            repo_type_1 = self.url_info[0]
            url_1 = self.url_info[1].rstrip("/") #.lower()
    
        if other.url_info:
            repo_type_2 = other.url_info[0]
            url_2 = other.url_info[1].rstrip("/") #.lower()

        #if both url_infos and both folder_names are given, the folder_names DON'T have to match.
        if url_1 and url_2:
            if repo_type_1 == repo_type_2 and url_1 == url_2:
                return True
        #if we don't have two url_infos, compare the folder_names
        elif folder_name_1 and folder_name_2 and not (url_1 and url_2):
            if folder_name_1 == folder_name_2:
                return True
        
    def __ne__(self, other):
        if not self.__eq__(other):
            return True
        else:
            return False
    
    def message(self, message, display_tag=True, end="\n"):
        """
        Use this function to display messages in the console.
        
        @param message: the message
        @type message: str
        @param display_tag: show the message tag [tag]: message
        @type display_tag: bool
        @param end: the string to be added at the end of the message
        @type end: str
        
        """
        self.__class__._message.print_message(str(message), display_tag, end)
    
    def message_ok(self):
        """
        calling self.message with special parameters.
        set end="" in the previous message to make it appear on the same line.
        """
        self.message(" [{yellow}ok{end}]".format(**Message.Color.colors), display_tag=False)
    
    def message_fail(self):
        """
        calling self.message with special parameters.
        set end="" in the previous message to make it appear on the same line.
        """
        self.message(" [{red}fail{end}]".format(**Message.Color.colors), display_tag=False)
    
    def _remove_tree(self, file):
        """
        A little support function to delete directories/files/links.
        Deleting files is only possible within the addon root folder.
        
        returns True, if everything worked. None otherwise
        
        @param file: file or folder (absolute path) to be removed recursively
        @type file: str
        
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
    
       
    def clone(self, stderr=subprocess.STDOUT, stdout=subprocess.PIPE): #stderr=None, stdout=None
        """Clones the given remote repository to a local folder."""
        #TODO add threading support here
        return self._clone(stderr, stdout)

    #TODO maybe add some error, that says if the repo didnt exists, or access denied, etc.. -> AddonRepository[...]Error
    #and use the subprocesss exit status
    def _clone(self, stderr=None, stdout=None): #stderr=subprocess.STDOUT, stdout=subprocess.PIPE
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
                        
                subprocess_exit_status = 0
                #using self.url_info[0] instead of self.repo_type, we checked if it exists
                if self.url_info[0] == "git":
                    subprocess_exit_status = subprocess.call(["git", "clone", self.url_info[1], self.home], stderr=stderr, stdout=stdout)
                elif self.url_info[0] == "svn":
                    subprocess_exit_status = subprocess.call(["svn", "checkout", self.url_info[1], self.home], stderr=stderr, stdout=stdout)
                elif self.url_info[0] == "hg":
                    subprocess_exit_status = subprocess.call(["hg", "clone", self.url_info[1], self.home], stderr=stderr, stdout=stdout)
                else:
                    #this should never every happen, since the _set_url_info is checking the repo_type already !
                    raise Error.AddonRepositoryTypeError(self, self.url_info[0], self.__class__._supported_repository_types)
                
                return subprocess_exit_status
                
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
 
    def update(self, stderr=None, stdout=None):
        """Updates the repository in an existing addon folder."""
        #TODO add threading support here
        return self._update(stderr,stdout)
      
    def _update(self, stderr=None, stdout=None): #stderr=subprocess.STDOUT, stdout=subprocess.PIPE
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
                    subprocess_exit_status = 0
                    if self.repo_type == "git":
                        subprocess_exit_status = subprocess.call(["git", "pull"], stderr=stderr, stdout=stdout)
                    elif self.repo_type == "svn":
                        subprocess_exit_status = subprocess.call(["svn", "update", self.home], stderr=stderr, stdout=stdout)
                    elif self.repo_type == "hg":
                        subprocess_exit_status = subprocess.call(["hg", "pull"], stderr=stderr, stdout=stdout)
                        if subprocess_exit_status != 0:
                            #TODO raise some error, if first part already failed
                            subprocess_exit_status= subprocess.call(["hg", "update"], stderr=stderr, stdout=stdout)
                    else:
                        #this should never every happen, since the _set_url_info is checking the repo_type already !
                        raise Error.AddonRepositoryTypeError(self, self.url_info[0], self.__class__._supported_repository_types)
                
                    return subprocess_exit_status
                
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
        """
        @param name: addon name
        @type name: str
        """
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
        """
        @param name: (repo_type, url)
        @type name: tuple
        """
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
        """
        @param folder_name: only the folder_name of the addon (NOT a path!)
        @type folder_name: str
        """
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
        """
        @param protected: protected addons can't be modified
        @type protected: bool
        """
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
    #TODO check
    def _get_repo_folder(self):
        """
        if no url_info is given, it checks the home folder for a repo folder.
        if not successful, it returns None
        """
        if self.url_info:
            return os.path.join(self.home, "." + self.url_info[0])
        else:
            if self.repo_type:
                return os.path.join(self.home, "." + self.repo_type)
    
    #'virtual' repo_type
    def _get_repo_type(self):
        """
        If there is no url_info given, we parse the home folder for repo_folders
        First one found will be the repo_type
        """
        if self.url_info:
            return self.url_info[0]
        else:
            try:
                try:
                    for file in os.listdir(self.home):
                        for repo_type in self.__class__._supported_repository_types:
                            if file == "." + repo_type:
                                return repo_type
                            
                except OSError as e:
                    raise Error.CommonOSError(e)
            
            except Error.CommonOSError as e:
                print(e)
    
    #'virtual' toc_file
    def _get_toc_file_name(self):
        """
        Returns the name (without the .toc ending) of the first *.toc file found in the home folder. 
        None, if there was no *.toc file found.
        The name of this file and the folder_name have to match.
        Otherwise the World of Warcraft client won't recognize it as a valid addon.
        
        Currently a valid name only contains the following characters [A-Z0-9a-z.!_-]
        """
        try:
            try:
                #currently returns the first toc file found. There shouldn't be more then one anyway !
                for line in os.listdir(self.home):
                    a = re.match("^([A-Z0-9a-z.!_-]+).toc$", line)
                    if a:
                        return a.group(1)
                            
            except OSError as e:
                raise Error.CommonOSError(e)

        except Error.CommonOSError as e:
            print(e)

    #'virtual' config_file
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
    #this only works for the .pgkmeta file (in the future we'll maybe have another function for more general config files)
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
    
    def parse_home_for_url_info(self):
        """
        gets the url_info from an given folder_name, if it exists.
        The Addon class works completly without this function.
        """
        #There is two ways to do this. Either read from the config files directly or run a subprocess and then regex the output
        #For now we only use the 2nd method.
        #git: .git/config:8:    url = git://git.wowace.com/wow/pitbull4/mainline.git
        #svn: .svn/entries -->take first url ?  
        #hg: .hg/hgrc:2:default = http://hg.curseforge.net/wow/gnosis/mainline

        try:
            try:
                dict_repo = {"git" : ("origin\s*([A-Z0-9a-z:./_~.-]+)\s*\(fetch\)", ["git", "remote", "-v"]),
                             "svn" : ("URL:\s*([A-Z0-9a-z:./_~.-]+)", ["svn", "info"]),
                             "hg" : ("default\s*=\s*([A-Z0-9a-z:./_~.s-]+)", ["hg", "paths"])}
                
                #we don't want to overwrite an existing url_info
                if self.url_info:
                    raise Error.AddonUrlOverwriteError(self)
                
                if self.repo_folder:
                    os.chdir(self.home)
                    repo_type = self.repo_type
                    output = subprocess.check_output(dict_repo[repo_type][1])
                    match = re.search(dict_repo[repo_type][0], str(output, sys.stdout.encoding)) 
                    if match:
                        self.url_info = (repo_type, match.group(1))
                        
                return True
                            
            except OSError as e:
                raise Error.CommonOSError(e)
            
            except (subprocess.CalledProcessError, Error.AddonUrlOverwriteError) as e:
                print(e)
            
        except Error.CommonOSError as e:
            print(e)
            
    #TODO make smarter !
    #add something to catch u:svn://svn.wowace.com/wow/callbackhandler/mainline/tags/1.0.3/CallbackHandler-1.0:
    #u:git://git.wowace.com/wow/drdata-1-0/mainline.git
    #u:git://git.wowace.com/wow/drdata-1-0/mainline
    #even if the .git is missing, consider them the same and remove the one without git
    # do something about libdatabroker-1-1, doesnt seam to come with .toc file
    def enhance_url_info(self):
        try:
            assert self.url_info != None
            assert self.protected == False
            
            if self.repo_type == "svn":
                match = re.match("^(.+?/trunk)/.+$", self.url_info[1])
                if match:
                    self.url_info = ("svn", match.group(1))
            
            return True
            
        except Exception as e:
            print(e)
      
    #make sure every situation is covered.
    #TODO test
    #add an option, remove addons if full renameing failed or keep them in the temp_folder
    #todo implement option clean_repo=
    def execute(self, allow_overwrite=False, update_only=False, clone_only=False, clean_repo=False):
        """
        run the addon update/clone
        
        @param allow_overwrite: allow to overwrite an existing folder. Should the cloned addon match this existing folder (after rename) 
        @type allow_overwrite: bool
        
        """
        try:
            try:
                try:
                    if not clone_only and self.repo_folder and os.path.exists(self.repo_folder): #not checking if the home exists firs (pointless)
                        self.message("Updating addon '{blue}{0}{end}'...".format(self.name, **Message.Color.colors)) #end=""
                        if self.update() != 0:
                            self.message_fail()
                            raise Error.AddonExecuteError(self, "update() returned non zero exit status")
                        
                        self.message_ok()
                        
                    elif not update_only and self.url_info:
                        self.message("Cloning addon '{blue}{0}{end}'...".format(self.name, **Message.Color.colors)) #end=""
                        
                        if self.clone() != 0:
                            self.message_fail()
                            raise Error.AddonExecuteError(self, "clone() returned non zero exit status")
                            
                        toc_file_name = self.toc_file_name
                        
                        if not toc_file_name:
                            self.message_fail()
                            #self._remove_tree(self.home)
                            raise Error.AddonExecuteError(self, "toc file name is None, can't continue")
                        
                        new_folder = os.path.join(self.root, toc_file_name)
                        if self.folder_name != toc_file_name:
                            #Note: On Unix, if dst exists and is a file, it will be replaced silently if the user has permission.
                            #rename folder, change self.folder_name
    
                            if os.path.exists(new_folder) and allow_overwrite:
                                self._remove_tree(new_folder)
                                os.rename(self.home, new_folder)
                                self.folder_name = toc_file_name
                              
                            elif os.path.exists(new_folder) and not allow_overwrite:
                                self.message_fail()
                                #self._remove_tree(self.home)
                                raise Error.AddonExecuteError(self, "not allowed to overwrite existing new_home_folder, therefor cannot rename")
    
                            else:
                                os.rename(self.home, new_folder)
                                self.folder_name = toc_file_name
                            
                        self.message_ok()
                        #TODO test, fix, implement
                        #if clean_repo:
                        #    self.clean_repository_folder()
                        return True
        
                    else:
                        raise Error.AddonExecuteError("no url given nor was any repo_folder found")
    
                except OSError as e:
                    raise Error.CommonOSError(e)
                
            except Error.CommonOSError as e:
                print(e)
                raise Error.AddonExecuteError(self, "OSError occured")
        
        except Error.AddonExecuteError as e:
            print(e)
        
    def clean_ignore(self, list_files):
        """
        Delete folders and files mentioned by the config file.
        
        Returns True, if every file/folder mentioned was deleted. None otherwise
        
        @param list_files: list of folder_names, file_names to be deleted (NOT paths!)
        @type list_files: list
        
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
    
    #TODO add a return to see if it worked
    def _crawl_directory(self, home, delete_name):
        """
        Search recursivly in the root for any folder matching the folder_name and delete it.
        """
        for folder_name in os.listdir(home):
            folder = os.path.join(home, folder_name)
            if os.path.isdir(folder):
                if folder_name == delete_name:
                    self._remove_tree(folder)
                else:
                    self._crawl_directory(folder, delete_name)
    
    def clean_repository_folder(self):
        """
        Deletes the repository folder.
        
        Returns True, if the operation worked or the folder didn't exist in the first place.
        
        """
        try:
            if self.protected:
                raise Error.AddonProtectedError(self)
            
            if self.repo_type == "svn":
                self._crawl_directory(self.home, ".svn")
                
            else:
                if os.path.exists(self.repo_folder):
                    #OSError handled by _remove_tree()
                    if not self._remove_tree(self.repo_folder):
                        return False
             
            return True
        
        except Error.AddonProtectedError as e:
            print(e)
        
    def clean_home(self):
        """
        delete the whole addon folder for a clean new install.
        """
        try:
            if self.protected:
                raise Error.AddonProtectedError(self)

            if os.path.exists(self.home):
                #OSError handled by _remove_tree()
                if not self._remove_tree(self.home):
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
    repo_type = property(_get_repo_type)
    toc_file_name = property(_get_toc_file_name)
    
    config_file = property(_get_config_file)
    config_info = property(_get_config_info)
    config_file_parsed = property(_get_config_file_parsed)


