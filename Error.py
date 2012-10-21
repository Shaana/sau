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


#TODO maybe rework CommonTypeError to be more colorful and accept more args, like given_type, expected type, etc.
# or even make it work both ways 

#TODO add a  self.addon = addon to every error, this checks if its type Addon

def enhance_addon_name(addon):
    protected_tag = ""
    if addon.protected:
        protected_tag += "{red}!"
        
    return (protected_tag + "{blue}{0}{end}").format(addon.name, **Message.Color.colors)

def color_list(l, color):
    """
    Input: list
    returns a colorful list for Error messages.
    """
    #
    pass

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
            if type(addon) != Addon.Addon:
                self._addon = None
                raise CommonTypeError(None, type(addon), Addon.Addon)
            
            self._addon = addon
            
        except CommonTypeError as e:
            print(e)
            assert type(addon) == Addon.Addon
    
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



###CommonError

class CommonError(Error):
    """basically just call the normal Error classes like TypeError, but make them look nicer."""
    def __init__(self, msg, error_name):
        Error.__init__(self, self.msg, self.error_name)
        

#Todo change, to accept lists of types as well
class CommonTypeError(CommonError):
    
    def __init__(self, error, given_type=None, expected_type=None):
        self.error_name = "CommonTypeError"
        if given_type and expected_type:
            self.msg = "Type '{blue}{0}{end}' used, was expecting '{blue}{1}{end}'.".format(given_type, expected_type, **Message.Color.colors)
        else:
            self.msg = "'{0}'.".format(error, **Message.Color.colors)
        CommonError.__init__(self, self.msg, self.error_name)
     
class CommonOSError(CommonError):
    
    def __init__(self, error):
        self.error_name = "CommonOSError"
        self.msg = "{0}: '{blue}{1}{end}'.".format(error.strerror, error.filename, **Message.Color.colors)
        CommonError.__init__(self, self.msg, self.error_name)
        

class CommonRemoveTreeError(CommonError):
    
    def __init__(self, root, file):
        self.error_name = "CommonRemoveTreeError"
        self.msg = "Unable to delete '{blue}{0}{end}', because it's not a subfolder/subfile of the addon root '{blue}{1}{end}' directory.".format(file, root, **Message.Color.colors)
        CommonError.__init__(self, self.msg, self.error_name)
        
       
       
###AddonError        

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
        self.addon = addon
        self.error_name = "AddonProtectedError"
        self.msg = "Addon '{0}' is protected and therefore can not be modified in any way (clone, update, clear_ignore, clear_repo, clean_home, ...)".format(enhance_addon_name(self.addon), **Message.Color.colors)
        AddonError.__init__(self, self.msg, self.error_name)


class AddonUrlError(AddonError):

    def __init__(self, addon):
        self.addon = addon
        self.error_name = "AddonUrlError"
        self.msg = "No url given for addon '{0}'.".format(enhance_addon_name(self.addon), **Message.Color.colors)
        AddonError.__init__(self, self.msg, self.error_name)


class AddonRepositoryTypeError(AddonError):
    
    def __init__(self, addon, used_type, supported_types):
        self.addon = addon
        self.error_name = "AddonRepositoryTypeError"
        self.msg = "'{blue}{0}{end}' is not a supported respository type for addon '{1}', Use '{blue}{2}{end}' instead.".format(used_type, enhance_addon_name(self.addon), supported_types, **Message.Color.colors)
        AddonError.__init__(self, self.msg, self.error_name)


class AddonRepositoryFolderError(AddonError):
    
    def __init__(self, addon):
        self.addon = addon
        self.error_name = "AddonRepositoryFolderError"
        self.msg = "The repository folder '{blue}{0}{end}' doesn't exists for addon '{1}'.".format(addon.repo_folder, enhance_addon_name(self.addon), **Message.Color.colors)
        AddonError.__init__(self, self.msg, self.error_name)


class AddonCloneError(AddonError):

    def __init__(self, addon, reason):
        self.addon = addon
        self.error_name = "AddonCloneError"
        if addon.url_info:
            self.msg = "Cloning from repository '{blue}{0}{end}' ({purple}{1}{end}) failed for addon '{2}' ({purple}{3}{end}).".format(addon.url_info[1], addon.url_info[0], enhance_addon_name(self.addon), reason, **Message.Color.colors)
        else:
            self.msg = "Cloning from repository '{blue}{0}{end}' ({purple}{1}{end}) failed for addon '{2}' ({purple}{3}{end}).".format("None", "None", enhance_addon_name(self.addon), reason, **Message.Color.colors)
        AddonError.__init__(self, self.msg, self.error_name)


class AddonUpdateError(AddonError):

    def __init__(self, addon, reason):
        self.addon = addon
        self.error_name = "AddonUpdateError"
        self.msg = "Updating addon '{0}' failed ({purple}{1}{end}).".format(enhance_addon_name(self.addon), reason, **Message.Color.colors)
        AddonError.__init__(self, self.msg, self.error_name)


class AddonExecuteError(AddonError):

    def __init__(self, addon, reason):
        self.addon = addon
        self.error_name = "AddonExecuteError"
        self.msg = "Executing addon '{0}' failed ({purple}{1}{end}).".format(enhance_addon_name(self.addon), reason, **Message.Color.colors)
        AddonError.__init__(self, self.msg, self.error_name)


class AddonCleanIgnoreError(AddonError):

    def __init__(self, addon, list_files):
        self.addon = addon
        self.error_name = "AddonCleanIgnoreError"
        self.msg = "The file(s) '{blue}{0}{end}' could not be deleted for addon '{1}'.".format(list_files, enhance_addon_name(self.addon), **Message.Color.colors)
        AddonError.__init__(self, self.msg, self.error_name)


class AddonUrlOverwriteError(AddonError):

    def __init__(self, addon):
        self.addon = addon
        self.error_name = "AddonUrlOverwriteError"
        self.msg = "url_info already exists for addon '{0}'.".format(enhance_addon_name(self.addon), **Message.Color.colors)
        AddonError.__init__(self, self.msg, self.error_name)



###AddonListError  

class AddonListRootError(AddonListError):
    
    def __init__(self):
        self.error_name = "AddonListRootError"
        self.msg = "No root folder given for addon list.".format(**Message.Color.colors)
        AddonListError.__init__(self, self.msg, self.error_name)


class AddonListNameError(AddonListError):
    
    def __init__(self):
        self.error_name = "AddonListNameError"
        self.msg = "No name given for addon list.".format(**Message.Color.colors)
        AddonListError.__init__(self, self.msg, self.error_name)


#TODO rename to AddonListAddError() to make it more clear ?
class AddonListColisionError(AddonListError):
    
    def __init__(self, addon_list, addon):
        #use self.name to specify the list
        self.addon = addon
        self.error_name = "AddonListColisionError"
        self.msg = "Addon '{0}' alredy exists in AddonList '{blue}{1}{end}'.".format(enhance_addon_name(self.addon), addon_list.name, **Message.Color.colors)
        AddonListError.__init__(self, self.msg, self.error_name)


class AddonListRemoveError(AddonListError):
    
    def __init__(self, addon_list, addon):
        self.addon = addon
        self.error_name = "AddonListRemoveError"
        self.msg = "Could not remove addon '{0}', because it's not in the addon_list '{blue}{1}{end}'".format(enhance_addon_name(self.addon), addon_list.name, **Message.Color.colors)
        AddonListError.__init__(self, self.msg, self.error_name)


#TODO, change to show the first few elements of the wrong list ?
class AddonListExtendError(AddonListError):

    def __init__(self, addon_list, list_addons):
        self.error_name = "AddonListExtendError"
        self.msg = "invalid list_extend given for addon_list '{blue}{0}{end}'".format(addon_list.name, **Message.Color.colors)
        AddonListError.__init__(self, self.msg, self.error_name)


#needed? so far never raised
class AddonListMergeError(AddonListError):

    def __init__(self, addon_list, reason):
        self.error_name = "AddonListMergeError"
        self.msg = "AddonList merged failed ({purple}{0}{end})".format(reason, **Message.Color.colors)
        AddonListError.__init__(self, self.msg, self.error_name)


class AddonListMergeRootError(AddonListError):

    def __init__(self, addon_list, other_list):
        self.error_name = "AddonListMergeRootError"
        self.msg = "AddonList root '{blue}{0}{end}' ({purple}{1}{end}) doesn't match '{blue}{2}{end}' ({purple}{3}{end}). Only AddonLists with the same root can be merged.".format(addon_list.root, addon_list.name, other_list.root, other_list.name, **Message.Color.colors)
        AddonListError.__init__(self, self.msg, self.error_name)


class AddonListMergeModeError(AddonListError):

    def __init__(self, addon_list,  mode, list_valid_modes):
        self.error_name = "AddonListMergeModeError"
        self.msg = "Invalid merge mode '{blue}{0}{end}', use '{blue}{1}{end}'".format(mode, list_valid_modes, **Message.Color.colors)
        AddonListError.__init__(self, self.msg, self.error_name)


