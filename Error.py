#!/usr/bin/env python

from bcolors import bcolors

class Error(Exception):
    prefix = bcolors.RED + "Error:" + bcolors.END + " "
    
    def __init__(self, addon):
        self.addon = addon
    

class AddonRootError(Error):
    
    def __str__(self):
        return self.__class__.prefix + "Not given a root folder for the addon '{0}'. The root folder is the folder in which all addons lie.".format("")


class AddonNotSupportedRepoTypeError(Error):
    
    def __init__(self, addon, used_type, supported_types):
        self.used_type = used_type
        self.supported_types = supported_types
    
    def __str__(self):
        return self.__class__.prefix + "'{0}' is not a supported type, Use {1} instead.".format(self.used_type, self.supported_types)


class AddonInitError(Error):

    def __str__(self):
        return self.__class__.prefix + "Could not init addon, provide at least the url_info tuple or an addon_folder."


class AddonMissingTocFileError(Error):

    def __str__(self):
        return self.__class__.prefix + "Could not find a .toc file in the addon folder '{0}'".format(self.addon.home)


class AddonCloneError(Error):

    def __str__(self):
        return self.__class__.prefix + "When cloning addon '{0}'".format("")


class AddonUpdateError(Error):

    def __str__(self):
        return self.__class__.prefix + "When updating addon '{0}'".format("")


class AddonProtectedError(Error):

    def __str__(self):
        return self.__class__.prefix + "'{0}' is protected".format("")


class AddonMultipleRepoFoldersError(Error):
    
    def __str__(self):
        return self.__class__.prefix + "More then one repository folder was found".format("")






#TODO add useful info about what addon failed to init
class AddonHomelessError(Error):
       
    def __str__(self, addon=""):
        return self.prefix + "Not give home folder for addon {0}.".format(addon)


class AddonTypeError(Error):
    pass
    
class AddonListAddError(Error):
    pass

class AddonListExtendError(Error):
    pass

class AddonListRemoveError(Error):
    pass
    
class InvalidLineInConfigFileError(Error):
    
    def __init__(self, file, line):
        self.file = file
        self.line = line
        
    def __str__(self):
        return self.prefix + "Invalid line in file \'{0}\', line {1}".format(bcolors.YELLOW + self.file + bcolors.END, bcolors.YELLOW + str(self.line) + bcolors.END)
