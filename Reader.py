#!/usr/bin/env python

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
    
    def dump_dict(self):
        return self.__class__._dict_read_files
    
    def get_instance():
        if Reader._instance == None:
            Reader._instance = Reader()            

        return Reader._instance
    
    get_instance = staticmethod(get_instance)
    
    
#r = Reader.get_instance()
#print(r.read_config("/home/share/Development/ignore.list"))
