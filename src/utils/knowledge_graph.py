import networkx as nx
import json
import os
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class KnowledgeGraph:
    def __init__(self, persist_path: str = "data/knowledge_graph/graph.json"):
        self.persist_path = persist_path
        self.graph = nx.DiGraph()
        self._load_graph()

    def _load_graph(self):
        """Load graph from JSON file if exists."""
        if os.path.exists(self.persist_path):
            try:
                with open(self.persist_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.graph = nx.node_link_graph(data)
                logger.info(f"Loaded knowledge graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges.")
            except Exception as e:
                logger.error(f"Failed to load knowledge graph: {e}")
                self.graph = nx.DiGraph()
        else:
            os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)
            self.graph = nx.DiGraph()

    def save_graph(self):
        """Save graph to JSON file."""
        try:
            data = nx.node_link_data(self.graph)
            with open(self.persist_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("Knowledge graph saved.")
        except Exception as e:
            logger.error(f"Failed to save knowledge graph: {e}")

    def add_entity(self, name: str, entity_type: str, properties: Dict = None):
        """Add a node to the graph."""
        if not properties:
            properties = {}
        properties['type'] = entity_type
        self.graph.add_node(name, **properties)

    def add_relation(self, source: str, target: str, relation_type: str, properties: Dict = None):
        """Add an edge between two nodes."""
        if not self.graph.has_node(source):
            self.add_entity(source, "Unknown")
        if not self.graph.has_node(target):
            self.add_entity(target, "Unknown")
            
        if not properties:
            properties = {}
        properties['relation'] = relation_type
        self.graph.add_edge(source, target, **properties)

    def query_related(self, entity_name: str, max_depth: int = 1) -> List[Dict]:
        """Find related entities within max_depth."""
        if not self.graph.has_node(entity_name):
            return []
        
        results = []
        # Get immediate neighbors (both incoming and outgoing)
        # For simple depth 1
        if max_depth == 1:
            for neighbor in self.graph.neighbors(entity_name):
                edge_data = self.graph.get_edge_data(entity_name, neighbor)
                node_data = self.graph.nodes[neighbor]
                results.append({
                    "entity": neighbor,
                    "type": node_data.get('type', 'Unknown'),
                    "relation": edge_data.get('relation', 'related_to')
                })
            # Also check incoming edges (predecessors)
            for pred in self.graph.predecessors(entity_name):
                edge_data = self.graph.get_edge_data(pred, entity_name)
                node_data = self.graph.nodes[pred]
                results.append({
                    "entity": pred,
                    "type": node_data.get('type', 'Unknown'),
                    "relation": f"target_of_{edge_data.get('relation', 'related_to')}"
                })
        
        return results

    def extract_triples_from_text(self, text: str):
        """
        Simple heuristic triple extractor.
        In production, this should use an LLM or NLP model.
        Format: "Subject | Predicate | Object"
        """
        lines = text.split('\n')
        for line in lines:
            if '|' in line and line.count('|') == 2:
                parts = [p.strip() for p in line.split('|')]
                if len(parts) == 3:
                    subj, rel, obj = parts
                    self.add_entity(subj, "Concept")
                    self.add_entity(obj, "Concept")
                    self.add_relation(subj, obj, rel)

    def search_path(self, start: str, end: str) -> List[str]:
        """Find path between two entities (e.g. Service -> Vulnerability -> Exploit)."""
        try:
            return nx.shortest_path(self.graph, start, end)
        except nx.NetworkXNoPath:
            return []
        except nx.NodeNotFound:
            return []
