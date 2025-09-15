"""
Chain-of-Thought Reasoning Engine for BharatLawAI
Implements advanced step-by-step reasoning patterns for complex legal analysis
"""

from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
import re
import json

@dataclass
class ReasoningStep:
    """Represents a single step in the reasoning chain"""
    step_number: int
    step_type: str  # 'analysis', 'evidence', 'conclusion', 'hypothesis'
    content: str
    confidence: float
    evidence: List[str] = field(default_factory=list)
    legal_references: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ReasoningChain:
    """Complete chain of reasoning for a legal query"""
    query: str
    steps: List[ReasoningStep] = field(default_factory=list)
    final_conclusion: str = ""
    overall_confidence: float = 0.0
    legal_domain: str = ""
    reasoning_pattern: str = ""  # 'cot', 'tot', 'react'
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LegalReasoningConfig:
    """Configuration for reasoning engine"""
    max_steps: int = 8
    min_confidence_threshold: float = 0.6
    enable_evidence_validation: bool = True
    enable_legal_cross_referencing: bool = True
    reasoning_depth: str = "comprehensive"  # 'basic', 'intermediate', 'comprehensive'
    domain_specific_patterns: bool = True

class ChainOfThoughtReasoning:
    """
    Advanced Chain-of-Thought reasoning engine for legal analysis
    Provides structured, step-by-step reasoning for complex legal queries
    """

    def __init__(self, config: Optional[LegalReasoningConfig] = None):
        self.config = config or LegalReasoningConfig()

        # Legal reasoning patterns for different domains
        self.reasoning_patterns = {
            'criminal_law': self._criminal_law_pattern,
            'constitutional_law': self._constitutional_law_pattern,
            'civil_law': self._civil_law_pattern,
            'family_law': self._family_law_pattern,
            'property_law': self._property_law_pattern,
            'corporate_law': self._corporate_law_pattern,
            'tax_law': self._tax_law_pattern,
            'general': self._general_legal_pattern
        }

        # Legal analysis frameworks
        self.analysis_frameworks = {
            'statutory_interpretation': self._statutory_interpretation_framework,
            'case_law_analysis': self._case_law_analysis_framework,
            'constitutional_challenge': self._constitutional_challenge_framework,
            'contract_dispute': self._contract_dispute_framework,
            'tort_analysis': self._tort_analysis_framework
        }

    def reason_step_by_step(self, query: str, context: str = "",
                           legal_domain: str = "general") -> ReasoningChain:
        """
        Perform step-by-step reasoning for a legal query

        Args:
            query: Legal query to analyze
            context: Available legal context/knowledge
            legal_domain: Legal domain for specialized reasoning

        Returns:
            Complete reasoning chain with all steps
        """
        start_time = datetime.now()

        # Initialize reasoning chain
        chain = ReasoningChain(
            query=query,
            legal_domain=legal_domain,
            reasoning_pattern='cot'
        )

        try:
            # Step 1: Query Analysis
            self._analyze_query(query, chain)

            # Step 2: Context Integration
            if context:
                self._integrate_context(context, chain)

            # Step 3: Domain-Specific Reasoning
            domain_pattern = self.reasoning_patterns.get(legal_domain, self.reasoning_patterns['general'])
            domain_pattern(query, context, chain)

            # Step 4: Evidence Validation
            if self.config.enable_evidence_validation:
                self._validate_evidence(chain)

            # Step 5: Legal Cross-Referencing
            if self.config.enable_legal_cross_referencing:
                self._cross_reference_legal_sources(chain)

            # Step 6: Conclusion Synthesis
            self._synthesize_conclusion(chain)

            # Step 7: Confidence Assessment
            self._assess_overall_confidence(chain)

        except Exception as e:
            # Handle reasoning errors gracefully
            error_step = ReasoningStep(
                step_number=len(chain.steps) + 1,
                step_type='error',
                content=f"Reasoning error: {str(e)}",
                confidence=0.0
            )
            chain.steps.append(error_step)
            chain.final_conclusion = "Unable to complete reasoning due to an error."
            chain.overall_confidence = 0.0

        # Calculate execution time
        end_time = datetime.now()
        chain.execution_time = (end_time - start_time).total_seconds()

        return chain

    def _analyze_query(self, query: str, chain: ReasoningChain):
        """Step 1: Analyze the legal query structure and intent"""
        step = ReasoningStep(
            step_number=1,
            step_type='analysis',
            content="",
            confidence=0.9
        )

        # Identify query type and legal elements
        query_lower = query.lower()

        # Detect legal sections/articles
        sections = re.findall(r'section\s+(\d+|[IVXLCDM]+)', query, re.IGNORECASE)
        articles = re.findall(r'article\s+(\d+)', query, re.IGNORECASE)

        # Detect legal actions/questions
        legal_actions = []
        if any(word in query_lower for word in ['punishment', 'penalty', 'sentence']):
            legal_actions.append('seeking_punishment_info')
        if any(word in query_lower for word in ['valid', 'constitutional', 'challenge']):
            legal_actions.append('validity_assessment')
        if any(word in query_lower for word in ['file', 'approach', 'court']):
            legal_actions.append('procedural_guidance')

        # Detect legal relationships
        relationships = []
        if 'employer' in query_lower and 'employee' in query_lower:
            relationships.append('employment')
        if any(word in query_lower for word in ['husband', 'wife', 'marriage', 'divorce']):
            relationships.append('marital')
        if any(word in query_lower for word in ['land', 'property', 'owner']):
            relationships.append('property')

        # Build analysis content
        analysis_parts = [
            f"Query Analysis: '{query}'",
            f"Legal Sections Identified: {', '.join(sections) if sections else 'None'}",
            f"Constitutional Articles: {', '.join(articles) if articles else 'None'}",
            f"Legal Actions Detected: {', '.join(legal_actions) if legal_actions else 'None'}",
            f"Legal Relationships: {', '.join(relationships) if relationships else 'None'}"
        ]

        step.content = "\n".join(analysis_parts)
        step.legal_references = sections + articles

        chain.steps.append(step)

    def _integrate_context(self, context: str, chain: ReasoningChain):
        """Step 2: Integrate available legal context"""
        step = ReasoningStep(
            step_number=2,
            step_type='evidence',
            content="",
            confidence=0.8
        )

        # Analyze context relevance and completeness
        context_lower = context.lower()

        # Check for key legal elements in context
        has_statutory_law = bool(re.search(r'section\s+\d+', context_lower))
        has_case_law = bool(re.search(r'supreme court|high court|judgment', context_lower))
        has_constitutional_refs = bool(re.search(r'article\s+\d+', context_lower))
        has_procedural_info = bool(re.search(r'procedure|process|steps', context_lower))

        context_quality = sum([has_statutory_law, has_case_law, has_constitutional_refs, has_procedural_info])

        analysis_parts = [
            "Context Integration Analysis:",
            f"Available Context Length: {len(context)} characters",
            f"Contains Statutory Law: {'Yes' if has_statutory_law else 'No'}",
            f"Contains Case Law: {'Yes' if has_case_law else 'No'}",
            f"Contains Constitutional References: {'Yes' if has_constitutional_refs else 'No'}",
            f"Contains Procedural Information: {'Yes' if has_procedural_info else 'No'}",
            f"Context Quality Score: {context_quality}/4"
        ]

        step.content = "\n".join(analysis_parts)
        step.evidence = [context[:200] + "..." if len(context) > 200 else context]

        chain.steps.append(step)

    def _criminal_law_pattern(self, query: str, context: str, chain: ReasoningChain):
        """Criminal law specific reasoning pattern"""
        # Step 3: Identify the offense
        step3 = ReasoningStep(
            step_number=3,
            step_type='analysis',
            content="Criminal Law Analysis - Step 3: Offense Identification",
            confidence=0.85
        )

        # Look for offense indicators
        offense_indicators = {
            'murder': ['murder', 'homicide', 'kill', 'death'],
            'rape': ['rape', 'sexual assault', 'molestation'],
            'theft': ['theft', 'robbery', 'burglary', 'steal'],
            'fraud': ['fraud', 'cheating', 'forgery', 'falsification'],
            'assault': ['assault', 'hurt', 'grievous hurt']
        }

        identified_offenses = []
        query_lower = query.lower()

        for offense, indicators in offense_indicators.items():
            if any(indicator in query_lower for indicator in indicators):
                identified_offenses.append(offense)

        step3.content += f"\nIdentified Offenses: {', '.join(identified_offenses) if identified_offenses else 'None clearly identified'}"
        chain.steps.append(step3)

        # Step 4: Determine applicable sections
        step4 = ReasoningStep(
            step_number=4,
            step_type='evidence',
            content="Criminal Law Analysis - Step 4: Applicable IPC Sections",
            confidence=0.9
        )

        section_mappings = {
            'murder': ['Section 300 (Definition)', 'Section 302 (Punishment)'],
            'rape': ['Section 375 (Definition)', 'Section 376 (Punishment)'],
            'theft': ['Section 378 (Theft)', 'Section 379 (Punishment)'],
            'fraud': ['Section 420 (Cheating)', 'Section 406 (Criminal Breach of Trust)']
        }

        applicable_sections = []
        for offense in identified_offenses:
            if offense in section_mappings:
                applicable_sections.extend(section_mappings[offense])

        step4.content += f"\nApplicable Sections: {', '.join(applicable_sections) if applicable_sections else 'General criminal law principles'}"
        step4.legal_references = applicable_sections
        chain.steps.append(step4)

        # Step 5: Consider defenses and exceptions
        step5 = ReasoningStep(
            step_number=5,
            step_type='analysis',
            content="Criminal Law Analysis - Step 5: Defenses and Exceptions",
            confidence=0.75
        )

        defenses = [
            "General Exceptions under Chapter IV IPC (Sections 76-106)",
            "Right of Private Defense (Sections 96-106)",
            "Mistake of Fact (Section 79)",
            "Consent and Insanity defenses"
        ]

        step5.content += "\nRelevant Defenses to Consider:\n" + "\n".join(f"• {defense}" for defense in defenses)
        chain.steps.append(step5)

    def _constitutional_law_pattern(self, query: str, context: str, chain: ReasoningChain):
        """Constitutional law specific reasoning pattern"""
        # Step 3: Identify constitutional principles
        step3 = ReasoningStep(
            step_number=3,
            step_type='analysis',
            content="Constitutional Law Analysis - Step 3: Fundamental Principles",
            confidence=0.9
        )

        principles = []
        query_lower = query.lower()

        if any(word in query_lower for word in ['equality', 'discrimination', 'equal']):
            principles.append("Article 14 - Equality before law")
        if any(word in query_lower for word in ['speech', 'expression', 'freedom']):
            principles.append("Article 19 - Freedom of speech and expression")
        if any(word in query_lower for word in ['life', 'liberty', 'personal']):
            principles.append("Article 21 - Right to life and liberty")
        if any(word in query_lower for word in ['property', 'acquisition']):
            principles.append("Article 31 - Right to property (pre-1978)")

        step3.content += "\nApplicable Constitutional Principles:\n" + "\n".join(f"• {principle}" for principle in principles)
        step3.legal_references = principles
        chain.steps.append(step3)

        # Step 4: Judicial review and precedent
        step4 = ReasoningStep(
            step_number=4,
            step_type='evidence',
            content="Constitutional Law Analysis - Step 4: Judicial Review Framework",
            confidence=0.85
        )

        framework_points = [
            "Doctrine of Judicial Review established in Kesavananda Bharati case",
            "Basic Structure Doctrine limits Parliament's amending power",
            "Judicial interpretation of fundamental rights",
            "Balancing test between fundamental rights and reasonable restrictions"
        ]

        step4.content += "\nJudicial Review Framework:\n" + "\n".join(f"• {point}" for point in framework_points)
        chain.steps.append(step4)

    def _civil_law_pattern(self, query: str, context: str, chain: ReasoningChain):
        """Civil law specific reasoning pattern"""
        # Step 3: Identify civil law principles
        step3 = ReasoningStep(
            step_number=3,
            step_type='analysis',
            content="Civil Law Analysis - Step 3: Applicable Legal Principles",
            confidence=0.8
        )

        principles = []
        query_lower = query.lower()

        if any(word in query_lower for word in ['contract', 'agreement', 'breach']):
            principles.extend([
                "Contract Act, 1872 - Formation and validity of contracts",
                "Specific Relief Act, 1963 - Remedies for breach",
                "Indian Contract Act - Essential elements of valid contract"
            ])
        if any(word in query_lower for word in ['property', 'land', 'ownership']):
            principles.extend([
                "Transfer of Property Act, 1882 - Property transfer rules",
                "Registration Act, 1908 - Document registration requirements"
            ])
        if any(word in query_lower for word in ['tort', 'negligence', 'damages']):
            principles.extend([
                "Law of Torts - Civil wrongs and remedies",
                "Negligence under tort law",
                "Compensation and damages"
            ])

        step3.content += "\nApplicable Civil Law Principles:\n" + "\n".join(f"• {principle}" for principle in principles)
        step3.legal_references = principles
        chain.steps.append(step3)

    def _family_law_pattern(self, query: str, context: str, chain: ReasoningChain):
        """Family law specific reasoning pattern"""
        # Step 3: Identify family law principles
        step3 = ReasoningStep(
            step_number=3,
            step_type='analysis',
            content="Family Law Analysis - Step 3: Applicable Legal Principles",
            confidence=0.85
        )

        principles = []
        query_lower = query.lower()

        if any(word in query_lower for word in ['marriage', 'divorce', 'maintenance']):
            principles.extend([
                "Hindu Marriage Act, 1955 - Marriage and divorce provisions",
                "Hindu Adoption and Maintenance Act, 1956 - Maintenance rights",
                "Section 125 CrPC - Maintenance for wife and children"
            ])
        if any(word in query_lower for word in ['child', 'custody', 'guardianship']):
            principles.extend([
                "Guardians and Wards Act, 1890 - Child custody and guardianship",
                "Hindu Minority and Guardianship Act, 1956 - Minor rights",
                "Juvenile Justice Act, 2015 - Child protection"
            ])
        if any(word in query_lower for word in ['inheritance', 'succession', 'property']):
            principles.extend([
                "Hindu Succession Act, 1956 - Property inheritance rights",
                "Indian Succession Act, 1925 - General succession rules",
                "Muslim Personal Law - Islamic inheritance rules"
            ])

        step3.content += "\nApplicable Family Law Principles:\n" + "\n".join(f"• {principle}" for principle in principles)
        step3.legal_references = principles
        chain.steps.append(step3)

        # Step 4: Consider personal laws
        step4 = ReasoningStep(
            step_number=4,
            step_type='evidence',
            content="Family Law Analysis - Step 4: Personal Law Considerations",
            confidence=0.8
        )

        personal_laws = [
            "Hindu personal laws apply to Hindus, Sikhs, Jains, and Buddhists",
            "Muslim personal laws apply to Muslims",
            "Christian personal laws apply to Christians",
            "Parsi personal laws apply to Parsis",
            "Special Marriage Act, 1954 for inter-religious marriages"
        ]

        step4.content += "\nPersonal Law Framework:\n" + "\n".join(f"• {law}" for law in personal_laws)
        chain.steps.append(step4)

    def _property_law_pattern(self, query: str, context: str, chain: ReasoningChain):
        """Property law specific reasoning pattern"""
        # Step 3: Identify property law principles
        step3 = ReasoningStep(
            step_number=3,
            step_type='analysis',
            content="Property Law Analysis - Step 3: Applicable Legal Principles",
            confidence=0.8
        )

        principles = []
        query_lower = query.lower()

        if any(word in query_lower for word in ['transfer', 'sale', 'conveyance']):
            principles.extend([
                "Transfer of Property Act, 1882 - Property transfer rules",
                "Registration Act, 1908 - Document registration requirements",
                "Indian Stamp Act, 1899 - Stamp duty requirements"
            ])
        if any(word in query_lower for word in ['mortgage', 'pledge', 'charge']):
            principles.extend([
                "Transfer of Property Act - Mortgage and charge provisions",
                "Companies Act, 2013 - Charges on company property",
                "SARFAESI Act, 2002 - Securitization of financial assets"
            ])
        if any(word in query_lower for word in ['easement', 'license', 'lease']):
            principles.extend([
                "Easements Act, 1882 - Easement rights",
                "Indian Easements Act - License and lease distinctions",
                "Transfer of Property Act - Lease provisions"
            ])

        step3.content += "\nApplicable Property Law Principles:\n" + "\n".join(f"• {principle}" for principle in principles)
        step3.legal_references = principles
        chain.steps.append(step3)

        # Step 4: Consider registration and documentation
        step4 = ReasoningStep(
            step_number=4,
            step_type='evidence',
            content="Property Law Analysis - Step 4: Registration and Documentation",
            confidence=0.85
        )

        registration_requirements = [
            "Section 17 of Registration Act - Documents requiring compulsory registration",
            "Section 49 of Registration Act - Time limit for registration",
            "Section 23 of Indian Stamp Act - Stamp duty payment before registration",
            "Section 60 of Transfer of Property Act - Notice requirements"
        ]

        step4.content += "\nRegistration Framework:\n" + "\n".join(f"• {req}" for req in registration_requirements)
        chain.steps.append(step4)

    def _corporate_law_pattern(self, query: str, context: str, chain: ReasoningChain):
        """Corporate law specific reasoning pattern"""
        # Step 3: Identify corporate law principles
        step3 = ReasoningStep(
            step_number=3,
            step_type='analysis',
            content="Corporate Law Analysis - Step 3: Applicable Legal Principles",
            confidence=0.8
        )

        principles = []
        query_lower = query.lower()

        if any(word in query_lower for word in ['incorporation', 'formation', 'registration']):
            principles.extend([
                "Companies Act, 2013 - Company incorporation process",
                "Companies Incorporation Rules, 2014 - Detailed incorporation procedures",
                "Ministry of Corporate Affairs - Digital incorporation platform"
            ])
        if any(word in query_lower for word in ['director', 'board', 'governance']):
            principles.extend([
                "Section 149 Companies Act - Board composition requirements",
                "Section 166 Companies Act - Director duties and responsibilities",
                "SEBI Listing Regulations - Corporate governance standards"
            ])
        if any(word in query_lower for word in ['shares', 'capital', 'dividend']):
            principles.extend([
                "Section 2(84) Companies Act - Share capital definition",
                "Section 123 Companies Act - Dividend distribution rules",
                "Section 68 Companies Act - Buy-back of shares"
            ])

        step3.content += "\nApplicable Corporate Law Principles:\n" + "\n".join(f"• {principle}" for principle in principles)
        step3.legal_references = principles
        chain.steps.append(step3)

    def _tax_law_pattern(self, query: str, context: str, chain: ReasoningChain):
        """Tax law specific reasoning pattern"""
        # Step 3: Identify tax law principles
        step3 = ReasoningStep(
            step_number=3,
            step_type='analysis',
            content="Tax Law Analysis - Step 3: Applicable Legal Principles",
            confidence=0.8
        )

        principles = []
        query_lower = query.lower()

        if any(word in query_lower for word in ['income', 'salary', 'business']):
            principles.extend([
                "Income-tax Act, 1961 - Income tax provisions",
                "Section 192 Income-tax Act - TDS on salary",
                "Section 195 Income-tax Act - TDS on non-residents"
            ])
        if any(word in query_lower for word in ['gst', 'goods', 'services']):
            principles.extend([
                "Central Goods and Services Tax Act, 2017 - GST framework",
                "Integrated Goods and Services Tax Act, 2017 - IGST provisions",
                "GST Compensation Cess Act, 2017 - Cess provisions"
            ])
        if any(word in query_lower for word in ['customs', 'import', 'export']):
            principles.extend([
                "Customs Act, 1962 - Import/export regulations",
                "Customs Tariff Act, 1975 - Duty rates and classifications",
                "Foreign Trade Policy - Export promotion schemes"
            ])

        step3.content += "\nApplicable Tax Law Principles:\n" + "\n".join(f"• {principle}" for principle in principles)
        step3.legal_references = principles
        chain.steps.append(step3)

    def _statutory_interpretation_framework(self) -> List[str]:
        """Framework for statutory interpretation"""
        return [
            "Literal Rule: Give words their plain, ordinary meaning",
            "Golden Rule: Avoid absurd results by modifying literal meaning",
            "Mischief Rule: Interpret to remedy the mischief the statute was intended to cure",
            "Purposive Approach: Consider the purpose and context of the legislation",
            "Harmonious Construction: Interpret statutes to avoid conflict"
        ]

    def _case_law_analysis_framework(self) -> List[str]:
        """Framework for case law analysis"""
        return [
            "Identify the ratio decidendi (binding principle)",
            "Distinguish obiter dicta (non-binding observations)",
            "Consider the hierarchy of courts and precedent value",
            "Analyze the facts and their similarity to the current case",
            "Assess the continuing relevance and any overruling decisions"
        ]

    def _constitutional_challenge_framework(self) -> List[str]:
        """Framework for constitutional challenges"""
        return [
            "Article 13: Laws inconsistent with fundamental rights are void",
            "Doctrine of Severability: Strike down only unconstitutional parts",
            "Doctrine of Eclipse: Unconstitutional law becomes dormant",
            "Reading Down: Interpret law narrowly to save constitutionality",
            "Judicial Review: Courts can declare laws unconstitutional"
        ]

    def _contract_dispute_framework(self) -> List[str]:
        """Framework for contract dispute analysis"""
        return [
            "Essential elements of valid contract (Section 10)",
            "Void and voidable contracts (Sections 24-30)",
            "Discharge of contracts (Sections 37-67)",
            "Remedies for breach (Sections 73-75)",
            "Specific performance and injunctions (Specific Relief Act)"
        ]

    def _tort_analysis_framework(self) -> List[str]:
        """Framework for tort analysis"""
        return [
            "Wrongful act or omission causing damage",
            "Duty of care owed by defendant to plaintiff",
            "Breach of that duty of care",
            "Damage or injury suffered by plaintiff",
            "Causation between breach and damage",
            "Defenses: Contributory negligence, volenti non fit injuria"
        ]

    def _general_legal_pattern(self, query: str, context: str, chain: ReasoningChain):
        """General legal reasoning pattern for unspecified domains"""
        # Step 3: General legal analysis
        step3 = ReasoningStep(
            step_number=3,
            step_type='analysis',
            content="General Legal Analysis - Step 3: Legal Framework Application",
            confidence=0.7
        )

        framework = [
            "Identify the applicable legal domain and governing law",
            "Determine the relevant legal principles and statutes",
            "Consider any applicable case law and precedents",
            "Evaluate the legal position based on facts and law",
            "Assess potential remedies or next steps"
        ]

        step3.content += "\nGeneral Legal Analysis Framework:\n" + "\n".join(f"• {point}" for point in framework)
        chain.steps.append(step3)

    def _validate_evidence(self, chain: ReasoningChain):
        """Step: Validate evidence and legal references"""
        step = ReasoningStep(
            step_number=len(chain.steps) + 1,
            step_type='evidence',
            content="Evidence Validation - Cross-referencing legal sources",
            confidence=0.8
        )

        # Validate legal references
        valid_references = []
        invalid_references = []

        for ref in chain.steps[-1].legal_references:
            # Simple validation - check if reference format is valid
            if re.match(r'(Section|Article)\s+\d+', ref):
                valid_references.append(ref)
            else:
                invalid_references.append(ref)

        validation_results = [
            f"Valid Legal References: {len(valid_references)}",
            f"Invalid References: {len(invalid_references)}"
        ]

        if valid_references:
            validation_results.append(f"Validated: {', '.join(valid_references[:3])}")

        step.content += "\n" + "\n".join(validation_results)
        step.evidence = valid_references
        chain.steps.append(step)

    def _cross_reference_legal_sources(self, chain: ReasoningChain):
        """Step: Cross-reference with other legal sources"""
        step = ReasoningStep(
            step_number=len(chain.steps) + 1,
            step_type='evidence',
            content="Legal Cross-Referencing - Related legal provisions and precedents",
            confidence=0.75
        )

        # Generate cross-references based on legal domain
        cross_refs = []

        if chain.legal_domain == 'criminal':
            cross_refs = [
                "Criminal Procedure Code, 1973 - Trial procedures",
                "Indian Evidence Act, 1872 - Evidence admissibility",
                "Protection of Children from Sexual Offences Act, 2012 (if applicable)"
            ]
        elif chain.legal_domain == 'constitutional':
            cross_refs = [
                "Constitutional Law precedents from Supreme Court",
                "Fundamental Rights case law",
                "Directive Principles of State Policy"
            ]
        elif chain.legal_domain == 'civil':
            cross_refs = [
                "Limitation Act, 1963 - Time limits for legal actions",
                "Civil Procedure Code, 1908 - Civil litigation procedures",
                "Specific Relief Act, 1963 - Equitable remedies"
            ]

        step.content += "\nRelated Legal Sources:\n" + "\n".join(f"• {ref}" for ref in cross_refs)
        step.legal_references = cross_refs
        chain.steps.append(step)

    def _synthesize_conclusion(self, chain: ReasoningChain):
        """Step: Synthesize final conclusion from all reasoning steps"""
        step = ReasoningStep(
            step_number=len(chain.steps) + 1,
            step_type='conclusion',
            content="Conclusion Synthesis - Integrating all reasoning steps",
            confidence=0.85
        )

        # Extract key insights from all previous steps
        key_insights = []

        for reasoning_step in chain.steps:
            if reasoning_step.step_type in ['analysis', 'evidence']:
                # Extract key points from step content
                lines = reasoning_step.content.split('\n')
                for line in lines:
                    if any(keyword in line.lower() for keyword in ['section', 'article', 'principle', 'conclusion']):
                        key_insights.append(line.strip())

        # Limit to most relevant insights
        key_insights = key_insights[:5]

        conclusion_parts = [
            "Based on the comprehensive legal analysis:",
            "",
            "KEY LEGAL INSIGHTS:"
        ] + [f"• {insight}" for insight in key_insights] + [
            "",
            "LEGAL POSITION SUMMARY:",
            f"This appears to be a matter falling under {chain.legal_domain} law.",
            "Consultation with a qualified legal professional is recommended for specific advice."
        ]

        step.content += "\n" + "\n".join(conclusion_parts)
        chain.steps.append(step)

        # Set final conclusion
        chain.final_conclusion = step.content

    def _assess_overall_confidence(self, chain: ReasoningChain):
        """Assess overall confidence in the reasoning chain"""
        if not chain.steps:
            chain.overall_confidence = 0.0
            return

        # Calculate weighted average confidence
        total_weight = 0
        weighted_sum = 0

        for step in chain.steps:
            weight = 1.0
            if step.step_type == 'conclusion':
                weight = 1.5  # Give more weight to conclusions
            elif step.step_type == 'evidence':
                weight = 1.2  # Give more weight to evidence-based steps

            weighted_sum += step.confidence * weight
            total_weight += weight

        chain.overall_confidence = weighted_sum / total_weight if total_weight > 0 else 0.0

    def get_reasoning_summary(self, chain: ReasoningChain) -> Dict[str, Any]:
        """Get a summary of the reasoning process"""
        return {
            'query': chain.query,
            'legal_domain': chain.legal_domain,
            'total_steps': len(chain.steps),
            'overall_confidence': chain.overall_confidence,
            'execution_time': chain.execution_time,
            'step_types': [step.step_type for step in chain.steps],
            'key_legal_references': list(set(
                ref for step in chain.steps for ref in step.legal_references
            )),
            'reasoning_quality_score': self._calculate_reasoning_quality(chain)
        }

    def _calculate_reasoning_quality(self, chain: ReasoningChain) -> float:
        """Calculate overall quality score of the reasoning process"""
        if not chain.steps:
            return 0.0

        quality_factors = {
            'step_completeness': len(chain.steps) / self.config.max_steps,
            'evidence_quality': sum(1 for step in chain.steps if step.evidence) / len(chain.steps),
            'legal_references': sum(len(step.legal_references) for step in chain.steps) / len(chain.steps),
            'confidence_stability': 1 - (max(s.confidence for s in chain.steps) - min(s.confidence for s in chain.steps))
        }

        # Weighted average of quality factors
        weights = {'step_completeness': 0.3, 'evidence_quality': 0.3,
                  'legal_references': 0.25, 'confidence_stability': 0.15}

        quality_score = sum(quality_factors[factor] * weights[factor] for factor in quality_factors)

        return min(1.0, quality_score)  # Cap at 1.0

# Example usage and testing
if __name__ == "__main__":
    # Initialize CoT reasoning engine
    config = LegalReasoningConfig(
        max_steps=8,
        enable_evidence_validation=True,
        reasoning_depth='comprehensive'
    )

    cot_engine = ChainOfThoughtReasoning(config)

    # Test queries
    test_cases = [
        {
            'query': 'What is the punishment for murder under IPC Section 302?',
            'domain': 'criminal_law',
            'context': 'Section 302 IPC prescribes punishment for murder'
        },
        {
            'query': 'Is the Aadhaar scheme constitutional?',
            'domain': 'constitutional_law',
            'context': 'Aadhaar case decided by Supreme Court in 2018'
        },
        {
            'query': 'What are the remedies for breach of contract?',
            'domain': 'civil_law',
            'context': 'Contract Act and Specific Relief Act'
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧠 TEST CASE {i}: {test_case['query']}")
        print("=" * 60)

        # Perform reasoning
        chain = cot_engine.reason_step_by_step(
            query=test_case['query'],
            context=test_case['context'],
            legal_domain=test_case['domain']
        )

        print(f"📊 Reasoning Chain Summary:")
        print(f"   Domain: {chain.legal_domain}")
        print(f"   Steps: {len(chain.steps)}")
        print(f"   Confidence: {chain.overall_confidence:.2f}")
        print(f"   Execution Time: {chain.execution_time:.2f}s")

        print("\n🔍 Reasoning Steps:")
        for step in chain.steps:
            print(f"   {step.step_number}. {step.step_type.upper()}: {step.content[:80]}...")
            if step.legal_references:
                print(f"      📚 References: {', '.join(step.legal_references[:2])}")

        print("\n🎯 Final Conclusion:")
        print(f"   {chain.final_conclusion[:200]}...")

        # Get reasoning summary
        summary = cot_engine.get_reasoning_summary(chain)
        print("\n📈 Quality Metrics:")
        print(f"   Reasoning Quality: {summary['reasoning_quality_score']:.2f}")
        print(f"   Key References: {len(summary['key_legal_references'])}")

    print("\n✅ Chain-of-Thought reasoning tests completed!")