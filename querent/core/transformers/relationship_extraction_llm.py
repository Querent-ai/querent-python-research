import json
from querent.callback.event_callback_interface import EventCallbackInterface
from querent.common.types.querent_event import EventState, EventType
from querent.common.types.querent_event import EventState, EventType
from typing import Any, List, Tuple
from querent.kg.ner_helperfunctions.graph_manager_semantic import Semantic_KnowledgeGraphManager
from querent.kg.rel_helperfunctions.BSM_relationfilter import BSMBranch
from querent.kg.rel_helperfunctions.embedding_store import EmbeddingStore
from querent.kg.rel_helperfunctions.questionanswer_llama2 import QASystem
from querent.kg.rel_helperfunctions.rag_retriever import RAGRetriever
from querent.kg.rel_helperfunctions.rel_normalize import TextNormalizer
from querent.logging.logger import setup_logger
from querent.config.core.relation_config import RelationshipExtractorConfig

from querent.common.types.querent_queue import QuerentQueue
from langchain.docstore.document import Document
import ast


"""
    A class that extends the EventCallbackInterface to extract relationships between entities in a contextual triple(s) to create semantic triples for a Knowledge Graph.

    The RelationExtractor is responsible for handling events, particularly updates to a Named Entity Recognition (NER)
    graph, and extracting relationships between entities. It uses an embedding store for efficient similarity searches
    and a QA system for relationship extraction.

    Attributes:
        logger (Logger): A logging instance for recording events and errors.
        config (RelationshipExtractorConfig): Configuration settings for the relationship extractor.
        create_emb (EmbeddingStore): An instance of EmbeddingStore for handling vector storage and retrieval.
        template (str): The template string for QA prompts.
        qa_system (QASystem): An instance of QASystem for asking questions about relationships.

    Methods:
        handle_event(event_type: EventType, event_state: EventState): Handles the event based on the type and state.
        validate(data) -> bool: Validates the input data format for relationship extraction.
        process_event(event_state: EventState): Processes the event and extracts relationships.
        normalizetriples_buildindex(triples): Normalizes triples and builds a FAISS index for them.
        extract_relationships(triples): Extracts relationships from triples using QA prompts.
        trim_triples(data): Trims triples to a required format.
        build_faiss_index(data): Builds a FAISS index from the provided data.
    """


class RelationExtractor():
    def __init__(self, config: RelationshipExtractorConfig):  
        self.logger = setup_logger(config.logger, "RelationshipExtractor")
        try:
            super().__init__()
            self.config = config
            self.create_emb = EmbeddingStore(vector_store_path=config.vector_store_path)
            self.qa_system = QASystem(
                rel_model_path=config.model_path,
                rel_model_type=config.model_type,
                )
            
            # self.qa_system_bsm_validator = QASystem(
            #     rel_model_path=config.bsm_validator_model_path,
            #     rel_model_type=config.bsm_validator_model_type,
            #     emb_model_name=config.emb_model_name,
            #     faiss_index_path=config.get_faiss_index_path()
            #     )
            self.rag_approach = config.rag_approach
            if  self.rag_approach == True:
                self.rag_retriever = RAGRetriever(
                faiss_index_path=config.get_faiss_index_path(),
                emb_model_name=config.emb_model_name,
                embedding_store=self.create_emb,
                logger=self.logger)
            self.bsmbranch = BSMBranch()
            self.sub_tasks = config.dynamic_sub_tasks
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            raise Exception(f"Initialization failed: {e}")
                rel_model_path=config.rel_model_path,
                rel_model_type="llama",
                emb_model_name=config.emb_model_name,
                faiss_index_path=config.faiss_index_path,
                template=self.template,
            )
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            raise Exception(f"Initialization failed: {e}")

    def validate(self, data) -> bool:
        try:
            if not data:
                self.logger.error(
                    f"Invalid {self.__class__.__name__} configuration. Empty List Error"
                )
                return False

            if not isinstance(data, list):
                self.logger.error(
                    f"Invalid {self.__class__.__name__} configuration. Incorrect Format Error: Not a list"
                )
                return False

            item = data[0]
            if not isinstance(item, tuple) or len(item) != 3:
                self.logger.error(
                    f"Invalid {self.__class__.__name__} configuration. Incorrect Format Error: Item is not a triple"
                )
                return False

            if not (
                isinstance(item[0], str)
                and isinstance(item[2], str)
                and isinstance(item[1], str)
            ):
                self.logger.error(
                    f"Invalid {self.__class__.__name__} configuration. Incorrect Format Error: Incorrect item format"
                )
                return False

            return True
        except Exception as e:
            self.logger.error(f"Error in validation: {e}")
            return False

    def generate_embeddings(self, event_state: EventState):
        try:
            triples = event_state.payload
            processed_pairs = []

            for entity, json_string, related_entity in triples:
                data = json.loads(json_string)
                context = data.get("context", "")
                predicate = data.get("predicate","")
                predicate_type = data.get("predicate_type","")

                # Generate embeddings for the context
                context_embeddings = self.create_emb.get_embeddings([context])[0]

                essential_data = {
                    "context": context,
                    "context_embeddings" : context_embeddings,
                    "predicate_type": predicate_type,
                    "predicate" : predicate
                }
                updated_json_string = json.dumps(essential_data)
                processed_pairs.append((entity, updated_json_string, related_entity))

            return processed_pairs
        except Exception as e:
            self.logger.error(f"Error in extracting embeddings: {e}")
            raise Exception(f"Error in extracting embeddings: {e}")
    
    def process_tokens(self, event_state: EventState):
        try:
            triples = event_state.payload
            trimmed_triples = self.normalizetriples_buildindex(triples)
            print("completed normaliziation")
            if self.rag_approach == True:
                print("inside rag approach")
                self.rag_retriever.build_faiss_index(trimmed_triples)
            relationships = self.extract_relationships(triples)
            graph_manager = Semantic_KnowledgeGraphManager()
            graph_manager.feed_input(relationships)
            final_triples = graph_manager.retrieve_triples()
        
            return relationships, final_triples
        
        except Exception as e:
            self.logger.error(f"Error in processing event: {e}")
            raise Exception(f"Invalid in processing event: {e}")

    def normalizetriples_buildindex(self, triples):
        try:
            if not self.validate(triples):
                self.logger.error("Invalid triples for relationship extractor")
                raise ValueError("Invalid triples for relationship extractor")
            normalizer = TextNormalizer()
            normalized_triples = normalizer.normalize_triples(triples)
            trimmed_triples = self.trim_triples(normalized_triples)
            return trimmed_triples
        except Exception as e:
            self.logger.error(f"Error in normalizing/building index: {e}")
            raise Exception(f"Error in normalizing/building index: {e}")
    
    def create_semantic_triple(self, input1, input2):
        input1_data = ast.literal_eval(input1)
        input2_data = ast.literal_eval(input2)
        triple = (
            input1_data.get("subject",""),
            json.dumps({
                "predicate": input1_data.get("predicate",""),
                "predicate_type": input1_data.get("predicate_type",""),
                "context": input2_data.get("context", ""),
                "file_path": input2_data.get("file_path", "")
            }),
            input1_data.get("object","")
        )
        return triple

    def extract_relationships(self, triples):
        try:
            updated_triples = []
            for _, predicate_str, _ in triples:
                all_tasks = []
                documents=[]
                data = json.loads(predicate_str)
                context = data['context']
                predicate = predicate_str if isinstance(predicate_str, dict) else json.loads(predicate_str)
                if self.rag_approach == True:
                    db = self.rag_retriever.load_faiss_index()
                    prompt=("What is the relationship between {entity1} and the Object is {entity2}.").format(entity1=predicate.get('entity1_nn_chunk', ''), entity2=predicate.get('entity2_nn_chunk', ''))
                    top_docs = self.rag_retriever.retrieve_documents(db, prompt=prompt)
                    print(top_docs)
                    documents = top_docs
                else:
                    doc =  Document(page_content=context)
                    documents.append(doc)    
                all_tasks.append((" I want to define a semantic knowledge graph triple (Subject, Predicate, Object). The Subject is {entity1} and the Object is {entity2}.").format(entity1=predicate.get('entity1_nn_chunk', ''), entity2=predicate.get('entity2_nn_chunk', '')))
                sub_task_list_llm = self.bsmbranch.create_sub_tasks(llm = self.qa_system.llm, template=self.config.get_template("default"), tasks=all_tasks,model_type=self.qa_system.rel_model_type)
                for task in sub_task_list_llm:    
                    answer_relation = self.qa_system.ask_question(prompt=task[2], top_docs=documents, llm_chain=task[0])
                    updated_triple= self.create_semantic_triple(answer_relation, predicate_str)
                    updated_triples.append(updated_triple)
            return updated_triples
        except Exception as e:
            self.logger.error(f"Error in extracting relationships: {e}")

    def trim_triples(self, data):
        try:
            trimmed_data = []
            for entity1, predicate, entity2 in data:
                predicate_dict = json.loads(predicate)
                trimmed_predicate = {
                    'context': predicate_dict.get('context', ''),
                    'entity1_nn_chunk': predicate_dict.get('entity1_nn_chunk', ''),
                    'entity2_nn_chunk': predicate_dict.get('entity2_nn_chunk', ''),
                    'file_path': predicate_dict.get('file_path', '')
                }
                trimmed_data.append((entity1, trimmed_predicate, entity2))

            return trimmed_data
        except Exception as e:
            self.logger.error(f"Error in trimming triples: {e}")
            raise Exception(f'Error in trimming triples: {e}')


       
def main():
    # Configuration for testing
    config = RelationshipExtractorConfig(
        # Add necessary configuration parameters here
    )

    # Initialize the RelationExtractor
    relation_extractor = RelationExtractor(config)

    # Simulate an event with triples
    test_triples = [
                    ('tectonic', '{"context": "In this study, we present evidence of a Paleocene\\u2013Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin.", "entity1_score": 1.0, "entity2_score": 1.0, "entity1_label": "B-GeoPetro", "entity2_label": "B-GeoMeth", "entity1_nn_chunk": "tectonic perturbations", "entity2_nn_chunk": "the upstream North American catchments", "file_path": "dummy_1_file.txt", "entity1_attnscore": 0.25, "entity2_attnscore": 0.11, "pair_attnscore": 0.15, "entity1_embedding": [4.53109884262085, 11.361151695251465, 2.6806282997131348, -1.9492037296295166, 1.8856709003448486, 10.950224876403809, 0.6408112049102783, -1.6457669734954834, 1.455888271331787, 0.33587002754211426], "entity2_embedding": [5.315560817718506, 10.279397964477539, 0.9560787081718445, -2.3691341876983643, 2.5708444118499756, 11.079018592834473, 1.4472755193710327, -0.649744987487793, 1.044495701789856, 1.2889022827148438], "sentence_embedding": [4.70822811126709, 4.0861968994140625, 6.845388889312744, 5.689976692199707, 4.647808074951172, 5.52365255355835, -1.1442636251449585, 6.748215198516846, 4.243872165679932, 8.574851989746094]}', 'upstream'), 
                    ('tectonic', '{"context": "In this study, we present evidence of a Paleocene\\u2013Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin.", "entity1_score": 1.0, "entity2_score": 1.0, "entity1_label": "B-GeoPetro", "entity2_label": "B-GeoPetro", "entity1_nn_chunk": "tectonic perturbations", "entity2_nn_chunk": "the downstream sectors", "file_path": "dummy_1_file.txt", "entity1_attnscore": 0.25, "entity2_attnscore": 0.49, "pair_attnscore": 0.33, "entity1_embedding": [4.159348011016846, 11.413848876953125, 3.0077531337738037, -1.673252820968628, 2.2821056842803955, 10.929729461669922, 0.8358833193778992, -1.7280113697052002, 1.3248097896575928, -0.01896567828953266], "entity2_embedding": [4.862512588500977, 11.96029281616211, 2.9977223873138428, -2.69915509223938, 2.1833457946777344, 10.813895225524902, 0.9246777892112732, -1.6998053789138794, 0.9003339409828186, -0.32436245679855347], "sentence_embedding": [4.900198936462402, 4.258647918701172, 7.03038215637207, 5.886263847351074, 4.795965194702148, 5.375088214874268, -1.3931838274002075, 6.579791069030762, 4.41320276260376, 8.368497848510742]}', 'downstream'), 
                    # ('basin', '{"context": "We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin.", "entity1_score": 1.0, "entity2_score": 1.0, "entity1_label": "B-GeoPetro", "entity2_label": "B-GeoPetro", "entity1_nn_chunk": "the GoM basin", "entity2_nn_chunk": "deposition", "file_path": "dummy_1_file.txt", "entity1_attnscore": 0.26, "entity2_attnscore": 0.26, "pair_attnscore": 0.26, "entity1_embedding": [4.934263229370117, 11.774312019348145, 3.022930145263672, -2.702202558517456, 3.046722412109375, 10.930811882019043, 0.5461289286613464, -2.7191731929779053, 1.175268292427063, 0.6289199590682983], "entity2_embedding": [4.053053855895996, 12.055774688720703, 3.1768407821655273, -2.1552419662475586, 2.7527339458465576, 10.879389762878418, 1.3220860958099365, -1.6639324426651, 1.2357418537139893, -0.2998717129230499], "sentence_embedding": [3.977400302886963, 3.567084550857544, 6.127756595611572, 4.913837432861328, 3.868380069732666, 6.299326419830322, -0.42848068475723267, 7.206186294555664, 4.454614162445068, 8.533939361572266]}', 'deposition'), 
                    # ('basin', '{"context": "We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin.", "entity1_score": 1.0, "entity2_score": 1.0, "entity1_label": "B-GeoPetro", "entity2_label": "B-GeoPetro", "entity1_nn_chunk": "the GoM basin", "entity2_nn_chunk": "a shale interval", "file_path": "dummy_1_file.txt", "entity1_attnscore": 0.26, "entity2_attnscore": 0.1, "pair_attnscore": 0.14, "entity1_embedding": [4.967203617095947, 12.023656845092773, 3.0271494388580322, -2.749804973602295, 2.9753799438476562, 10.82083511352539, 0.7863883376121521, -2.389293909072876, 1.39449942111969, 0.6251224279403687], "entity2_embedding": [4.121479034423828, 11.785114288330078, 3.3272645473480225, -2.3444883823394775, 2.9253554344177246, 10.702908515930176, 0.9783485531806946, -2.212533473968506, 1.558760404586792, 0.9618946313858032], "sentence_embedding": [3.9194209575653076, 3.538297176361084, 6.077632904052734, 4.849460124969482, 3.8654282093048096, 6.30136251449585, -0.4998748004436493, 7.141021251678467, 4.273437976837158, 8.550708770751953]}', 'shale'), 
                    # ('basin', '{"context": "We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin.", "entity1_score": 1.0, "entity2_score": 1.0, "entity1_label": "B-GeoPetro", "entity2_label": "B-GeoMeth", "entity1_nn_chunk": "the GoM basin", "entity2_nn_chunk": "upstream", "file_path": "dummy_1_file.txt", "entity1_attnscore": 0.26, "entity2_attnscore": 0.09, "pair_attnscore": 0.13, "entity1_embedding": [4.8886003494262695, 12.261992454528809, 2.8996336460113525, -2.774608850479126, 3.050241708755493, 11.048797607421875, 0.891882598400116, -2.389878749847412, 1.2021150588989258, -0.13697971403598785], "entity2_embedding": [5.162384510040283, 10.326823234558105, 1.4897805452346802, -2.6529133319854736, 2.926510810852051, 10.958639144897461, 1.2534445524215698, -0.7501385807991028, 0.8368440270423889, 1.6652268171310425], "sentence_embedding": [4.01706600189209, 3.5616888999938965, 6.165895462036133, 4.963111400604248, 3.961824893951416, 6.206106662750244, -0.6160885095596313, 7.147684574127197, 4.14679479598999, 8.693338394165039]}', 'upstream'), 
                    # ('deposition', '{"context": "We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin.", "entity1_score": 1.0, "entity2_score": 1.0, "entity1_label": "B-GeoPetro", "entity2_label": "B-GeoPetro", "entity1_nn_chunk": "deposition", "entity2_nn_chunk": "a shale interval", "file_path": "dummy_1_file.txt", "entity1_attnscore": 0.26, "entity2_attnscore": 0.1, "pair_attnscore": 0.14, "entity1_embedding": [4.073841094970703, 11.899940490722656, 3.1453816890716553, -2.096740961074829, 2.9288885593414307, 10.895021438598633, 1.2852692604064941, -1.7730344533920288, 1.281164288520813, -0.4728916883468628], "entity2_embedding": [4.241306781768799, 11.913191795349121, 3.348283529281616, -2.3395373821258545, 2.7789437770843506, 10.83830738067627, 0.9491587281227112, -2.0985398292541504, 1.602471947669983, 0.7614753842353821], "sentence_embedding": [3.9496638774871826, 3.5428617000579834, 6.105378150939941, 4.885227203369141, 3.9083197116851807, 6.258923053741455, -0.5565788745880127, 7.139645576477051, 4.217475414276123, 8.606756210327148]}', 'shale'), 
                    # ('deposition', '{"context": "We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin.", "entity1_score": 1.0, "entity2_score": 1.0, "entity1_label": "B-GeoPetro", "entity2_label": "B-GeoMeth", "entity1_nn_chunk": "deposition", "entity2_nn_chunk": "upstream", "file_path": "dummy_1_file.txt", "entity1_attnscore": 0.26, "entity2_attnscore": 0.09, "pair_attnscore": 0.13, "entity1_embedding": [3.9298927783966064, 11.672919273376465, 2.9006597995758057, -2.1623315811157227, 2.8971853256225586, 10.672797203063965, 1.1368777751922607, -1.8468892574310303, 1.5289751291275024, -0.41427430510520935], "entity2_embedding": [5.004333019256592, 10.867509841918945, 1.525020718574524, -2.5237743854522705, 2.615407943725586, 10.994601249694824, 1.479994297027588, -0.845661461353302, 0.29171520471572876, 1.6745482683181763], "sentence_embedding": [3.9413139820098877, 3.5352959632873535, 6.098677158355713, 4.8766560554504395, 3.9269216060638428, 6.240334510803223, -0.5966213345527649, 7.1256608963012695, 4.19922399520874, 8.645011901855469]}', 'upstream')
                    
                    ]
    try:
        # extracted_relationships = relation_extractor.extract_relationships(test_triples)
        # extracted_relationships = relation_extractor.process_tokens(EventState(EventType.ContextualEmbeddings, 1.0, test_triples, "dummy.txt"))
        # print("Extracted Relationships:", extracted_relationships)
        extracted_relationships = relation_extractor.generate_embeddings(EventState(EventType.ContextualEmbeddings, 1.0, test_triples, "dummy.txt"))
        print("Extracted Relationships:", extracted_relationships)
    except Exception as e:
        print(f"Error during extraction: {e}")

  main()

  
