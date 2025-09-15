"""
Legal Prompt Chain System for BharatLawAI
Implements multi-stage prompt pipelines for sophisticated legal reasoning
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio

class ChainStage(Enum):
    CONTEXT_EXTRACTION = "context_extraction"
    LEGAL_ANALYSIS = "legal_analysis"
    PRECEDENT_REVIEW = "precedent_review"
    CONCLUSION = "conclusion"
    VALIDATION = "validation"
    SAFETY_CHECK = "safety_check"

class LegalChainType(Enum):
    STATUTORY_INTERPRETATION = "statutory_interpretation"
    CASE_ANALYSIS = "case_analysis"
    CONTRACT_REVIEW = "contract_review"
    CONSTITUTIONAL_ANALYSIS = "constitutional_analysis"
    PROCEDURAL_GUIDANCE = "procedural_guidance"
    COMPLIANCE_CHECK = "compliance_check"
    RISK_ASSESSMENT = "risk_assessment"

@dataclass
class ChainStep:
    """Represents a single step in a prompt chain"""
    stage: ChainStage
    prompt_template: str
    parameters: Dict[str, Any]
    required_inputs: List[str]
    output_format: str
    validation_rules: Optional[List[Callable]] = None

@dataclass
class ChainResult:
    """Result of executing a prompt chain"""
    chain_type: LegalChainType
    steps_executed: List[ChainStep]
    intermediate_outputs: Dict[str, Any]
    final_output: str
    confidence_score: float
    execution_time: float

class LegalPromptChain:
    """
    Orchestrates multi-stage prompt chains for complex legal reasoning tasks
    """

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self.chains = self._initialize_chains()

    def _initialize_chains(self) -> Dict[LegalChainType, List[ChainStep]]:
        """Initialize all predefined legal prompt chains"""

        return {
            LegalChainType.STATUTORY_INTERPRETATION: self._create_statutory_chain(),
            LegalChainType.CASE_ANALYSIS: self._create_case_analysis_chain(),
            LegalChainType.CONTRACT_REVIEW: self._create_contract_chain(),
            LegalChainType.CONSTITUTIONAL_ANALYSIS: self._create_constitutional_chain(),
            LegalChainType.PROCEDURAL_GUIDANCE: self._create_procedural_chain(),
            LegalChainType.COMPLIANCE_CHECK: self._create_compliance_chain(),
            LegalChainType.RISK_ASSESSMENT: self._create_risk_chain()
        }

    def _create_statutory_chain(self) -> List[ChainStep]:
        """Create chain for statutory interpretation"""

        return [
            ChainStep(
                stage=ChainStage.CONTEXT_EXTRACTION,
                prompt_template=STATUTORY_CONTEXT_PROMPT,
                parameters={'temperature': 0.05, 'max_tokens': 500},
                required_inputs=['query', 'statute_text'],
                output_format='structured_analysis'
            ),
            ChainStep(
                stage=ChainStage.LEGAL_ANALYSIS,
                prompt_template=STATUTORY_ANALYSIS_PROMPT,
                parameters={'temperature': 0.08, 'max_tokens': 800},
                required_inputs=['query', 'context', 'previous_analysis'],
                output_format='legal_interpretation'
            ),
            ChainStep(
                stage=ChainStage.PRECEDENT_REVIEW,
                prompt_template=PRECEDENT_REVIEW_PROMPT,
                parameters={'temperature': 0.1, 'max_tokens': 600},
                required_inputs=['query', 'analysis', 'relevant_cases'],
                output_format='case_law_analysis'
            ),
            ChainStep(
                stage=ChainStage.CONCLUSION,
                prompt_template=STATUTORY_CONCLUSION_PROMPT,
                parameters={'temperature': 0.05, 'max_tokens': 400},
                required_inputs=['query', 'analysis', 'precedents'],
                output_format='final_interpretation'
            ),
            ChainStep(
                stage=ChainStage.SAFETY_CHECK,
                prompt_template=LEGAL_SAFETY_PROMPT,
                parameters={'temperature': 0.03, 'max_tokens': 200},
                required_inputs=['final_output'],
                output_format='safety_validation'
            )
        ]

    def _create_case_analysis_chain(self) -> List[ChainStep]:
        """Create chain for case law analysis"""

        return [
            ChainStep(
                stage=ChainStage.CONTEXT_EXTRACTION,
                prompt_template=CASE_CONTEXT_PROMPT,
                parameters={'temperature': 0.05, 'max_tokens': 600},
                required_inputs=['query', 'case_text', 'facts'],
                output_format='case_facts'
            ),
            ChainStep(
                stage=ChainStage.LEGAL_ANALYSIS,
                prompt_template=CASE_ANALYSIS_PROMPT,
                parameters={'temperature': 0.1, 'max_tokens': 1000},
                required_inputs=['query', 'facts', 'legal_issues'],
                output_format='legal_analysis'
            ),
            ChainStep(
                stage=ChainStage.PRECEDENT_REVIEW,
                prompt_template=PRECEDENT_IMPACT_PROMPT,
                parameters={'temperature': 0.08, 'max_tokens': 700},
                required_inputs=['analysis', 'similar_cases'],
                output_format='precedent_analysis'
            ),
            ChainStep(
                stage=ChainStage.CONCLUSION,
                prompt_template=CASE_CONCLUSION_PROMPT,
                parameters={'temperature': 0.06, 'max_tokens': 500},
                required_inputs=['analysis', 'precedents'],
                output_format='case_holding'
            )
        ]

    def _create_contract_chain(self) -> List[ChainStep]:
        """Create chain for contract review"""

        return [
            ChainStep(
                stage=ChainStage.CONTEXT_EXTRACTION,
                prompt_template=CONTRACT_CONTEXT_PROMPT,
                parameters={'temperature': 0.05, 'max_tokens': 400},
                required_inputs=['query', 'contract_text'],
                output_format='contract_elements'
            ),
            ChainStep(
                stage=ChainStage.LEGAL_ANALYSIS,
                prompt_template=CONTRACT_ANALYSIS_PROMPT,
                parameters={'temperature': 0.08, 'max_tokens': 800},
                required_inputs=['contract_elements', 'legal_issues'],
                output_format='contract_analysis'
            ),
            ChainStep(
                stage=ChainStage.VALIDATION,
                prompt_template=CONTRACT_VALIDATION_PROMPT,
                parameters={'temperature': 0.05, 'max_tokens': 300},
                required_inputs=['analysis'],
                output_format='validity_assessment'
            ),
            ChainStep(
                stage=ChainStage.CONCLUSION,
                prompt_template=CONTRACT_CONCLUSION_PROMPT,
                parameters={'temperature': 0.05, 'max_tokens': 400},
                required_inputs=['analysis', 'validation'],
                output_format='contract_advice'
            )
        ]

    def _create_constitutional_chain(self) -> List[ChainStep]:
        """Create chain for constitutional analysis"""

        return [
            ChainStep(
                stage=ChainStage.CONTEXT_EXTRACTION,
                prompt_template=CONSTITUTIONAL_CONTEXT_PROMPT,
                parameters={'temperature': 0.03, 'max_tokens': 500},
                required_inputs=['query', 'constitutional_text'],
                output_format='constitutional_elements'
            ),
            ChainStep(
                stage=ChainStage.LEGAL_ANALYSIS,
                prompt_template=CONSTITUTIONAL_ANALYSIS_PROMPT,
                parameters={'temperature': 0.05, 'max_tokens': 900},
                required_inputs=['elements', 'challenged_law'],
                output_format='constitutional_analysis'
            ),
            ChainStep(
                stage=ChainStage.PRECEDENT_REVIEW,
                prompt_template=CONSTITUTIONAL_PRECEDENTS_PROMPT,
                parameters={'temperature': 0.06, 'max_tokens': 700},
                required_inputs=['analysis', 'relevant_judgments'],
                output_format='precedent_review'
            ),
            ChainStep(
                stage=ChainStage.CONCLUSION,
                prompt_template=CONSTITUTIONAL_CONCLUSION_PROMPT,
                parameters={'temperature': 0.04, 'max_tokens': 500},
                required_inputs=['analysis', 'precedents'],
                output_format='constitutional_holding'
            )
        ]

    def _create_procedural_chain(self) -> List[ChainStep]:
        """Create chain for procedural guidance"""

        return [
            ChainStep(
                stage=ChainStage.CONTEXT_EXTRACTION,
                prompt_template=PROCEDURAL_CONTEXT_PROMPT,
                parameters={'temperature': 0.05, 'max_tokens': 300},
                required_inputs=['query', 'procedure_type'],
                output_format='procedural_context'
            ),
            ChainStep(
                stage=ChainStage.LEGAL_ANALYSIS,
                prompt_template=PROCEDURAL_ANALYSIS_PROMPT,
                parameters={'temperature': 0.08, 'max_tokens': 600},
                required_inputs=['context', 'requirements'],
                output_format='procedural_analysis'
            ),
            ChainStep(
                stage=ChainStage.CONCLUSION,
                prompt_template=PROCEDURAL_GUIDANCE_PROMPT,
                parameters={'temperature': 0.06, 'max_tokens': 400},
                required_inputs=['analysis'],
                output_format='step_by_step_guidance'
            )
        ]

    def _create_compliance_chain(self) -> List[ChainStep]:
        """Create chain for compliance checking"""

        return [
            ChainStep(
                stage=ChainStage.CONTEXT_EXTRACTION,
                prompt_template=COMPLIANCE_CONTEXT_PROMPT,
                parameters={'temperature': 0.05, 'max_tokens': 400},
                required_inputs=['query', 'regulatory_framework'],
                output_format='compliance_requirements'
            ),
            ChainStep(
                stage=ChainStage.LEGAL_ANALYSIS,
                prompt_template=COMPLIANCE_ANALYSIS_PROMPT,
                parameters={'temperature': 0.06, 'max_tokens': 700},
                required_inputs=['requirements', 'current_practices'],
                output_format='compliance_analysis'
            ),
            ChainStep(
                stage=ChainStage.VALIDATION,
                prompt_template=COMPLIANCE_VALIDATION_PROMPT,
                parameters={'temperature': 0.04, 'max_tokens': 300},
                required_inputs=['analysis'],
                output_format='compliance_status'
            ),
            ChainStep(
                stage=ChainStage.CONCLUSION,
                prompt_template=COMPLIANCE_RECOMMENDATIONS_PROMPT,
                parameters={'temperature': 0.05, 'max_tokens': 500},
                required_inputs=['status', 'gaps'],
                output_format='compliance_plan'
            )
        ]

    def _create_risk_chain(self) -> List[ChainStep]:
        """Create chain for legal risk assessment"""

        return [
            ChainStep(
                stage=ChainStage.CONTEXT_EXTRACTION,
                prompt_template=RISK_CONTEXT_PROMPT,
                parameters={'temperature': 0.05, 'max_tokens': 400},
                required_inputs=['query', 'scenario'],
                output_format='risk_factors'
            ),
            ChainStep(
                stage=ChainStage.LEGAL_ANALYSIS,
                prompt_template=RISK_ANALYSIS_PROMPT,
                parameters={'temperature': 0.08, 'max_tokens': 800},
                required_inputs=['factors', 'legal_framework'],
                output_format='risk_assessment'
            ),
            ChainStep(
                stage=ChainStage.VALIDATION,
                prompt_template=RISK_VALIDATION_PROMPT,
                parameters={'temperature': 0.05, 'max_tokens': 300},
                required_inputs=['assessment'],
                output_format='risk_validation'
            ),
            ChainStep(
                stage=ChainStage.CONCLUSION,
                prompt_template=RISK_MITIGATION_PROMPT,
                parameters={'temperature': 0.06, 'max_tokens': 600},
                required_inputs=['assessment', 'validation'],
                output_format='risk_mitigation_plan'
            )
        ]

    async def execute_chain(self,
                          chain_type: LegalChainType,
                          inputs: Dict[str, Any],
                          llm_client=None) -> ChainResult:
        """
        Execute a complete prompt chain

        Args:
            chain_type: Type of legal analysis chain to execute
            inputs: Input data for the chain
            llm_client: LLM client to use (optional)

        Returns:
            ChainResult: Complete chain execution result
        """

        if chain_type not in self.chains:
            raise ValueError(f"Unknown chain type: {chain_type}")

        chain = self.chains[chain_type]
        llm = llm_client or self.llm_client

        if not llm:
            raise ValueError("LLM client is required")

        intermediate_outputs = {}
        start_time = asyncio.get_event_loop().time()

        try:
            for step in chain:
                # Validate required inputs
                self._validate_inputs(step, inputs, intermediate_outputs)

                # Prepare prompt
                prompt = self._prepare_prompt(step, inputs, intermediate_outputs)

                # Execute step
                output = await self._execute_step(llm, step, prompt)

                # Store output for next steps
                intermediate_outputs[step.stage.value] = output

            # Generate final result
            final_output = intermediate_outputs.get('conclusion', '')
            confidence_score = self._calculate_confidence(intermediate_outputs)

            execution_time = asyncio.get_event_loop().time() - start_time

            return ChainResult(
                chain_type=chain_type,
                steps_executed=chain,
                intermediate_outputs=intermediate_outputs,
                final_output=final_output,
                confidence_score=confidence_score,
                execution_time=execution_time
            )

        except Exception as e:
            execution_time = asyncio.get_event_loop().time() - start_time
            raise RuntimeError(f"Chain execution failed at step {step.stage.value}: {str(e)}")

    def _validate_inputs(self, step: ChainStep, inputs: Dict[str, Any], intermediate: Dict[str, Any]):
        """Validate that all required inputs are available"""
        for required_input in step.required_inputs:
            if required_input not in inputs and required_input not in intermediate:
                raise ValueError(f"Missing required input: {required_input} for step {step.stage.value}")

    def _prepare_prompt(self, step: ChainStep, inputs: Dict[str, Any], intermediate: Dict[str, Any]) -> str:
        """Prepare the prompt by filling in template variables"""
        prompt = step.prompt_template

        # Fill from inputs
        for key, value in inputs.items():
            placeholder = f"{{{key}}}"
            if placeholder in prompt:
                prompt = prompt.replace(placeholder, str(value))

        # Fill from intermediate outputs
        for key, value in intermediate.items():
            placeholder = f"{{{key}}}"
            if placeholder in prompt:
                prompt = prompt.replace(placeholder, str(value))

        return prompt

    async def _execute_step(self, llm, step: ChainStep, prompt: str) -> str:
        """Execute a single chain step"""
        # This would integrate with your actual LLM client
        # For now, return a placeholder
        return f"Executed {step.stage.value} with prompt: {prompt[:100]}..."

    def _calculate_confidence(self, intermediate_outputs: Dict[str, Any]) -> float:
        """Calculate overall confidence score for the chain result"""
        # Simple confidence calculation based on output completeness
        confidence = 0.5  # Base confidence

        if 'safety_check' in intermediate_outputs:
            confidence += 0.2  # Safety validation passed

        if 'validation' in intermediate_outputs:
            confidence += 0.15  # Validation step completed

        if len(intermediate_outputs) >= 4:
            confidence += 0.15  # All major steps completed

        return min(confidence, 1.0)

    def get_available_chains(self) -> List[LegalChainType]:
        """Get list of available chain types"""
        return list(self.chains.keys())

    def get_chain_description(self, chain_type: LegalChainType) -> str:
        """Get description of a specific chain type"""
        descriptions = {
            LegalChainType.STATUTORY_INTERPRETATION: "Analyzes and interprets statutory provisions with context and precedents",
            LegalChainType.CASE_ANALYSIS: "Performs detailed analysis of case law and judicial precedents",
            LegalChainType.CONTRACT_REVIEW: "Reviews contract terms, validity, and legal implications",
            LegalChainType.CONSTITUTIONAL_ANALYSIS: "Analyzes laws against constitutional provisions and fundamental rights",
            LegalChainType.PROCEDURAL_GUIDANCE: "Provides step-by-step guidance for legal procedures",
            LegalChainType.COMPLIANCE_CHECK: "Assesses compliance with regulatory requirements",
            LegalChainType.RISK_ASSESSMENT: "Evaluates legal risks and provides mitigation strategies"
        }
        return descriptions.get(chain_type, "Legal analysis chain")

# Prompt Templates (would be moved to separate file in production)

STATUTORY_CONTEXT_PROMPT = """
Extract key elements from the following statutory provision:

STATUTE: {statute_text}
QUERY: {query}

Identify:
1. Relevant sections and subsections
2. Key legal terms and definitions
3. Scope and applicability
4. Any conditions or exceptions
5. Related provisions

Provide structured analysis.
"""

STATUTORY_ANALYSIS_PROMPT = """
Analyze the statutory provision in the context of the query:

CONTEXT: {context}
QUERY: {query}
PREVIOUS ANALYSIS: {previous_analysis}

Perform detailed legal analysis including:
1. Plain meaning interpretation
2. Contextual analysis
3. Purpose and intent
4. Potential ambiguities
5. Practical implications

Provide comprehensive statutory interpretation.
"""

# Additional prompt templates would be defined here...
# (Truncated for brevity - would include all chain-specific prompts)

if __name__ == "__main__":
    # Example usage
    chain_system = LegalPromptChain()

    print("Available Legal Prompt Chains:")
    for chain_type in chain_system.get_available_chains():
        print(f"- {chain_type.value}: {chain_system.get_chain_description(chain_type)}")

    print(f"\nTotal chains available: {len(chain_system.get_available_chains())}")