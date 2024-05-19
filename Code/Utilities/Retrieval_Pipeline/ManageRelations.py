from Code.Utilities.Retrieval_Pipeline.relationdb import networkxDB

class Relations:
    """
    A class for managing relations using various storage types.

    attr:
        - strgType (str): Type of storage used for relations.
        - GraphObj: Graph object for storing relations.
    """

    def __init__(self, strgType = "networkx"):
        """
        Initialize the Relations object.
        """
        self.strgType = strgType
        self.GraphObj = None

    def __instGraphObj__(self):
        """
        Initialize the graph object based on the storage type.
        """
        if self.strgType == "networkx":
            self.GraphObj = networkxDB.getObj()

    def addRelation(self, edges):
        """
        Add relations to the graph object.

        args:
            - nodes (dict): Dictionary containing node names as keys and node attributes as values.
            - edges (dict): Dictionary containing edge tuples as keys (source, target) and edge attributes as values.
        """
        self.__instGraphObj__()

        if self.strgType == "networkx":
            networkxDB.addRelations(self.GraphObj, edges)


    def getRelation(self, target_nodes = []):
        """
        Retrieve relations from the graph object.

        args:
            - target_nodes (list): List of target nodes to retrieve relations for.

        returns:
            - dict: Dictionary containing retrieved relations.
        """
        self.__instGraphObj__()

        if self.strgType == "networkx":
            return networkxDB.getRelations(self.GraphObj, target_nodes)


    def visRelations(self):
        self.__instGraphObj__()

        if self.strgType == "networkx":
            networkxDB.visualizeRelations(self.GraphObj)

            return "Refreshed relations map"
