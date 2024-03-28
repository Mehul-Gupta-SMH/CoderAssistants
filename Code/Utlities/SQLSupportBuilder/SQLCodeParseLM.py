from Code.Utlities.base_utils import get_config_val
import requests
import json

class SQLCodeParse:
    """
    Class to parse SQL queries and extract SQL components.
    """
    def __init__(self, service, TableDDL, TableInsert):
        """
        Invokes the language model API to generate text based on the provided queries.

        Returns:
            str: Generated text.

        Raises:
            ValueError: If the API call fails.
        """
        self.service = service
        self.TableDDL = TableDDL
        self.TableInsert = TableInsert

    def invoke_LM(self):

        # Setting up prompt
        with open(r"C:\Users\mehul\Documents\Projects - GIT\Agents\Decompose KG from Code\pythonProject\CoderAssistants\Code\Utlities\Configs\apiTemplates\taskTemplate.txt","r") as promptTmplt_fobj:
            prompt_template = promptTmplt_fobj.read()

        prompt = prompt_template.replace("<<DDLQUERY>>",self.TableDDL)
        prompt = prompt.replace("<<INSERETQUERY>>",self.TableInsert)

        model_config = get_config_val("model_config",[str(self.service).upper()],True)
        # Load API calling template
        with open(model_config["api_template"],"r") as api_temp_fobj:
            api_temp_str = api_temp_fobj.read()
            api_temp_str = api_temp_str.replace("<<api_key>>",model_config["api_key"])
            api_temp_str = api_temp_str.replace("<<model>>",model_config["model_name"])
            # api_temp_str = api_temp_str.replace("<<input_text>>",repr(prompt.replace("'",r"\'")))

            # print(api_temp_str[298:])

        # print(api_temp_str)

        api_temp_dict = eval(api_temp_str)

        if self.service.lower() == "open_ai":
            api_temp_dict["payload"]["messages"][0]["content"] = prompt

        if self.service.lower() == "anthropic":
            api_temp_dict["payload"]["prompt"] = api_temp_dict["payload"]["prompt"].replace("<<input_text>>",prompt)


        response = requests.post(api_temp_dict["endpoint"],
                                 headers=api_temp_dict["headers"],
                                 json=api_temp_dict["payload"])

        data = response.json()

        if self.service.lower() == "open_ai":

            if response.status_code == 200:
                return data['choices'][0]['message']['content']

            else:
                raise  ValueError(f"Failed to create message. Status code: {response.status_code}")

        if self.service.lower() == "anthropic":

            if response.status_code == 200:
                return data['completion']

            else:
                print(response.json())
                raise  ValueError(f"Failed to create message. Status code: {response.status_code}")


TableDDL = """
CREATE TABLE ComplexTable (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT CHECK (age >= 18),
    gender ENUM('Male', 'Female', 'Other'),
    salary DECIMAL(10, 2),
    registration_date DATE,
    CONSTRAINT check_salary CHECK (salary >= 0),
    CONSTRAINT check_name_length CHECK (LENGTH(name) <= 100),
    CONSTRAINT check_registration_date CHECK (registration_date >= '2000-01-01'),
    CONSTRAINT unique_name_age UNIQUE (name, age)
);
"""

TableInsert = """
INSERT INTO Employees (employee_id, employee_name, department_id, manager_id, salary)
SELECT 
    e.employee_id,
    e.employee_name,
    d.department_id,
    m.manager_id,
    -- Salary calculation based on employee's experience, department's budget, and manager's performance rating
    e.years_of_experience * d.budget_per_employee * (m.performance_rating / 10) AS salary
FROM 
    Employees_Table AS e
JOIN 
    Departments_Table AS d ON e.department_name = d.department_name
JOIN 
    Managers_Table AS m ON d.manager_name = m.manager_name;
"""
service = "ANTHROPIC"

print(SQLCodeParse(service,TableDDL,TableInsert).invoke_LM())