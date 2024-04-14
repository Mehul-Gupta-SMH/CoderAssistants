"""
Module: call_llm_api.py

Description:
    This module defines the CallLLMApi class, which is used to interact with various Language Model (LLM) APIs such as OpenAI, Anthropic, and Google.
    It provides methods to call the LLM service API with a provided prompt and retrieve the generated text.

Classes:
    - CallLLMApi: Class to call Language Model (LLM) APIs.

Attributes:
    - llmService (str): The LLM service to be used (e.g., "OpenAI", "Anthropic").
    - api_temp_dict (dict): The API dictionary containing endpoint, headers, and payload.

Methods:
    - __init__(self, llmService="OpenAI"): Initializes an instance of CallLLMApi class.
    - __set_apidict__(self, llmService): Set up the API dictionary based on the specified LLM service.
    - CallService(self, prompt: str) -> str: Call the LLM service API with the provided prompt and return the generated text.
"""

import requests
from Code.Utlities.base_utils import get_config_val


class CallLLMApi:
    """
    Class to call Language Model (LLM) APIs.

    Attributes:
        llmService (str): The LLM service to be used (e.g., "OpenAI", "Anthropic").
        api_temp_dict (dict): The API dictionary containing endpoint, headers, and payload.
    """
    def __init__(self, llmService = "OpenAI"):
        """
        Initializes an instance of CallLLMApi class.

        Args:
            llmService (str, optional): The LLM service to be used. Defaults to "OpenAI".
        """
        self.llmService = llmService
        self.api_temp_dict = self.__set_apidict__(llmService)

    def __set_apidict__(self, llmService):
        """
        Set up the API dictionary based on the specified LLM service.

        Args:
            llmService (str): The LLM service.

        Returns:
            dict: The API dictionary.
        """
        # Get model configuration from the config file
        model_config = get_config_val("model_config",[str(llmService).upper()],True)

        # Load API calling template
        with open(model_config["api_template"],"r") as api_temp_fobj:
            api_temp_str = api_temp_fobj.read()
            api_temp_str = api_temp_str.replace("<<api_key>>",model_config["api_key"])
            api_temp_str = api_temp_str.replace("<<model>>",model_config["model_name"])

        # Convert API template string to dictionary
        self.api_temp_dict = eval(api_temp_str)


    def CallService(self, prompt: str) -> str:
        """
        Call the LLM service API with the provided prompt.

        Args:
            prompt (str): The prompt text.

        Returns:
            str: Generated text.

        Raises:
            ValueError: If the API call fails.
        """
        self.__set_apidict__(self.llmService)

        if self.llmService.lower() in ("open_ai","groq"):
            # Update the payload with the prompt for OpenAI API
            self.api_temp_dict["payload"]["messages"][0]["content"] = prompt

        if self.llmService.lower() == "anthropic":
            # Update the payload with the prompt for Anthropic AI API
            self.api_temp_dict["payload"]["prompt"] = self.api_temp_dict["payload"]["prompt"].replace("<<input_text>>",prompt)

        if self.llmService.lower() == "google":
            # Update the payload with the prompt for Google API
            self.api_temp_dict["payload"]["contents"][0]["parts"][0]["text"] = prompt


        # Make the API call
        response = requests.post(self.api_temp_dict["endpoint"],
                                 headers=self.api_temp_dict["headers"],
                                 json=self.api_temp_dict["payload"])
        # Process the response
        data = response.json()

        if response.status_code == 200:
            if self.llmService.lower() in ("open_ai","groq"):
                return data['choices'][0]['message']['content']
            if self.llmService.lower() == "anthropic":
                return data['completion']
            if self.llmService.lower() == "google":
                return data['candidates'][0]['content']['parts'][0]['text']

        else:
            raise  ValueError(f"Failed to create message. Status code: {response.status_code}")

