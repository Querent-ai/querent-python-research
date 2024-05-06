# import asyncio
# import json
# import pytest
# from querent.callback.event_callback_interface import EventCallbackInterface
# from querent.common.types.querent_queue import QuerentQueue
# from querent.common.types.querent_event import EventState, EventType
# from querent.common.types.ingested_tokens import IngestedTokens
# from querent.common.types.querent_queue import QuerentQueue
# from querent.config.core.llm_config import LLM_Config
# from querent.core.transformers.bert_ner_opensourcellm import BERTLLM
# from querent.querent.resource_manager import ResourceManager
# from querent.querent.querent import Querent


# @pytest.mark.asyncio
# @pytest.mark.parametrize("input_data,ner_model_name, llm_class,expected_entities,filter_entities", [
#     #("Nishant is working from Delhi. Ansh is working from Punjab. Ayush is working from Odisha. India is very good at playing cricket. Nishant is working from Houston.", "dbmdz/bert-large-cased-finetuned-conll03-english", BERTLLM, ["http://geodata.org/Nishant", "http://geodata.org/Delhi"], False),
#     #("Nishant is working from Delhi. Ansh is working from Punjab. Ayush is working from Odisha. India is very good at playing cricket. Nishant is working from Houston.", "dbmdz/bert-large-cased-finetuned-conll03-english", BERTLLM, ["http://geodata.org/Nishant", "http://geodata.org/Delhi"], False),
#     (["In this study, we present evidence of a Paleocene–Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accommodation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sediment supply during the PETM, which is archived as a particularly thick sedimentary section in  the deep-sea fans of the GoM basin. The Paleocene–Eocene Thermal Maximum (PETM) (ca. 56 Ma) was a rapid global warming event characterized by the rise of temperatures to5–9 °C (Kennett and Stott, 1991), which caused substantial environmental changes around the globe."],
# "botryan96/GeoBERT", BERTLLM, ["tectonic perturbations","downstream sectors"], True)])



# async def test_bertllm_ner_tokenization_and_entity_extraction(input_data, ner_model_name, llm_class, expected_entities, filter_entities):
#     input_queue = QuerentQueue()
#     resource_manager = ResourceManager()
#     ingested_data = IngestedTokens(file="dummy_1_file.txt", data=["""In the verdant campus of Greenwood University, nestled within the bustling city of Metroville, the dynamics of academic and administrative decisions paint a complex tableau of interactions and outcomes. Recently, the University Board announced a significant increase in research funding for environmental science programs, aiming to position Greenwood as a leader in sustainable urban development studies. This decision was influenced heavily by the growing concern among the student body and faculty about the city's escalating pollution levels.
# Dr. Emily Stanton, a prominent figure in the Environmental Sciences Department, has been advocating for cleaner energy use on campus for years. Her relentless efforts finally paid off when the university committed to a 40% reduction in carbon emissions over the next five years. Dr. Stanton's research on the impact of urban green spaces on mental health has not only garnered international acclaim but has also led to the integration of more biophilic design elements in the university's new architectural plans.
# The sociology department, led by Professor Liam Zheng, has embarked on a collaborative project with the Environmental Sciences Department to study the socio-economic factors affecting access to clean water in underserved communities within Metroville. This interdisciplinary approach has fostered a unique synergy between the two departments, enriching the academic experience for students enrolled in both programs.
# Meanwhile, the student government, recognizing the importance of mental health awareness, has launched a series of workshops and seminars on stress management, particularly focusing on the stresses associated with academic life. These initiatives have been well-received, with many students reporting a greater sense of well-being and community support.
# In a surprising turn of events, the university's sports teams have seen a remarkable improvement in performance, a phenomenon some attribute to the enhanced fitness programs and nutritional guidelines introduced by the new athletic director, Coach Anna Torres. Coach Torres, with her innovative approach to student-athlete health and her emphasis on holistic training methods, has significantly influenced the physical and mental preparedness of Greenwood's athletes.
# Amid these developments, the university library announced a partnership with the local public library system to expand access to digital resources, a move that promises to democratize information access and support lifelong learning within the broader Metroville community.
# This narrative tapestry of Greenwood University showcases a myriad of relationships, from causal links between advocacy and policy changes to collaborative synergies across departments, reflecting the rich and interconnected life of its inhabitants."""])
#     await input_queue.put(ingested_data)
#     ingested_data = IngestedTokens(file="dummy_1_file.txt", data=None)
#     await input_queue.put(ingested_data)
#     await input_queue.put(IngestedTokens(file="dummy_2_file.txt", data=None, error="error"))
#     bert_llm_config = LLM_Config(
#         # ner_model_name=ner_model_name,
#         enable_filtering=filter_entities,
#         filter_params={
#             'score_threshold': 0.5,
#             'attention_score_threshold': 0.1,
#             'similarity_threshold': 0.5,
#             'min_cluster_size': 5,
#             'min_samples': 3,
#             'cluster_persistence_threshold':0.2
#         }
#             , fixed_relationships=[
#     "Increase in research funding leads to environmental science focus",
#     "Dr. Emily Stanton's advocacy for cleaner energy",
#     "University's commitment to reduce carbon emissions",
#     "Dr. Stanton's research influences architectural plans",
#     "Collaborative project between sociology and environmental sciences",
#     "Student government launches mental health awareness workshops",
#     "Enhanced fitness programs improve sports teams' performance",
#     "Coach Torres influences student-athletes' holistic health",
#     "Partnership expands access to digital resources",
#     "Interdisciplinary approach enriches academic experience"
# ]
#             , sample_relationships=[
#     "Causal",
#     "Contributory",
#     "Causal",
#     "Influential",
#     "Collaborative",
#     "Initiative",
#     "Beneficial",
#     "Influential",
#     "Collaborative",
#     "Enriching"
# ]
#     )
#     llm_instance = BERTLLM(input_queue, bert_llm_config)
#     class StateChangeCallback(EventCallbackInterface):
#         async def handle_event(self, event_type: EventType, event_state: EventState):
#             print("------------------------------inside state change callback handle")
#             if event_state['event_type'] == EventType.Graph:
#                 triple = json.loads(event_state['payload'])
#                 print("------------------------------------triple: {}".format(triple))
#     llm_instance.subscribe(EventType.Graph, StateChangeCallback())
#     querent = Querent(
#         [llm_instance],
#         resource_manager=resource_manager,
#     )

#     await querent.start()

