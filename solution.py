import sys

class Solution:
    def __init__(self):
        pass

    def evaluate(self):
        if self.validate() == False:
            return sys.float_info.max
    
    def validate(self):
        return False 