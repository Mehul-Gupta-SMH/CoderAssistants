from Code.SystemBuilder.SQLReference import SQLBuilderSupport


def getRelevantContext(user_query: str):
    """
    Retrieves the context for building the query based on the question bu user

    :param user_query: question by user for which query is to be generated
    :return: JSON object containing context for building thq SQL query
    """
    queryContext = SQLBuilderSupport()
    return queryContext.getBuildComponents(user_query)


