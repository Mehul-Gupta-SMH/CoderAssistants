# Scoring Models
from FlagEmbedding import FlagReranker
from rank_bm25 import BM25Okapi
from detoxify import Detoxify
from transformers import AutoTokenizer, TFAutoModelForSequenceClassification
from transformers import pipeline
from sentence_transformers import SentenceTransformer

import uuid

from CoderAssistants.Code.Utlities.Retrieval_Pipeline.vdb import Chroma
from CoderAssistants.Code.Utlities import base_utils



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
        self.RerankerModel = FlagReranker('BAAI/bge-reranker-large', use_fp16=True)
        self.ToxicityModel = Detoxify('original')
        self.BiasModel_tokenizer = AutoTokenizer.from_pretrained("d4data/bias-detection-model")
        self.BiasModel = TFAutoModelForSequenceClassification.from_pretrained("d4data/bias-detection-model")

    @staticmethod
    def __ScoreResults_reranker__(base_query: str, retrieved_info: str):
        """
        Score the retrieved information using a reranker model.

        args:
            - base_query (str): The original query used for retrieval.
            - retrieved_info (str): Retrieved information to be scored.

        returns:
            - dict: Scores generated by the reranker model.
        """
        return FilterContext.RerankerModel.compute_score([base_query,retrieved_info])

    @staticmethod
    def __ScoreResults_keyword__(base_query: str, retrieved_info: str):
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

        return bm25.get_scores(tokenized_query)

    @staticmethod
    def __ScoreResults_bias__(retrieved_info: str):
        """
        Score the retrieved information for bias.

        args:
            - retrieved_info (str): Retrieved information to be scored.

        returns:
            - dict: Scores generated for bias.
        """
        # https://huggingface.co/d4data/bias-detection-model
        return pipeline('text-classification', model=FilterContext.BiasModel, tokenizer=FilterContext.BiasModel_tokenizer)

    @staticmethod
    def __ScoreResults_toxicity__(retrieved_info: str):
        """
        Score the retrieved information for toxicity.

        args:
            - retrieved_info (str): Retrieved information to be scored.

        returns:
            - dict: Scores generated for toxicity.
        """
        # https://huggingface.co/unitary/toxic-bert
        return FilterContext.ToxicityModel.predict(retrieved_info)


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
        score_results['toxicity'] = self.__ScoreResults_toxicity__(retrieved_info)
        score_results['bias'] = self.__ScoreResults_bias__(retrieved_info)

        # Contextual scores
        score_results['reranker'] = self.__ScoreResults_reranker__(base_query,retrieved_info)
        score_results['keyword'] = self.__ScoreResults_keyword__(base_query,retrieved_info)

        return score_results


class ManageInformation(FilterContext):
    """
    A class for managing information in a database.

    attr:
        - dbName (str): Name of the database being managed.
        - client: Client object for interacting with the database.
        - embedding_model: Sentence embedding model for generating embeddings.
    """
    def __init__(self, dbName: str):
        """
        Initialize the ManageInformation instance.

        args:
            - dbName (str): Name of the database to manage.
        """
        self.dbName = dbName
        self.client = None
        self.embedding_model = SentenceTransformer('BAAI/bge-small-en-v1.5')

    def initialize_client(self, path: str):
        """
        Initialize the client for the specified database.

        args:
            - path (str): Path to the database.

        notes:
            - This method is specific to the 'chroma' database.
        """
        if self.dbName == 'chroma':
            self.client = Chroma.getclient(path=path)

    def add_new_data(self, data, data_metadata, vdb_metadata):
        """
        Add new data to the database.

        args:
            - data: Data to be added.
            - data_metadata: Metadata for the data.
            - vdb_metadata: Metadata specific to the virtual database (vdb).

        returns:
            - str: Message indicating the success of the operation.

        notes:
            - Embeddings are generated for the data using the embedding model.
            - Each data point is represented as a dictionary containing 'chunked_data', 'embedding', 'metadata', and 'id'.
        """
        embedding_data = [
            {
                'chunked_data' : info,
                'embedding' : self.embedding_model.encode(info),
                'metadata' : md,
                'id' : uuid.uuid3(uuid.NAMESPACE_DNS, info)
            } for info, md in zip(data, data_metadata)
        ]

        Chroma.addData(self.client, embedding_data, vdb_metadata)

        return "Success"

    def get_data(self, query, vdb_metadata):
        """
        Retrieve data from the database and score each retrieved data point.

        args:
            - query: Query to retrieve data.
            - vdb_metadata: Metadata specific to the virtual database.

        returns:
            - dict: Scored results containing retrieved data, distance, and scores.
        """
        # Encode the query using the embedding model
        query_embed = self.embedding_model.encode(query)

        # Retrieve information from the database
        retrieved_info = Chroma.getData(self.client,query_embed,vdb_metadata)

        # Dictionary to store scored results
        results_scored = {}

        # Iterate over retrieved data points and score each one
        for ind, retrieved_dp in enumerate(retrieved_info):
            # Score the retrieved data point using the superclass ScoreResults method
            results_scored[ind] = {
                'data' : retrieved_dp['Document'],                              # Retrieved data
                'distance' : retrieved_dp['distance'],                          # Distance metric
                'scores' : super().ScoreResults(query,retrieved_dp['Document']) # Scores generated for the retrieved data
            }

        return results_scored