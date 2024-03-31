from Code.Utlities.base_utils import get_config_val
from Code.Utlities.base_utils import cachefunc
import requests
import json
import yaml
import pickle

memoizer = cachefunc()

class CodeParse:
    """
    Class to parse SQL queries and extract SQL components.
    """
    def __init__(self, service):
        """
        Initializes an instance of SQLCodeParse class.

        Args:
            service (str): The service to be used for text generation (e.g., "open_ai", "anthropic").
            tableDDL (str): The DDL query string.
            tableInsert (str): The INSERT query string.
        """
        self.service = service

    @memoizer.memoize
    def __invoke_LM__(self, service, tableDDL, tableInsert):
        """
        Invokes the language model API to generate text based on the provided queries.

        Returns:
            str: Generated text.

        Raises:
            ValueError: If the API call fails.
        """
        print("Gonna Cost : Invoking LLM")
        # Setting up prompt
        with open(r"C:\Users\mehul\Documents\Projects - GIT\Agents\Decompose KG from Code\pythonProject\CoderAssistants\Code\Utlities\Configs\apiTemplates\taskTemplate.txt","r") as promptTmplt_fobj:
            prompt_template = promptTmplt_fobj.read()

        prompt = prompt_template.replace("<<DDLQUERY>>",tableDDL)
        prompt = prompt.replace("<<INSERETQUERY>>",tableInsert)

        # Get model configuration from the config file
        model_config = get_config_val("model_config",[str(self.service).upper()],True)


        # Load API calling template
        with open(model_config["api_template"],"r") as api_temp_fobj:
            api_temp_str = api_temp_fobj.read()
            api_temp_str = api_temp_str.replace("<<api_key>>",model_config["api_key"])
            api_temp_str = api_temp_str.replace("<<model>>",model_config["model_name"])
            # api_temp_str = api_temp_str.replace("<<input_text>>",prompt)


        # Convert API template string to dictionary
        api_temp_dict = eval(api_temp_str)



        if self.service.lower() == "open_ai":

            # Update the payload with the prompt for OpenAI API
            api_temp_dict["payload"]["messages"][0]["content"] = prompt

            # Make the API call
            response = requests.post(api_temp_dict["endpoint"], headers=api_temp_dict["headers"], json=api_temp_dict["payload"])
            # Process the response
            data = response.json()

            if response.status_code == 200:
                return data['choices'][0]['message']['content']

            else:
                raise  ValueError(f"Failed to create message. Status code: {response.status_code}")

        if self.service.lower() == "anthropic":

            # Update the payload with the prompt for Anthropic AI API
            api_temp_dict["payload"]["prompt"] = api_temp_dict["payload"]["prompt"].replace("<<input_text>>",prompt)

            # Make the API call
            response = requests.post(api_temp_dict["endpoint"], headers=api_temp_dict["headers"], json=api_temp_dict["payload"])
            # Process the response
            data = response.json()

            if response.status_code == 200:
                return data['completion']

            else:
                print(response.json())
                raise  ValueError(f"Failed to create message. Status code: {response.status_code}")

    @staticmethod
    def __cleanTableMetadata__(genTM: dict):
        """
        Placeholder method to clean generated table metadata.

        Args:
            genTM (dict): Generated table metadata.

        Returns:
            dict: Cleaned table metadata.
        """
        cleanedTM = genTM

        try:
            cleanedTM = yaml.load(cleanedTM.strip(),yaml.FullLoader)

            clean_rule_list = [
                # ('metadata key', 'string to replace', 'alternative value')
                ('logic', 'Select ', ''),
            ]

            for col, inf in cleanedTM.items():
                for clean_rule in clean_rule_list:
                    cleanedTM[col][clean_rule[0]] = cleanedTM[col][clean_rule[0]].replace(clean_rule[1],
                                                                                          clean_rule[2])
        except:
            print("Failed!")

        return cleanedTM

    def getTableMetadata(self, tableDDL, tableInsert):
        """
        Retrieves table metadata using the language model API.

        Returns:
            dict: Table metadata.
        """
        tableMetadata = self.__invoke_LM__(self.service, tableDDL, tableInsert)

        tableMetadata = CodeParse.__cleanTableMetadata__(tableMetadata)

        return tableMetadata

vTableDDL = """
CREATE TABLE Campaigns (
    campaign_id INT PRIMARY KEY,
    campaign_name VARCHAR(100) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    budget DECIMAL(12, 2) NOT NULL,
    status VARCHAR(20) NOT NULL,
    impressions INT,
    clicks INT,
    conversions INT,
    campaign_performance DECIMAL(10, 2), -- Campaign Performance column with complex calculation
    CONSTRAINT check_campaign_performance CHECK (campaign_performance >= 0)
);
"""

vTableInsert = """
INSERT INTO Campaigns (campaign_id, campaign_name, start_date, end_date, budget, status, impressions, clicks, conversions, campaign_performance)
SELECT
    c.campaign_id,
    c.campaign_name,
    c.start_date,
    c.end_date,
    c.budget,
    c.status,
    COALESCE(SUM(i.impressions), 0) AS impressions,
    COALESCE(SUM(a.clicks), 0) AS clicks,
    COALESCE(SUM(a.conversions), 0) AS conversions,
    (COALESCE(SUM(a.clicks), 0) * 0.5 + COALESCE(SUM(a.conversions), 0) * 0.8) / COALESCE(SUM(i.impressions), 1) * 100 AS campaign_performance
FROM
    Campaigns_Table c
LEFT JOIN
    Impressions_Table i ON c.campaign_id = i.campaign_id
LEFT JOIN
    Actions_Table a ON c.campaign_id = a.campaign_id
GROUP BY
    c.campaign_id, c.campaign_name, c.start_date, c.end_date, c.budget, c.status;
"""

vservice = "ANTHROPIC"

if __name__ == "__main__":
    SQLObj = CodeParse(vservice)
    print(SQLObj.getTableMetadata(vTableDDL,vTableInsert))
    print("Calling again")
    SQLObj.getTableMetadata(vTableDDL,vTableInsert)