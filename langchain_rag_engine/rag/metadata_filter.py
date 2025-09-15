"""
Advanced Metadata Filtering System for BharatLawAI
Implements sophisticated filtering for legal documents by domain, jurisdiction, date, and court type
"""

from typing import Dict, List, Any, Optional, Set, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import re

@dataclass
class MetadataFilter:
    """Represents a metadata filter configuration"""
    field: str
    operator: str  # 'eq', 'in', 'range', 'contains', 'regex'
    value: Any
    boost: float = 1.0  # Relevance boost for this filter

@dataclass
class LegalMetadata:
    """Standardized legal document metadata"""
    document_type: str  # 'act', 'judgment', 'section', 'article'
    legal_domain: str   # 'criminal', 'civil', 'constitutional', 'family', etc.
    jurisdiction: str   # 'central', 'delhi', 'maharashtra', etc.
    court_type: Optional[str] = None  # 'supreme', 'high_court', 'district'
    year: Optional[int] = None
    citation: Optional[str] = None
    section_number: Optional[str] = None
    act_name: Optional[str] = None
    judge_name: Optional[str] = None
    case_category: Optional[str] = None
    keywords: List[str] = None

class LegalMetadataFilter:
    """
    Advanced metadata filtering system for legal document retrieval
    Supports complex queries with multiple filters and relevance boosting
    """

    def __init__(self):
        # Legal domain mappings
        self.domain_keywords = {
            'criminal': ['ipc', 'crpc', 'criminal', 'punishment', 'offense', 'crime', 'police', 'arrest', 'bail', 'sentence'],
            'civil': ['civil', 'cpc', 'contract', 'property', 'tort', 'damages', 'suit', 'plaintiff', 'defendant'],
            'constitutional': ['constitution', 'fundamental rights', 'article', 'supreme court', 'high court', 'writ', 'petition'],
            'family': ['marriage', 'divorce', 'adoption', 'guardianship', 'maintenance', 'hindu marriage act', 'family court'],
            'labor': ['employment', 'termination', 'wage', 'industrial dispute', 'trade union', 'labor law', 'workman'],
            'tax': ['income tax', 'gst', 'customs', 'excise', 'assessment', 'taxation', 'revenue'],
            'property': ['land', 'building', 'lease', 'mortgage', 'easement', 'transfer of property act'],
            'corporate': ['company', 'director', 'shareholder', 'incorporation', 'companies act', 'partnership'],
            'environmental': ['environment', 'pollution', 'forest', 'wildlife', 'ecological', 'sustainable'],
            'intellectual_property': ['patent', 'trademark', 'copyright', 'design', 'geographical indication'],
            'cyber': ['cyber crime', 'it act', 'hacking', 'data theft', 'digital signature', 'electronic record'],
            'consumer': ['consumer protection', 'defect', 'complaint', 'unfair trade', 'consumer court'],
            'arbitration': ['arbitration', 'conciliation', 'mediation', 'alternative dispute resolution'],
            'banking': ['banking', 'negotiable instruments', 'cheque', 'promissory note', 'banking regulation'],
            'insurance': ['insurance', 'insurer', 'insured', 'premium', 'claim', 'marine insurance']
        }

        # Jurisdiction mappings
        self.jurisdiction_states = {
            'delhi': ['delhi', 'national capital territory'],
            'maharashtra': ['maharashtra', 'mumbai', 'pune', 'nagpur'],
            'karnataka': ['karnataka', 'bangalore', 'bengaluru', 'mysore'],
            'tamil_nadu': ['tamil nadu', 'chennai', 'madras', 'coimbatore'],
            'gujarat': ['gujarat', 'ahmedabad', 'surat', 'vadodara'],
            'rajasthan': ['rajasthan', 'jaipur', 'jodhpur', 'udaipur'],
            'punjab': ['punjab', 'chandigarh', 'amritsar', 'ludhiana'],
            'haryana': ['haryana', 'gurgaon', 'faridabad', 'panipat'],
            'uttar_pradesh': ['uttar pradesh', 'lucknow', 'kanpur', 'allahabad'],
            'bihar': ['bihar', 'patna', 'gaya', 'bhagalpur'],
            'west_bengal': ['west bengal', 'kolkata', 'calcutta', 'howrah'],
            'odisha': ['odisha', 'bhubaneswar', 'cuttack', 'puri'],
            'andhra_pradesh': ['andhra pradesh', 'hyderabad', 'visakhapatnam', 'vijayawada'],
            'telangana': ['telangana', 'hyderabad', 'warangal', 'karimnagar'],
            'kerala': ['kerala', 'kochi', 'thiruvananthapuram', 'calicut'],
            'madhya_pradesh': ['madhya pradesh', 'bhopal', 'indore', 'jabalpur'],
            'chhattisgarh': ['chhattisgarh', 'raipur', 'bilaspur', 'durg'],
            'jharkhand': ['jharkhand', 'ranchi', 'jamshedpur', 'dhanbad'],
            'assam': ['assam', 'guwahati', 'dibrugarh', 'silchar'],
            'meghalaya': ['meghalaya', 'shillong', 'tura', 'jowai'],
            'tripura': ['tripura', 'agartala', 'udaipur', 'dharmanagar'],
            'mizoram': ['mizoram', 'aizawl', 'lunglei', 'saiha'],
            'manipur': ['manipur', 'imphal', 'bishnupur', 'thoubal'],
            'nagaland': ['nagaland', 'kohima', 'dimapur', 'mokokchung'],
            'arunachal_pradesh': ['arunachal pradesh', 'itanagar', 'naharlagun', 'pasighat'],
            'sikkim': ['sikkim', 'gangtok', 'namchi', 'geyzing'],
            'goa': ['goa', 'panaji', 'margoa', 'ponda'],
            'himachal_pradesh': ['himachal pradesh', 'shimla', 'dharamshala', 'solan'],
            'uttarakhand': ['uttarakhand', 'dehradun', 'haridwar', 'rishikesh'],
            'central': ['central', 'union', 'parliament', 'president', 'supreme court']
        }

        # Court type mappings
        self.court_types = {
            'supreme_court': ['supreme court', 'apex court', 'highest court'],
            'high_court': ['high court', 'hc', 'highcourt'],
            'district_court': ['district court', 'civil court', 'criminal court', 'sessions court'],
            'tribunal': ['tribunal', 'national company law tribunal', 'debt recovery tribunal'],
            'consumer_court': ['consumer court', 'consumer disputes redressal commission'],
            'family_court': ['family court', 'matrimonial court'],
            'labor_court': ['labor court', 'industrial tribunal']
        }

    def create_filters_from_query(self, query: str, intent: Optional[str] = None) -> List[MetadataFilter]:
        """
        Automatically create metadata filters based on query analysis

        Args:
            query: User's legal query
            intent: Classified query intent (optional)

        Returns:
            List of metadata filters to apply
        """
        filters = []
        query_lower = query.lower()

        # 1. Legal Domain Filter
        domain = self._infer_legal_domain(query_lower)
        if domain:
            filters.append(MetadataFilter(
                field='legal_domain',
                operator='eq',
                value=domain,
                boost=2.0
            ))

        # 2. Jurisdiction Filter
        jurisdiction = self._infer_jurisdiction(query_lower)
        if jurisdiction:
            filters.append(MetadataFilter(
                field='jurisdiction',
                operator='eq',
                value=jurisdiction,
                boost=1.5
            ))

        # 3. Court Type Filter
        court_type = self._infer_court_type(query_lower)
        if court_type:
            filters.append(MetadataFilter(
                field='court_type',
                operator='eq',
                value=court_type,
                boost=1.8
            ))

        # 4. Year Range Filter (for recent cases)
        if 'recent' in query_lower or 'latest' in query_lower:
            current_year = datetime.now().year
            filters.append(MetadataFilter(
                field='year',
                operator='range',
                value={'min': current_year - 5, 'max': current_year},
                boost=1.3
            ))

        # 5. Section/Article Filter
        sections = self._extract_sections(query_lower)
        if sections:
            filters.append(MetadataFilter(
                field='section_number',
                operator='in',
                value=sections,
                boost=3.0  # High boost for exact section matches
            ))

        # 6. Act Name Filter
        act_name = self._extract_act_name(query_lower)
        if act_name:
            filters.append(MetadataFilter(
                field='act_name',
                operator='contains',
                value=act_name,
                boost=2.5
            ))

        return filters

    def _infer_legal_domain(self, query: str) -> Optional[str]:
        """Infer the legal domain from query keywords"""
        domain_scores = {}

        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query)
            if score > 0:
                domain_scores[domain] = score

        if domain_scores:
            return max(domain_scores, key=domain_scores.get)

        return None

    def _infer_jurisdiction(self, query: str) -> Optional[str]:
        """Infer jurisdiction from query location mentions"""
        for jurisdiction, keywords in self.jurisdiction_states.items():
            if any(keyword in query for keyword in keywords):
                return jurisdiction

        return None

    def _infer_court_type(self, query: str) -> Optional[str]:
        """Infer court type from query"""
        for court_type, keywords in self.court_types.items():
            if any(keyword in query for keyword in keywords):
                return court_type

        return None

    def _extract_sections(self, query: str) -> List[str]:
        """Extract section numbers from query"""
        # Pattern for section references
        section_patterns = [
            r'section\s+(\d+)',  # Section 302
            r'sec\.?\s*(\d+)',   # Sec 302 or Sec. 302
            r's\.?\s*(\d+)',     # S 302 or S. 302
            r'article\s+(\d+)',  # Article 14
            r'art\.?\s*(\d+)'    # Art 14 or Art. 14
        ]

        sections = []
        for pattern in section_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            sections.extend(matches)

        return list(set(sections))  # Remove duplicates

    def _extract_act_name(self, query: str) -> Optional[str]:
        """Extract act name from query"""
        act_keywords = {
            'indian penal code': ['ipc', 'indian penal code'],
            'criminal procedure code': ['crpc', 'criminal procedure code', 'code of criminal procedure'],
            'civil procedure code': ['cpc', 'civil procedure code', 'code of civil procedure'],
            'indian evidence act': ['indian evidence act', 'evidence act'],
            'indian contract act': ['indian contract act', 'contract act'],
            'hindu marriage act': ['hindu marriage act', 'hma'],
            'motor vehicles act': ['motor vehicles act', 'mva'],
            'consumer protection act': ['consumer protection act', 'copra'],
            'companies act': ['companies act', 'company law'],
            'income tax act': ['income tax act', 'income-tax act'],
            'transfer of property act': ['transfer of property act', 'property act']
        }

        for act_name, keywords in act_keywords.items():
            if any(keyword in query for keyword in keywords):
                return act_name

        return None

    def apply_filters(self, documents: List[Dict[str, Any]], filters: List[MetadataFilter]) -> List[Dict[str, Any]]:
        """
        Apply metadata filters to documents and return filtered results with relevance scores

        Args:
            documents: List of documents with metadata
            filters: List of filters to apply

        Returns:
            Filtered and scored documents
        """
        filtered_docs = []

        for doc in documents:
            score = self._calculate_document_score(doc, filters)

            if score > 0:  # Document passes at least one filter
                doc_copy = doc.copy()
                doc_copy['_relevance_score'] = score
                filtered_docs.append(doc_copy)

        # Sort by relevance score
        filtered_docs.sort(key=lambda x: x.get('_relevance_score', 0), reverse=True)

        return filtered_docs

    def _calculate_document_score(self, document: Dict[str, Any], filters: List[MetadataFilter]) -> float:
        """Calculate relevance score for a document against filters"""
        total_score = 0.0
        match_count = 0

        for filter_obj in filters:
            if self._document_matches_filter(document, filter_obj):
                total_score += filter_obj.boost
                match_count += 1

        # Bonus for multiple filter matches
        if match_count > 1:
            total_score *= (1 + (match_count - 1) * 0.1)

        return total_score

    def _document_matches_filter(self, document: Dict[str, Any], filter_obj: MetadataFilter) -> bool:
        """Check if document matches a specific filter"""
        field_value = self._get_nested_field_value(document, filter_obj.field)

        if field_value is None:
            return False

        if filter_obj.operator == 'eq':
            return str(field_value).lower() == str(filter_obj.value).lower()

        elif filter_obj.operator == 'in':
            if isinstance(filter_obj.value, list):
                return str(field_value).lower() in [str(v).lower() for v in filter_obj.value]
            return str(field_value).lower() == str(filter_obj.value).lower()

        elif filter_obj.operator == 'contains':
            return str(filter_obj.value).lower() in str(field_value).lower()

        elif filter_obj.operator == 'range':
            if isinstance(filter_obj.value, dict):
                min_val = filter_obj.value.get('min')
                max_val = filter_obj.value.get('max')
                if min_val is not None and field_value < min_val:
                    return False
                if max_val is not None and field_value > max_val:
                    return False
                return True
            return False

        elif filter_obj.operator == 'regex':
            try:
                return bool(re.search(str(filter_obj.value), str(field_value), re.IGNORECASE))
            except re.error:
                return False

        return False

    def _get_nested_field_value(self, document: Dict[str, Any], field_path: str) -> Any:
        """Get value from nested document field (supports dot notation)"""
        keys = field_path.split('.')
        current = document

        try:
            for key in keys:
                if isinstance(current, dict):
                    current = current[key]
                elif isinstance(current, list):
                    # For list fields, check if any item matches
                    for item in current:
                        if isinstance(item, dict) and key in item:
                            return item[key]
                    return None
                else:
                    return None
            return current
        except (KeyError, TypeError, IndexError):
            return None

    def get_filter_statistics(self, documents: List[Dict[str, Any]], filters: List[MetadataFilter]) -> Dict[str, Any]:
        """Get statistics about filter application"""
        stats = {
            'total_documents': len(documents),
            'filters_applied': len(filters),
            'documents_matched': 0,
            'average_score': 0.0,
            'filter_performance': {}
        }

        filtered_docs = self.apply_filters(documents, filters)
        stats['documents_matched'] = len(filtered_docs)

        if filtered_docs:
            scores = [doc.get('_relevance_score', 0) for doc in filtered_docs]
            stats['average_score'] = sum(scores) / len(scores)

        # Per-filter statistics
        for filter_obj in filters:
            matching_docs = [
                doc for doc in filtered_docs
                if self._document_matches_filter(doc, filter_obj)
            ]
            stats['filter_performance'][filter_obj.field] = {
                'matches': len(matching_docs),
                'boost': filter_obj.boost
            }

        return stats

# Example usage and testing
if __name__ == "__main__":
    # Initialize filter system
    filter_system = LegalMetadataFilter()

    # Test queries
    test_queries = [
        "What is the punishment for murder under IPC Section 302?",
        "Recent Supreme Court judgments on Article 14",
        "Delhi High Court cases on property disputes",
        "Family law cases in Karnataka for the last 3 years"
    ]

    for query in test_queries:
        print(f"\n🔍 Query: {query}")

        # Create filters
        filters = filter_system.create_filters_from_query(query)
        print(f"   📋 Generated {len(filters)} filters:")

        for f in filters:
            print(f"      • {f.field} {f.operator} {f.value} (boost: {f.boost})")

        # Example document matching
        sample_docs = [
            {
                'legal_domain': 'criminal',
                'jurisdiction': 'central',
                'section_number': '302',
                'year': 2023,
                'court_type': 'supreme_court'
            },
            {
                'legal_domain': 'constitutional',
                'jurisdiction': 'delhi',
                'section_number': '14',
                'year': 2024,
                'court_type': 'high_court'
            }
        ]

        filtered = filter_system.apply_filters(sample_docs, filters)
        print(f"   📊 Filtered to {len(filtered)} relevant documents")

        if filtered:
            print(f"   🏆 Top match score: {filtered[0].get('_relevance_score', 0):.2f}")