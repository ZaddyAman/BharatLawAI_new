INTENTS = {
    "greeting": ["hi", "hello", "hey", "good morning", "good evening"],
    "goodbye": ["bye", "goodbye", "see you", "take care"],
    "thanks": ["thanks", "thank you", "much appreciated"],
    "chitchat": ["what's up", "how are you", "lol", "cool", "great", "nice"],
    "feedback": ["you’re helpful", "good answer", "awesome", "love it"],
    "legal_query": ["section", "act", "law", "ipc", "procedure", "legal"]
}

def classify_intent(text: str) -> str:
    """
    Classifies the user's message as a predefined intent
    using keyword matching (fallback to 'legal_query').
    """
    text_lower = text.lower()

    # Prioritize legal queries
    for keyword in INTENTS["legal_query"]:
        if keyword in text_lower:
            return "legal_query"

    for intent, keywords in INTENTS.items():
        if intent == "legal_query":
            continue
        for keyword in keywords:
            if keyword in text_lower:
                return intent
    return "legal_query"

def get_quick_reply(intent: str) -> str:
    """
    Returns a quick, appropriate response based on the classified intent.
    """
    responses = {
        "greeting": "Hello! I'm BharatLawAI, your Indian legal assistant. How can I help you with legal matters today?",
        "goodbye": "Goodbye! Remember, justice delayed is justice denied. Stay on the right side of the law!",
        "thanks": "You're welcome! If you have more legal questions, I'm here to help.",
        "chitchat": "I'm doing well, thanks for asking! Ready to dive into some Indian legal matters?",
        "feedback": "Thank you for the feedback! I'm here to make Indian law more accessible to everyone."
    }

    return responses.get(intent, "I'm here to help with Indian legal questions. What would you like to know?")

def detect_follow_up_patterns(question: str, history: list) -> float:
    """
    Return confidence score (0-1) that this is a follow-up question
    """
    score = 0.0

    # Pattern 1: Pronouns referencing previous content
    pronouns = ["this", "that", "these", "those", "it", "they"]
    if any(pronoun in question.lower() for pronoun in pronouns):
        score += 0.3

    # Pattern 2: Follow-up question starters
    starters = ["can you", "could you", "please", "explain", "what about", "how about"]
    if any(starter in question.lower() for starter in starters):
        score += 0.4

    # Pattern 3: Question words in middle of sentence
    question_words = ["what", "how", "why", "when", "where"]
    words = question.lower().split()
    for i, word in enumerate(words):
        if word in question_words and i > 0:  # Not at start
            score += 0.2
            break

    # Pattern 4: Recent legal conversation
    if history and any(msg.get('source') in ['vector_db', 'vector_db_langchain']
                      for msg in history[-2:]):
        score += 0.3

    return min(score, 1.0)  # Cap at 1.0

def context_aware_intent_classifier(question: str, conversation_history: list = None) -> str:
    """
    Context-aware intent classification that considers conversation history
    """
    if conversation_history is None:
        conversation_history = []

    # Step 1: Check for legal keywords first (highest priority)
    legal_keywords = ["section", "act", "law", "ipc", "procedure", "legal", "court", "case", "article"]
    if any(word in question.lower() for word in legal_keywords):
        return "legal_query"

    # Step 2: Check follow-up probability
    follow_up_score = detect_follow_up_patterns(question, conversation_history)
    if follow_up_score > 0.5:
        return "legal_query"

    # Step 3: Check recent conversation context
    if conversation_history:
        recent_assistant_messages = [msg for msg in conversation_history[-3:] if msg.get('role') == 'assistant']
        if any(msg.get('source') in ['vector_db', 'vector_db_langchain'] for msg in recent_assistant_messages):
            # Recent legal conversation, bias towards legal intent
            intent = classify_intent(question)
            if intent == "chitchat" and follow_up_score > 0.2:
                return "legal_query"

    # Step 4: Default intent classification
    return classify_intent(question)
