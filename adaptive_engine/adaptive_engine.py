"""
Adaptive Engine - AI learning and adaptation
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from knowledge.knowledge_base import knowledge_graph
from utils.logger import get_logger
import random

logger = get_logger("adaptive_engine")


class AdaptiveEngine:
    """Learn and adapt from interactions and data"""
    
    def __init__(self):
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        self.interaction_history: Dict[str, List[Dict]] = {}
        self.performance_metrics: Dict[str, float] = {}
        self.communication_style: Dict[str, str] = {}
    
    def build_user_profile(self, user_id: str, user_data: Dict) -> Dict:
        """Build user profile from interactions"""
        try:
            profile = {
                "user_id": user_id,
                "preferences": user_data.get("preferences", {}),
                "interaction_count": 0,
                "average_sentiment": 0.0,
                "most_common_topics": [],
                "communication_style": "formal",
                "response_time_preference": "normal",
                "last_updated": datetime.utcnow().isoformat()
            }
            
            self.user_profiles[user_id] = profile
            logger.info(f"User profile built for {user_id}")
            return profile
        
        except Exception as e:
            logger.error(f"Error building user profile: {e}")
            return {}
    
    def learn_from_interaction(
        self,
        user_id: str,
        user_message: str,
        assistant_response: str,
        feedback: Optional[float] = None
    ):
        """Learn from user interaction"""
        try:
            if user_id not in self.interaction_history:
                self.interaction_history[user_id] = []
            
            interaction = {
                "timestamp": datetime.utcnow().isoformat(),
                "user_message": user_message,
                "assistant_response": assistant_response,
                "feedback": feedback or 0.5,  # 0.0 to 1.0
                "message_length": len(user_message),
                "response_length": len(assistant_response)
            }
            
            self.interaction_history[user_id].append(interaction)
            
            # Update profile
            if user_id in self.user_profiles:
                self.user_profiles[user_id]["interaction_count"] += 1
                self.user_profiles[user_id]["average_sentiment"] = self._calculate_avg_sentiment(user_id)
            
            # Update knowledge graph
            knowledge_graph.learn_from_conversation(
                user_id=user_id,
                user_message=user_message,
                assistant_response=assistant_response
            )
            
            logger.info(f"Learned from interaction with {user_id}")
        
        except Exception as e:
            logger.error(f"Error learning from interaction: {e}")
    
    def adapt_communication_style(
        self,
        user_id: str,
        response_text: str
    ) -> str:
        """Adapt communication based on user profile"""
        try:
            if user_id not in self.user_profiles:
                return response_text
            
            profile = self.user_profiles[user_id]
            style = profile.get("communication_style", "formal")
            
            # Adapt based on style
            if style == "casual":
                response_text = response_text.replace("However,", "But").replace("Furthermore,", "Also,")
            elif style == "technical":
                response_text += "\n[Technical mode enabled]"
            elif style == "brief":
                sentences = response_text.split(".")[:2]  # Shorten to first 2 sentences
                response_text = ".".join(sentences) + "."
            
            return response_text
        
        except Exception as e:
            logger.error(f"Error adapting communication: {e}")
            return response_text
    
    def predict_user_needs(
        self,
        user_id: str
    ) -> List[str]:
        """Predict what user might need"""
        try:
            if user_id not in self.interaction_history:
                return []
            
            interactions = self.interaction_history[user_id]
            topics = {}
            
            # Extract common topics
            for interaction in interactions[-10:]:  # Last 10 interactions
                words = interaction["user_message"].lower().split()
                for word in words:
                    if len(word) > 4:
                        topics[word] = topics.get(word, 0) + 1
            
            # Get top topics
            top_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)[:5]
            return [topic[0] for topic in top_topics]
        
        except Exception as e:
            logger.error(f"Error predicting user needs: {e}")
            return []
    
    def calculate_response_quality(
        self,
        user_id: str,
        feedback: float
    ) -> float:
        """Calculate response quality score"""
        try:
            if user_id not in self.interaction_history:
                return feedback
            
            interactions = self.interaction_history[user_id]
            feedbacks = [i["feedback"] for i in interactions[-10:]]
            
            if not feedbacks:
                return feedback
            
            average = sum(feedbacks) / len(feedbacks)
            return (average + feedback) / 2  # Weight recent feedback
        
        except Exception as e:
            logger.error(f"Error calculating quality: {e}")
            return 0.5
    
    def recommend_features(
        self,
        user_id: str
    ) -> List[str]:
        """Recommend features based on usage"""
        try:
            needs = self.predict_user_needs(user_id)
            
            recommendations = []
            if "income" in needs or "money" in needs:
                recommendations.append("income_generation")
            if "crypto" in needs or "bitcoin" in needs:
                recommendations.append("crypto_tracking")
            if "portfolio" in needs or "investment" in needs:
                recommendations.append("portfolio_management")
            if "market" in needs or "news" in needs:
                recommendations.append("market_alerts")
            
            return recommendations
        
        except Exception as e:
            logger.error(f"Error recommending features: {e}")
            return []
    
    def _calculate_avg_sentiment(
        self,
        user_id: str
    ) -> float:
        """Calculate average sentiment from interactions"""
        try:
            interactions = self.interaction_history.get(user_id, [])
            if not interactions:
                return 0.5
            
            feedbacks = [i["feedback"] for i in interactions]
            return sum(feedbacks) / len(feedbacks)
        
        except Exception as e:
            logger.error(f"Error calculating sentiment: {e}")
            return 0.5
    
    def get_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile"""
        return self.user_profiles.get(user_id)
    
    def get_statistics(self, user_id: str) -> Dict:
        """Get adaptive engine statistics"""
        try:
            interactions = self.interaction_history.get(user_id, [])
            profile = self.user_profiles.get(user_id, {})
            
            return {
                "total_interactions": len(interactions),
                "average_message_length": sum(i["message_length"] for i in interactions) / len(interactions) if interactions else 0,
                "average_response_length": sum(i["response_length"] for i in interactions) / len(interactions) if interactions else 0,
                "average_sentiment": profile.get("average_sentiment", 0),
                "communication_style": profile.get("communication_style", "formal"),
                "predicted_needs": self.predict_user_needs(user_id),
                "recommended_features": self.recommend_features(user_id)
            }
        
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}


# Global adaptive engine instance
adaptive_engine = AdaptiveEngine()
