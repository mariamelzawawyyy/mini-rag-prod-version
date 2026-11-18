from ..helpers.config import get_settings
import os 
import random 
import string 
 
# Provides what services share: the application settings  
# (the most important one), the files directory, and a helper  
# for generating random strings.  

class BaseService:  
    def __init__(self):
        
        self.app_settings = get_settings()
        self.base_dir = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)) )
        # this file lives in src/services/, so two dirname calls give src/ 
        self.file_dir = os.path.join(
            self.base_dir ,
            "assets/files"
        )
        os.makedirs(self.file_dir, exist_ok=True)
        #file_dir = /src/assets/files  

    def generate_random_string(self, length: int = 12) -> str:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))