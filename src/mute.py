import os
import sys


class Mute():

    def __init__(self):
        self.old_stdout = None
    
    def __enter__(self):
        self.old_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")
    
    def __exit__(self, *args, **kwargs):
        sys.stdout = self.old_stdout