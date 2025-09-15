"""
Advanced Conversation Manager for BharatLawAI
Implements context-aware conversation handling with legal topic continuity and follow-up question management
"""

from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import re
import json

@dataclass
class ConversationContext:
    """Represents the current conversation context"""
    conversation_id: str
    user_id: str
    current_topic: str = ""
    legal_domain: str = ""
    jurisdiction: str = ""
    referenced_sections: Set[str] = field(default_factory=set)
    referenced_cases: Set[str] = field(default_factory=set)
    key_concepts: Set[str] = field(default_factory=set)
    conversation_summary: str = ""
    last_activity: datetime = field(default_factory=datetime.now)
    message_count: int = 0
    topic_confidence: float = 0.0

@dataclass
class MessageContext:
    """Context information for a single message"""
    message_id: str
    content: str
    role: str  # 'user' or 'assistant'
    timestamp: datetime
    legal_entities: Dict[str, Any] = field(default_factory=dict)
    intent: str = ""
    sentiment: str = ""
    urgency_level: str = "normal"

class ConversationManager:
    """
    Advanced conversation manager that maintains legal context,
    handles follow-up questions, and provides topic continuity
    """

    def __init__(self, max_context_window: int = 10):
        self.max_context_window = max_context_window
        self.active_conversations: Dict[str, ConversationContext] = {}
        self.message_cache: Dict[str, List[MessageContext]] = {}

        # Legal topic patterns for continuity detection
        self.topic_patterns = {
            'criminal_law': [
                r'murder|homicide|rape|theft|assault|crime|criminal|police|arrest|bail|sentence|punishment',
                r'ipc|indian penal code|section 302|section 376|section 378'
            ],
            'civil_law': [
                r'contract|property|civil suit|tort|damages|plaintiff|defendant',
                r'cpc|civil procedure code|specific relief|limitation act'
            ],
            'constitutional_law': [
                r'constitution|fundamental rights|article|supreme court|high court',
                r'article 14|article 19|article 21|writ|petition'
            ],
            'family_law': [
                r'marriage|divorce|adoption|guardianship|maintenance|child custody',
                r'hindu marriage act|family court|section 13|section 125'
            ],
            'property_law': [
                r'land|building|lease|mortgage|easement|ownership|title',
                r'transfer of property act|registration|stamp duty'
            ],
            'corporate_law': [
                r'company|director|shareholder|incorporation|board meeting',
                r'companies act|partnership|llp|corporate governance'
            ],
            'labor_law': [
                r'employment|termination|wage|industrial dispute|trade union',
                r'labor law|workman|retrenchment|industrial tribunal'
            ]
        }

        # Follow-up question patterns
        self.followup_patterns = [
            r'what about|and what|how about|tell me more|explain further',
            r'what does that mean|can you clarify|what is the difference',
            r'give me an example|show me|can you elaborate',
            r'why is that|how does that work|what happens if',
            r'what are the consequences|what are the penalties|what is the punishment'
        ]

    def process_message(self, conversation_id: str, user_id: str, message: str, role: str = 'user') -> MessageContext:
        """
        Process a new message and update conversation context

        Args:
            conversation_id: Unique conversation identifier
            user_id: User identifier
            message: Message content
            role: 'user' or 'assistant'

        Returns:
            MessageContext: Processed message with context
        """
        # Create or get conversation context
        if conversation_id not in self.active_conversations:
            self.active_conversations[conversation_id] = ConversationContext(
                conversation_id=conversation_id,
                user_id=user_id
            )

        context = self.active_conversations[conversation_id]

        # Analyze message content
        legal_entities = self._extract_legal_entities(message)
        intent = self._classify_message_intent(message, context)
        sentiment = self._analyze_sentiment(message)
        urgency_level = self._assess_urgency(message)

        # Create message context
        message_context = MessageContext(
            message_id=f"{conversation_id}_{context.message_count}",
            content=message,
            role=role,
            timestamp=datetime.now(),
            legal_entities=legal_entities,
            intent=intent,
            sentiment=sentiment,
            urgency_level=urgency_level
        )

        # Update conversation context
        self._update_conversation_context(context, message_context)

        # Cache message
        if conversation_id not in self.message_cache:
            self.message_cache[conversation_id] = []
        self.message_cache[conversation_id].append(message_context)

        # Maintain context window
        if len(self.message_cache[conversation_id]) > self.max_context_window:
            self.message_cache[conversation_id] = self.message_cache[conversation_id][-self.max_context_window:]

        context.message_count += 1
        context.last_activity = datetime.now()

        return message_context

    def get_relevant_context(self, conversation_id: str, current_query: str, max_messages: int = 5) -> Dict[str, Any]:
        """
        Get relevant context from conversation history for the current query

        Args:
            conversation_id: Conversation identifier
            current_query: Current user query
            max_messages: Maximum number of relevant messages to return

        Returns:
            Dictionary containing relevant context information
        """
        if conversation_id not in self.message_cache:
            return self._create_empty_context()

        messages = self.message_cache[conversation_id]
        context = self.active_conversations.get(conversation_id)

        if not context or not messages:
            return self._create_empty_context()

        # Find relevant messages
        relevant_messages = self._find_relevant_messages(messages, current_query, context)

        # Limit to max_messages
        relevant_messages = relevant_messages[-max_messages:] if len(relevant_messages) > max_messages else relevant_messages

        # Build context summary
        context_summary = self._build_context_summary(relevant_messages, context)

        return {
            'conversation_id': conversation_id,
            'current_topic': context.current_topic,
            'legal_domain': context.legal_domain,
            'jurisdiction': context.jurisdiction,
            'referenced_sections': list(context.referenced_sections),
            'referenced_cases': list(context.referenced_cases),
            'key_concepts': list(context.key_concepts),
            'topic_confidence': context.topic_confidence,
            'relevant_messages': [
                {
                    'content': msg.content,
                    'role': msg.role,
                    'timestamp': msg.timestamp.isoformat(),
                    'legal_entities': msg.legal_entities
                } for msg in relevant_messages
            ],
            'context_summary': context_summary,
            'followup_detected': self._is_followup_question(current_query, context)
        }

    def _extract_legal_entities(self, message: str) -> Dict[str, Any]:
        """Extract legal entities from message content"""
        entities = {
            'sections': [],
            'acts': [],
            'cases': [],
            'courts': [],
            'legal_terms': []
        }

        # Extract sections
        section_pattern = r'section\s+(\d+|[IVXLCDM]+)'
        sections = re.findall(section_pattern, message, re.IGNORECASE)
        entities['sections'] = [f"Section {s}" for s in sections]

        # Extract acts
        act_patterns = [
            (r'indian penal code|ipc', 'Indian Penal Code'),
            (r'criminal procedure code|crpc', 'Criminal Procedure Code'),
            (r'civil procedure code|cpc', 'Civil Procedure Code'),
            (r'indian evidence act', 'Indian Evidence Act'),
            (r'hindu marriage act|hma', 'Hindu Marriage Act'),
            (r'motor vehicles act|mva', 'Motor Vehicles Act')
        ]

        for pattern, act_name in act_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                entities['acts'].append(act_name)

        # Extract court mentions
        court_patterns = [
            (r'supreme court', 'Supreme Court'),
            (r'high court', 'High Court'),
            (r'district court', 'District Court'),
            (r'family court', 'Family Court')
        ]

        for pattern, court_name in court_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                entities['courts'].append(court_name)

        # Extract legal terms
        legal_terms = [
            'bail', 'arrest', 'warrant', 'summons', 'charge', 'plea',
            'evidence', 'witness', 'testimony', 'judgment', 'order',
            'appeal', 'revision', 'review', 'stay', 'injunction'
        ]

        for term in legal_terms:
            if term in message.lower():
                entities['legal_terms'].append(term)

        return entities

    def _classify_message_intent(self, message: str, context: ConversationContext) -> str:
        """Classify the intent of the message"""
        message_lower = message.lower()

        # Check for follow-up questions
        if self._is_followup_question(message, context):
            return 'followup_question'

        # Check for clarification requests
        if any(word in message_lower for word in ['explain', 'clarify', 'elaborate', 'detail']):
            return 'clarification_request'

        # Check for specific legal queries
        if any(word in message_lower for word in ['what is', 'how to', 'what are', 'explain']):
            return 'information_request'

        # Check for advice-seeking
        if any(word in message_lower for word in ['should i', 'can i', 'do i need to', 'advice']):
            return 'advice_request'

        # Check for case-specific questions
        if any(word in message_lower for word in ['my case', 'my situation', 'i have']):
            return 'case_specific'

        return 'general_query'

    def _is_followup_question(self, message: str, context: ConversationContext) -> bool:
        """Determine if the message is a follow-up question"""
        if not context or not context.current_topic:
            return False

        message_lower = message.lower()

        # Check followup patterns
        for pattern in self.followup_patterns:
            if re.search(pattern, message_lower):
                return True

        # Check if message references previous topics
        topic_keywords = context.key_concepts
        referenced_count = sum(1 for concept in topic_keywords if concept.lower() in message_lower)

        return referenced_count >= 2  # Multiple topic references indicate followup

    def _analyze_sentiment(self, message: str) -> str:
        """Analyze sentiment of the message"""
        positive_words = ['good', 'great', 'excellent', 'helpful', 'clear', 'understand', 'thanks']
        negative_words = ['confusing', 'unclear', 'wrong', 'bad', 'difficult', 'frustrated', 'worried']
        urgent_words = ['urgent', 'emergency', 'immediately', 'asap', 'quickly', 'serious']

        message_lower = message.lower()

        if any(word in message_lower for word in urgent_words):
            return 'urgent'
        elif any(word in message_lower for word in negative_words):
            return 'negative'
        elif any(word in message_lower for word in positive_words):
            return 'positive'
        else:
            return 'neutral'

    def _assess_urgency(self, message: str) -> str:
        """Assess urgency level of the message"""
        urgent_indicators = [
            'emergency', 'urgent', 'immediately', 'asap', 'quickly',
            'danger', 'threat', 'violence', 'arrest', 'court today',
            'deadline', 'time sensitive', 'critical'
        ]

        message_lower = message.lower()
        urgent_count = sum(1 for indicator in urgent_indicators if indicator in message_lower)

        if urgent_count >= 2:
            return 'high'
        elif urgent_count == 1:
            return 'medium'
        else:
            return 'normal'

    def _update_conversation_context(self, context: ConversationContext, message: MessageContext):
        """Update conversation context based on new message"""
        entities = message.legal_entities

        # Update referenced sections and cases
        context.referenced_sections.update(entities.get('sections', []))
        context.referenced_cases.update(entities.get('cases', []))

        # Update key concepts
        context.key_concepts.update(entities.get('legal_terms', []))

        # Update topic and domain
        detected_topic = self._detect_topic(message.content)
        if detected_topic:
            if context.current_topic:
                # Check if topic changed significantly
                if detected_topic != context.current_topic:
                    context.topic_confidence *= 0.7  # Reduce confidence on topic change
                else:
                    context.topic_confidence = min(1.0, context.topic_confidence + 0.1)
            else:
                context.current_topic = detected_topic
                context.topic_confidence = 0.8

            # Infer legal domain from topic
            context.legal_domain = self._topic_to_domain(detected_topic)

        # Update jurisdiction if mentioned
        jurisdiction = self._extract_jurisdiction(message.content)
        if jurisdiction:
            context.jurisdiction = jurisdiction

    def _detect_topic(self, message: str) -> Optional[str]:
        """Detect the main legal topic from message"""
        message_lower = message.lower()
        topic_scores = {}

        for topic, patterns in self.topic_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, message_lower)
                score += len(matches)
            if score > 0:
                topic_scores[topic] = score

        if topic_scores:
            return max(topic_scores, key=topic_scores.get)

        return None

    def _topic_to_domain(self, topic: str) -> str:
        """Convert topic to legal domain"""
        topic_domain_map = {
            'criminal_law': 'criminal',
            'civil_law': 'civil',
            'constitutional_law': 'constitutional',
            'family_law': 'family',
            'property_law': 'property',
            'corporate_law': 'corporate',
            'labor_law': 'labor'
        }
        return topic_domain_map.get(topic, 'general')

    def _extract_jurisdiction(self, message: str) -> Optional[str]:
        """Extract jurisdiction from message"""
        states = [
            'delhi', 'maharashtra', 'karnataka', 'tamil nadu', 'gujarat',
            'rajasthan', 'punjab', 'haryana', 'uttar pradesh', 'bihar',
            'west bengal', 'odisha', 'andhra pradesh', 'telangana', 'kerala'
        ]

        message_lower = message.lower()
        for state in states:
            if state in message_lower:
                return state

        return None

    def _find_relevant_messages(self, messages: List[MessageContext], current_query: str, context: ConversationContext) -> List[MessageContext]:
        """Find messages relevant to the current query"""
        relevant_messages = []
        current_keywords = set(current_query.lower().split())

        for message in messages:
            relevance_score = 0

            # Keyword overlap
            message_keywords = set(message.content.lower().split())
            overlap = len(current_keywords.intersection(message_keywords))
            relevance_score += overlap * 2

            # Topic continuity
            if context.current_topic and context.current_topic in message.content.lower():
                relevance_score += 3

            # Legal entity overlap
            current_entities = self._extract_legal_entities(current_query)
            message_entities = message.legal_entities

            for entity_type in ['sections', 'acts', 'courts']:
                current_set = set(current_entities.get(entity_type, []))
                message_set = set(message_entities.get(entity_type, []))
                overlap = len(current_set.intersection(message_set))
                relevance_score += overlap * 4

            # Recency boost (more recent messages are more relevant)
            hours_old = (datetime.now() - message.timestamp).total_seconds() / 3600
            recency_boost = max(0, 2 - (hours_old / 24))  # Boost decays over 24 hours
            relevance_score += recency_boost

            if relevance_score > 3:  # Threshold for relevance
                message.relevance_score = relevance_score  # Add score to message
                relevant_messages.append(message)

        # Sort by relevance score
        relevant_messages.sort(key=lambda x: getattr(x, 'relevance_score', 0), reverse=True)

        return relevant_messages

    def _build_context_summary(self, relevant_messages: List[MessageContext], context: ConversationContext) -> str:
        """Build a summary of the conversation context"""
        if not relevant_messages:
            return ""

        summary_parts = []

        if context.current_topic:
            summary_parts.append(f"Current topic: {context.current_topic}")

        if context.legal_domain:
            summary_parts.append(f"Legal domain: {context.legal_domain}")

        if context.referenced_sections:
            sections = list(context.referenced_sections)[:3]  # Limit to 3
            summary_parts.append(f"Referenced sections: {', '.join(sections)}")

        if context.key_concepts:
            concepts = list(context.key_concepts)[:3]  # Limit to 3
            summary_parts.append(f"Key concepts: {', '.join(concepts)}")

        # Add recent message summary
        recent_messages = relevant_messages[-2:]  # Last 2 messages
        if recent_messages:
            summary_parts.append("Recent discussion:")
            for msg in recent_messages:
                role = "User" if msg.role == "user" else "Assistant"
                summary_parts.append(f"  {role}: {msg.content[:100]}...")

        return " | ".join(summary_parts)

    def _create_empty_context(self) -> Dict[str, Any]:
        """Create empty context for new conversations"""
        return {
            'conversation_id': None,
            'current_topic': '',
            'legal_domain': '',
            'jurisdiction': '',
            'referenced_sections': [],
            'referenced_cases': [],
            'key_concepts': [],
            'topic_confidence': 0.0,
            'relevant_messages': [],
            'context_summary': '',
            'followup_detected': False
        }

    def get_conversation_stats(self, conversation_id: str) -> Dict[str, Any]:
        """Get statistics about a conversation"""
        if conversation_id not in self.active_conversations:
            return {}

        context = self.active_conversations[conversation_id]
        messages = self.message_cache.get(conversation_id, [])

        return {
            'conversation_id': conversation_id,
            'message_count': len(messages),
            'current_topic': context.current_topic,
            'legal_domain': context.legal_domain,
            'topic_confidence': context.topic_confidence,
            'referenced_sections_count': len(context.referenced_sections),
            'referenced_cases_count': len(context.referenced_cases),
            'key_concepts_count': len(context.key_concepts),
            'last_activity': context.last_activity.isoformat(),
            'duration_hours': (datetime.now() - context.last_activity).total_seconds() / 3600
        }

    def cleanup_old_conversations(self, max_age_hours: int = 24):
        """Clean up old inactive conversations"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        conversations_to_remove = []

        for conv_id, context in self.active_conversations.items():
            if context.last_activity < cutoff_time:
                conversations_to_remove.append(conv_id)

        for conv_id in conversations_to_remove:
            self.active_conversations.pop(conv_id, None)
            self.message_cache.pop(conv_id, None)

        return len(conversations_to_remove)

# Example usage and testing
if __name__ == "__main__":
    # Initialize conversation manager
    manager = ConversationManager()

    # Simulate a conversation
    conv_id = "test_conv_001"
    user_id = "user_123"

    # First message
    msg1 = manager.process_message(conv_id, user_id, "What is the punishment for murder under IPC?", 'user')
    print(f"📝 Message 1 processed - Topic: {manager.active_conversations[conv_id].current_topic}")

    # Second message
    msg2 = manager.process_message(conv_id, user_id, "Tell me more about Section 302", 'user')
    print(f"📝 Message 2 processed - Followup detected: {manager.get_relevant_context(conv_id, msg2.content)['followup_detected']}")

    # Get context for current query
    context = manager.get_relevant_context(conv_id, "What are the exceptions to Section 302?")
    print(f"🔍 Context retrieved - Topic: {context['current_topic']}")
    print(f"📊 Referenced sections: {context['referenced_sections']}")
    print(f"💬 Relevant messages: {len(context['relevant_messages'])}")

    # Get conversation stats
    stats = manager.get_conversation_stats(conv_id)
    print(f"📈 Conversation stats: {stats['message_count']} messages, confidence: {stats['topic_confidence']:.2f}")