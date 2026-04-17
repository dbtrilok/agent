import re

with open("main.py", "r") as f:
    text = f.read()

# Update ProjectManifest Model
old_manifest = """class ProjectManifest(BaseModel):
    \"\"\"Tracks what the agent has extracted vs what's missing.\"\"\"
    app_name: Optional[str] = None
    app_type: Optional[str] = None  # eCommerce, SaaS, Fintech, etc.
    target_audience: Optional[str] = None
    platform: Optional[str] = None  # mobile, web, both
    
    # Design Direction
    primary_color: Optional[str] = None
    color_palette: Optional[List[str]] = None
    ui_style: Optional[str] = None  # minimal, premium, playful, etc.
    inspiration_apps: Optional[List[str]] = None
    
    # UX Strategy
    navigation_pattern: Optional[str] = None  # bottom nav, tabs, drawer
    primary_user_goal: Optional[str] = None  # fast checkout, browsing, etc.
    
    # Business
    conversion_focus: Optional[bool] = None
    special_logic: Optional[List[str]] = None  # discounts, subscriptions, etc.
    
    # Extracted from docs
    features: List[str] = Field(default_factory=list)
    user_flows: List[str] = Field(default_factory=list)
    data_structures: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    
    # Status tracking
    @property
    def is_complete(self) -> bool:
        required = [
            self.app_name, self.app_type, self.target_audience,
            self.platform, self.primary_color, self.ui_style,
            self.navigation_pattern, self.primary_user_goal
        ]
        return all(field is not None for field in required)
    
    @property
    def completion_percentage(self) -> int:
        fields = [
            self.app_name, self.app_type, self.target_audience,
            self.platform, self.primary_color, self.ui_style,
            self.navigation_pattern, self.primary_user_goal,
            self.inspiration_apps, self.conversion_focus
        ]
        filled = sum(1 for f in fields if f is not None)
        return int((filled / len(fields)) * 100)"""

new_manifest = """class ProjectManifest(BaseModel):
    \"\"\"Tracks what the agent has extracted vs what's missing.\"\"\"
    app_name: Optional[str] = None
    app_type: Optional[str] = None  # eCommerce, SaaS, Fintech, etc.
    target_audience: Optional[str] = None
    platform: Optional[str] = None  # mobile, web, both
    
    # Design Direction
    primary_color: Optional[str] = None
    color_palette: Optional[List[str]] = None
    ui_style: Optional[str] = None  # minimal, premium, playful, etc.
    inspiration_apps: Optional[List[str]] = None
    
    # Gen UI Platform Requirements
    tech_stack: Optional[str] = None
    component_library: Optional[str] = None
    icon_set: Optional[str] = None
    responsive_rules: Optional[str] = None
    
    # UX Strategy
    navigation_pattern: Optional[str] = None  # bottom nav, tabs, drawer
    primary_user_goal: Optional[str] = None  # fast checkout, browsing, etc.
    
    # Business
    conversion_focus: Optional[bool] = None
    special_logic: Optional[List[str]] = None  # discounts, subscriptions, etc.
    
    # Extracted from docs
    features: List[str] = Field(default_factory=list)
    user_flows: List[str] = Field(default_factory=list)
    data_structures: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    
    # Status tracking
    @property
    def is_complete(self) -> bool:
        required = [
            self.app_name, self.app_type, self.target_audience,
            self.platform, self.primary_color, self.ui_style,
            self.navigation_pattern, self.primary_user_goal,
            self.tech_stack, self.component_library, self.icon_set
        ]
        return all(field is not None for field in required)
    
    @property
    def completion_percentage(self) -> int:
        fields = [
            self.app_name, self.app_type, self.target_audience,
            self.platform, self.primary_color, self.ui_style,
            self.navigation_pattern, self.primary_user_goal,
            self.tech_stack, self.component_library, self.icon_set,
            self.inspiration_apps, self.conversion_focus, self.responsive_rules
        ]
        filled = sum(1 for f in fields if f is not None)
        return int((filled / len(fields)) * 100)"""

text = text.replace(old_manifest, new_manifest)

# System Prompt rewrite
old_system_prompt = """        system_prompt = \"\"\"You are a Senior Product Designer, UX Architect, Interaction Designer, and AI Prompt Engineer.

Your task is to intelligently convert provided product documents into a PERFECT Stitch AI prompt for generating a complete mobile app UI with strong UX and prototype-ready flow.

CORE BEHAVIOR (STRICTLY FOLLOW):
1. Analyze the input documents deeply
2. Extract all relevant product information
3. Identify missing, unclear, or assumed details
4. Ask structured, minimal, high-impact questions
5. WAIT for user response
6. Then generate the final Stitch prompt

DO NOT generate the final prompt immediately
ALWAYS ask questions if ANY critical detail is missing or ambiguous
DO NOT assume important product decisions without confirmation

GOAL:
Create a HIGH-QUALITY Stitch prompt that:
- Covers ALL features from the input
- Dynamically generates UI screens (no hardcoding)
- Includes strong UX decisions and improvements
- Defines complete prototype flow (screen-to-screen interactions)
- Is optimized for production-ready UI generation\"\"\"

        analysis_prompt = f\"\"\"
{system_prompt}

STEP 1: ANALYZE & EXTRACT

Analyze the following documents deeply and extract:

- App type (eCommerce, SaaS, Fintech, etc.)
- Features and modules
- User flows (explicit or implied)
- Input fields and data structures
- Acceptance criteria
- Business intent (conversion, engagement, retention)

DOCUMENTS:
{combined_text[:15000]}

STEP 2: DETECT MISSING CRITICAL DETAILS

Check and validate if the following are clearly defined:

Product Basics:
- App name
- Target audience
- Platform (mobile/web)

Design Direction:
- Color system / branding
- UI style (minimal, premium, playful, etc.)
- Inspiration or reference apps

UX Strategy:
- Navigation pattern (bottom nav, tabs, drawer, etc.)
- Primary user goal (fast checkout, browsing, engagement, etc.)

Business Intent:
- Conversion focus or engagement focus
- Special logic (discounts, subscriptions, offers, etc.)

STEP 3: ASK QUESTIONS (MANDATORY)

If ANY critical detail is missing or unclear:
- Ask only necessary questions (avoid overload)
- Group related questions logically
- Keep questions precise and decision-focused

Return a JSON response with:
{{
    "app_type": "...",
    "features": ["..."],
    "user_flows": ["..."],
    "data_structures": ["..."],
    "business_intent": "...",
    "missing_critical_details": {{
        "product_basics": ["..."],
        "design_direction": ["..."],
        "ux_strategy": ["..."],
        "business_intent": ["..."]
    }},
    "questions_to_ask": [
        {{
            "field": "app_name",
            "question": "What is the app name?",
            "context": "This will be used throughout the UI"
        }}
    ]
}}

If ALL critical details are present, set "questions_to_ask" to empty array [].
\"\"\""""


new_system_prompt = """        system_prompt = \"\"\"You are a Senior Product Designer and AI UI Agent Prompt Engineer.

Your task is to intelligently convert provided product documents into a PERFECT prompt for an AI GUI Generator (like Stitch, v0, Lovable, or Bolt) to generate a complete, production-ready app UI.

ZERO-HALLUCINATION RULE (STRICTLY FOLLOW):
You are strictly forbidden from guessing or inventing ANY missing details. If the tech stack, app name, color palette, or routing requirements are not explicitly clear in the provided documents, YOU MUST NOT IMAGINE THEM. Instead, YOU MUST ask the user.

CORE BEHAVIOR:
1. Analyze the input documents.
2. Extract all relevant existing details.
3. Identify missing GUI platform generation requirements.
4. Ask precise questions to collect the missing requirements.
5. You MUST WAIT for the user to answer those questions.

GOAL: Build an unbreakable blueprint architecture prompt that platforms can map perfectly into working code components.\"\"\"

        analysis_prompt = f\"\"\"
{system_prompt}

STEP 1: ANALYZE & EXTRACT

Analyze the following documents deeply and extract:
- App type (eCommerce, SaaS, Fintech, etc.)
- Features and modules
- User flows (explicit or implied)
- Input fields and data JSON structures

DOCUMENTS:
{combined_text[:15000]}

STEP 2: DETECT MISSING CRITICAL DETAILS

Check and validate if the following are clearly defined in the text. If NOT, mark them to be questioned.

Tech & AI Gen Rules:
- tech_stack (React vs Next.js vs HTML)
- component_library (Tailwind, Radix, shadcn/ui)
- icon_set (lucide-react, heroicons)

App Fundamentals:
- App Name
- Target Audience & Platform

Design System:
- Primary Brand Color
- UI Style (minimal, glassmorphism, corporate)

STEP 3: ASK QUESTIONS FOR ANY MISSING ITEMS

Return a JSON response EXACTLY matching:
{{
    "app_type": "...",
    "features": ["..."],
    "user_flows": ["..."],
    "questions_to_ask": [
        {{
            "field": "tech_stack",
            "type": "select",
            "options": ["Next.js (App Router)", "React (Vite)", "Vanilla HTML/JS"],
            "required": true,
            "question": "What tech stack should the UI generator use?",
            "context": "AI platforms need to know the framework."
        }},
        {{
            "field": "component_library",
            "type": "select",
            "options": ["Tailwind + shadcn/ui", "Material UI", "Tailwind + Headless UI"],
            "required": true,
            "question": "Which component library do you prefer?",
            "context": "Dictates how buttons and modals are styled."
        }},
        {{
            "field": "icon_set",
            "type": "select",
            "options": ["lucide-react", "heroicons", "radix-icons"],
            "required": true,
            "question": "What icon set should the AI import from?",
            "context": "Prevents broken SVG hallucination."
        }},
        {{
            "field": "app_name",
            "type": "text",
            "required": true,
            "question": "What is the App Name?"
        }},
        {{
            "field": "primary_color",
            "type": "color",
            "required": true,
            "question": "What is the primary brand color?"
        }}
    ]
}}

If an item is explicitly written in the document, DO NOT add a question for it.
\"\"\""""

text = text.replace(old_system_prompt, new_system_prompt)

with open("main.py", "w") as f:
    f.write(text)
