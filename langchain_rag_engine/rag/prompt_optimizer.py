"""
Advanced Prompt Parameter Optimizer for BharatLawAI
Dynamically adjusts LLM parameters based on query characteristics for optimal legal reasoning
"""

from typing import Dict, Any, Tuple
from dataclasses import dataclass
from enum import Enum

class QueryComplexity(Enum):
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"

class LegalDomain(Enum):
    CRIMINAL = "criminal"
    CIVIL = "civil"
    CONSTITUTIONAL = "constitutional"
    ADMINISTRATIVE = "administrative"
    COMMERCIAL = "commercial"
    FAMILY = "family"
    LABOR = "labor"
    TAX = "tax"
    PROPERTY = "property"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    ENVIRONMENTAL = "environmental"
    INTERNATIONAL = "international"
    GENERAL = "general"

@dataclass
class OptimizedParameters:
    """Container for optimized LLM parameters"""
    temperature: float
    top_p: float
    max_tokens: int
    presence_penalty: float
    frequency_penalty: float
    reasoning_effort: str  # For models that support it

class PromptParameterOptimizer:
    """
    Dynamically optimizes LLM parameters based on legal query characteristics
    for optimal reasoning and response quality.
    """

    def __init__(self):
        # Base parameter configurations for different scenarios
        self.base_configs = {
            'precision_focused': {
                'temperature': 0.05,
                'top_p': 0.85,
                'max_tokens': 1500,
                'presence_penalty': 0.1,
                'frequency_penalty': 0.05,
                'reasoning_effort': 'medium'
            },
            'balanced_reasoning': {
                'temperature': 0.15,
                'top_p': 0.9,
                'max_tokens': 2000,
                'presence_penalty': 0.15,
                'frequency_penalty': 0.1,
                'reasoning_effort': 'high'
            },
            'creative_analysis': {
                'temperature': 0.25,
                'top_p': 0.95,
                'max_tokens': 2500,
                'presence_penalty': 0.2,
                'frequency_penalty': 0.15,
                'reasoning_effort': 'high'
            },
            'conservative_legal': {
                'temperature': 0.03,
                'top_p': 0.8,
                'max_tokens': 1200,
                'presence_penalty': 0.05,
                'frequency_penalty': 0.03,
                'reasoning_effort': 'low'
            }
        }

        # Domain-specific parameter adjustments
        self.domain_adjustments = {
            LegalDomain.CRIMINAL: {
                'temperature': -0.05,  # More precise
                'max_tokens': 200,     # Detailed sentencing analysis
                'presence_penalty': 0.1  # Encourage comprehensive coverage
            },
            LegalDomain.CONSTITUTIONAL: {
                'temperature': -0.08,  # Very precise
                'max_tokens': 300,     # Detailed constitutional analysis
                'presence_penalty': 0.15  # Comprehensive coverage of rights
            },
            LegalDomain.CIVIL: {
                'temperature': 0.05,   # Balanced
                'max_tokens': 150,     # Contract/property analysis
                'frequency_penalty': 0.1  # Avoid repetitive legal jargon
            },
            LegalDomain.FAMILY: {
                'temperature': 0.02,   # Conservative
                'max_tokens': 100,     # Focused on specific provisions
                'presence_penalty': 0.05  # Clear, direct answers
            },
            LegalDomain.COMMERCIAL: {
                'temperature': 0.08,   # Slightly creative
                'max_tokens': 250,     # Complex commercial analysis
                'presence_penalty': 0.12  # Comprehensive business considerations
            }
        }

        # Complexity-based adjustments
        self.complexity_multipliers = {
            QueryComplexity.SIMPLE: {
                'temperature': 0.8,
                'max_tokens': 0.6,
                'presence_penalty': 0.7,
                'frequency_penalty': 0.7
            },
            QueryComplexity.MODERATE: {
                'temperature': 1.0,
                'max_tokens': 1.0,
                'presence_penalty': 1.0,
                'frequency_penalty': 1.0
            },
            QueryComplexity.COMPLEX: {
                'temperature': 1.2,
                'max_tokens': 1.4,
                'presence_penalty': 1.3,
                'frequency_penalty': 1.2
            },
            QueryComplexity.VERY_COMPLEX: {
                'temperature': 1.4,
                'max_tokens': 1.8,
                'presence_penalty': 1.5,
                'frequency_penalty': 1.4
            }
        }

    def optimize_parameters(self,
                          query: str,
                          legal_domain: str = None,
                          complexity: str = None,
                          context_length: int = 0,
                          user_expertise: str = "general") -> OptimizedParameters:
        """
        Main method to optimize LLM parameters based on query characteristics

        Args:
            query: The user's legal query
            legal_domain: Legal domain (criminal, civil, constitutional, etc.)
            complexity: Query complexity level
            context_length: Length of retrieved context
            user_expertise: User's legal knowledge level

        Returns:
            OptimizedParameters: Fine-tuned LLM parameters
        """

        # Determine legal domain if not provided
        if not legal_domain:
            legal_domain = self._infer_legal_domain(query)

        # Determine complexity if not provided
        if not complexity:
            complexity = self._assess_complexity(query, context_length)

        # Select base configuration
        base_config = self._select_base_config(legal_domain, complexity, user_expertise)

        # Apply domain-specific adjustments
        adjusted_config = self._apply_domain_adjustments(base_config, legal_domain)

        # Apply complexity multipliers
        final_config = self._apply_complexity_multipliers(adjusted_config, complexity)

        # Apply context-based adjustments
        final_config = self._apply_context_adjustments(final_config, context_length)

        # Apply user expertise adjustments
        final_config = self._apply_expertise_adjustments(final_config, user_expertise)

        # Ensure parameters are within valid ranges
        final_config = self._clamp_parameters(final_config)

        return OptimizedParameters(**final_config)

    def _infer_legal_domain(self, query: str) -> LegalDomain:
        """Infer the legal domain from the query content"""
        query_lower = query.lower()

        # Criminal law indicators
        criminal_terms = ['murder', 'rape', 'theft', 'assault', 'crime', 'criminal', 'police', 'arrest', 'bail', 'sentence', 'punishment', 'ipc']
        if any(term in query_lower for term in criminal_terms):
            return LegalDomain.CRIMINAL

        # Constitutional law indicators
        constitutional_terms = ['constitution', 'fundamental rights', 'article', 'supreme court', 'high court', 'judicial review', 'amendment']
        if any(term in query_lower for term in constitutional_terms):
            return LegalDomain.CONSTITUTIONAL

        # Civil law indicators
        civil_terms = ['contract', 'property', 'civil suit', 'plaintiff', 'defendant', 'damages', 'compensation']
        if any(term in query_lower for term in civil_terms):
            return LegalDomain.CIVIL

        # Family law indicators
        family_terms = ['marriage', 'divorce', 'adoption', 'guardianship', 'maintenance', 'child custody']
        if any(term in query_lower for term in family_terms):
            return LegalDomain.FAMILY

        # Commercial law indicators
        commercial_terms = ['company', 'partnership', 'director', 'shareholder', 'incorporation', 'business', 'commercial']
        if any(term in query_lower for term in commercial_terms):
            return LegalDomain.COMMERCIAL

        # Labor law indicators
        labor_terms = ['employment', 'termination', 'wage', 'industrial dispute', 'trade union', 'labor']
        if any(term in query_lower for term in labor_terms):
            return LegalDomain.LABOR

        # Tax law indicators
        tax_terms = ['income tax', 'gst', 'customs', 'excise', 'assessment', 'tax']
        if any(term in query_lower for term in tax_terms):
            return LegalDomain.TAX

        # Property law indicators
        property_terms = ['land', 'building', 'lease', 'mortgage', 'easement', 'property']
        if any(term in query_lower for term in property_terms):
            return LegalDomain.PROPERTY

        return LegalDomain.GENERAL

    def _assess_complexity(self, query: str, context_length: int) -> QueryComplexity:
        """Assess the complexity of the legal query"""

        # Length-based complexity
        query_length = len(query.split())
        if query_length < 5:
            base_complexity = QueryComplexity.SIMPLE
        elif query_length < 10:
            base_complexity = QueryComplexity.MODERATE
        elif query_length < 15:
            base_complexity = QueryComplexity.COMPLEX
        else:
            base_complexity = QueryComplexity.VERY_COMPLEX

        # Content-based complexity adjustments
        complexity_indicators = {
            'very_complex': ['analyze', 'constitutional validity', 'legal implications', 'comprehensive', 'detailed analysis'],
            'complex': ['explain', 'interpretation', 'case law', 'precedent', 'procedure'],
            'moderate': ['how to', 'what is', 'difference', 'comparison', 'example'],
            'simple': ['meaning', 'definition', 'basic', 'simple']
        }

        query_lower = query.lower()
        for level, indicators in complexity_indicators.items():
            if any(indicator in query_lower for indicator in indicators):
                if level == 'very_complex':
                    return QueryComplexity.VERY_COMPLEX
                elif level == 'complex':
                    return QueryComplexity.COMPLEX
                elif level == 'moderate':
                    return QueryComplexity.MODERATE
                else:
                    return QueryComplexity.SIMPLE

        # Context length adjustment
        if context_length > 5000:
            # Complex context requires more sophisticated analysis
            if base_complexity == QueryComplexity.SIMPLE:
                return QueryComplexity.MODERATE
            elif base_complexity == QueryComplexity.MODERATE:
                return QueryComplexity.COMPLEX

        return base_complexity

    def _select_base_config(self, legal_domain: LegalDomain, complexity: QueryComplexity, user_expertise: str) -> Dict[str, Any]:
        """Select the most appropriate base configuration"""

        # Domain-based selection
        if legal_domain in [LegalDomain.CRIMINAL, LegalDomain.CONSTITUTIONAL]:
            return self.base_configs['precision_focused'].copy()
        elif legal_domain in [LegalDomain.COMMERCIAL, LegalDomain.INTERNATIONAL]:
            return self.base_configs['creative_analysis'].copy()
        elif legal_domain in [LegalDomain.FAMILY, LegalDomain.LABOR]:
            return self.base_configs['conservative_legal'].copy()
        else:
            return self.base_configs['balanced_reasoning'].copy()

    def _apply_domain_adjustments(self, config: Dict[str, Any], legal_domain: LegalDomain) -> Dict[str, Any]:
        """Apply domain-specific parameter adjustments"""
        if legal_domain in self.domain_adjustments:
            adjustments = self.domain_adjustments[legal_domain]
            for param, adjustment in adjustments.items():
                if param in config:
                    if param == 'temperature':
                        config[param] += adjustment  # Additive adjustment
                    else:
                        config[param] = max(0, config[param] + adjustment)  # Ensure non-negative

        return config

    def _apply_complexity_multipliers(self, config: Dict[str, Any], complexity: QueryComplexity) -> Dict[str, Any]:
        """Apply complexity-based parameter multipliers"""
        if complexity in self.complexity_multipliers:
            multipliers = self.complexity_multipliers[complexity]
            for param, multiplier in multipliers.items():
                if param in config and param != 'reasoning_effort':
                    if param == 'max_tokens':
                        config[param] = int(config[param] * multiplier)
                    else:
                        config[param] *= multiplier

        return config

    def _apply_context_adjustments(self, config: Dict[str, Any], context_length: int) -> Dict[str, Any]:
        """Adjust parameters based on context length"""

        # Longer context requires more focused responses
        if context_length > 3000:
            config['temperature'] *= 0.9  # Slightly more focused
            config['max_tokens'] = min(config['max_tokens'], 2000)  # Reasonable limit
        elif context_length < 500:
            config['temperature'] *= 1.1  # Slightly more creative for sparse context
            config['max_tokens'] = min(config['max_tokens'], 1500)  # Shorter responses

        return config

    def _apply_expertise_adjustments(self, config: Dict[str, Any], user_expertise: str) -> Dict[str, Any]:
        """Adjust parameters based on user expertise level"""

        if user_expertise == 'expert':
            # Experts can handle more complex, technical responses
            config['temperature'] *= 1.2
            config['max_tokens'] = int(config['max_tokens'] * 1.3)
            config['presence_penalty'] *= 1.2
        elif user_expertise == 'intermediate':
            # Balanced approach
            pass  # No changes
        else:  # beginner or general
            # Simpler, clearer responses
            config['temperature'] *= 0.9
            config['max_tokens'] = int(config['max_tokens'] * 0.8)
            config['frequency_penalty'] *= 0.8

        return config

    def _clamp_parameters(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all parameters are within valid ranges"""

        # Temperature: 0.0 to 2.0
        config['temperature'] = max(0.0, min(2.0, config['temperature']))

        # Top-p: 0.0 to 1.0
        config['top_p'] = max(0.0, min(1.0, config['top_p']))

        # Max tokens: 100 to 4000
        config['max_tokens'] = max(100, min(4000, config['max_tokens']))

        # Presence penalty: -2.0 to 2.0
        config['presence_penalty'] = max(-2.0, min(2.0, config['presence_penalty']))

        # Frequency penalty: -2.0 to 2.0
        config['frequency_penalty'] = max(-2.0, min(2.0, config['frequency_penalty']))

        return config

    def get_parameter_explanation(self, params: OptimizedParameters) -> str:
        """Provide explanation for why these parameters were chosen"""
        explanations = []

        if params.temperature < 0.1:
            explanations.append("Low temperature for precise, factual legal responses")
        elif params.temperature > 0.8:
            explanations.append("Higher temperature for creative legal analysis")

        if params.max_tokens > 2000:
            explanations.append("Extended response length for comprehensive legal analysis")
        elif params.max_tokens < 1000:
            explanations.append("Concise response for focused legal information")

        if params.presence_penalty > 0.5:
            explanations.append("Higher presence penalty to encourage comprehensive coverage")
        if params.frequency_penalty > 0.5:
            explanations.append("Higher frequency penalty to avoid repetitive legal jargon")

        return " | ".join(explanations) if explanations else "Standard parameters for balanced legal responses"

# Example usage and testing
if __name__ == "__main__":
    optimizer = PromptParameterOptimizer()

    # Test queries with different characteristics
    test_cases = [
        ("What is Section 302 of IPC?", "criminal", "simple"),
        ("Explain the constitutional validity of Aadhaar scheme", "constitutional", "complex"),
        ("How to file a divorce petition?", "family", "moderate"),
        ("Analyze the legal implications of cryptocurrency regulation", "commercial", "very_complex")
    ]

    for query, domain, complexity in test_cases:
        params = optimizer.optimize_parameters(
            query=query,
            legal_domain=domain,
            complexity=complexity,
            context_length=2000,
            user_expertise="general"
        )

        print(f"\nQuery: {query}")
        print(f"Temperature: {params.temperature:.3f}")
        print(f"Max Tokens: {params.max_tokens}")
        print(f"Top-p: {params.top_p:.3f}")
        print(f"Explanation: {optimizer.get_parameter_explanation(params)}")