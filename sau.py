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
from optparse import OptionParser


import Addon
import AddonList
import Reader
import Error
    

def main():
    if sys.platform.startswith('linux'):
        #parse script arguments
        (options, args) = parse_args()
        
    sys.exit(0)

def parse_args():
    parser = OptionParser(usage="Usage: %prog [options] ", version="%prog {0}".format(0.1))
    parser.add_option("-f", "--file",
                        help="Path to the addon.list folder",
                        action="store", type="string", dest="file", metavar="DIR")
    
    #rename to root              
    parser.add_option("-r", "--root",
                        help="The addon root directory.",
                        action="store", type="string", dest="root", metavar="DIR" , default=os.getcwd())
                     
    parser.add_option("-c", "--clean",
                        help="Delete .git/.svn/.hg repo folders from the addon folder.",
                        action="store_true", dest="clear", default=False)
                    
    parser.add_option("--delete",
                        help="Delete all non protected folders in the root directory.",
                        action="store_true", dest="delete", default=False)

    parser.add_option("-u", "--url",
                        help="Download addons from a specific list of urls.",
                        action="store", type="string", dest="list_url", metavar="URL")

    #???
    parser.add_option("-p", "--protected",
                        help="a list protected folder patterns",
                        action="store", type="string", dest="list_protected_folder", metavar="PROTECTED")

    parser.add_option("--update",
                        help="only update existing addons",
                        action="store_true", dest="update", default=False)

    return parser.parse_args()


if __name__ == "__main__":
    main()