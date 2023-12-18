import os
import requests
from synapse_selector.utils.hash import sha256_hash


class ModelZoo:
    """
    A class for managing and updating machine learning models from a GitHub repository.

    Attributes:
    - models_folder (str): The folder name where models are stored locally.
    - github_repo_url (str): The URL of the GitHub repository containing the models.
    - github_api_url (str): The API URL for accessing the contents of the models folder on GitHub.

    Methods:
    - check_for_updates(): Checks for updates in the GitHub repository and downloads new models.
    - download_model(url, local_path): Downloads a model from a given URL and saves it locally.

    Example:
    ```
    model_zoo = ModelZoo()
    model_zoo.check_for_updates()
    ```
    """

    def __init__(self, modelzoo_path: str):
        """
        Initializes a ModelZoo instance.

        Sets default values for models_folder, github_repo_url, and constructs github_api_url.
        """
        self.modelzoo_path = modelzoo_path
        self.github_repo_url = (
            "https://github.com/s-weissbach/synapse_selector_modelzoo.git"
        )
        self.github_api_url = "https://api.github.com/repos/s-weissbach/synapse_selector_modelzoo/contents/models"
        # find all downloaded models
        self.available_models = {}
        os.makedirs(self.modelzoo_path, exist_ok=True)
        for filename in os.listdir(self.modelzoo_path):
            if not filename.endswith(".pt"):
                continue
            filename_no_ext = filename.split(".pt")[0]
            self.available_models[filename_no_ext] = {
                'filepath': os.path.join(self.modelzoo_path, filename),
                'hash': sha256_hash(os.path.join(self.modelzoo_path,filename))
            }
        self.load_model_info()

    
    def load_model_info(self):
        """
        Loads model information from the 'model.json' file in the GitHub repository.
        """
        try:
            model_json_url = "https://raw.githubusercontent.com/s-weissbach/synapse_selector_modelzoo/main/models.json"
            response = requests.get(model_json_url)
            response.raise_for_status()
            self.model_info = response.json()
        except requests.RequestException as e:
            print(f"Error loading model information: {e}")

    def check_for_updates(self):
        """
        Checks for updates in the GitHub repository and downloads new models if available.

        Raises:
        - requests.RequestException: If an error occurs during the update check.
        """
        try:
            response = requests.get(self.github_api_url)
            response.raise_for_status()
            github_files = response.json()

            for file_info in github_files:
                filename = file_info["name"]
                download_url = file_info["download_url"]
                if not filename.endswith('.pt'): continue
                if os.path.exists(os.path.join(self.modelzoo_path, filename)):
                    # model exists
                    filename_no_ext = filename.split('.pt')[0]
                    if filename_no_ext in self.model_info.keys():
                        if self.model_info[filename_no_ext] == self.available_models[filename_no_ext]['hash']:
                            # weights are unchanged, otherwise reload model
                            continue
                        print(f'Model {filename_no_ext} has new weights.')
                # in all other cases -> load new model weights
                self.download_model(download_url, filename)
                

            print("All models are up-to-date.")

        except requests.RequestException as e:
            print(f"Error checking for updates: {e}")

    def download_model(self, url, filename):
        """
        Downloads a model from the given URL and saves it locally.

        Args:
        - url (str): The URL from which to download the model.

        Raises:
        - requests.RequestException: If an error occurs during the model download.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            local_path = os.path.join(self.modelzoo_path, filename)
            with open(local_path, "wb") as file:
                file.write(response.content)
            filename_no_ext = filename.split(".pt")[0]
            self.available_models[filename_no_ext] = {
                'filepath': os.path.join(self.modelzoo_path, filename),
                'hash': sha256_hash(local_path)
            }
            print(f'Downloaded model: {filename_no_ext} ({self.available_models[filename_no_ext]["hash"]})')

        except requests.RequestException as e:
            print(f"Error downloading model: {e}")

    
