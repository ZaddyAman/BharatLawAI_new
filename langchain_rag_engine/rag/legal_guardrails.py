"""
Legal Guardrails System for BharatLawAI
Implements comprehensive safety checks and ethical constraints for legal AI responses
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

class GuardrailSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class GuardrailCategory(Enum):
    LEGAL_ADVICE = "legal_advice"
    JURISDICTION = "jurisdiction"
    ETHICS = "ethics"
    ACCURACY = "accuracy"
    SENSITIVITY = "sensitivity"
    CONFIDENTIALITY = "confidentiality"

@dataclass
class GuardrailViolation:
    """Represents a guardrail violation"""
    category: GuardrailCategory
    severity: GuardrailSeverity
    message: str
    suggestion: str
    confidence: float
    location: Optional[str] = None

@dataclass
class GuardrailResult:
    """Result of guardrail evaluation"""
    violations: List[GuardrailViolation]
    safe_to_proceed: bool
    risk_score: float
    recommendations: List[str]
    sanitized_response: Optional[str] = None

class LegalGuardrails:
    """
    Comprehensive guardrails system for legal AI responses
    Ensures ethical, accurate, and safe legal information delivery
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Initialize guardrail rules
        self.legal_advice_patterns = self._initialize_legal_advice_patterns()
        self.jurisdiction_patterns = self._initialize_jurisdiction_patterns()
        self.ethical_patterns = self._initialize_ethical_patterns()
        self.sensitivity_patterns = self._initialize_sensitivity_patterns()

        # Disclaimer templates
        self.disclaimers = self._initialize_disclaimers()

    def _initialize_legal_advice_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize patterns for detecting unauthorized legal advice"""

        return {
            'direct_advice': {
                'patterns': [
                    r'\byou should\b',
                    r'\byou must\b',
                    r'\byou need to\b',
                    r'\bi recommend\b',
                    r'\bi suggest\b',
                    r'\bconsult me\b',
                    r'\bi advise\b',
                    r'\blegal advice\b',
                    r'\bmy advice\b'
                ],
                'severity': GuardrailSeverity.HIGH,
                'category': GuardrailCategory.LEGAL_ADVICE
            },
            'actionable_instructions': {
                'patterns': [
                    r'\bfile a\b.*\bcase\b',
                    r'\bsue\b.*\bfor\b',
                    r'\bapply for\b.*\bbail\b',
                    r'\bregister\b.*\bcomplaint\b',
                    r'\bapproach\b.*\bcourt\b',
                    r'\bsign\b.*\bagreement\b',
                    r'\bterminate\b.*\bemployment\b'
                ],
                'severity': GuardrailSeverity.CRITICAL,
                'category': GuardrailCategory.LEGAL_ADVICE
            },
            'specific_legal_outcomes': {
                'patterns': [
                    r'\byou will\b.*\bwin\b',
                    r'\byou will\b.*\blose\b',
                    r'\byour case\b.*\bstrong\b',
                    r'\byour case\b.*\bweak\b',
                    r'\bguaranteed\b.*\bsuccess\b',
                    r'\bdefinitely\b.*\bget\b'
                ],
                'severity': GuardrailSeverity.HIGH,
                'category': GuardrailCategory.LEGAL_ADVICE
            }
        }

    def _initialize_jurisdiction_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize patterns for jurisdiction-related issues"""

        return {
            'state_specific': {
                'patterns': [
                    r'\bin\s+(delhi|maharashtra|gujarat|rajasthan|punjab|haryana|uttar pradesh|bihar|west bengal|odisha|andhra pradesh|telangana|kerala|madhya pradesh|chhattisgarh|jharkhand|assam|meghalaya|tripura|mizoram|manipur|nagaland|arunachal pradesh|sikkim|goa|karnataka|tamil nadu)\b',
                    r'\bunder\s+(delhi|maharashtra|gujarat|rajasthan|punjab|haryana|uttar pradesh|bihar|west bengal|odisha|andhra pradesh|telangana|kerala|madhya pradesh|chhattisgarh|jharkhand|assam|meghalaya|tripura|mizoram|manipur|nagaland|arunachal pradesh|sikkim|goa|karnataka|tamil nadu)\s+law\b'
                ],
                'severity': GuardrailSeverity.MEDIUM,
                'category': GuardrailCategory.JURISDICTION
            },
            'central_vs_state': {
                'patterns': [
                    r'\bcentral\s+government\b',
                    r'\bstate\s+government\b',
                    r'\bunion\s+territory\b',
                    r'\bconcurrent\s+list\b',
                    r'\bstate\s+list\b',
                    r'\bunion\s+list\b'
                ],
                'severity': GuardrailSeverity.LOW,
                'category': GuardrailCategory.JURISDICTION
            }
        }

    def _initialize_ethical_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize patterns for ethical concerns"""

        return {
            'conflict_of_interest': {
                'patterns': [
                    r'\bmy\s+client\b',
                    r'\bmy\s+case\b',
                    r'\bi\s+represent\b',
                    r'\bmy\s+firm\b',
                    r'\bmy\s+practice\b'
                ],
                'severity': GuardrailSeverity.CRITICAL,
                'category': GuardrailCategory.ETHICS
            },
            'undue_influence': {
                'patterns': [
                    r'\bpressure\b.*\bto\b',
                    r'\bforce\b.*\bto\b',
                    r'\bcoerce\b.*\bto\b',
                    r'\bmanipulate\b.*\bto\b',
                    r'\bintimidate\b.*\bto\b'
                ],
                'severity': GuardrailSeverity.HIGH,
                'category': GuardrailCategory.ETHICS
            },
            'sensitive_matters': {
                'patterns': [
                    r'\bmental\s+health\b',
                    r'\bmedical\s+emergency\b',
                    r'\bchild\s+abuse\b',
                    r'\bdomestic\s+violence\b',
                    r'\bsexual\s+assault\b',
                    r'\bsuicide\b',
                    r'\bself-harm\b'
                ],
                'severity': GuardrailSeverity.HIGH,
                'category': GuardrailCategory.SENSITIVITY
            }
        }

    def _initialize_sensitivity_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize patterns for sensitive content"""

        return {
            'personal_identifiers': {
                'patterns': [
                    r'\b\d{10}\b',  # Phone numbers
                    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
                    r'\b\d{12}\b',  # Aadhaar numbers
                    r'\b[A-Z]{5}\d{4}[A-Z]{1}\b'  # PAN numbers
                ],
                'severity': GuardrailSeverity.MEDIUM,
                'category': GuardrailCategory.CONFIDENTIALITY
            },
            'case_numbers': {
                'patterns': [
                    r'\b\d{4}\s*\/\s*\d{1,4}\b',  # Case numbers like 2023/123
                    r'\b[Cc]ase\s+No\.?\s*\d+\b',
                    r'\b[Ff]irst\s+[Ii]nformation\s+[Rr]eport\b',
                    r'\b[Ff]\.?I\.?R\.?\b'
                ],
                'severity': GuardrailSeverity.LOW,
                'category': GuardrailCategory.CONFIDENTIALITY
            }
        }

    def _initialize_disclaimers(self) -> Dict[str, str]:
        """Initialize disclaimer templates"""

        return {
            'legal_advice': """

⚠️ **LEGAL DISCLAIMER:**
This response is for informational purposes only and does not constitute legal advice.
Please consult a qualified legal professional for your specific situation.
Laws vary by jurisdiction and can change over time.
""",

            'jurisdiction': """

📍 **JURISDICTIONAL NOTE:**
Legal provisions may vary by state/territory. Please verify the applicable laws
in your specific jurisdiction or consult local legal authorities.
""",

            'accuracy': """

🔍 **ACCURACY NOTE:**
While we strive for accuracy, legal interpretations can be complex and context-dependent.
This information should not be considered exhaustive or definitive.
""",

            'emergency': """

🚨 **EMERGENCY NOTICE:**
If you are in immediate danger or facing a legal emergency,
please contact emergency services (112) or seek immediate legal assistance.
""",

            'sensitivity': """

🤝 **SENSITIVE MATTER:**
This topic involves sensitive personal matters. Consider seeking support from
appropriate professionals or helplines in addition to legal advice.
"""
        }

    def evaluate_response(self, query: str, response: str, context: Optional[Dict[str, Any]] = None) -> GuardrailResult:
        """
        Evaluate a response against all guardrail rules

        Args:
            query: The user's original query
            response: The AI-generated response
            context: Additional context information

        Returns:
            GuardrailResult: Complete evaluation result
        """

        violations = []
        risk_score = 0.0
        recommendations = []

        # Check all guardrail categories
        violations.extend(self._check_legal_advice(response))
        violations.extend(self._check_jurisdiction(response))
        violations.extend(self._check_ethics(response))
        violations.extend(self._check_sensitivity(response))
        violations.extend(self._check_accuracy(response, context))

        # Calculate risk score
        risk_score = self._calculate_risk_score(violations)

        # Generate recommendations
        recommendations = self._generate_recommendations(violations, risk_score)

        # Determine if safe to proceed
        safe_to_proceed = risk_score < 0.7  # Allow low-medium risk

        # Sanitize response if needed
        sanitized_response = self._sanitize_response(response, violations) if violations else None

        return GuardrailResult(
            violations=violations,
            safe_to_proceed=safe_to_proceed,
            risk_score=risk_score,
            recommendations=recommendations,
            sanitized_response=sanitized_response
        )

    def _check_legal_advice(self, response: str) -> List[GuardrailViolation]:
        """Check for unauthorized legal advice"""
        violations = []

        for rule_name, rule_config in self.legal_advice_patterns.items():
            for pattern in rule_config['patterns']:
                matches = re.findall(pattern, response, re.IGNORECASE)
                if matches:
                    violation = GuardrailViolation(
                        category=rule_config['category'],
                        severity=rule_config['severity'],
                        message=f"Detected potential legal advice: '{matches[0]}'",
                        suggestion="Replace with general information and disclaimer",
                        confidence=0.9,
                        location=f"Pattern: {pattern}"
                    )
                    violations.append(violation)

        return violations

    def _check_jurisdiction(self, response: str) -> List[GuardrailViolation]:
        """Check for jurisdiction-specific issues"""
        violations = []

        for rule_name, rule_config in self.jurisdiction_patterns.items():
            for pattern in rule_config['patterns']:
                if re.search(pattern, response, re.IGNORECASE):
                    violation = GuardrailViolation(
                        category=rule_config['category'],
                        severity=rule_config['severity'],
                        message="Response contains jurisdiction-specific information",
                        suggestion="Add jurisdictional disclaimer",
                        confidence=0.8,
                        location=f"Pattern: {pattern}"
                    )
                    violations.append(violation)

        return violations

    def _check_ethics(self, response: str) -> List[GuardrailViolation]:
        """Check for ethical concerns"""
        violations = []

        for rule_name, rule_config in self.ethical_patterns.items():
            for pattern in rule_config['patterns']:
                matches = re.findall(pattern, response, re.IGNORECASE)
                if matches:
                    violation = GuardrailViolation(
                        category=rule_config['category'],
                        severity=rule_config['severity'],
                        message=f"Potential ethical concern detected: '{matches[0]}'",
                        suggestion="Remove personal references and maintain neutrality",
                        confidence=0.95,
                        location=f"Pattern: {pattern}"
                    )
                    violations.append(violation)

        return violations

    def _check_sensitivity(self, response: str) -> List[GuardrailViolation]:
        """Check for sensitive content"""
        violations = []

        for rule_name, rule_config in self.sensitivity_patterns.items():
            for pattern in rule_config['patterns']:
                matches = re.findall(pattern, response)
                if matches:
                    violation = GuardrailViolation(
                        category=rule_config['category'],
                        severity=rule_config['severity'],
                        message=f"Sensitive information detected: '{matches[0]}'",
                        suggestion="Remove or anonymize personal identifiers",
                        confidence=0.9,
                        location=f"Pattern: {pattern}"
                    )
                    violations.append(violation)

        return violations

    def _check_accuracy(self, response: str, context: Optional[Dict[str, Any]]) -> List[GuardrailViolation]:
        """Check for potential accuracy issues"""
        violations = []

        # Check for outdated references
        if '2023' in response or '2022' in response:
            violation = GuardrailViolation(
                category=GuardrailCategory.ACCURACY,
                severity=GuardrailSeverity.LOW,
                message="Response contains potentially outdated information",
                suggestion="Add note about verifying current law",
                confidence=0.6
            )
            violations.append(violation)

        # Check for absolute statements
        absolute_patterns = [
            r'\balways\b',
            r'\bnever\b',
            r'\bdefinitely\b',
            r'\bguaranteed\b',
            r'\babsolutely\b'
        ]

        for pattern in absolute_patterns:
            if re.search(pattern, response, re.IGNORECASE):
                violation = GuardrailViolation(
                    category=GuardrailCategory.ACCURACY,
                    severity=GuardrailSeverity.LOW,
                    message="Response contains absolute statements that may not apply universally",
                    suggestion="Use qualified language",
                    confidence=0.7
                )
                violations.append(violation)
                break

        return violations

    def _calculate_risk_score(self, violations: List[GuardrailViolation]) -> float:
        """Calculate overall risk score from violations"""
        if not violations:
            return 0.0

        severity_weights = {
            GuardrailSeverity.LOW: 0.2,
            GuardrailSeverity.MEDIUM: 0.4,
            GuardrailSeverity.HIGH: 0.7,
            GuardrailSeverity.CRITICAL: 1.0
        }

        total_weight = 0.0
        for violation in violations:
            total_weight += severity_weights[violation.severity]

        # Normalize to 0-1 scale
        return min(total_weight / len(violations), 1.0)

    def _generate_recommendations(self, violations: List[GuardrailViolation], risk_score: float) -> List[str]:
        """Generate recommendations based on violations"""
        recommendations = []

        if risk_score >= 0.7:
            recommendations.append("🚨 HIGH RISK: Consider blocking this response or requiring human review")

        # Group violations by category
        category_counts = {}
        for violation in violations:
            category_counts[violation.category] = category_counts.get(violation.category, 0) + 1

        # Generate category-specific recommendations
        for category, count in category_counts.items():
            if category == GuardrailCategory.LEGAL_ADVICE:
                recommendations.append("⚖️ Add comprehensive legal disclaimer")
            elif category == GuardrailCategory.JURISDICTION:
                recommendations.append("📍 Add jurisdictional limitation notice")
            elif category == GuardrailCategory.ETHICS:
                recommendations.append("🤝 Review for potential conflicts of interest")
            elif category == GuardrailCategory.SENSITIVITY:
                recommendations.append("🤝 Add sensitivity warning and support resources")
            elif category == GuardrailCategory.CONFIDENTIALITY:
                recommendations.append("🔒 Remove or anonymize personal information")

        if not recommendations:
            recommendations.append("✅ Response appears safe, but consider adding standard disclaimer")

        return recommendations

    def _sanitize_response(self, response: str, violations: List[GuardrailViolation]) -> str:
        """Sanitize response by removing or modifying problematic content"""
        sanitized = response

        # Remove personal identifiers
        for violation in violations:
            if violation.category == GuardrailCategory.CONFIDENTIALITY:
                # Simple sanitization - replace with placeholders
                sanitized = re.sub(r'\b\d{10}\b', '[PHONE NUMBER]', sanitized)
                sanitized = re.sub(r'\b\d{12}\b', '[IDENTIFIER]', sanitized)
                sanitized = re.sub(r'\b[A-Z]{5}\d{4}[A-Z]{1}\b', '[TAX ID]', sanitized)

        return sanitized

    def add_disclaimer(self, response: str, disclaimer_type: str) -> str:
        """Add appropriate disclaimer to response"""
        if disclaimer_type in self.disclaimers:
            return response + self.disclaimers[disclaimer_type]
        return response

    def get_violation_summary(self, violations: List[GuardrailViolation]) -> Dict[str, Any]:
        """Get summary of violations by category and severity"""
        summary = {
            'total_violations': len(violations),
            'by_category': {},
            'by_severity': {},
            'critical_issues': []
        }

        for violation in violations:
            # Count by category
            cat_name = violation.category.value
            summary['by_category'][cat_name] = summary['by_category'].get(cat_name, 0) + 1

            # Count by severity
            sev_name = violation.severity.value
            summary['by_severity'][sev_name] = summary['by_severity'].get(sev_name, 0) + 1

            # Track critical issues
            if violation.severity in [GuardrailSeverity.HIGH, GuardrailSeverity.CRITICAL]:
                summary['critical_issues'].append(violation.message)

        return summary

# Example usage and testing
if __name__ == "__main__":
    guardrails = LegalGuardrails()

    # Test queries
    test_cases = [
        ("Should I file a case against my employer?", "You should definitely file a case immediately"),
        ("What is Section 302 IPC?", "In Delhi, Section 302 IPC carries life imprisonment"),
        ("I want to divorce my spouse", "You must approach the family court in your jurisdiction"),
        ("My phone number is 9876543210", "Contact me at 9876543210 for legal help")
    ]

    for query, response in test_cases:
        result = guardrails.evaluate_response(query, response)

        print(f"\nQuery: {query}")
        print(f"Response: {response}")
        print(f"Safe to proceed: {result.safe_to_proceed}")
        print(f"Risk score: {result.risk_score:.2f}")
        print(f"Violations: {len(result.violations)}")

        if result.violations:
            print("Issues found:")
            for violation in result.violations:
                print(f"  - {violation.category.value}: {violation.message}")

        if result.recommendations:
            print("Recommendations:")
            for rec in result.recommendations:
                print(f"  - {rec}")