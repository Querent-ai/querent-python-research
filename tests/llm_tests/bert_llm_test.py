import asyncio
import pytest
from querent.callback.event_callback_interface import EventCallbackInterface
from querent.common.types.querent_queue import QuerentQueue
from querent.common.types.querent_event import EventState, EventType
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.querent_queue import QuerentQueue
from querent.config.core.bert_llm_config import BERTLLMConfig
from querent.core.transformers.bert_llm import BERTLLM
from querent.querent.resource_manager import ResourceManager
from querent.querent.querent import Querent
import os
from querent.config.core.relation_config import RelationshipExtractorConfig
from querent.core.transformers.relationship_extraction_llm import RelationExtractor
from querent.config.core.relation_config import RelationshipExtractorConfig
from querent.core.transformers.relationship_extraction_llm import RelationExtractor


@pytest.mark.asyncio
@pytest.mark.parametrize("input_data,ner_model_name, llm_class,expected_entities,filter_entities", [
    #("Nishant is working from Delhi. Ansh is working from Punjab. Ayush is working from Odisha. India is very good at playing cricket. Nishant is working from Houston.", "dbmdz/bert-large-cased-finetuned-conll03-english", BERTLLM, ["http://geodata.org/Nishant", "http://geodata.org/Delhi"], False),
    #("Nishant is working from Delhi. Ansh is working from Punjab. Ayush is working from Odisha. India is very good at playing cricket. Nishant is working from Houston.", "dbmdz/bert-large-cased-finetuned-conll03-english", BERTLLM, ["http://geodata.org/Nishant", "http://geodata.org/Delhi"], False),
    ("""In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM)
record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM)
using organic carbon stable isotopes and biostratigraphic constraints. We suggest that
climate and tectonic perturbations in the upstream North American catchments can induce
a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately
in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom-
modation and deposition of a shale interval when coarse-grained terrigenous material
was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi-
ment supply during the PETM, which is archived as a particularly thick sedimentary
section in the deep-sea fans of the GoM basin.""","botryan96/GeoBERT", BERTLLM, ["http://geodata.org/tectonic","http://geodata.org/upstream"], True)])



async def test_bertllm_ner_tokenization_and_entity_extraction(input_data, ner_model_name, llm_class, expected_entities, filter_entities):
    input_queue = QuerentQueue()
    resource_manager = ResourceManager()
    
    ingested_data = IngestedTokens(file="dummy_1_file.txt", data=input_data)
    await input_queue.put(ingested_data)
    await input_queue.put(IngestedTokens(file="dummy_2_file.txt", data="dummy"))
    await input_queue.put(IngestedTokens(file="dummy_2_file.txt", data=None, error="error"))
    bert_llm_config = BERTLLMConfig(
        ner_model_name=ner_model_name,
        enable_filtering=filter_entities,
        filter_params={
            'score_threshold': 0.5,
            'attention_score_threshold': 0.1,
            'similarity_threshold': 0.5,
            'min_cluster_size': 5,
            'min_samples': 3,
            'cluster_persistence_threshold':0.2
            'cluster_persistence_threshold':0.2
        }
    )
    llm_instance = llm_class(input_queue, bert_llm_config)
    class StateChangeCallback(EventCallbackInterface):
        async def handle_event(self, event_type: EventType, event_state: EventState):
            assert event_state.event_type == EventType.TOKEN_PROCESSED or event_state.event_type == EventType.RELATIONSHIP_ESTABLISHED
            assert event_state.event_type == EventType.TOKEN_PROCESSED or event_state.event_type == EventType.RELATIONSHIP_ESTABLISHED
            triples = event_state.payload
            subjects = [triple[0].value for triple in triples]
            objects = [triple[2].value for triple in triples]
            predicates = [triple[1].value for triple in triples]
            if event_state.event_type == EventType.TOKEN_PROCESSED:
                assert expected_entities[0] in subjects
                assert expected_entities[1] in objects
            elif event_type == EventType.RELATIONSHIP_ESTABLISHED:
                assert 'http://geodata.org/tectonic' in subjects
            # Assuming 'triples' is already defined and populated
            for triple in triples:
                subject, predicate, object_ = triple[0].value, triple[1].value, triple[2].value
                print(f"({subject}, {predicate}, {object_})")


    llm_instance.subscribe(EventType.TOKEN_PROCESSED, StateChangeCallback())
    llm_instance.subscribe(EventType.RELATIONSHIP_ESTABLISHED, StateChangeCallback())
    llm_instance.subscribe(EventType.RELATIONSHIP_ESTABLISHED, StateChangeCallback())
    querent = Querent(
        [llm_instance],
        resource_manager=resource_manager,
    )

    await querent.start()

