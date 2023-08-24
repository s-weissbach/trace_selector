import os
import json
import platform
from PyQt6.QtWidgets import QFileDialog

class gui_settings:
    def __init__(self) -> None:
        self.parse_settings()
    
    def parse_settings(self):
        '''
        Parses the config file from a json file. If the programm is run for the
        first time, the default "default_config.json" file is used, otherwise the
        settings from the previous run are loaded.
        '''
        # ------------------------- user path specific for OS ------------------------ #
        if platform.system() == 'Windows':
            self.config_folder = os.path.join(os.environ.get('USERPROFILE'),'.synapse')
            self.user_config_path = os.path.join(self.config_folder,'config.json')
        else:
            self.config_folder = os.path.join(os.environ.get('HOME'),'.synapse')
            self.user_config_path = os.path.join(self.config_folder,'config.json')
        # -------------------------------- parse file -------------------------------- #
        if os.path.exists(self.user_config_path) and os.path.isfile(self.user_config_path):
            config_path = self.user_config_path
        else:
            config_path = 'default_config.json'
        with open(config_path, 'r') as in_json:
            self.config = json.load(in_json)
    
    def write_settings(self) -> None:
        if not os.path.exists(self.config_folder):
            os.mkdir(self.config_folder)
        with open(self.user_config_path,'w') as out_json:
            json.dump(self.config, out_json)
    
    def get_output_folder(self,parent) -> None:
        self.config['output_folder'] = str(QFileDialog.getExistingDirectory(parent, "Select output directory"))
        self.config['keep_folder'] = os.path.join(self.config['output_folder'],'keep_folder')
        self.config['trash_folder'] = os.path.join(self.config['output_folder'],'trash_folder')
        if not os.path.exists(self.config['keep_folder']):
            os.mkdir(self.config['keep_folder'] )
        if not os.path.exists(self.config['trash_folder']):
            os.mkdir(self.config['trash_folder'])
    
    def refresh_plot(self) -> None:
        pass