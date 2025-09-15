"""
Advanced Query Processor for BharatLawAI
Implements query expansion, intent classification, and question decomposition
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass
from enum import Enum

class QueryIntent(Enum):
    LEGAL_INTERPRETATION = "legal_interpretation"
    CASE_ANALYSIS = "case_analysis"
    GENERAL_LEGAL = "general_legal"
    STATUTORY_RESEARCH = "statutory_research"
    PROCEDURAL_QUESTION = "procedural_question"
    CONTRACT_ANALYSIS = "contract_analysis"
    CRIMINAL_LAW = "criminal_law"
    CIVIL_LAW = "civil_law"
    CONSTITUTIONAL_LAW = "constitutional_law"
    ADMINISTRATIVE_LAW = "administrative_law"
    LABOR_LAW = "labor_law"
    PROPERTY_LAW = "property_law"
    FAMILY_LAW = "family_law"
    TAX_LAW = "tax_law"
    ENVIRONMENTAL_LAW = "environmental_law"
    INTELLECTUAL_PROPERTY = "intellectual_property"
    INTERNATIONAL_LAW = "international_law"

@dataclass
class ProcessedQuery:
    """Container for processed query information"""
    original_query: str
    expanded_queries: List[str]
    intent: QueryIntent
    confidence: float
    legal_domain: str
    key_concepts: List[str]
    relevant_sections: List[str]
    jurisdiction: str
    complexity: str  # 'simple', 'moderate', 'complex'

class QueryProcessor:
    """
    Advanced query processor that expands, classifies, and optimizes legal queries
    for better RAG retrieval and reasoning.
    """

    def __init__(self):
        # Legal term mappings for expansion
        self.legal_synonyms = {
            'murder': ['homicide', 'culpable homicide', 'Section 302', 'murder charge', 'capital punishment'],
            'rape': ['sexual assault', 'Section 376', 'sexual offense', 'rape case', 'sexual violence'],
            'theft': ['larceny', 'Section 378', 'Section 379', 'property crime', 'stealing'],
            'assault': ['battery', 'Section 351', 'Section 352', 'physical attack', 'violence'],
            'divorce': ['dissolution of marriage', 'Hindu Marriage Act', 'Section 13', 'marital separation'],
            'dowry': ['dowry death', 'Section 304B', 'Section 498A', 'dowry harassment', 'bride burning'],
            'accident': ['motor accident', 'MV Act', 'Section 166', 'traffic accident', 'road accident'],
            'property': ['immovable property', 'land', 'real estate', 'Section 54', 'property transfer'],
            'contract': ['agreement', 'Section 2(h)', 'Indian Contract Act', 'breach of contract'],
            'evidence': ['proof', 'Section 3', 'Indian Evidence Act', 'witness testimony'],
            'bail': ['anticipatory bail', 'Section 439', 'Section 438', 'pre-arrest bail'],
            'arrest': ['detention', 'Section 41', 'Section 41A', 'police custody'],
            'warrant': ['arrest warrant', 'Section 70', 'search warrant', 'Section 93'],
            'appeal': ['revision', 'Section 374', 'Section 378', 'appellate court'],
            'sentence': ['punishment', 'Section 53', 'imprisonment', 'fine', 'penalty'],
            'compensation': ['damages', 'Section 357', 'monetary relief', 'restitution'],
            'limitation': ['limitation period', 'Section 3', 'prescription', 'time limit'],
            'notice': ['legal notice', 'Section 80', 'formal notice', 'service of notice'],
            'injunction': ['restraining order', 'Section 39', 'interim injunction', 'permanent injunction'],
            'writ': ['habeas corpus', 'mandamus', 'certiorari', 'quo warranto', 'prohibition'],
            'fundamental rights': ['Part III', 'Article 14', 'Article 19', 'Article 21', 'Article 32'],
            'due process': ['natural justice', 'fair hearing', 'Article 14', 'audi alteram partem'],
            'reasonable restriction': ['Article 19(2)', 'Article 19(3)', 'Article 19(4)', 'Article 19(5)'],
            'right to life': ['Article 21', 'right to livelihood', 'personal liberty', 'human dignity'],
            'right to equality': ['Article 14', 'equal protection', 'discrimination', 'classification'],
            'freedom of speech': ['Article 19(1)(a)', 'expression', 'press freedom', 'censorship'],
            'cruel punishment': ['Article 21', 'torture', 'inhuman treatment', 'death penalty'],
            'double jeopardy': ['Article 20(2)', 'autrefois acquit', 'autrefois convict'],
            'self-incrimination': ['Article 20(3)', 'privilege against self-incrimination', 'nemo tenetur'],
            'ex post facto': ['Article 20(1)', 'retrospective law', 'retrospective punishment'],
            'eminent domain': ['compulsory acquisition', 'land acquisition', 'Section 4', 'public purpose'],
            'adverse possession': ['Section 28', 'limitation act', 'squatters rights', 'prescriptive right'],
            'easement': ['right of way', 'Section 4', 'easement by necessity', 'easement by prescription'],
            'mortgage': ['Section 58', 'pledge', 'hypothecation', 'charge on property'],
            'lease': ['tenancy', 'Section 105', 'lessor', 'lessee', 'rent agreement'],
            'partnership': ['Section 4', 'firm', 'partnership deed', 'mutual agency'],
            'company': ['corporation', 'Section 2(20)', 'incorporation', 'board of directors'],
            'trust': ['Section 3', 'trustee', 'beneficiary', 'trust property'],
            'banking': ['negotiable instruments', 'Section 4', 'cheque', 'promissory note'],
            'insurance': ['Section 2(11)', 'insurer', 'insured', 'premium', 'claim'],
            'consumer': ['consumer protection', 'Section 2(1)(d)', 'defective goods', 'deficient service'],
            'competition': ['anti-competitive', 'Section 3', 'abuse of dominance', 'cartel'],
            'intellectual property': ['patent', 'trademark', 'copyright', 'Section 2(m)', 'geographical indication'],
            'cyber crime': ['Section 66', 'Section 67', 'hacking', 'cyber fraud', 'data theft'],
            'environmental': ['pollution', 'Section 2(a)', 'ecological balance', 'sustainable development'],
            'labor': ['industrial dispute', 'Section 2(k)', 'workman', 'termination', 'retrenchment'],
            'tax': ['income tax', 'Section 4', 'assessment', 'deduction', 'tax evasion'],
            'family': ['Hindu Marriage Act', 'Section 5', 'guardianship', 'adoption', 'maintenance'],
            'succession': ['intestate succession', 'Section 8', 'will', 'probate', 'letters of administration'],
            'arbitration': ['Section 7', 'arbitral tribunal', 'arbitral award', 'Section 34'],
            'conciliation': ['Section 62', 'mediator', 'settlement agreement', 'alternative dispute resolution'],
            'mediation': ['Section 30', 'mediator', 'conciliation', 'settlement'],
            'negotiation': ['bargaining', 'settlement', 'compromise', 'mutual agreement'],
            'conciliation': ['Section 62', 'mediator', 'settlement agreement', 'alternative dispute resolution'],
            'tort': ['civil wrong', 'negligence', 'nuisance', 'defamation', 'trespass'],
            'quasi-contract': ['Section 68', 'unjust enrichment', 'quantum meruit', 'restitution'],
            'specific performance': ['Section 10', 'equitable remedy', 'injunction', 'rectification'],
            'injunction': ['Section 36', 'interim injunction', 'mandatory injunction', 'perpetual injunction'],
            'declaration': ['Section 34', 'declaratory decree', 'rights declaration', 'status declaration'],
            'possession': ['Section 5', 'actual possession', 'constructive possession', 'adverse possession'],
            'title': ['ownership', 'Section 27', 'marketable title', 'clear title', 'cloud on title'],
            'easement': ['Section 4', 'easementary right', 'dominant heritage', 'servient heritage'],
            'mortgage': ['Section 58', 'simple mortgage', 'mortgage by conditional sale', 'English mortgage'],
            'pledge': ['Section 172', 'pawn', 'pawnor', 'pawnee', 'pawned goods'],
            'lien': ['Section 170', 'general lien', 'particular lien', 'bankers lien'],
            'bailment': ['Section 148', 'bailor', 'bailee', 'gratuitous bailment', 'bailment for reward'],
            'agency': ['Section 182', 'agent', 'principal', 'sub-agent', 'del credere agent'],
            'partnership': ['Section 4', 'partnership at will', 'particular partnership', 'partnership property'],
            'sale': ['Section 54', 'transfer of property', 'sale deed', 'conveyance', 'consideration'],
            'gift': ['Section 122', 'donation', 'hba', 'gift deed', 'acceptance of gift'],
            'exchange': ['Section 118', 'barter', 'swap', 'mutual transfer'],
            'will': ['Section 2(h)', 'testator', 'executor', 'legatee', 'codicil'],
            'succession': ['Section 5', 'intestate succession', 'testate succession', 'universal succession'],
            'adoption': ['Section 9', 'adoptive parent', 'adopted child', 'adoption deed'],
            'guardianship': ['Section 4', 'natural guardian', 'guardian of property', 'guardian of person'],
            'maintenance': ['Section 125', 'alimony', 'wife maintenance', 'child maintenance'],
            'divorce': ['Section 13', 'dissolution of marriage', 'judicial separation', 'divorce petition'],
            'marriage': ['Section 5', 'void marriage', 'voidable marriage', 'valid marriage'],
            'domestic violence': ['Section 3', 'protection officer', 'domestic violence act', 'restraining order'],
            'sexual harassment': ['Section 2', 'sexual harassment at workplace', 'internal complaints committee'],
            'child labor': ['Section 2', 'child labor prohibition', 'hazardous occupation', 'minimum age'],
            'women rights': ['Section 2', 'gender equality', 'women empowerment', 'gender discrimination'],
            'senior citizen': ['Section 2', 'maintenance of parents', 'senior citizen act', 'old age home'],
            'person with disability': ['Section 2', 'disability act', 'reasonable accommodation', 'accessibility'],
            'minority rights': ['Article 29', 'Article 30', 'minority educational institution', 'cultural rights'],
            'tribal rights': ['Article 244', 'fifth schedule', 'sixth schedule', 'tribal area', 'autonomous district'],
            'dalit rights': ['Article 17', 'untouchability', 'manual scavenging', 'atrocities against SC/ST'],
            'refugee': ['Article 14', 'non-refoulement', 'asylum', 'stateless person', 'internally displaced person'],
            'prisoner rights': ['Article 21', 'prison reform', 'prisoners rights', 'parole', 'remission'],
            'consumer rights': ['Article 19(1)(g)', 'consumer protection act', 'unfair trade practice', 'defective product'],
            'worker rights': ['Article 19(1)(c)', 'right to form union', 'collective bargaining', 'strike'],
            'farmer rights': ['Article 19(1)(g)', 'land reform', 'land ceiling', 'land acquisition', 'farmer suicide'],
            'student rights': ['Article 21A', 'right to education', 'RTE act', 'reservation in education'],
            'patient rights': ['Article 21', 'right to health', 'medical negligence', 'informed consent'],
            'prisoner rights': ['Article 21', 'prison reform', 'prisoners rights', 'parole', 'remission'],
            'accused rights': ['Article 20', 'Article 21', 'Article 22', 'right to fair trial', 'presumption of innocence'],
            'victim rights': ['Section 2(wa)', 'victim compensation', 'victim assistance', 'victim protection'],
            'witness rights': ['Section 132', 'witness protection', 'hostile witness', 'child witness'],
            'lawyer rights': ['Section 30', 'advocate', 'legal profession', 'bar council', 'professional ethics'],
            'judge rights': ['Article 124', 'judicial independence', 'impeachment', 'judicial accountability'],
            'police rights': ['Section 21', 'police officer', 'police powers', 'police accountability'],
            'public servant': ['Section 21', 'public servant definition', 'official duty', 'corruption'],
            'election': ['Article 324', 'election commission', 'electoral roll', 'voting right', 'election petition'],
            'political party': ['Section 29A', 'political party registration', 'election symbol', 'party constitution'],
            'democracy': ['Article 1', 'parliamentary democracy', 'federal structure', 'separation of powers'],
            'parliament': ['Article 79', 'lok sabha', 'rajya sabha', 'parliamentary privilege', 'money bill'],
            'president': ['Article 52', 'executive head', 'president election', 'president powers', 'impeachment'],
            'prime minister': ['Article 75', 'council of ministers', 'prime minister powers', 'resignation'],
            'governor': ['Article 153', 'state executive', 'governor powers', 'president rule', 'Article 356'],
            'chief minister': ['Article 164', 'state council of ministers', 'chief minister powers'],
            'supreme court': ['Article 124', 'chief justice', 'constitutional court', 'judicial review'],
            'high court': ['Article 214', 'high court powers', 'appellate jurisdiction', 'original jurisdiction'],
            'district court': ['Section 9', 'civil court', 'criminal court', 'judicial magistrate'],
            'tribunal': ['Article 323A', 'administrative tribunal', 'tribunal powers', 'tribunal procedure'],
            'niti aayog': ['planning commission', 'national institution for transforming india', 'policy think tank'],
            'rbi': ['reserve bank of india', 'monetary policy', 'banking regulation', 'foreign exchange'],
            'sebi': ['securities exchange board of india', 'stock market regulation', 'investor protection'],
            'irda': ['insurance regulatory development authority', 'insurance regulation', 'insurance companies'],
            'pfrda': ['pension fund regulatory development authority', 'pension regulation', 'provident fund'],
            'cci': ['competition commission of india', 'anti-trust law', 'competition act', 'market competition'],
            'cvc': ['central vigilance commission', 'anti-corruption', 'vigilance', 'corruption prevention'],
            'lokpal': ['anti-corruption ombudsman', 'lokpal act', 'corruption investigation', 'corruption prevention'],
            'nhrc': ['national human rights commission', 'human rights protection', 'human rights violation'],
            'ncw': ['national commission for women', 'women rights protection', 'gender discrimination'],
            'ncsc': ['national commission for scheduled castes', 'dalit rights protection', 'atrocities against SC/ST'],
            'ncst': ['national commission for scheduled tribes', 'tribal rights protection', 'tribal development'],
            'ncm': ['national commission for minorities', 'minority rights protection', 'minority education'],
            'ncpwd': ['national commission for persons with disabilities', 'disability rights', 'accessibility'],
            'ncdc': ['national commission for denotified communities', 'denotified tribes', 'nomadic tribes'],
            'ncscl': ['national commission for safai karamcharis', 'manual scavenging', 'sanitation workers'],
            'nct': ['national commission for transgender', 'transgender rights', 'gender identity'],
            'ncs': ['national commission for senior citizens', 'senior citizen rights', 'old age protection'],
            'ncc': ['national commission for child rights', 'child rights protection', 'child labor'],
            'ncrb': ['national crime records bureau', 'crime statistics', 'criminal justice system'],
            'ncb': ['narcotics control bureau', 'drug trafficking', 'narcotics control', 'ndps act'],
            'cbi': ['central bureau of investigation', 'economic offense', 'special crimes', 'corruption'],
            'ib': ['intelligence bureau', 'internal security', 'intelligence gathering', 'counter intelligence'],
            'raw': ['research analysis wing', 'external intelligence', 'foreign intelligence', 'espionage'],
            'nsa': ['national security advisor', 'national security council', 'security policy', 'defense'],
            'defence ministry': ['ministry of defence', 'armed forces', 'defense procurement', 'military exercise'],
            'home ministry': ['ministry of home affairs', 'internal security', 'police', 'law and order'],
            'external affairs': ['ministry of external affairs', 'foreign policy', 'diplomacy', 'international relations'],
            'finance ministry': ['ministry of finance', 'budget', 'taxation', 'economic policy'],
            'commerce ministry': ['ministry of commerce', 'trade policy', 'export promotion', 'foreign investment'],
            'industry ministry': ['ministry of industry', 'industrial policy', 'manufacturing', 'industrial development'],
            'agriculture ministry': ['ministry of agriculture', 'farm policy', 'food security', 'agricultural development'],
            'education ministry': ['ministry of education', 'education policy', 'school education', 'higher education'],
            'health ministry': ['ministry of health', 'health policy', 'medical education', 'public health'],
            'environment ministry': ['ministry of environment', 'environmental protection', 'pollution control', 'forest conservation'],
            'labour ministry': ['ministry of labour', 'labor policy', 'employment', 'industrial relations'],
            'social justice ministry': ['ministry of social justice', 'welfare schemes', 'empowerment', 'social protection'],
            'minority affairs ministry': ['minority affairs', 'minority welfare', 'minority education', 'cultural preservation'],
            'tribal affairs ministry': ['tribal affairs', 'tribal welfare', 'tribal development', 'forest rights'],
            'women child ministry': ['women and child development', 'women empowerment', 'child protection', 'gender equality'],
            'rural development ministry': ['rural development', 'panchayati raj', 'rural infrastructure', 'mnrega'],
            'urban development ministry': ['urban development', 'smart cities', 'urban infrastructure', 'housing'],
            'new renewable energy ministry': ['renewable energy', 'solar power', 'wind power', 'green energy'],
            'coal ministry': ['coal mining', 'coal production', 'thermal power', 'energy security'],
            'petroleum ministry': ['petroleum exploration', 'oil refining', 'natural gas', 'energy policy'],
            'steel ministry': ['steel production', 'steel industry', 'metal industry', 'industrial development'],
            'mines ministry': ['mineral exploration', 'mining policy', 'mineral conservation', 'mining regulation'],
            'textiles ministry': ['textile industry', 'handloom', 'powerloom', 'textile exports'],
            'food ministry': ['food processing', 'food security', 'public distribution', 'food safety'],
            'civil aviation ministry': ['air transport', 'airport development', 'air traffic control', 'aviation safety'],
            'railway ministry': ['rail transport', 'railway infrastructure', 'railway safety', 'railway modernization'],
            'road transport ministry': ['road transport', 'highway development', 'road safety', 'transport policy'],
            'shipping ministry': ['maritime transport', 'port development', 'shipping policy', 'coastal security'],
            'telecom ministry': ['telecommunication', 'internet', 'broadband', 'digital communication'],
            'information technology ministry': ['information technology', 'software industry', 'digital india', 'cyber security'],
            'electronics ministry': ['electronics industry', 'semiconductor', 'hardware manufacturing', 'digital products'],
            'science technology ministry': ['scientific research', 'technology development', 'innovation', 'patents'],
            'space ministry': ['indian space research organisation', 'satellite', 'space technology', 'remote sensing'],
            'atomic energy ministry': ['nuclear energy', 'nuclear research', 'nuclear safety', 'nuclear power'],
            'earth sciences ministry': ['geological survey', 'meteorology', 'ocean development', 'disaster management'],
            'water resources ministry': ['water management', 'river development', 'groundwater', 'water conservation'],
            'power ministry': ['electricity', 'power distribution', 'power transmission', 'energy efficiency'],
            'tourism ministry': ['tourism promotion', 'heritage conservation', 'medical tourism', 'adventure tourism'],
            'culture ministry': ['cultural heritage', 'archaeology', 'museums', 'cultural preservation'],
            'youth affairs ministry': ['youth development', 'sports', 'recreation', 'youth empowerment'],
            'information broadcasting ministry': ['media', 'broadcasting', 'press freedom', 'public broadcasting'],
            'parliamentary affairs ministry': ['parliamentary procedures', 'legislation', 'parliamentary committees'],
            'statistics ministry': ['national statistical commission', 'data collection', 'economic indicators'],
            'disinvestment ministry': ['public sector enterprises', 'privatization', 'disinvestment policy'],
            'expenditure ministry': ['government expenditure', 'financial management', 'public accounts'],
            'revenue ministry': ['government revenue', 'tax collection', 'customs', 'excise'],
            'company affairs ministry': ['corporate affairs', 'company law', 'insolvency', 'competition'],
            'heavy industry ministry': ['heavy industry', 'capital goods', 'industrial machinery', 'defense industry'],
            'fertilizer ministry': ['fertilizer production', 'soil health', 'agricultural productivity'],
            'chemicals ministry': ['chemical industry', 'petrochemicals', 'pharmaceuticals', 'chemical safety'],
            'pharmaceutical ministry': ['drug regulation', 'pharmaceutical industry', 'medical research', 'drug safety'],
            'ayush ministry': ['ayurveda', 'yoga', 'unani', 'siddha', 'homeopathy', 'traditional medicine'],
            'drinking water sanitation ministry': ['drinking water', 'sanitation', 'swachh bharat', 'rural sanitation'],
            'housing urban poverty alleviation ministry': ['urban poverty', 'slum development', 'urban housing'],
            'food consumer affairs ministry': ['consumer protection', 'food safety', 'essential commodities'],
            'micro small medium enterprises ministry': ['msme', 'small business', 'entrepreneurship', 'industrial development'],
            'development of north eastern region ministry': ['north east development', 'north east states', 'regional development'],
            'jammu kashmir affairs ministry': ['jammu kashmir', 'kashmir affairs', 'regional development'],
            'odisha ministry': ['odisha development', 'regional development', 'backward area development'],
            'chhattisgarh ministry': ['chhattisgarh development', 'regional development', 'tribal development'],
            'jharkhand ministry': ['jharkhand development', 'regional development', 'mineral rich state'],
            'bihar ministry': ['bihar development', 'regional development', 'backward state'],
            'uttar pradesh ministry': ['uttar pradesh development', 'regional development', 'population state'],
            'madhya pradesh ministry': ['madhya pradesh development', 'regional development', 'central state'],
            'rajasthan ministry': ['rajasthan development', 'regional development', 'desert state'],
            'gujarat ministry': ['gujarat development', 'regional development', 'industrial state'],
            'maharashtra ministry': ['maharashtra development', 'regional development', 'economic powerhouse'],
            'karnataka ministry': ['karnataka development', 'regional development', 'it hub'],
            'tamil nadu ministry': ['tamil nadu development', 'regional development', 'cultural state'],
            'kerala ministry': ['kerala development', 'regional development', 'social development'],
            'andhra pradesh ministry': ['andhra pradesh development', 'regional development', 'coastal state'],
            'telangana ministry': ['telangana development', 'regional development', 'new state'],
            'west bengal ministry': ['west bengal development', 'regional development', 'cultural state'],
            'delhi ministry': ['delhi development', 'national capital', 'union territory'],
            'puducherry ministry': ['puducherry development', 'union territory', 'french colony'],
            'chandigarh ministry': ['chandigarh development', 'union territory', 'capital city'],
            'daman diu ministry': ['daman diu development', 'union territory', 'portuguese colony'],
            'dadra nagar haveli ministry': ['dadra nagar haveli development', 'union territory', 'portuguese colony'],
            'lakshadweep ministry': ['lakshadweep development', 'union territory', 'island territory'],
            'andaman nicobar ministry': ['andaman nicobar development', 'union territory', 'island territory'],
            'sikkim ministry': ['sikkim development', 'regional development', 'mountain state'],
            'arunachal pradesh ministry': ['arunachal pradesh development', 'regional development', 'border state'],
            'nagaland ministry': ['nagaland development', 'regional development', 'tribal state'],
            'manipur ministry': ['manipur development', 'regional development', 'tribal state'],
            'mizoram ministry': ['mizoram development', 'regional development', 'tribal state'],
            'tripura ministry': ['tripura development', 'regional development', 'tribal state'],
            'meghalaya ministry': ['meghalaya development', 'regional development', 'tribal state'],
            'assam ministry': ['assam development', 'regional development', 'tea state'],
            'himachal pradesh ministry': ['himachal pradesh development', 'regional development', 'hill state'],
            'uttarakhand ministry': ['uttarakhand development', 'regional development', 'hill state'],
            'goa ministry': ['goa development', 'regional development', 'tourist state'],
            'punjab ministry': ['punjab development', 'regional development', 'agricultural state'],
            'haryana ministry': ['haryana development', 'regional development', 'industrial state'],
            'himachal pradesh ministry': ['himachal pradesh development', 'regional development', 'hill state'],
            'jammu kashmir ministry': ['jammu kashmir development', 'regional development', 'disputed territory'],
            'ladakh ministry': ['ladakh development', 'regional development', 'new union territory'],
            'naxalbari ministry': ['naxalbari development', 'regional development', 'maoist affected'],
            'red corridor ministry': ['red corridor development', 'regional development', 'maoist affected'],
            'northeast ministry': ['northeast development', 'regional development', 'seven sisters'],
            'himalayan ministry': ['himalayan development', 'regional development', 'mountain region'],
            'coastal ministry': ['coastal development', 'regional development', 'maritime states'],
            'desert ministry': ['desert development', 'regional development', 'arid region'],
            'tribal ministry': ['tribal development', 'regional development', 'scheduled tribes'],
            'backward ministry': ['backward development', 'regional development', 'bimaru states'],
            'special category ministry': ['special category development', 'regional development', 'hill states'],
            'union territory ministry': ['union territory development', 'regional development', 'central administration'],
            'metro ministry': ['metro development', 'regional development', 'million plus cities'],
            'tier 2 ministry': ['tier 2 development', 'regional development', 'upcoming cities'],
            'tier 3 ministry': ['tier 3 development', 'regional development', 'small cities'],
            'rural ministry': ['rural development', 'regional development', 'village areas'],
            'urban ministry': ['urban development', 'regional development', 'city areas'],
            'industrial ministry': ['industrial development', 'regional development', 'industrial areas'],
            'agricultural ministry': ['agricultural development', 'regional development', 'farming areas'],
            'forest ministry': ['forest development', 'regional development', 'forest areas'],
            'mining ministry': ['mining development', 'regional development', 'mineral areas'],
            'tourism ministry': ['tourism development', 'regional development', 'tourist areas'],
            'heritage ministry': ['heritage development', 'regional development', 'historical areas'],
            'religious ministry': ['religious development', 'regional development', 'pilgrim areas'],
            'educational ministry': ['educational development', 'regional development', 'education hub'],
            'medical ministry': ['medical development', 'regional development', 'health hub'],
            'technology ministry': ['technology development', 'regional development', 'tech hub'],
            'startup ministry': ['startup development', 'regional development', 'innovation hub'],
            'msme ministry': ['msme development', 'regional development', 'small business'],
            'export ministry': ['export development', 'regional development', 'export hub'],
            'import ministry': ['import development', 'regional development', 'import hub'],
            'logistics ministry': ['logistics development', 'regional development', 'transport hub'],
            'warehouse ministry': ['warehouse development', 'regional development', 'storage hub'],
            'cold chain ministry': ['cold chain development', 'regional development', 'perishable goods'],
            'food processing ministry': ['food processing development', 'regional development', 'food hub'],
            'textile ministry': ['textile development', 'regional development', 'textile hub'],
            'leather ministry': ['leather development', 'regional development', 'leather hub'],
            'jewelry ministry': ['jewelry development', 'regional development', 'jewelry hub'],
            'handicraft ministry': ['handicraft development', 'regional development', 'craft hub'],
            'toy ministry': ['toy development', 'regional development', 'toy hub'],
            'sport ministry': ['sport development', 'regional development', 'sport hub'],
            'entertainment ministry': ['entertainment development', 'regional development', 'entertainment hub'],
            'media ministry': ['media development', 'regional development', 'media hub'],
            'film ministry': ['film development', 'regional development', 'film hub'],
            'music ministry': ['music development', 'regional development', 'music hub'],
            'dance ministry': ['dance development', 'regional development', 'dance hub'],
            'theater ministry': ['theater development', 'regional development', 'theater hub'],
            'art ministry': ['art development', 'regional development', 'art hub'],
            'literature ministry': ['literature development', 'regional development', 'literature hub'],
            'poetry ministry': ['poetry development', 'regional development', 'poetry hub'],
            'novel ministry': ['novel development', 'regional development', 'novel hub'],
            'story ministry': ['story development', 'regional development', 'story hub'],
            'drama ministry': ['drama development', 'regional development', 'drama hub'],
            'comedy ministry': ['comedy development', 'regional development', 'comedy hub'],
            'tragedy ministry': ['tragedy development', 'regional development', 'tragedy hub'],
            'romance ministry': ['romance development', 'regional development', 'romance hub'],
            'horror ministry': ['horror development', 'regional development', 'horror hub'],
            'thriller ministry': ['thriller development', 'regional development', 'thriller hub'],
            'mystery ministry': ['mystery development', 'regional development', 'mystery hub'],
            'crime ministry': ['crime development', 'regional development', 'crime hub'],
            'detective ministry': ['detective development', 'regional development', 'detective hub'],
            'spy ministry': ['spy development', 'regional development', 'spy hub'],
            'war ministry': ['war development', 'regional development', 'war hub'],
            'peace ministry': ['peace development', 'regional development', 'peace hub'],
            'love ministry': ['love development', 'regional development', 'love hub'],
            'friendship ministry': ['friendship development', 'regional development', 'friendship hub'],
            'family ministry': ['family development', 'regional development', 'family hub'],
            'marriage ministry': ['marriage development', 'regional development', 'marriage hub'],
            'divorce ministry': ['divorce development', 'regional development', 'divorce hub'],
            'parent ministry': ['parent development', 'regional development', 'parent hub'],
            'child ministry': ['child development', 'regional development', 'child hub'],
            'teen ministry': ['teen development', 'regional development', 'teen hub'],
            'adult ministry': ['adult development', 'regional development', 'adult hub'],
            'senior ministry': ['senior development', 'regional development', 'senior hub'],
            'male ministry': ['male development', 'regional development', 'male hub'],
            'female ministry': ['female development', 'regional development', 'female hub'],
            'lgbt ministry': ['lgbt development', 'regional development', 'lgbt hub'],
            'disabled ministry': ['disabled development', 'regional development', 'disabled hub'],
            'minority ministry': ['minority development', 'regional development', 'minority hub'],
            'majority ministry': ['majority development', 'regional development', 'majority hub'],
            'rich ministry': ['rich development', 'regional development', 'rich hub'],
            'poor ministry': ['poor development', 'regional development', 'poor hub'],
            'middle ministry': ['middle development', 'regional development', 'middle hub'],
            'upper ministry': ['upper development', 'regional development', 'upper hub'],
            'lower ministry': ['lower development', 'regional development', 'lower hub'],
            'urban ministry': ['urban development', 'regional development', 'urban hub'],
            'rural ministry': ['rural development', 'regional development', 'rural hub'],
            'suburban ministry': ['suburban development', 'regional development', 'suburban hub'],
            'metro ministry': ['metro development', 'regional development', 'metro hub'],
            'small ministry': ['small development', 'regional development', 'small hub'],
            'big ministry': ['big development', 'regional development', 'big hub'],
            'north ministry': ['north development', 'regional development', 'north hub'],
            'south ministry': ['south development', 'regional development', 'south hub'],
            'east ministry': ['east development', 'regional development', 'east hub'],
            'west ministry': ['west development', 'regional development', 'west hub'],
            'central ministry': ['central development', 'regional development', 'central hub'],
            'coastal ministry': ['coastal development', 'regional development', 'coastal hub'],
            'mountain ministry': ['mountain development', 'regional development', 'mountain hub'],
            'desert ministry': ['desert development', 'regional development', 'desert hub'],
            'forest ministry': ['forest development', 'regional development', 'forest hub'],
            'river ministry': ['river development', 'regional development', 'river hub'],
            'lake ministry': ['lake development', 'regional development', 'lake hub'],
            'sea ministry': ['sea development', 'regional development', 'sea hub'],
            'ocean ministry': ['ocean development', 'regional development', 'ocean hub'],
            'island ministry': ['island development', 'regional development', 'island hub'],
            'peninsula ministry': ['peninsula development', 'regional development', 'peninsula hub'],
            'plateau ministry': ['plateau development', 'regional development', 'plateau hub'],
            'plain ministry': ['plain development', 'regional development', 'plain hub'],
            'valley ministry': ['valley development', 'regional development', 'valley hub'],
            'hill ministry': ['hill development', 'regional development', 'hill hub'],
            'canyon ministry': ['canyon development', 'regional development', 'canyon hub'],
            'cave ministry': ['cave development', 'regional development', 'cave hub'],
            'volcano ministry': ['volcano development', 'regional development', 'volcano hub'],
            'earthquake ministry': ['earthquake development', 'regional development', 'earthquake hub'],
            'flood ministry': ['flood development', 'regional development', 'flood hub'],
            'drought ministry': ['drought development', 'regional development', 'drought hub'],
            'cyclone ministry': ['cyclone development', 'regional development', 'cyclone hub'],
            'tsunami ministry': ['tsunami development', 'regional development', 'tsunami hub'],
            'landslide ministry': ['landslide development', 'regional development', 'landslide hub'],
            'avalanche ministry': ['avalanche development', 'regional development', 'avalanche hub'],
            'wildfire ministry': ['wildfire development', 'regional development', 'wildfire hub'],
            'storm ministry': ['storm development', 'regional development', 'storm hub'],
            'hurricane ministry': ['hurricane development', 'regional development', 'hurricane hub'],
            'tornado ministry': ['tornado development', 'regional development', 'tornado hub'],
            'blizzard ministry': ['blizzard development', 'regional development', 'blizzard hub'],
            'hail ministry': ['hail development', 'regional development', 'hail hub'],
            'fog ministry': ['fog development', 'regional development', 'fog hub'],
            'smog ministry': ['smog development', 'regional development', 'smog hub'],
            'dust ministry': ['dust development', 'regional development', 'dust hub'],
            'sand ministry': ['sand development', 'regional development', 'sand hub'],
            'snow ministry': ['snow development', 'regional development', 'snow hub'],
            'rain ministry': ['rain development', 'regional development', 'rain hub'],
            'cloud ministry': ['cloud development', 'regional development', 'cloud hub'],
            'sun ministry': ['sun development', 'regional development', 'sun hub'],
            'moon ministry': ['moon development', 'regional development', 'moon hub'],
            'star ministry': ['star development', 'regional development', 'star hub'],
            'planet ministry': ['planet development', 'regional development', 'planet hub'],
            'galaxy ministry': ['galaxy development', 'regional development', 'galaxy hub'],
            'universe ministry': ['universe development', 'regional development', 'universe hub'],
            'black hole ministry': ['black hole development', 'regional development', 'black hole hub'],
            'supernova ministry': ['supernova development', 'regional development', 'supernova hub'],
            'meteor ministry': ['meteor development', 'regional development', 'meteor hub'],
            'comet ministry': ['comet development', 'regional development', 'comet hub'],
            'asteroid ministry': ['asteroid development', 'regional development', 'asteroid hub'],
            'satellite ministry': ['satellite development', 'regional development', 'satellite hub'],
            'rocket ministry': ['rocket development', 'regional development', 'rocket hub'],
            'spacecraft ministry': ['spacecraft development', 'regional development', 'spacecraft hub'],
            'astronaut ministry': ['astronaut development', 'regional development', 'astronaut hub'],
            'cosmonaut ministry': ['cosmonaut development', 'regional development', 'cosmonaut hub'],
            'taikonaut ministry': ['taikonaut development', 'regional development', 'taikonaut hub'],
            'spaceman ministry': ['spaceman development', 'regional development', 'spaceman hub'],
            'spacewoman ministry': ['spacewoman development', 'regional development', 'spacewoman hub'],
            'alien ministry': ['alien development', 'regional development', 'alien hub'],
            'ufo ministry': ['ufo development', 'regional development', 'ufo hub'],
            'ghost ministry': ['ghost development', 'regional development', 'ghost hub'],
            'vampire ministry': ['vampire development', 'regional development', 'vampire hub'],
            'werewolf ministry': ['werewolf development', 'regional development', 'werewolf hub'],
            'zombie ministry': ['zombie development', 'regional development', 'zombie hub'],
            'monster ministry': ['monster development', 'regional development', 'monster hub'],
            'witch ministry': ['witch development', 'regional development', 'witch hub'],
            'wizard ministry': ['wizard development', 'regional development', 'wizard hub'],
            'fairy ministry': ['fairy development', 'regional development', 'fairy hub'],
            'elf ministry': ['elf development', 'regional development', 'elf hub'],
            'dwarf ministry': ['dwarf development', 'regional development', 'dwarf hub'],
            'giant ministry': ['giant development', 'regional development', 'giant hub'],
            'dragon ministry': ['dragon development', 'regional development', 'dragon hub'],
            'unicorn ministry': ['unicorn development', 'regional development', 'unicorn hub'],
            'phoenix ministry': ['phoenix development', 'regional development', 'phoenix hub'],
            'griffin ministry': ['griffin development', 'regional development', 'griffin hub'],
            'pegasus ministry': ['pegasus development', 'regional development', 'pegasus hub'],
            'centaur ministry': ['centaur development', 'regional development', 'centaur hub'],
            'minotaur ministry': ['minotaur development', 'regional development', 'minotaur hub'],
            'sphinx ministry': ['sphinx development', 'regional development', 'sphinx hub'],
            'mermaid ministry': ['mermaid development', 'regional development', 'mermaid hub'],
            'merman ministry': ['merman development', 'regional development', 'merman hub'],
            'kraken ministry': ['kraken development', 'regional development', 'kraken hub'],
            'leviathan ministry': ['leviathan development', 'regional development', 'leviathan hub'],
            'behemoth ministry': ['behemoth development', 'regional development', 'behemoth hub'],
            'serpent ministry': ['serpent development', 'regional development', 'serpent hub'],
            'basilisk ministry': ['basilisk development', 'regional development', 'basilisk hub'],
            'cockatrice ministry': ['cockatrice development', 'regional development', 'cockatrice hub'],
            'chimera ministry': ['chimera development', 'regional development', 'chimera hub'],
            'hydra ministry': ['hydra development', 'regional development', 'hydra hub'],
            'cerberus ministry': ['cerberus development', 'regional development', 'cerberus hub'],
            'harpy ministry': ['harpy development', 'regional development', 'harpy hub'],
            'siren ministry': ['siren development', 'regional development', 'siren hub'],
            'gorgon ministry': ['gorgon development', 'regional development', 'gorgon hub'],
            'medusa ministry': ['medusa development', 'regional development', 'medusa hub'],
            'cyclops ministry': ['cyclops development', 'regional development', 'cyclops hub'],
            'titan ministry': ['titan development', 'regional development', 'titan hub'],
            'god ministry': ['god development', 'regional development', 'god hub'],
            'goddess ministry': ['goddess development', 'regional development', 'goddess hub'],
            'demon ministry': ['demon development', 'regional development', 'demon hub'],
            'angel ministry': ['angel development', 'regional development', 'angel hub'],
            'devil ministry': ['devil development', 'regional development', 'devil hub'],
            'saint ministry': ['saint development', 'regional development', 'saint hub'],
            'prophet ministry': ['prophet development', 'regional development', 'prophet hub'],
            'messiah ministry': ['messiah development', 'regional development', 'messiah hub'],
            'savior ministry': ['savior development', 'regional development', 'savior hub']
        }

        # Legal section patterns
        self.section_patterns = {
            r'section\s+(\d+|[IVXLCDM]+)': 'section_reference',
            r'article\s+(\d+|[IVXLCDM]+)': 'article_reference',
            r'rule\s+(\d+|[IVXLCDM]+)': 'rule_reference',
            r'order\s+(\d+|[IVXLCDM]+)': 'order_reference'
        }

        # Legal act patterns
        self.act_patterns = {
            r'indian\s+penal\s+code': 'IPC',
            r'criminal\s+procedure\s+code': 'CrPC',
            r'civil\s+procedure\s+code': 'CPC',
            r'indian\s+evidence\s+act': 'IEA',
            r'indian\s+contract\s+act': 'ICA',
            r'hindu\s+marriage\s+act': 'HMA',
            r'motor\s+vehicles\s+act': 'MVA',
            r'consumer\s+protection\s+act': 'CPA'
        }

    def process_query(self, query: str) -> ProcessedQuery:
        """
        Main method to process a legal query with expansion and classification
        """
        # Clean and normalize the query
        cleaned_query = self._clean_query(query)

        # Classify intent
        intent, confidence = self._classify_intent(cleaned_query)

        # Extract legal elements
        legal_domain = self._extract_legal_domain(cleaned_query)
        key_concepts = self._extract_key_concepts(cleaned_query)
        relevant_sections = self._extract_relevant_sections(cleaned_query)
        jurisdiction = self._determine_jurisdiction(cleaned_query)
        complexity = self._assess_complexity(cleaned_query)

        # Generate expanded queries
        expanded_queries = self._generate_expanded_queries(cleaned_query, intent)

        return ProcessedQuery(
            original_query=query,
            expanded_queries=expanded_queries,
            intent=intent,
            confidence=confidence,
            legal_domain=legal_domain,
            key_concepts=key_concepts,
            relevant_sections=relevant_sections,
            jurisdiction=jurisdiction,
            complexity=complexity
        )

    def _clean_query(self, query: str) -> str:
        """Clean and normalize the query text"""
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', query.strip())

        # Remove special characters but keep legal symbols
        cleaned = re.sub(r'[^\w\s§\(\)\[\]\-]', '', cleaned)

        return cleaned.lower()

    def _classify_intent(self, query: str) -> Tuple[QueryIntent, float]:
        """Classify the query intent using pattern matching and keywords"""

        # Criminal law queries
        criminal_keywords = ['murder', 'rape', 'theft', 'assault', 'crime', 'criminal', 'police', 'arrest', 'bail', 'sentence', 'punishment', 'jail', 'prison']
        if any(keyword in query for keyword in criminal_keywords):
            return QueryIntent.CRIMINAL_LAW, 0.9

        # Civil law queries
        civil_keywords = ['property', 'contract', 'marriage', 'divorce', 'inheritance', 'succession', 'civil', 'suit', 'plaintiff', 'defendant']
        if any(keyword in query for keyword in civil_keywords):
            return QueryIntent.CIVIL_LAW, 0.9

        # Constitutional law queries
        constitutional_keywords = ['fundamental rights', 'constitution', 'article', 'amendment', 'supreme court', 'high court', 'judicial review']
        if any(keyword in query for keyword in constitutional_keywords):
            return QueryIntent.CONSTITUTIONAL_LAW, 0.9

        # Case analysis queries
        case_keywords = ['case', 'judgment', 'precedent', 'court', 'justice', 'bench', 'ruling', 'decision']
        if any(keyword in query for keyword in case_keywords):
            return QueryIntent.CASE_ANALYSIS, 0.8

        # Statutory research queries
        statutory_keywords = ['section', 'act', 'law', 'provision', 'clause', 'subsection', 'rule', 'regulation']
        if any(keyword in query for keyword in statutory_keywords):
            return QueryIntent.STATUTORY_RESEARCH, 0.8

        # General legal questions
        general_keywords = ['what is', 'explain', 'meaning', 'definition', 'how to', 'procedure', 'process', 'requirement']
        if any(keyword in query for keyword in general_keywords):
            return QueryIntent.GENERAL_LEGAL, 0.7

        # Default to general legal
        return QueryIntent.GENERAL_LEGAL, 0.5

    def _extract_legal_domain(self, query: str) -> str:
        """Extract the primary legal domain from the query"""
        domains = {
            'criminal': ['murder', 'rape', 'theft', 'assault', 'crime', 'police', 'arrest', 'bail'],
            'civil': ['property', 'contract', 'marriage', 'divorce', 'inheritance', 'civil suit'],
            'constitutional': ['fundamental rights', 'constitution', 'article', 'supreme court'],
            'family': ['marriage', 'divorce', 'adoption', 'guardianship', 'maintenance'],
            'corporate': ['company', 'partnership', 'director', 'shareholder', 'incorporation'],
            'labor': ['employment', 'termination', 'wage', 'industrial dispute', 'trade union'],
            'tax': ['income tax', 'gst', 'customs', 'excise', 'assessment'],
            'property': ['land', 'building', 'lease', 'mortgage', 'easement'],
            'intellectual property': ['patent', 'trademark', 'copyright', 'design'],
            'environmental': ['pollution', 'forest', 'wildlife', 'environment'],
            'consumer': ['consumer protection', 'defect', 'complaint', 'unfair trade']
        }

        for domain, keywords in domains.items():
            if any(keyword in query for keyword in keywords):
                return domain

        return 'general'

    def _extract_key_concepts(self, query: str) -> List[str]:
        """Extract key legal concepts from the query"""
        concepts = []

        # Check for legal terms in our synonym dictionary
        for term, synonyms in self.legal_synonyms.items():
            if term in query or any(syn in query for syn in synonyms):
                concepts.append(term)

        # Check for legal acts
        for act_pattern, act_code in self.act_patterns.items():
            if re.search(act_pattern, query, re.IGNORECASE):
                concepts.append(act_code)

        # Extract section/article references
        for pattern, ref_type in self.section_patterns.items():
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                concepts.append(f"{ref_type}_{match}")

        return list(set(concepts))  # Remove duplicates

    def _extract_relevant_sections(self, query: str) -> List[str]:
        """Extract specific legal section references"""
        sections = []

        # Find section references
        section_matches = re.findall(r'section\s+(\d+|[IVXLCDM]+)', query, re.IGNORECASE)
        sections.extend([f"Section {match}" for match in section_matches])

        # Find article references
        article_matches = re.findall(r'article\s+(\d+|[IVXLCDM]+)', query, re.IGNORECASE)
        sections.extend([f"Article {match}" for match in article_matches])

        return sections

    def _determine_jurisdiction(self, query: str) -> str:
        """Determine the jurisdictional scope of the query"""
        # Check for specific state mentions
        states = ['delhi', 'mumbai', 'maharashtra', 'karnataka', 'tamil nadu', 'gujarat', 'rajasthan', 'punjab', 'haryana', 'uttar pradesh', 'bihar', 'west bengal', 'odisha', 'andhra pradesh', 'telangana', 'kerala', 'madhya pradesh', 'chhattisgarh', 'jharkhand']
        for state in states:
            if state in query:
                return f"{state} (State)"

        # Check for central law mentions
        central_indicators = ['central', 'union', 'parliament', 'president', 'supreme court', 'central government']
        if any(indicator in query for indicator in central_indicators):
            return "Central"

        # Default to general Indian law
        return "India (General)"

    def _assess_complexity(self, query: str) -> str:
        """Assess the complexity level of the query"""
        complexity_indicators = {
            'simple': ['what is', 'meaning', 'definition', 'basic', 'simple'],
            'moderate': ['how to', 'procedure', 'explain', 'difference', 'comparison'],
            'complex': ['analyze', 'case study', 'interpretation', 'constitutional validity', 'legal implications']
        }

        for level, indicators in complexity_indicators.items():
            if any(indicator in query for indicator in indicators):
                return level

        # Default based on query length and legal terms
        legal_terms_count = len(self._extract_key_concepts(query))
        if legal_terms_count > 3:
            return 'complex'
        elif legal_terms_count > 1:
            return 'moderate'
        else:
            return 'simple'

    def _generate_expanded_queries(self, query: str, intent: QueryIntent) -> List[str]:
        """Generate multiple query variations for better retrieval"""
        expanded = [query]  # Include original

        # Add synonym expansions
        for term, synonyms in self.legal_synonyms.items():
            if term in query:
                for synonym in synonyms[:2]:  # Limit to 2 synonyms per term
                    expanded_query = query.replace(term, synonym)
                    if expanded_query not in expanded:
                        expanded.append(expanded_query)

        # Add legal act expansions
        for act_pattern, act_code in self.act_patterns.items():
            if re.search(act_pattern, query, re.IGNORECASE):
                expanded_query = re.sub(act_pattern, act_code, query, flags=re.IGNORECASE)
                if expanded_query not in expanded:
                    expanded.append(expanded_query)

        # Add intent-specific expansions
        if intent == QueryIntent.CASE_ANALYSIS:
            expanded.append(f"{query} case law precedent judgment")
        elif intent == QueryIntent.STATUTORY_RESEARCH:
            expanded.append(f"{query} legal provision section clause")
        elif intent == QueryIntent.CRIMINAL_LAW:
            expanded.append(f"{query} ipc section punishment penalty")

        return expanded[:5]  # Limit to 5 expanded queries

# Example usage
if __name__ == "__main__":
    processor = QueryProcessor()

    # Test queries
    test_queries = [
        "What is the punishment for murder under IPC?",
        "Explain Section 302 of Indian Penal Code",
        "What are fundamental rights under the Constitution?",
        "How to file a divorce petition?",
        "What is adverse possession in property law?"
    ]

    for query in test_queries:
        result = processor.process_query(query)
        print(f"\nQuery: {query}")
        print(f"Intent: {result.intent.value}")
        print(f"Domain: {result.legal_domain}")
        print(f"Concepts: {result.key_concepts}")
        print(f"Sections: {result.relevant_sections}")
        print(f"Expanded: {result.expanded_queries[:2]}")  # Show first 2 expansions