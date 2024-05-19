"""
Module Definition:
    - This module provides functions for interacting with a database using the chromadb library.

Functions:
    - getclient(session_type='local', **sessions_args): Retrieve a client based on session type.
    - addData(client, data: list): Add data to a collection using the provided client.
    - getData(client, query_emb, metadata: dict, **add_filters): Retrieve data from a collection using the provided client.

Classes:
    - FilterContext: A class providing filtering and scoring functionalities for retrieved information.
"""

import chromadb
import uuid



# ------------------------------------------------------------------
def getclient(sessions_args, session_type = 'local'):
    """
    Function to retrieve a client based on session type.

    Args:
        session_type (str): Type of session. Can be 'local' or 'hosted'.
        **sessions_args: Additional keyword arguments specific to the session type.

    Returns:
        client: A client object based on the specified session type.

    Raises:
        ValueError: If session_type is not 'local' or 'hosted', or if required arguments are missing for the chosen session type.
    """

    if session_type not in ['local','hosted']:
        raise ValueError(f"Session type incorrect. Possible values accepted : {['local','hosted']}")

    # Handling for local session type
    if session_type == 'local':
        try:
            # Create a PersistentClient object with the specified path
            client = chromadb.PersistentClient(path=sessions_args['path'])
        except:
            # Raise an error if the specified path is inaccessible
            raise ValueError(f"Path shared is not accessible: {sessions_args['path']}")

    # Handling for hosted session type
    if session_type == 'hosted':
        try:
            # Create an HttpClient object with the specified host and port
            client = chromadb.HttpClient(host=sessions_args['host'], port=sessions_args['port'])
        except:
            # Raise an error if host information is inaccessible
            raise ValueError(f"Host information not accessible: {sessions_args}")


    print("----------------------------------------------")
    print("Client check : ",client.heartbeat())
    print("----------------------------------------------")

    return client


# ------------------------------------------------------------------
def addData(client, data: list, metadata: dict):
    """
    Add data to a collection using the provided client.

    Args:
        client: Client object to interact with the database.
        data (list): List of dictionaries, where each dictionary represents a datapoint with keys 'chunked_data', 'embedding', 'metadata'.
        metadata (dict

    Returns:
        str: Message indicating the success of the operation.

    Example Usage:
        ```
        addData(my_client, [
            {'chunked_data': ..., 'embedding': ..., 'metadata': ...},
            {'chunked_data': ..., 'embedding': ..., 'metadata': ...},
            ...
        ])
        ```
    Notes:
        - If the collection specified in metadata doesn't exist, it will be created.
        - The 'metadata' dictionary should contain a key 'collection_name' indicating the name of the collection.
        - Each datapoint should have 'chunked_data', 'embedding', and 'metadata' keys.
        - The 'ids' for documents are generated using UUID version 3 based on the 'chunked_data'.
    """
    # Attempt to get the collection specified in metadata, create it if it doesn't exist
    try:
        collection = client.get_collection(name=metadata['collection_name'])
    except:
        collection = client.create_collection(
            name=metadata['collection_name'],
            metadata={"hnsw:space": metadata.get('sim_metric','cosine')} # 'cosine' is the default space type
        )

    # Add each datapoint to the collection
    for datapoint in data:
        # print("----------------------------------------------")
        # print("Data to be : ", datapoint)
        # print("----------------------------------------------")

        collection.upsert(
            embeddings=datapoint['embedding'],
            metadatas=datapoint['metadata'],
            documents=datapoint['documents'],
            ids= datapoint['id']
        )

    return f"Success : Added into Collection {metadata['collection_name']}"


# ------------------------------------------------------------------
def getData(client, query_emb, metadata: dict, **add_filters):
    """
    Retrieve data from a collection using the provided client.

    Args:
        client: Client object to interact with the database.
        query_emb: Query embedding vector to search for similar items.
        metadata (dict): Dictionary containing metadata information, including 'collection_name' and 'n_chunks'.
        **add_filters: Additional keyword arguments for filtering the query results.

    Returns:
        retrieved_data: Data retrieved from the collection based on the query and filters.

    Raises:
        ValueError: If the specified collection doesn't exist.

    Example Usage:
        ```
        retrieved_data = getData(my_client, query_emb, {'collection_name': 'my_collection', 'n_chunks': 10}, filter_key='filter_value')
        ```

    Notes:
        - The 'metadata' dictionary should contain a key 'collection_name' indicating the name of the collection.
        - 'n_chunks' specifies the number of chunks to retrieve.
        - Additional filters can be applied using **add_filters.
    """
    # Attempt to get the collection specified in metadata
    try:
        collection = client.get_collection(name=metadata['collection_name'])
    except:
        # Raise an error if the collection doesn't exist
        raise ValueError(f"Collection doesn't exists : {metadata['collection_name']}")

    # Query the collection with provided query embeddings and filters
    if add_filters:
        retrieved_data = collection.query(
            query_embeddings=query_emb,
            n_results=metadata['n_chunks'],
            where=add_filters
        )
    else:
        retrieved_data = collection.query(
            query_embeddings=query_emb,
            n_results=metadata['n_chunks']
        )

    return retrieved_data