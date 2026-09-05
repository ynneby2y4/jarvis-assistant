"""
Knowledge Base - AI learning and memory system
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from database.models import KnowledgeEntry
from config import config
from utils.logger import get_logger
import networkx as nx

logger = get_logger("knowledge_base")


class KnowledgeGraph:
    """Knowledge graph for learning and memory"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.db: Optional[Session] = None
        self.cache: Dict[str, Any] = {}
    
    def set_db(self, db: Session):
        """Set database connection"""
        self.db = db
    
    def add_knowledge(
        self,
        user_id: str,
        concept: str,
        data: Dict[str, Any],
        weight: float = 1.0,
        source: str = "user"
    ) -> Optional[KnowledgeEntry]:
        """Add knowledge entry"""
        try:
            entry = KnowledgeEntry(
                user_id=user_id,
                concept=concept,
                data=data,
                weight=weight,
                source=source
            )
            
            if self.db:
                self.db.add(entry)
                self.db.commit()
            
            # Add to graph
            self.graph.add_node(concept, weight=weight, data=data)
            self.cache[concept] = data
            
            logger.info(f"Knowledge added: {concept}")
            return entry
        
        except Exception as e:
            logger.error(f"Error adding knowledge: {e}")
            if self.db:
                self.db.rollback()
            return None
    
    def get_knowledge(self, user_id: str, concept: str) -> Optional[Dict]:
        """Get knowledge entry"""
        try:
            # Check cache first
            if concept in self.cache:
                return self.cache[concept]
            
            if self.db:
                entry = self.db.query(KnowledgeEntry)\
                    .filter(KnowledgeEntry.user_id == user_id)\
                    .filter(KnowledgeEntry.concept == concept)\
                    .first()
                
                if entry:
                    # Update access info
                    entry.last_accessed = datetime.utcnow()
                    entry.access_count += 1
                    self.db.commit()
                    
                    # Cache it
                    self.cache[concept] = entry.data
                    return entry.data
            
            return None
        
        except Exception as e:
            logger.error(f"Error getting knowledge: {e}")
            return None
    
    def get_related_knowledge(
        self,
        user_id: str,
        concept: str,
        depth: int = 2
    ) -> List[Dict]:
        """Get related knowledge entries"""
        try:
            if concept not in self.graph:
                return []
            
            # Find neighbors in graph
            neighbors = set()
            for node in nx.dfs_preorder_nodes(self.graph, concept, depth_limit=depth):
                if node != concept:
                    neighbors.add(node)
            
            # Fetch from database
            related = []
            if self.db:
                for neighbor in neighbors:
                    entry = self.db.query(KnowledgeEntry)\
                        .filter(KnowledgeEntry.user_id == user_id)\
                        .filter(KnowledgeEntry.concept == neighbor)\
                        .first()
                    
                    if entry:
                        related.append(entry.data)
            
            return related
        
        except Exception as e:
            logger.error(f"Error getting related knowledge: {e}")
            return []
    
    def link_concepts(self, concept1: str, concept2: str, weight: float = 1.0):
        """Create relationship between concepts"""
        try:
            self.graph.add_edge(concept1, concept2, weight=weight)
            logger.info(f"Concepts linked: {concept1} -> {concept2}")
        except Exception as e:
            logger.error(f"Error linking concepts: {e}")
    
    def learn_from_conversation(
        self,
        user_id: str,
        user_message: str,
        assistant_response: str,
        context: Dict = None
    ):
        """Learn from conversation"""
        try:
            # Extract concepts from conversation
            concepts = self._extract_concepts(user_message, assistant_response)
            
            for concept in concepts:
                self.add_knowledge(
                    user_id=user_id,
                    concept=concept,
                    data={
                        "user_message": user_message,
                        "response": assistant_response,
                        "context": context or {}
                    },
                    source="conversation"
                )
        
        except Exception as e:
            logger.error(f"Error learning from conversation: {e}")
    
    def _extract_concepts(self, user_message: str, response: str) -> List[str]:
        """Extract concepts from text"""
        concepts = []
        
        # Simple concept extraction (in production, use NLP)
        words = (user_message + " " + response).lower().split()
        
        # Filter common words and extract concepts
        stop_words = {"the", "a", "an", "and", "or", "is", "are", "was", "were", "in", "on", "at"}
        for word in words:
            if word not in stop_words and len(word) > 3:
                concepts.append(word)
        
        return list(set(concepts))  # Remove duplicates
    
    def adapt_response(
        self,
        user_id: str,
        user_message: str,
        base_response: str
    ) -> str:
        """Adapt response based on learned knowledge"""
        try:
            # Extract concepts from user message
            concepts = self._extract_concepts(user_message, "")
            
            # Get related knowledge
            related = []
            for concept in concepts[:3]:  # Top 3 concepts
                knowledge = self.get_knowledge(user_id, concept)
                if knowledge:
                    related.append(knowledge)
            
            # Enhance response with related knowledge
            if related:
                base_response += "\n\nRelated information:"
                for item in related:
                    if isinstance(item, dict) and "response" in item:
                        base_response += f"\n- {item['response'][:100]}..."
            
            return base_response
        
        except Exception as e:
            logger.error(f"Error adapting response: {e}")
            return base_response
    
    def get_statistics(self, user_id: str) -> Dict:
        """Get knowledge base statistics"""
        try:
            if self.db:
                count = self.db.query(KnowledgeEntry)\
                    .filter(KnowledgeEntry.user_id == user_id)\
                    .count()
                
                total_access = self.db.query(KnowledgeEntry)\
                    .filter(KnowledgeEntry.user_id == user_id)\
                    .with_entities(lambda: KnowledgeEntry.access_count.sum())\
                    .scalar() or 0
                
                return {
                    "total_entries": count,
                    "graph_nodes": self.graph.number_of_nodes(),
                    "graph_edges": self.graph.number_of_edges(),
                    "total_accesses": total_access,
                    "cache_size": len(self.cache)
                }
            
            return {
                "total_entries": 0,
                "graph_nodes": self.graph.number_of_nodes(),
                "graph_edges": self.graph.number_of_edges(),
                "total_accesses": 0,
                "cache_size": len(self.cache)
            }
        
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    def export_knowledge(self, user_id: str, file_path: str):
        """Export knowledge base"""
        try:
            if self.db:
                entries = self.db.query(KnowledgeEntry)\
                    .filter(KnowledgeEntry.user_id == user_id)\
                    .all()
                
                data = {
                    "entries": [
                        {
                            "concept": e.concept,
                            "data": e.data,
                            "weight": e.weight,
                            "source": e.source
                        }
                        for e in entries
                    ],
                    "exported_at": datetime.utcnow().isoformat()
                }
                
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2)
                
                logger.info(f"Knowledge exported to {file_path}")
        
        except Exception as e:
            logger.error(f"Error exporting knowledge: {e}")


# Global knowledge graph instance
knowledge_graph = KnowledgeGraph()
