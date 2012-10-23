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

#import Error

#TODO replace Errors with error classes from Error.py
#TODO add a config option, like lines starting with @![variable]=....
# @!list_protected=["..", ".."]

def chomp(s, c=None):
    """Removes leading and trailing chars of a string."""
    return s.lstrip(c).rstrip(c)

class Reader(object):
    
    _instance = None
    _dict_read_files = {}
    
    def __int__(self):
        pass
    
    def read_config(self, file, comment_char=["#"]):
        """ 
        Reads a file and returns lines as a list. Furthermore comments are ignored.
        Use comment_char = [...] for a list of comment characters.
        """
        try:
            if not file:
                print("Reader:Warnsing:nofile")
                return []
            
            with open(file, "r") as f:
                list_line = []
                for line in f:
                    #ignore comments
                    for cc in comment_char:
                        if line.find(cc) > -1:
                            #ignore comments
                            line = line[:line.find(cc)]
                    #Remove whitespace chars
                    line = chomp(line, "\t\n\r\f\v ")
                    #ignore empty lines
                    if not line == "":
                        list_line.append(line)
                        
            #add it to class dict of read files
            self.__class__._dict_read_files[file] = list_line
            return list_line
        
        except IOError as e:
            print(e)
            return []
    
    def dump_dict(self):
        return self.__class__._dict_read_files
    
    def get_instance():
        if Reader._instance == None:
            Reader._instance = Reader()            

        return Reader._instance
    
    get_instance = staticmethod(get_instance)
    

#r = Reader.get_instance()
#print(r.read_config("/home/share/Development/ignore.list"))
