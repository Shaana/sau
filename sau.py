#!/usr/bin/python3.2

"""sau is a python script to download and update World of Warcraft addons from git, svn, hg repositories"""
 
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
import sys
import re
from optparse import OptionParser


import Addon
import AddonList
import Reader
import Error

#Note: a lot of the errors in this code should be assert

#TODO add a debug class that allows to dump variables after execution

def main():
    if sys.platform.startswith('linux'):
        #parse script arguments
        (options, args) = parse_args()
        
        if not args and args[0]:
            print("root missing")
            sys.exit(-1)
            
        root = args[0]
        
        #create lists
        addon_list = AddonList.AddonList("share_addons", root, options.file)
        libs = AddonList.AddonList("share_libs", root)
        
        #test patterns
        #for AddonList.parse_root(list_protected=list_protected)
        list_protected=["^Blizzard_.+?$", "s[A-Z].+?", "^SharedMedia_MyMedia$", "^DCSpam$"]
        
        #addon_list.parse_root(True, list_protected) #implement list_protected option first !
        addon_list.parse_url_config_file() #terrible error, if there is no file given
        
        #TODO remember to change back _remove tree in Addon.execute()
        #remove print in Reader
        

        
        
        if options.url:
            #pretty bad pattern ... seams to work though
            pattern = "^.*?(!?)(git|svn|hg);(.+?)$"
            match = re.match(pattern, options.url)
            print(options.url)
            if match:
                protected = False
                if match.group(1) == "!":
                    protected = True
                temp_addon = Addon.Addon(root, (match.group(2), match.group(3)), protected=protected)
                #check if it doesnt already exist
                temp_addon.execute()
                #todo add to libs
                
        return 
        #TEMP
        
        for addon in addon_list.list_addons:
            addon.execute()
            addon.parse_pkgmeta_file()
            temp_list =AddonList.AddonList("temp", root)
            temp_list.parse_pkgmeta_info(addon.config_info)
            libs = libs.merge(temp_list, 1)
        
        print("-------------------------")
        
        libs = libs.enhance_addon_list()
        libs = libs.merge(addon_list, "unique")
        libs.dump_list_addons()

        for lib in libs.list_addons:
            lib.execute()
        
        #print(addon_list.root)
        #print(addon_list.url_config_file)
        
    sys.exit(0)

def parse_args():
    parser = OptionParser(usage="Usage: %prog [options] root", version="%prog {0}".format(0.1))
    parser.add_option("-f", "--file",
                        help="Path to the addon.list file",
                        action="store", type="string", dest="file", metavar="DIR")
    
    #remove, we need a root in any case, just make it a arg          
    parser.add_option("-r", "--root",
                        help="The addon root directory.",
                        action="store", type="string", dest="root", metavar="DIR" , default=os.getcwd())
                     
    parser.add_option("-c", "--clean",
                        help="Delete .git/.svn/.hg repo folders from the addon folder after update/clone.",
                        action="store_true", dest="clear", default=False)
                    
    parser.add_option("--delete",
                        help="Delete all non protected folders in the root directory.",
                        action="store_true", dest="delete", default=False)

    parser.add_option("-u", "--url",
                        help="Download one addons from a specific url, use format: '-u repo_type;url'",
                        action="store", type="string", dest="url", metavar="URL")

    #not sure how to implement that yet, maybe just skip ?
    #or when used with -u, this url is protected ? (or via !)
    #when set, every addon is loaded as protected?
    parser.add_option("-p", "--protected",
                        help="a list of protected folder patterns",
                        action="store", type="string", dest="list_protected_folder", metavar="PROTECTED")

    parser.add_option("--update",
                        help="only update existing addons",
                        action="store_true", dest="update", default=False)
    
    parser.add_option("--clone",
                        help="only clone from urls",
                        action="store_true", dest="clone", default=False)

    return parser.parse_args()


if __name__ == "__main__":
    main()