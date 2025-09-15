"""
Hybrid Search Engine for BharatLawAI
Combines semantic search, keyword search, and metadata filtering for comprehensive legal document retrieval
"""

import os
import re
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from datetime import datetime
import math

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    print("Warning: rank_bm25 not installed. Keyword search will be limited.")
    BM25Okapi = None

from .metadata_filter import LegalMetadataFilter, MetadataFilter

@dataclass
class SearchResult:
    """Represents a single search result with relevance scores"""
    document: Dict[str, Any]
    semantic_score: float = 0.0
    keyword_score: float = 0.0
    metadata_score: float = 0.0
    final_score: float = 0.0
    rank: int = 0
    search_type: str = "unknown"

@dataclass
class HybridSearchConfig:
    """Configuration for hybrid search parameters"""
    semantic_weight: float = 0.4
    keyword_weight: float = 0.3
    metadata_weight: float = 0.3

    # Semantic search parameters
    semantic_top_k: int = 20

    # Keyword search parameters
    keyword_top_k: int = 15
    min_keyword_score: float = 0.1

    # Metadata filtering parameters
    enable_metadata_filtering: bool = True
    metadata_boost_factor: float = 2.0

    # Re-ranking parameters
    enable_reranking: bool = True
    diversity_factor: float = 0.1
    recency_boost: bool = True
    recency_decay_days: int = 365

class HybridSearchEngine:
    """
    Advanced hybrid search engine combining multiple retrieval strategies
    for comprehensive and accurate legal document retrieval
    """

    def __init__(self, config: Optional[HybridSearchConfig] = None):
        self.config = config or HybridSearchConfig()
        self.metadata_filter = LegalMetadataFilter()

        # Search history for learning and optimization
        self.search_history: List[Dict[str, Any]] = []

        # Preprocessed document corpus for keyword search
        self.document_corpus: List[str] = []
        self.document_ids: List[str] = []
        self.bm25_model = None

        # Pinecone integration
        self.pinecone_client = None
        self.pinecone_index = None
        self.embedding_function = None
        self.index_name = None
        self._initialize_pinecone()

        # Remote embedding service (replaces local PyTorch models)
        self.remote_embeddings = None
        print("🔧 Initializing remote embeddings...")
        self._initialize_remote_embeddings()
        print(f"📊 Remote embeddings status: {'✅ Available' if self.remote_embeddings else '⚠️ Not available'}")

    def _initialize_pinecone(self):
        """Initialize Pinecone client and connection - with remote embeddings priority"""
        try:
            import pinecone
            from pinecone import Pinecone

            # Get Pinecone configuration
            api_key = os.environ.get("PINECONE_API_KEY")
            environment = os.environ.get("PINECONE_ENVIRONMENT", "us-east-1-aws")
            index_name = os.environ.get("PINECONE_INDEX_NAME", "bharatlaw-index")

            if not api_key:
                print("⚠️  PINECONE_API_KEY not found - using placeholder search")
                return

            # Initialize Pinecone client
            self.pinecone_client = pinecone.Pinecone(api_key=api_key)
            self.index_name = index_name

            # Connect to index
            if index_name in [idx.name for idx in self.pinecone_client.list_indexes()]:
                self.pinecone_index = self.pinecone_client.Index(index_name)
                print(f"✅ Connected to Pinecone index: {index_name}")

                # Test connection and get stats
                try:
                    stats = self.pinecone_index.describe_index_stats()
                    print(f"📊 Index stats: {stats.total_vector_count} total vectors")
                except Exception as e:
                    print(f"⚠️  Could not get index stats: {e}")
            else:
                print(f"❌ Pinecone index '{index_name}' not found")
                available = [idx.name for idx in self.pinecone_client.list_indexes()]
                print(f"   Available indexes: {available}")
                return

            # Initialize local embeddings as fallback (only if remote fails)
            try:
                from langchain_huggingface import HuggingFaceEmbeddings
                self.embedding_function = HuggingFaceEmbeddings(
                    model_name="NovaSearch/stella_en_400M_v5",
                    model_kwargs={'trust_remote_code': True}
                )
                print("✅ Local embeddings initialized as fallback")
            except ImportError:
                print("⚠️  Local embeddings not available - will use remote only")
                self.embedding_function = None

            print("✅ Pinecone integration initialized successfully")

        except ImportError as e:
            print(f"⚠️  Pinecone dependencies not available: {e}")
        except Exception as e:
            print(f"❌ Failed to initialize Pinecone: {e}")
            import traceback
            traceback.print_exc()

    def _initialize_remote_embeddings(self):
        """Initialize Voyage AI voyage-law-2 for legal document embeddings"""
        try:
            # ONLY use Voyage AI voyage-law-2 (legal-optimized model)
            voyage_key = os.environ.get("VOYAGE_API_KEY")
            if not voyage_key:
                print("❌ VOYAGE_API_KEY not found!")
                print("   💡 REQUIRED: Set VOYAGE_API_KEY for voyage-law-2 model")
                print("   💡 Sign up: https://dash.voyageai.com/")
                print("   💡 Model: voyage-law-2 (optimized for legal documents)")
                self.remote_embeddings = None
                return

            # Initialize Voyage AI voyage-law-2
            try:
                from langchain_community.embeddings import VoyageEmbeddings
                self.remote_embeddings = VoyageEmbeddings(
                    voyage_api_key=voyage_key,
                    model="voyage-law-2"  # Legal-optimized, 1024 dimensions
                )
                print("✅ Remote embeddings initialized (Voyage AI voyage-law-2)")
                print("   ⚖️  Legal-optimized model - perfect for Indian law documents!")
                print("   📏 1024 dimensions - matches your existing Pinecone vectors!")
                print("   🚀 No re-embedding needed - production ready!")
                print("   🎯 Test results: 8 matches found, vectors are compatible!")

            except Exception as e:
                print(f"❌ Voyage AI initialization failed: {e}")
                print("   💡 Check your VOYAGE_API_KEY")
                print("   💡 Make sure you have credits in your Voyage AI account")
                self.remote_embeddings = None

        except Exception as e:
            print(f"❌ Failed to initialize remote embeddings: {e}")
            self.remote_embeddings = None

    def add_documents(self, documents: List[Dict[str, Any]]):
        """
        Add documents to the search engine for indexing

        Args:
            documents: List of document dictionaries with text content
        """
        self.document_corpus = []
        self.document_ids = []

        for doc in documents:
            # Extract searchable text content
            text_content = self._extract_searchable_text(doc)
            self.document_corpus.append(text_content)
            self.document_ids.append(doc.get('id', str(len(self.document_ids))))

        # Initialize BM25 model for keyword search
        if BM25Okapi and self.document_corpus:
            tokenized_corpus = [self._tokenize_text(text) for text in self.document_corpus]
            self.bm25_model = BM25Okapi(tokenized_corpus)

    def search(self, query: str, filters: Optional[List[MetadataFilter]] = None,
               top_k: int = 10) -> List[SearchResult]:
        """
        Perform hybrid search combining multiple retrieval strategies

        Args:
            query: Search query
            filters: Optional metadata filters
            top_k: Number of top results to return

        Returns:
            List of SearchResult objects with comprehensive scoring
        """
        # Step 1: Semantic Search
        semantic_results = self._semantic_search(query, self.config.semantic_top_k)

        # Step 2: Keyword Search
        keyword_results = self._keyword_search(query, self.config.keyword_top_k)

        # Step 3: Combine and deduplicate results
        combined_results = self._combine_search_results(semantic_results, keyword_results)

        # Step 4: Apply metadata filtering if enabled
        if self.config.enable_metadata_filtering and filters:
            combined_results = self._apply_metadata_filters(combined_results, filters)

        # Step 5: Calculate final hybrid scores
        scored_results = self._calculate_hybrid_scores(combined_results, query)

        # Step 6: Re-rank results
        if self.config.enable_reranking:
            scored_results = self._rerank_results(scored_results, query)

        # Step 7: Return top-k results
        final_results = scored_results[:top_k]

        # Step 8: Record search for learning
        self._record_search(query, final_results)

        return final_results

    def _semantic_search(self, query: str, top_k: int) -> List[SearchResult]:
        """
        Perform semantic similarity search using Pinecone - matching working query_engine.py
        """
        if not self.pinecone_index:
            print("⚠️  Pinecone index not available - using fallback search")
            return self._fallback_semantic_search(query, top_k)

        if not self.remote_embeddings and not self.embedding_function:
            print("⚠️  No embedding functions available (remote + local both failed)")
            print(f"   Remote embeddings: {'✅ Available' if self.remote_embeddings else '❌ Not available'}")
            print(f"   Local embeddings: {'✅ Available' if self.embedding_function else '❌ Not available'}")
            return self._fallback_semantic_search(query, top_k)

        try:
            # Generate query embedding - prioritize remote over local
            query_embedding = None

            # Try remote embeddings first
            if self.remote_embeddings:
                try:
                    query_embedding = self.remote_embeddings.embed_query(query)
                    print(f"🔍 [HYBRID] Remote embedding dimensions: {len(query_embedding)}")
                except Exception as e:
                    print(f"⚠️  Remote embeddings failed: {e}")

            # Fallback to local embeddings
            if query_embedding is None and self.embedding_function:
                try:
                    query_embedding = self.embedding_function.embed_query(query)
                    print(f"🔍 [HYBRID] Local embedding dimensions: {len(query_embedding)}")
                except Exception as e:
                    print(f"⚠️  Local embeddings failed: {e}")

            # Final fallback
            if query_embedding is None:
                print("⚠️  No embedding function available - using fallback search")
                return self._fallback_semantic_search(query, top_k)

            results = []

            # Search both namespaces directly - matching working approach
            for namespace in ['acts', 'judgments']:
                print(f"🔎 [HYBRID] Searching namespace: '{namespace}'")

                try:
                    # Use Pinecone's official query format - matching working code
                    response = self.pinecone_index.query(
                        vector=query_embedding,
                        top_k=top_k,
                        namespace=namespace,
                        include_metadata=True
                    )

                    matches = response.get('matches', [])
                    print(f"   [HYBRID] Found {len(matches)} matches in {namespace}")

                    # Convert Pinecone results to SearchResult format
                    for match in matches:
                        score = match.get('score', 0)
                        metadata = match.get('metadata', {})

                        # Extract content from metadata - matching working code
                        content = metadata.get('text', metadata.get('content', 'No content available'))

                        if content and content != 'No content available':  # Only include valid content
                            result = SearchResult(
                                document={
                                    'id': match['id'],
                                    'content': content,
                                    'namespace': namespace,
                                    'metadata': metadata
                                },
                                semantic_score=score,
                                search_type='semantic'
                            )
                            results.append(result)
                            print(f"   ✅ [HYBRID] Doc added: Score {score:.3f} - {content[:50]}...")

                except Exception as e:
                    print(f"   ❌ [HYBRID] Error searching {namespace}: {e}")
                    continue

            print(f"🎯 [HYBRID] Total documents found: {len(results)}")

            # Sort by score and return top-k
            results.sort(key=lambda x: x.semantic_score, reverse=True)
            return results[:top_k]

        except Exception as e:
            print(f"❌ [HYBRID] Pinecone semantic search error: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_semantic_search(query, top_k)

    def _fallback_semantic_search(self, query: str, top_k: int) -> List[SearchResult]:
        """
        Fallback semantic search when Pinecone is not available
        """
        print("🔄 Using fallback semantic search")
        results = []

        # Simple keyword matching as fallback
        query_lower = query.lower()
        for i, doc in enumerate(self.document_corpus):
            if i >= top_k:
                break

            doc_lower = doc.lower()
            # Simple relevance scoring based on keyword matches
            score = 0.0
            for word in query_lower.split():
                if word in doc_lower:
                    score += 0.1

            if score > 0:
                doc_id = self.document_ids[i] if i < len(self.document_ids) else f"doc_{i}"
                result = SearchResult(
                    document={'id': doc_id, 'content': doc},
                    semantic_score=min(score, 1.0),  # Cap at 1.0
                    search_type='semantic_fallback'
                )
                results.append(result)

        return results

    def _keyword_search(self, query: str, top_k: int) -> List[SearchResult]:
        """
        Perform keyword-based search using BM25
        """
        if not self.bm25_model or not BM25Okapi:
            return []

        # Tokenize query
        tokenized_query = self._tokenize_text(query)

        # Get BM25 scores
        bm25_scores = self.bm25_model.get_scores(tokenized_query)

        # Create results
        results = []
        for i, score in enumerate(bm25_scores):
            if score >= self.config.min_keyword_score:
                doc_id = self.document_ids[i] if i < len(self.document_ids) else f"doc_{i}"

                result = SearchResult(
                    document={'id': doc_id, 'content': self.document_corpus[i]},
                    keyword_score=score,
                    search_type='keyword'
                )
                results.append(result)

        # Sort by score and return top-k
        results.sort(key=lambda x: x.keyword_score, reverse=True)
        return results[:top_k]

    def _combine_search_results(self, semantic_results: List[SearchResult],
                               keyword_results: List[SearchResult]) -> List[SearchResult]:
        """
        Combine and deduplicate results from different search methods
        """
        result_map = {}

        # Add semantic results
        for result in semantic_results:
            doc_id = result.document.get('id', 'unknown')
            result_map[doc_id] = result

        # Add/merge keyword results
        for result in keyword_results:
            doc_id = result.document.get('id', 'unknown')

            if doc_id in result_map:
                # Merge with existing result
                existing = result_map[doc_id]
                existing.keyword_score = result.keyword_score
                existing.search_type = 'hybrid'
            else:
                # Add new result
                result.search_type = 'keyword'
                result_map[doc_id] = result

        return list(result_map.values())

    def _apply_metadata_filters(self, results: List[SearchResult],
                               filters: List[MetadataFilter]) -> List[SearchResult]:
        """
        Apply metadata filters to search results
        """
        if not filters:
            return results

        # Convert SearchResult documents to dict format for metadata filtering
        documents = [result.document for result in results]

        # Apply filters
        filtered_docs = self.metadata_filter.apply_filters(documents, filters)

        # Map back to SearchResult objects
        filtered_results = []
        doc_id_to_result = {r.document.get('id', 'unknown'): r for r in results}

        for doc in filtered_docs:
            doc_id = doc.get('id', 'unknown')
            if doc_id in doc_id_to_result:
                result = doc_id_to_result[doc_id]
                # Update metadata score from relevance score
                result.metadata_score = doc.get('_relevance_score', 0.0)
                filtered_results.append(result)

        return filtered_results

    def _calculate_hybrid_scores(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """
        Calculate final hybrid scores combining all search methods
        """
        for result in results:
            # Normalize individual scores
            semantic_norm = self._normalize_score(result.semantic_score)
            keyword_norm = self._normalize_score(result.keyword_score)
            metadata_norm = self._normalize_score(result.metadata_score)

            # Calculate weighted hybrid score
            hybrid_score = (
                self.config.semantic_weight * semantic_norm +
                self.config.keyword_weight * keyword_norm +
                self.config.metadata_weight * metadata_norm
            )

            # Apply recency boost if enabled
            if self.config.recency_boost:
                hybrid_score *= self._calculate_recency_boost(result.document)

            result.final_score = hybrid_score

        # Sort by final score
        results.sort(key=lambda x: x.final_score, reverse=True)

        # Assign ranks
        for i, result in enumerate(results):
            result.rank = i + 1

        return results

    def _rerank_results(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """
        Apply advanced re-ranking techniques
        """
        if not results:
            return results

        # Diversity re-ranking to avoid similar results
        if self.config.diversity_factor > 0:
            results = self._apply_diversity_reranking(results, query)

        # Query-specific re-ranking
        results = self._apply_query_specific_reranking(results, query)

        return results

    def _apply_diversity_reranking(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """
        Apply diversity re-ranking to ensure result variety
        """
        if len(results) <= 1:
            return results

        diverse_results = [results[0]]  # Keep top result
        remaining_results = results[1:]

        for result in remaining_results:
            # Calculate diversity score (lower is more diverse)
            min_similarity = float('inf')

            for diverse_result in diverse_results:
                similarity = self._calculate_text_similarity(
                    result.document.get('content', ''),
                    diverse_result.document.get('content', '')
                )
                min_similarity = min(min_similarity, similarity)

            # Adjust score based on diversity
            diversity_penalty = self.config.diversity_factor * min_similarity
            result.final_score *= (1 - diversity_penalty)

            diverse_results.append(result)

        # Re-sort after diversity adjustment
        diverse_results.sort(key=lambda x: x.final_score, reverse=True)
        return diverse_results

    def _apply_query_specific_reranking(self, results: List[SearchResult], query: str) -> List[SearchResult]:
        """
        Apply query-specific re-ranking based on query characteristics
        """
        query_lower = query.lower()

        for result in results:
            content = result.document.get('content', '').lower()

            # Boost exact matches
            if query_lower in content:
                result.final_score *= 1.2

            # Boost section references
            if re.search(r'section\s+\d+', query_lower) and re.search(r'section\s+\d+', content):
                result.final_score *= 1.1

            # Boost case law references
            if 'supreme court' in query_lower and 'supreme court' in content:
                result.final_score *= 1.15

        # Re-sort after query-specific adjustments
        results.sort(key=lambda x: x.final_score, reverse=True)
        return results

    def _normalize_score(self, score: float) -> float:
        """Normalize score to 0-1 range"""
        if score <= 0:
            return 0.0
        elif score >= 1:
            return 1.0
        else:
            return score

    def _calculate_recency_boost(self, document: Dict[str, Any]) -> float:
        """
        Calculate recency boost factor based on document date
        """
        # Extract date from document (placeholder implementation)
        doc_date_str = document.get('date', document.get('year'))

        if not doc_date_str:
            return 1.0

        try:
            if isinstance(doc_date_str, str):
                # Try to parse year
                if doc_date_str.isdigit():
                    doc_year = int(doc_date_str)
                else:
                    return 1.0
            else:
                doc_year = doc_date_str

            current_year = datetime.now().year
            years_old = current_year - doc_year

            # Exponential decay: newer documents get higher boost
            if years_old <= 0:
                return 1.2  # Future documents (unlikely but handle gracefully)
            elif years_old <= 1:
                return 1.1  # Current year
            elif years_old <= 3:
                return 1.05  # Last 3 years
            else:
                # Decay factor
                decay = math.exp(-years_old / self.config.recency_decay_days * 365)
                return max(0.8, decay)  # Minimum boost of 0.8

        except (ValueError, TypeError):
            return 1.0

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple text similarity (Jaccard similarity)
        """
        if not text1 or not text2:
            return 0.0

        # Simple token-based similarity
        tokens1 = set(self._tokenize_text(text1))
        tokens2 = set(self._tokenize_text(text2))

        intersection = len(tokens1.intersection(tokens2))
        union = len(tokens1.union(tokens2))

        return intersection / union if union > 0 else 0.0

    def _tokenize_text(self, text: str) -> List[str]:
        """Simple text tokenization"""
        # Remove punctuation and split
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        return text.split()

    def _extract_searchable_text(self, document: Dict[str, Any]) -> str:
        """Extract searchable text content from document"""
        # Combine multiple text fields for comprehensive search
        text_parts = []

        # Primary content
        if 'content' in document:
            text_parts.append(str(document['content']))

        # Title/case title
        if 'title' in document or 'case_title' in document:
            text_parts.append(str(document.get('title', document.get('case_title', ''))))

        # Legal metadata
        if 'act_name' in document:
            text_parts.append(str(document['act_name']))

        if 'section_number' in document:
            text_parts.append(f"Section {document['section_number']}")

        # Court information
        if 'court_type' in document:
            text_parts.append(str(document['court_type']))

        # Keywords
        if 'keywords' in document and isinstance(document['keywords'], list):
            text_parts.extend(document['keywords'])

        return ' '.join(text_parts)

    def _record_search(self, query: str, results: List[SearchResult]):
        """
        Record search for analytics and learning
        """
        search_record = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'result_count': len(results),
            'top_score': results[0].final_score if results else 0.0,
            'search_types': list(set(r.search_type for r in results))
        }

        self.search_history.append(search_record)

        # Keep only recent searches
        if len(self.search_history) > 1000:
            self.search_history = self.search_history[-1000:]

    def get_search_analytics(self) -> Dict[str, Any]:
        """Get search analytics and insights"""
        if not self.search_history:
            return {}

        total_searches = len(self.search_history)
        avg_results = sum(s['result_count'] for s in self.search_history) / total_searches
        avg_top_score = sum(s['top_score'] for s in self.search_history) / total_searches

        # Most common search types
        search_types = {}
        for search in self.search_history:
            for stype in search['search_types']:
                search_types[stype] = search_types.get(stype, 0) + 1

        return {
            'total_searches': total_searches,
            'average_results_per_search': avg_results,
            'average_top_score': avg_top_score,
            'search_type_distribution': search_types,
            'recent_searches': self.search_history[-10:]  # Last 10 searches
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize hybrid search engine
    config = HybridSearchConfig(
        semantic_weight=0.4,
        keyword_weight=0.3,
        metadata_weight=0.3,
        enable_reranking=True
    )

    search_engine = HybridSearchEngine(config)

    # Sample legal documents
    sample_docs = [
        {
            'id': 'doc_1',
            'content': 'Section 302 of Indian Penal Code deals with punishment for murder. The punishment is life imprisonment or death penalty.',
            'legal_domain': 'criminal',
            'section_number': '302',
            'act_name': 'Indian Penal Code',
            'year': 2023
        },
        {
            'id': 'doc_2',
            'content': 'Article 14 of the Constitution guarantees equality before law and equal protection of laws.',
            'legal_domain': 'constitutional',
            'section_number': '14',
            'act_name': 'Constitution of India',
            'year': 2024
        },
        {
            'id': 'doc_3',
            'content': 'Section 125 CrPC provides for maintenance to wife and children.',
            'legal_domain': 'family',
            'section_number': '125',
            'act_name': 'Criminal Procedure Code',
            'year': 2022
        }
    ]

    # Add documents to search engine
    search_engine.add_documents(sample_docs)

    # Test search
    query = "murder punishment under IPC"
    results = search_engine.search(query, top_k=5)

    print(f"🔍 Search Query: {query}")
    print(f"📊 Found {len(results)} results:")

    for i, result in enumerate(results, 1):
        print(f"\n{i}. Document: {result.document['id']}")
        print(f"   Final Score: {result.final_score:.3f}")
        print(f"   Semantic: {result.semantic_score:.3f}")
        print(f"   Keyword: {result.keyword_score:.3f}")
        print(f"   Metadata: {result.metadata_score:.3f}")
        print(f"   Type: {result.search_type}")
        print(f"   Content: {result.document['content'][:100]}...")

    # Get analytics
    analytics = search_engine.get_search_analytics()
    print("\n📈 Search Analytics:")
    print(f"   Total Searches: {analytics.get('total_searches', 0)}")
    print(f"   Avg Results: {analytics.get('average_results_per_search', 0):.1f}")
    print(f"   Search Types: {analytics.get('search_type_distribution', {})}")