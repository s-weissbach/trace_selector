import os
import json
import platform
from PyQt6.QtWidgets import QFileDialog
from synapse_selector.detection.model_zoo import ModelZoo


class gui_settings:
    def __init__(self, modelzoo: ModelZoo) -> None:
        self.modelzoo = modelzoo

        # setup paths
        current_directory = os.path.dirname(os.path.abspath(__file__))
        parent_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
        settings_path = os.path.join(parent_directory, "settings")
        self.default_config_path = os.path.join(settings_path, "default_settings.json")
        self.user_config_path = os.path.join(settings_path, "settings.json")

        self.parse_settings()

    def parse_settings(self):
        """
        Parses the config file from a json file. If the programm is run for the
        first time, the default "default_config.json" file is used, otherwise the
        settings from the previous run are loaded.
        """
        # user settings exist
        if os.path.exists(self.user_config_path) and os.path.isfile(
            self.user_config_path
        ):
            config_path = self.user_config_path

            with open(config_path, "r") as in_json:
                self.config = json.load(in_json)

            # in case the settings file is updated add new keys to the saved config
            with open(self.default_config_path, "r") as in_json:
                template_config = json.load(in_json)
            for key in template_config:
                if key not in self.config:
                    self.config[key] = template_config[key]
                    self.write_settings()
        # user settings don't exist -> load default settings
        else:
            with open(self.default_config_path, "r") as in_json:
                self.config = json.load(in_json)

    def write_settings(self) -> None:
        with open(self.user_config_path, "w") as out_json:
            json.dump(self.config, out_json)

    def get_output_folder(self, parent) -> None:
        self.config["output_filepath"] = str(
            QFileDialog.getExistingDirectory(parent, "Select output directory")
        )
        keep_path = os.path.join(self.config["output_filepath"], "keep_folder")
        trash_path = os.path.join(self.config["output_filepath"], "trash_folder")
        if not os.path.exists(keep_path):
            os.mkdir(keep_path)
        if not os.path.exists(trash_path):
            os.mkdir(trash_path)
        self.write_settings()
