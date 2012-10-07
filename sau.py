#!/usr/bin/python3.2

"""sau is a python script to download and update World of Warcraft addons from git, svn, hg repositories"""
 
__author__ = "Share"
__email__  = "shaana@student.ethz.ch"
__license__= """
Copyright (c) 2008-2012 Share <shaana@student.ethz.ch>
 
This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License as
published by the Free Software Foundation; either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
USA

"""

import os
import sys
from optparse import OptionParser

from Addon import Addon
from AddonList import AddonList

from Error import *
from bcolors import bcolors
    

class Error_msg(object):

    def Print(self, message):
        print("Error: {0}".format(message))
        
    def ReadFile_LineError(self, file_name, line):
        print(bcolors.RED + "Error: " + bcolors.END + "Invalid line in file \'{0}\', line {1}".format(bcolors.YELLOW + file_name + bcolors.END, bcolors.YELLOW + str(line) + bcolors.END))
    
error = Error_msg()   


def main():
    if sys.platform.startswith('linux'):
        #parse standart prog arguments
        (options, args) = ParseCommandOptions()
        
    sys.exit(0)

def ParseCommandOptions():
    parser = OptionParser(usage="Usage: %prog [options] ", version="%prog {0}".format(0.1))
    parser.add_option("-f", "--file",
                        help="Path to the addon.list folder",
                        action="store", type="string", dest="file", metavar="DIR")
                    
    parser.add_option("--home",
                        help="The addon home directory.",
                        action="store", type="string", dest="home", metavar="DIR" , default=os.getcwd())
                     
    parser.add_option("-c", "--clean",
                        help="Delete .git/.svn/.hg repo folders from the addon folder.",
                        action="store_true", dest="clear", default=False)
                    
    parser.add_option("--delete",
                        help="Delete all non protected folders in the root directory.",
                        action="store_true", dest="delete", default=False)

    parser.add_option("-u", "--url",
                        help="Download addons from a specific list of urls.",
                        action="store", type="string", dest="list_url", metavar="URL")

    parser.add_option("-p", "--protected",
                        help="a list protected folder patterns",
                        action="store", type="string", dest="list_protected_folder", metavar="PROTECTED")

    parser.add_option("--update",
                        help="only update existing addons",
                        action="store_true", dest="clear", default=False)

    return parser.parse_args()

def chomp(s, c=None):
    """Removes leading and trailing chars of a s                 tring."""
    return s.lstrip(c).rstrip(c)

def ReadFile(filename):
    """Reads a file and returns lines as dictionary. The string after '#' is being ignored."""
    try:
        with open(filename, "r") as f:
            list_line = []
            for line in f:
                if line.find("#") > -1:
                    #ignore comments indicated by '#'
                    line = line[:line.find("#")]
                #Remove whitespace chars
                line = chomp(line, "\t\n\r\f\v ")
                #ignore empty lines
                if not line == "":
                    list_line.append(line)
        return list_line
    except IOError as e:
        error.Print("({})".format(e))


if __name__ == "__main__":
    addon = Addon("~", "Name1", "url1", "git", "folder_name1", True)
    addon.name = "nice"
    print(addon.name)
      
    #sys.exit()
    #for folder in os.listdir(os.path.expanduser("~")):
     #   print(folder)
    addon2 = Addon("~", "Name1", "url1", "git", "folder_name1", True)
    addon_l = AddonList("~/Development/Addon_test", addon_list_file="~/Development/addon.list")
    addon_l.Add(addon)
    addon_l.Print()
    main()