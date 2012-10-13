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

import traceback

import Message
import Addon

# Error
#   -AddonError
#        - ...
#   -AddonListError
#        - ...
#   -CommonError
#        - ...

def is_module(name):
    if name == "<module>":
        return name
    else:
        return name + "()" # to make clear its a function

class Error(Exception):
    
    _debug = False
    
    def __init__(self, msg, error_name):
        self.error_name = error_name
        self.msg = "{red}Error{end} [{yellow}{0}{end}]: {1}".format(self._error_name, msg, **Message.Color.colors)
        if self.__class__._debug:
            #Traceback
            self.msg += "\n({green}debug{end}::{green}traceback{end})".format(**Message.Color.colors)
            for trace in traceback.extract_stack():
                #only trace it back until we call *Error.__init__(), from there we know where it's going.
                if trace[3].find("Error.__init__") > -1:
                    break
                self.msg += "\n {purple}{0}{end}:{yellow}{1}{end} in {blue}{2}{end}".format(trace[0],trace[1],is_module(trace[2]),**Message.Color.colors)
                self.msg += "\n    {0}".format(trace[3])
        Exception.__init__(self, self.msg)
    
    #def __str__(self):
    #    return self.msg
    
    def _set_addon(self, addon):
        try:
            if type(addon) != Addon:
                raise AddonTypeError(addon, type(addon), Addon)
            self._addon = addon
        except AddonTypeError as e:
            print(e)
    
    def _get_addon(self):
        return self._addon
        
    def _set_msg(self, msg):
        #TODO check if its a string
        self._msg = msg
    
    def _get_msg(self):
        return self._msg
    
    def _set_error_name(self, error_name):
        self._error_name = error_name
        
    def _get_error_name(self):
        return self._error_name

    addon = property(_get_addon, _set_addon)
    msg = property(_get_msg, _set_msg)
    error_name = property(_get_error_name, _set_error_name)


class CommonError(Error):
    """basically just call the normal Error classes like TypeError, but make them look nicer."""
    def __init__(self, msg, error_name):
        Error.__init__(self, self.msg, self.error_name)
        

#todo: not done 
class CommonTypeError(CommonError):
    
    def __init__(self, msg, error_name):
        CommonError.__init__(self, self.msg, self.error_name)

     
class CommonOSError(CommonError):
    
    def __init__(self, str_error, file_name):
        self.error_name = "CommonOSError"
        self.msg = "{0}: '{blue}{1}{end}'.".format(str_error, file_name, **Message.Color.colors)
        CommonError.__init__(self, self.msg, self.error_name)
        



class CommonRemoveTreeError(CommonError):
    
    def __init__(self, root, file):
        self.error_name = "CommonRemoveTreeError"
        self.msg = "Unable to delete '{blue}{0}{end}', because it's not a subfolder/subfile of the addon root '{blue}{1}{end}' directory.".format(file, root, **Message.Color.colors)
        CommonError.__init__(self, self.msg, self.error_name)
        
       
        

class AddonError(Error):
    
    def __init__(self, msg, error_name):
        self.error_name = error_name
        self.msg = msg
        Error.__init__(self, self.msg, self.error_name)


#TODO not done yet
class AddonListError(Error):
    
    def __init__(self, msg, error_name):
        self.error_name = error_name
        self.msg = msg
        Error.__init__(self, self.msg, self.error_name)


class AddonRootError(AddonError):
    
    def __init__(self):
        self.error_name = "AddonRootError"
        self.msg = "No root folder given for addon.".format(**Message.Color.colors)
        AddonError.__init__(self, self.msg, self.error_name)

class AddonInitError(AddonError):

    def __init__(self):
        self.error_name = "AddonInitError"
        self.msg = "Addon initialization failed. Provide at least a (repo_type, url) tuple or an addon_folder.".format(**Message.Color.colors)
        AddonError.__init__(self, self.msg, self.error_name)

class AddonProtectedError(AddonError):

    def __init__(self, addon):
        self.error_name = "AddonProtectedError"
        self.msg = "Addon '{blue}{0}{end}' is protected and therefore can not be modified in any way (clone, update, clear_ignore, clear_repo)".format(addon.name, **Message.Color.colors)
        AddonError.__init__(self, self.msg, self.error_name)


class AddonRepositoryTypeError(AddonError):
    
    def __init__(self, addon, used_type, supported_types):
        self.error_name = "AddonRepositoryTypeError"
        self.msg = "'{blue}{0}{end}' is not a supported respository type for addon '{blue}{1}{end}', Use '{blue}{2}{end}' instead.".format(used_type, addon.name, supported_types, **Message.Color.colors)
        AddonError.__init__(self, self.msg, self.error_name)


class AddonRepositoryFolderError(AddonError):
    
    def __init__(self, addon):
        self.error_name = "AddonRepositoryFolderError"
        self.msg = "The repository folder '{blue}{0}{end}' doesn't exists for addon '{blue}{1}{end}'.".format(addon.repo_folder, addon.name, **Message.Color.colors)
        AddonError.__init__(self, self.msg, self.error_name)


class AddonCloneError(AddonError):

    def __init__(self, addon, reason):
        self.error_name = "AddonCloneError"
        self.msg = "Cloning from repository '{blue}{0}{end}' ({purple}{1}{end}) failed for addon '{blue}{2}{end}' ({purple}{3}{end}).".format(addon.url_info[1], addon.url_info[0], addon.name, reason, **Message.Color.colors)
        AddonError.__init__(self, self.msg, self.error_name)

class AddonUpdateError(AddonError):

    def __init__(self, addon, reason):
        self.error_name = "AddonUpdateError"
        self.msg = "Updating addon '{blue}{0}{end}' ({purple}{1}{end}) failed.".format(addon.name, reason, **Message.Color.colors)
        AddonError.__init__(self, self.msg, self.error_name)



#TODO !
class AddonHomelessError(AddonError):
       
    def __init__(self, addon, reason):
        self.error_name = "AddonHomelessError"
        self.msg = "Updating addon '{blue}{0}{end}' ({1}).".format(addon.name, reason, **Message.Color.colors)
        AddonError.__init__(self, self.msg, self.error_name)

#TODO
class AddonTocFileError(AddonError):

    def __init__(self, addon, reason):
        self.error_name = "AddonTocFileError"
        self.msg = "Updating addon '{blue}{0}{end}' ({1}).".format(addon.name, reason, **Message.Color.colors)
        AddonError.__init__(self, self.msg, self.error_name)




#TODO addon something like for addon (name)
class AddonTypeError(AddonError):
    
    def __init__(self, given_type, expected_type):
        #self.addon = addon #TODO piss, does this work so ?
        self.error_name = "AddonTypeError"
        self.msg = "Type '{blue}{0}{end}' used, was expecting '{blue}{1}{end}'.".format(given_type, expected_type, **Message.Color.colors)
        AddonError.__init__(self, self.msg, self.error_name)







class AddonListAddError(AddonListError):
    pass

class AddonListExtendError(AddonListError):
    pass

class AddonListRemoveError(AddonListError):
    pass
    
class InvalidLineInConfigFileError(AddonListError):
    
    def __init__(self, file, line):
        self.file = file
        self.line = line
        
    def __str__(self):
        pass
        #return self.prefix + "Invalid line in file \'{0}\', line {1}".format(bcolors.YELLOW + self.file + bcolors.END, bcolors.YELLOW + str(self.line) + bcolors.END)
