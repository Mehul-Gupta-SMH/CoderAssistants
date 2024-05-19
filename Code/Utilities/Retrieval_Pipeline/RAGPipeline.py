# --------------------------------------------------------------------------------------------
from FlagEmbedding import FlagReranker
from rank_bm25 import BM25Okapi
from detoxify import Detoxify
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
from transformers import pipeline
from sentence_transformers import SentenceTransformer

# --------------------------------------------------------------------------------------------

import uuid

# --------------------------------------------------------------------------------------------

from Code.Utilities.Retrieval_Pipeline.vdb import Chroma
from Code.Utilities.base_utils import get_config_val

# --------------------------------------------------------------------------------------------
models_repo = get_config_val("retrieval_config",["models_repo"],True)
indexing_configs = get_config_val("retrieval_config",["indexing"],True)
scoring_configs = get_config_val("retrieval_config",["scoring"],True)
vectordb_configs = get_config_val("retrieval_config",["vectordb"],True)

# --------------------------------------------------------------------------------------------

class FilterContext:
    """
    A class to provide filtering and scoring functionalities for retrieved information.

    Attr:
        - RerankerModel: Model for reranking retrieved information.
        - ToxicityModel: Model for detecting toxicity in retrieved information.
        - BiasModel_tokenizer: Tokenizer for bias detection model.
        - BiasModel: Model for detecting bias in retrieved information.
    """

    def __init__(self):
        """
        Initialize the FilterContext with pre-trained models.
        """
        self.RerankerModel = FlagReranker(models_repo['path'] + "/" + scoring_configs["crossencoder"],
                                          use_fp16=True)
        # self.ToxicityModel = Detoxify('original')
        # self.BiasModel_tokenizer = AutoTokenizer.from_pretrained(models_repo['path'] + "/" + scoring_configs["bias_detection"])
        # self.BiasModel = TFAutoModelForSequenceClassification.from_pretrained(models_repo['path'] + "/" + scoring_configs["bias_detection"])

    def __ScoreResults_reranker__(self, base_query: str, retrieved_info: str):
        """
        Score the retrieved information using a reranker model.

        args:
            - base_query (str): The original query used for retrieval.
            - retrieved_info (str): Retrieved information to be scored.

        returns:
            - dict: Scores generated by the reranker model.
        """
        return self.RerankerModel.compute_score([base_query, retrieved_info])


    def __ScoreResults_keyword__(self, base_query: str, retrieved_info: str):
        """
        Score the retrieved information using a keyword-based model.

        args:
            - base_query (str): The original query used for retrieval.
            - retrieved_info (str): Retrieved information to be scored.

        returns:
            - list: Scores generated by the BM25 algorithm.
        """
        tokenized_query = base_query.split(" ")

        tokenized_corpus = retrieved_info.split(" ")
        bm25 = BM25Okapi(tokenized_corpus)

        return max(bm25.get_scores(tokenized_query))


    # def __ScoreResults_bias__(self, retrieved_info: str):
    #     """
    #     Score the retrieved information for bias.
    #
    #     args:
    #         - retrieved_info (str): Retrieved information to be scored.
    #
    #     returns:
    #         - dict: Scores generated for bias.
    #     """
    #     # https://huggingface.co/d4data/bias-detection-model
    #     return pipeline('text-classification', model=self.BiasModel, tokenizer=self.BiasModel_tokenizer)
    #
    #
    # def __ScoreResults_toxicity__(self, retrieved_info: str):
    #     """
    #     Score the retrieved information for toxicity.
    #
    #     args:
    #         - retrieved_info (str): Retrieved information to be scored.
    #
    #     returns:
    #         - dict: Scores generated for toxicity.
    #     """
    #     # https://huggingface.co/unitary/toxic-bert
    #     return self.ToxicityModel.predict(retrieved_info)

    def ScoreResults(self, base_query: str, retrieved_info: str) -> dict:
        """
        Score the retrieved information using available models.

        args:
            - base_query (str): The original query used for retrieval.
            - retrieved_info (str): Retrieved information to be scored.

        returns:
            - dict: Scores generated by different scoring models.

        notes:
            - Standalone scores for toxicity and bias are provided.
            - Contextual scores using reranker and keyword models are also included.
        """

        score_results = dict()

        # Standalone scores
        # score_results['toxicity'] = self.__ScoreResults_toxicity__(retrieved_info)
        # score_results['bias'] = self.__ScoreResults_bias__(retrieved_info)

        # Contextual scores
        score_results['reranker'] = self.__ScoreResults_reranker__(base_query, retrieved_info)
        score_results['keyword'] = self.__ScoreResults_keyword__(base_query, retrieved_info)

        return score_results

# --------------------------------------------------------------------------------------------

class ManageInformation:
    """
    A class for managing information in a database.

    attr:
        - dbName (str): Name of the database being managed.
        - client: Client object for interacting with the database.
        - embedding_model: Sentence embedding model for generating embeddings.
    """

    def __init__(self):
        """
        Initialize the ManageInformation instance.

        Args:
            dbName (str): Name of the database to manage.
        """
        self.dbName = vectordb_configs["name"]
        self.client = None
        self.embedding_model = SentenceTransformer(models_repo['path'] + "/" + indexing_configs["model"])
        self.FilterScoreObj = FilterContext()

    def initialize_client(self):
        """
        Initialize the client for the specified database.

        Args:
            path (str): Path to the database.

        Notes:
            - This method is specific to the 'chroma' database.
        """
        if self.dbName == 'chroma':
            self.client = Chroma.getclient(sessions_args = {
                                                                'path':vectordb_configs["path"],
                                                                'host':"0.0.0.0",
                                                                'port':"5432"
                                                            },
                                           session_type = 'local')

    def add_new_data(self, data, data_metadata, vdb_metadata):
        """
        Add new data to the database.

        Args:
            data: Data to be added.
            data_metadata: Metadata for the data.
            vdb_metadata: Metadata specific to the virtual database (vdb).

        Returns:
            - str: Message indicating the success of the operation.

        Notes:
            - Embeddings are generated for the data using the embedding model.
            - Each data point is represented as a dictionary containing 'chunked_data', 'embedding', 'metadata', and 'id'.
        """
        embedding_data = [
            {
                'documents': str(data),
                'embedding': self.embedding_model.encode(str(data)).tolist(),
                'metadata': data_metadata,
                'id': str(uuid.uuid3(uuid.NAMESPACE_DNS, str(data)))
            }
        ]

        Chroma.addData(self.client, embedding_data, vdb_metadata)

        return "Success"

    def get_data(self, query, vdb_metadata):
        """
        Retrieve data from the database and score each retrieved data point.

        Args:
            query: Query to retrieve data.
            vdb_metadata: Metadata specific to the virtual database.

        Returns:
            dict: Scored results containing retrieved data, distance, and scores.
        """
        # Encode the query using the embedding model
        query_embed = self.embedding_model.encode(query).tolist()

        # Retrieve information from the database
        retrieved_info = Chroma.getData(self.client, query_embed, vdb_metadata)

        # Dictionary to store scored results
        results_scored = {}

        # Iterate over retrieved data points and score each one
        for ind in range(len(retrieved_info['ids'][0])):
            # Score the retrieved data point using the superclass ScoreResults method
            results_scored[retrieved_info['ids'][0][ind]] = {
                'data': retrieved_info['documents'][0][ind],  # Retrieved data
                'metadata': retrieved_info['metadatas'][0][ind],  # Retrieved data
                'distance': retrieved_info['distances'][0][ind],  # Distance metric
                'scores': self.FilterScoreObj.ScoreResults(query, retrieved_info['documents'][0][ind])
                # Scores generated for the retrieved data
            }

        return results_scored

        # return retrieved_info

# --------------------------------------------------------------------------------------------