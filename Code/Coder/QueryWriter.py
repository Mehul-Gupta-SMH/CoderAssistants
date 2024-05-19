from Code.Coder.ToolBox.SQLTB.instFunctions import getRelevantContext
from Code.Utilities.apiSupport.allApi import CallLLMApi

def generateQuery(userQuery: str, LLMservice: str):
    """

    :param userQuery:
    :param LLMservice:
    :return:
    """

    ContextJson_str = getRelevantContext(userQuery)

    prompt = f"""
    Using the context provided below, write a SQL query.
    {ContextJson_str}
    """

    print(prompt)

    LLMObj = CallLLMApi(LLMservice)

    return LLMObj.CallService(prompt)


print(generateQuery("Give me product wise split for each territory", "google"))