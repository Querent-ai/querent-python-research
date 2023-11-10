from querent.common.types.querent_event import EventState, EventType
from querent.core.base_engine import BaseEngine
from querent.common.types.querent_event import EventState, EventType
from querent.common.types.querent_queue import QuerentQueue
from typing import Any, List, Tuple
from querent.logging.logger import setup_logger
from querent.kg.querent_kg import QuerentKG
from querent.common.types.ingested_tokens import IngestedTokens
from querent.common.types.ingested_messages import IngestedMessages
from querent.common.types.ingested_code import IngestedCode

from querent.config.core.relation_config import RelationshipExtractorConfig


class RealtionExtractor(BaseEngine):
    def __init__(self, config: RelationshipExtractorConfig):  
        super().__init__()
        self.logger = setup_logger(config.logger, "RelationshipExtractor")
        self.semantic_graph = QuerentKG(config.graph_config)
        self.config = config
        # Subscribe to TOKEN_PROCESSED event
        self.subscribe(EventType.TOKEN_PROCESSED, self.handle_event)

    def validate(self) -> bool:
        pass

    def process_messages(self, data: IngestedMessages):
        return super().process_messages(data)

    async def process_code(self, data: IngestedCode):
        return super().process_messages(data)
    
    async def handle_event(self, event_type: EventType, event_state: EventState):
        # This method is called when a TOKEN_PROCESSED event occurs
        if event_type == EventType.TOKEN_PROCESSED:
            await self.process_event(event_state)

    async def process_event(self, event_state: EventState):
        # Asynchronous processing of the event
        triples = event_state.payload
        # Extract relationships here (placeholder for your logic)
        relationships = self.extract_relationships(triples)
        # Emit a relationship_extracted signal with the extracted relationships
        current_state = EventState(EventType.RELATIONSHIP_ESTABLISHED, 1.0, relationships)
        await self.set_state(new_state=current_state)
        
    def extract_relationships(self, triples):
        # Actual extraction logic goes here
        # This is a placeholder for your relationship extraction method
        # For the sake of example, let's just return the triples
        return triples




 








[
  ('tectonic', '{"context": "In this study, we present evidence of a Paleocene\\u2013Eocene Thermal Maximum (PETM) record within a 543-m-thick (1780 ft) deep-marine section in the Gulf of Mexico (GoM) using organic carbon stable isotopes and biostratigraphic constraints. We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin.", "entity1_score": 1.0, "entity2_score": 1.0, "entity1_label": "B-GeoPetro", "entity2_label": "B-GeoMeth", "entity1_nn_chunk": "tectonic perturbations", "entity2_nn_chunk": "the upstream North American catchments", "file_path": "dummy_1_file.txt", "entity1_attnscore": 0.25, "entity2_attnscore": 0.11, "pair_attnscore": 0.15, "entity1_embedding": [4.785828113555908, 4.2147417068481445, 4.608402729034424, 7.86382532119751, -3.119875907897949, 6.4056620597839355, 4.736032962799072, 0.40054139494895935, -1.7422124147415161, 9.150322914123535], "entity2_embedding": [4.749422073364258, 3.777057647705078, 6.303576946258545, 8.151358604431152, -2.55820369720459, 5.3259968757629395, 6.484385967254639, 0.4279687702655792, -0.9084129333496094, 7.9470624923706055], "sentence_embedding": [-0.4015790522098541, 3.746861696243286, 6.176400661468506, 5.342568397521973, -0.9461199641227722, -6.17316198348999, -4.8703389167785645, 13.388699531555176, 8.222224235534668, 14.191060066223145]}', 'upstream'), 
  ('basin', '{"context": "We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin.", "entity1_score": 1.0, "entity2_score": 1.0, "entity1_label": "B-GeoPetro", "entity2_label": "B-GeoMeth", "entity1_nn_chunk": "the GoM basin", "entity2_nn_chunk": "upstream", "file_path": "dummy_1_file.txt", "entity1_attnscore": 0.26, "entity2_attnscore": 0.09, "pair_attnscore": 0.13, "entity1_embedding": [4.75761604309082, 3.4331743717193604, 4.266805171966553, 8.083751678466797, -3.261979103088379, 5.861548900604248, 5.962497234344482, 0.6605709195137024, -1.374169945716858, 10.495802879333496], "entity2_embedding": [4.707525253295898, 3.565460205078125, 6.727005958557129, 7.980961322784424, -2.6597471237182617, 5.267481327056885, 6.5619893074035645, 0.22673408687114716, -0.8828330039978027, 8.61778736114502], "sentence_embedding": [0.15698224306106567, 3.8285863399505615, 6.090454578399658, 4.998751163482666, -2.00986647605896, -6.002192497253418, -4.941530704498291, 13.459432601928711, 8.741031646728516, 11.845033645629883]}', 'upstream'),
  ('deposition', '{"context": "We suggest that climate and tectonic perturbations in the upstream North American catchments can induce a substantial response in the downstream sectors of the Gulf Coastal Plain and ultimately in the GoM. This relationship is illustrated in the deep-water basin by (1) a high accom- modation and deposition of a shale interval when coarse-grained terrigenous material was trapped upstream at the onset of the PETM, and (2) a considerable increase in sedi- ment supply during the PETM, which is archived as a particularly thick sedimentary section in the deep-sea fans of the GoM basin.", "entity1_score": 1.0, "entity2_score": 1.0, "entity1_label": "B-GeoPetro", "entity2_label": "B-GeoMeth", "entity1_nn_chunk": "deposition", "entity2_nn_chunk": "upstream", "file_path": "dummy_1_file.txt", "entity1_attnscore": 0.26, "entity2_attnscore": 0.09, "pair_attnscore": 0.13, "entity1_embedding": [4.505099773406982, 4.15098762512207, 4.646312713623047, 7.436164379119873, -3.1875975131988525, 6.197781085968018, 4.853282451629639, 0.5896610617637634, -0.9382550120353699, 9.722227096557617], "entity2_embedding": [4.713261127471924, 3.442910671234131, 6.62761926651001, 8.26006031036377, -2.7525744438171387, 5.223714351654053, 6.508554935455322, 0.2672390639781952, -1.0225239992141724, 8.644356727600098], "sentence_embedding": [0.1906796097755432, 3.833495616912842, 6.085261344909668, 4.97797966003418, -2.1924057006835938, -5.993052005767822, -4.952077865600586, 13.469947814941406, 8.780710220336914, 11.937219619750977]}', 'upstream')
]