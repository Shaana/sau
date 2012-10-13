#!/usr/bin/env python



class bcolors(object):
    #prob only works on unix/linux systems
    GREY = '\033[90m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    END = '\033[0m'

    def __init__(self, enabled=True):
        if enabled:
            self.enable()
        else:
            self.disable()

    def enable(self):
        self.GREY = '\033[90m'
        self.RED = '\033[91m'
        self.GREEN = '\033[92m'
        self.YELLOW = '\033[93m'
        self.BLUE = '\033[94m'
        self.PURPLE = '\033[95m'
        self.CYAN = '\033[96m'
        self.END = '\033[0m'

    def disable(self):
        self.GREY = ''
        self.RED = ''
        self.GREEN = ''
        self.YELLOW = ''
        self.BLUE = ''
        self.PURPLE = ''
        self.CYAN = ''
        self.END = ''
        
#EXAMPLE
#print(bcolors.YELLOW + "Warning: No active frommets remain. Continue?" + bcolors.END)