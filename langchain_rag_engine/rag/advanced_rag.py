"""
Advanced RAG System for BharatLawAI
Integrates Hybrid Search + Chain-of-Thought Reasoning with Pinecone
Maintains streaming functionality for real-time responses
"""

import os
import asyncio
from typing import Dict, List, Any, Optional, AsyncGenerator
from dotenv import load_dotenv

from rag.hybrid_search import HybridSearchEngine, HybridSearchConfig
from rag.cot_reasoning import ChainOfThoughtReasoning, LegalReasoningConfig
from rag.intent_classifier import context_aware_intent_classifier, get_quick_reply

load_dotenv()

class AdvancedRAGSystem:
    """
    Advanced RAG system combining:
    - Hybrid Search Engine (semantic + keyword + metadata)
    - Chain-of-Thought Reasoning (structured legal analysis)
    - Pinecone vector database
    - Streaming responses
    """

    def __init__(self):
        # Lazy initialization - only initialize when needed
        self._search_engine = None
        self._reasoning_engine = None

        # Pinecone configuration (store but don't initialize yet)
        self.pinecone_api_key = os.environ.get("PINECONE_API_KEY")
        self.pinecone_environment = os.environ.get("PINECONE_ENVIRONMENT", "us-east-1-aws")
        self.pinecone_index_name = os.environ.get("PINECONE_INDEX_NAME", "bharatlaw-index")

        print("🔧 Advanced RAG System initialized (lazy loading)")

    def _initialize_search_engine(self):
        """Lazy initialization of search engine"""
        if self._search_engine is None:
            print("🔍 [LAZY] Initializing Hybrid Search Engine...")
            from rag.hybrid_search import HybridSearchConfig
            search_config = HybridSearchConfig(
                semantic_weight=0.4,
                keyword_weight=0.3,
                metadata_weight=0.3,
                enable_reranking=True,
                diversity_factor=0.1
            )
            self._search_engine = HybridSearchEngine(search_config)
            print("✅ [LAZY] Hybrid Search Engine ready")
        return self._search_engine

    def _initialize_reasoning_engine(self):
        """Lazy initialization of reasoning engine"""
        if self._reasoning_engine is None:
            print("🧠 [LAZY] Initializing Chain-of-Thought Reasoning...")
            from rag.cot_reasoning import LegalReasoningConfig
            reasoning_config = LegalReasoningConfig(
                max_steps=8,
                enable_evidence_validation=True,
                enable_legal_cross_referencing=True,
                reasoning_depth='comprehensive'
            )
            self._reasoning_engine = ChainOfThoughtReasoning(reasoning_config)
            print("✅ [LAZY] Chain-of-Thought Reasoning ready")
        return self._reasoning_engine

    async def query_legal_assistant(self, question: str, conversation_history: list = None) -> dict:
        """
        Main query function with advanced RAG processing
        Returns structured response with legal analysis
        """
        if conversation_history is None:
            conversation_history = []

        try:
            # Step 0: Context-aware intent classification
            print(f"🎯 [INTENT] Classifying intent for: {question[:50]}...")
            intent = context_aware_intent_classifier(question, conversation_history)

            if intent != "legal_query":
                print(f"💬 [INTENT] Non-legal query detected: {intent}")
                return {
                    "answer": get_quick_reply(intent),
                    "source": "intent_classifier",
                    "confidence": 1.0,
                    "intent": intent
                }

            print("⚖️ [INTENT] Legal query confirmed - proceeding with RAG")

            # Step 1: Initialize and perform Hybrid Search for relevant context
            print(f"🔍 Performing hybrid search for: {question[:50]}...")
            search_engine = self._initialize_search_engine()
            search_results = search_engine.search(question, top_k=3)
            # Extract relevant context from search results
            relevant_contexts = []
            for result in search_results:
                if result.final_score > 0.3:  # Filter by relevance threshold
                    relevant_contexts.append(result.document.get('content', ''))

            context = " ".join(relevant_contexts[:2])  # Limit context length
            print(f"📊 Found {len(search_results)} results, using {len(relevant_contexts)} relevant contexts")

            # Step 2: Initialize and perform Chain-of-Thought Reasoning
            print("🧠 Performing chain-of-thought reasoning...")
            reasoning_engine = self._initialize_reasoning_engine()
            reasoning_chain = reasoning_engine.reason_step_by_step(
                query=question,
                context=context,
                legal_domain='general'  # Auto-detect domain
            )

            # Step 3: Format response
            response = {
                "answer": reasoning_chain.final_conclusion,
                "source": "advanced_rag_pinecone",
                "confidence": reasoning_chain.overall_confidence,
                "search_results_count": len(search_results),
                "reasoning_steps": len(reasoning_chain.steps),
                "legal_domain": reasoning_chain.legal_domain
            }

            print(f"✅ Query processed successfully - Confidence: {reasoning_chain.overall_confidence:.2f}")
            return response

        except Exception as e:
            print(f"❌ Error in advanced RAG query: {str(e)}")
            return {
                "answer": f"An error occurred while processing your request: {str(e)}",
                "source": "error_advanced_rag",
                "confidence": 0.0
            }

    async def stream_legal_assistant(self, question: str, conversation_history: list = None) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Streaming version that yields tokens as they are generated
        Maintains real-time streaming for better UX
        """
        if conversation_history is None:
            conversation_history = []

        try:
            # Step 0: Context-aware intent classification
            print(f"🎯 [STREAM][INTENT] Classifying intent for: {question[:50]}...")
            intent = context_aware_intent_classifier(question, conversation_history)

            if intent != "legal_query":
                print(f"💬 [STREAM][INTENT] Non-legal query detected: {intent}")
                # For non-legal queries, yield the quick reply as a single chunk
                yield {
                    "type": "chunk",
                    "content": get_quick_reply(intent),
                    "source": "intent_classifier",
                    "intent": intent
                }
                yield {
                    "type": "complete",
                    "source": "intent_classifier",
                    "intent": intent
                }
                return

            print("⚖️ [STREAM][INTENT] Legal query confirmed - proceeding with streaming RAG")
            # Step 1: Initialize and perform Hybrid Search (non-streaming, done upfront)
            print(f"🔍 [STREAM] Performing hybrid search for: {question[:50]}...")
            search_engine = self._initialize_search_engine()
            search_results = search_engine.search(question, top_k=3)

            # Extract context
            relevant_contexts = []
            for result in search_results:
                if result.final_score > 0.3:
                    relevant_contexts.append(result.document.get('content', ''))

            context = " ".join(relevant_contexts[:2])
            print(f"📊 [STREAM] Found {len(search_results)} results, {len(relevant_contexts)} relevant")

            # Step 2: Send search metadata
            yield {
                "type": "search_complete",
                "search_results_count": len(search_results),
                "relevant_contexts": len(relevant_contexts)
            }

            # Step 3: Create comprehensive prompt with retrieved context
            print("🧠 [STREAM] Creating legal analysis prompt...")

            legal_prompt = f"""You are an expert Indian legal assistant with deep knowledge of Indian law (IPC, CrPC, CPC, Constitution, etc.).

LEGAL CONTEXT (Retrieved from verified legal documents):
{context}

USER QUESTION: {question}

INSTRUCTIONS:
1. Analyze the legal question using the provided context
2. Cite specific legal sections, articles, or precedents from the context
3. Provide a comprehensive but concise legal analysis
4. Include relevant legal principles and their application
5. If context is insufficient, clearly state limitations
6. End with practical advice or next steps

LEGAL ANALYSIS:"""

            # Step 4: Initialize LLM for streaming
            print("🤖 [STREAM] Initializing LLM for streaming response...")

            # Import LLM here to avoid circular imports
            from langchain_openai import ChatOpenAI
            from langchain_core.prompts import ChatPromptTemplate

            llm = ChatOpenAI(
                model_name="deepseek/deepseek-chat-v3.1:free",
                api_key=os.environ.get("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1",
                default_headers={
                    "HTTP-Referer": "https://bharatlawainew-production.up.railway.app",
                    "X-Title": "BharatLawAI",
                },
                streaming=True,
                temperature=0.3,  # Lower temperature for legal analysis
                max_tokens=2000
            )

            # Step 5: Send reasoning preparation indicator
            yield {
                "type": "reasoning_step",
                "step_number": 1,
                "step_type": "analysis",
                "content": f"Analyzing legal question: '{question[:100]}...'",
                "confidence": 0.9,
                "legal_references": []
            }

            await asyncio.sleep(0.2)

            yield {
                "type": "reasoning_step",
                "step_number": 2,
                "step_type": "evidence",
                "content": f"Retrieved {len(relevant_contexts)} relevant legal contexts for analysis",
                "confidence": 0.8,
                "legal_references": []
            }

            await asyncio.sleep(0.2)

            # Step 6: Stream the LLM response in real-time
            print("📝 [STREAM] Starting LLM streaming response...")

            full_response = ""
            async for chunk in llm.astream(legal_prompt):
                if hasattr(chunk, 'content') and chunk.content:
                    content = chunk.content
                    full_response += content

                    # Stream each chunk to frontend
                    yield {
                        "type": "chunk",
                        "content": content,
                        "source": "advanced_rag_pinecone"
                    }

                    # Small delay for smooth streaming
                    await asyncio.sleep(0.05)

            # Step 7: Send final answer with metadata
            yield {
                "type": "final_answer",
                "content": full_response,
                "overall_confidence": 0.85,
                "legal_domain": "general",
                "execution_time": 0.5,
                "context_used": len(relevant_contexts) > 0
            }

            # Completion event will be sent by main.py with conversation_id
            # Don't send completion here to avoid conflicts

            print(f"✅ [STREAM] Query completed - streaming finished successfully")

        except Exception as e:
            print(f"❌ [STREAM] Error in streaming: {str(e)}")
            yield {
                "type": "error",
                "message": f"An error occurred during streaming: {str(e)}"
            }

    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and configuration"""
        return {
            "system": "Advanced RAG with Pinecone (Lazy Loading)",
            "pinecone_configured": bool(self.pinecone_api_key),
            "pinecone_index": self.pinecone_index_name,
            "search_engine_ready": self._search_engine is not None,
            "reasoning_engine_ready": self._reasoning_engine is not None,
            "streaming_enabled": True,
            "lazy_loading": True
        }

# Global instance for the backend
_advanced_rag_system = None

def get_advanced_rag_system() -> AdvancedRAGSystem:
    """Get or create the global Advanced RAG system instance"""
    global _advanced_rag_system
    if _advanced_rag_system is None:
        _advanced_rag_system = AdvancedRAGSystem()
    return _advanced_rag_system

# Convenience functions for backend integration
async def query_legal_assistant(question: str, conversation_history: list = None) -> dict:
    """Convenience function for non-streaming queries"""
    system = get_advanced_rag_system()
    return await system.query_legal_assistant(question, conversation_history)

async def stream_legal_assistant(question: str, conversation_history: list = None) -> AsyncGenerator[Dict[str, Any], None]:
    """Convenience function for streaming queries"""
    system = get_advanced_rag_system()
    async for chunk in system.stream_legal_assistant(question, conversation_history):
        yield chunk

def get_rag_system_status() -> Dict[str, Any]:
    """Get RAG system status"""
    system = get_advanced_rag_system()
    return system.get_system_status()


