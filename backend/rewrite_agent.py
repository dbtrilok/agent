with open("main.py", "r") as f:
    text = f.read()

# 1. Replace ProjectManifest
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

new_manifest = """class ProjectManifest(BaseModel):
    \"\"\"Tracks what the agent has extracted vs what's missing for pure design platforms.\"\"\"
    app_name: Optional[str] = None
    app_type: Optional[str] = None  
    target_audience: Optional[str] = None
    platform: Optional[str] = None  
    
    # Design Direction
    primary_color: Optional[str] = None
    color_palette: Optional[List[str]] = None
    ui_style: Optional[str] = None  
    inspiration_apps: Optional[List[str]] = None
    brand_assets: Optional[str] = None
    
    # UI/UX Specifications
    rtl_support: Optional[str] = None
    design_system: Optional[str] = None
    visual_content: Optional[str] = None
    
    # UX Strategy
    navigation_pattern: Optional[str] = None  
    primary_user_goal: Optional[str] = None  
    
    # Business
    conversion_focus: Optional[bool] = None
    special_logic: Optional[List[str]] = None  
    
    # Extracted from docs
    features: List[str] = Field(default_factory=list)
    screen_inventory: List[str] = Field(default_factory=list)
    user_flows: List[str] = Field(default_factory=list)
    data_structures: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    
    # Status tracking
    @property
    def is_complete(self) -> bool:
        required = [
            self.app_name, self.app_type, self.target_audience,
            self.platform, self.primary_color, self.ui_style,
            self.primary_user_goal, self.rtl_support, self.design_system
        ]
        return all(field is not None for field in required)
    
    @property
    def completion_percentage(self) -> int:
        fields = [
            self.app_name, self.app_type, self.target_audience,
            self.platform, self.primary_color, self.ui_style,
            self.navigation_pattern, self.primary_user_goal,
            self.rtl_support, self.design_system, self.visual_content,
            self.inspiration_apps, self.conversion_focus, self.brand_assets
        ]
        filled = sum(1 for f in fields if f is not None)
        return int((filled / len(fields)) * 100)"""

text = text.replace(old_manifest, new_manifest)

# 2. Update analysis_prompt JSON to ask for the correct stuff
old_analysis_prompt = """        analysis_prompt = f\"\"\"
{system_prompt}

YOUR EXACT TASK:
1. Review the input text.
2. Determine what elements of the standard Application Design are genuinely missing from the text.
3. Extract features, user_flows, and screen requirements.
4. Output ONLY valid JSON containing the extracted data and the specific questions you need to ask the user.

MISSING REQUIREMENT EXAMPLES YOU SHOULD CHECK FOR:
- "What frontend tech stack should be used (e.g. Next.js, Vite, React Native)?" -> field: 'tech_stack'
- "Which UI component library should I specify (e.g. Shadcn/ui, Material UI, Tailwind HTML)?" -> field: 'component_library'
- "What icon set is preferred (e.g. Lucide, Heroicons)?" -> field: 'icon_set'
- "What is the primary brand color in HEX?" -> field: 'primary_color'

OUTPUT JSON FORMAT:
{{
    "extracted_data": {{
        "app_name": "string or null",
        "app_type": "string or null",
        "target_audience": "string or null",
        "platform": "string or null",
        "primary_color": "string or null",
        "ui_style": "string or null",
        "navigation_pattern": "string or null",
        "primary_user_goal": "string or null",
        "tech_stack": "string or null",
        "component_library": "string or null",
        "icon_set": "string or null",
        "features": ["list", "of", "features"],
        "user_flows": ["list", "of", "flows"]
    }},
    "questions_to_ask": [
        {{
            "field": "tech_stack",
            "type": "select",
            "question": "What tech stack should this app be built with?",
            "options": ["Next.js", "React Vite", "React Native", "Flutter", "HTML/JS"],
            "required": true,
            "context": "Stitch AI needs to know the exact frameworks to write code for."
        }}
    ]
}}"""

new_analysis_prompt = """        analysis_prompt = f\"\"\"
{system_prompt}

YOUR EXACT TASK:
1. Review the input text.
2. Determine what elements of the standard Application Design are genuinely missing from the text.
3. Extract features, user_flows, and the SCREEN INVENTORY.
4. Output ONLY valid JSON containing the extracted data and the specific questions you need to ask the user.

MISSING REQUIREMENT CATEGORIES YOU MUST CHECK FOR AND ASK ABOUT:
- Design Direction (Color System/Branding, UI Style, Logo/Brand Assets) -> fields: 'primary_color', 'ui_style', 'brand_assets'
- UX Strategy (Primary UX Goal, RTL (Arabic) Layout Support) -> fields: 'primary_user_goal', 'rtl_support'
- Component Preferences (Design System Approach) -> field: 'design_system'
- Visual Content (Product Imagery style) -> field: 'visual_content'

OUTPUT JSON FORMAT:
{{
    "extracted_data": {{
        "app_name": "string or null",
        "app_type": "string or null",
        "target_audience": "string or null",
        "platform": "string or null",
        "primary_color": "string or null",
        "ui_style": "string or null",
        "primary_user_goal": "string or null",
        "rtl_support": "string or null",
        "design_system": "string or null",
        "visual_content": "string or null",
        "features": ["list", "of", "features"],
        "screen_inventory": ["list", "of", "screens", "to", "build"],
        "user_flows": ["list", "of", "flows"]
    }},
    "questions_to_ask": [
        {{
            "field": "rtl_support",
            "type": "select",
            "question": "Should the layout support Arabic RTL layout, or English LTR?",
            "options": ["Arabic RTL", "English LTR", "Both Variants"],
            "required": true,
            "context": "Necessary for generating the correct mirrored layouts."
        }}
    ]
}}"""
text = text.replace(old_analysis_prompt, new_analysis_prompt)

# 3. OVERHAUL generate_stitch_prompt
old_generate = """        final_prompt = f\"\"\"You are the Ultimate AI GUI Generator Prompt Engineer.
You have successfully collected all project variables. Now you must generate the absolute perfect blueprint instructions for an AI Design Platform (like v0, Lovable, Stitch, or Bolt) to generate the UI code exactly as specified.

APP CONTEXT
App Name: {manifest.app_name}
App Type: {manifest.app_type}
Target Audience: {manifest.target_audience}
Platform Constraint: {manifest.platform}

GEN AI TECH STACK RULES (MANDATORY TO ENFORCE)
- Framework: {manifest.tech_stack or 'Next.js App Router with React'}
- Styling & Components: {manifest.component_library or 'Tailwind CSS'}
- Icons: {manifest.icon_set or 'lucide-react'}
You MUST explicitly tell the AI code generator to ONLY use imports from these specific libraries.

DESIGN SYSTEM
- Primary Theme Color: {manifest.primary_color or '#000000'}
- UI Style Identity: {manifest.ui_style or 'Clean, modern, accessible'}

FEATURES TO BUILD
{features_list}

USER FLOWS & ARCHITECTURE
{flows_list}

YOUR OUTPUT REQUIREMENT:
Generate ONLY the comprehensive prompt text that the user will paste into their AI UI generation platform. 

The prompt you output must include:
1. "System Rules" paragraph explicitly forcing the Tech Stack and Icon libraries.
2. "Data Schemas" section providing concrete, realistic JSON arrays data so the UI generator doesn't use 'Lorem Ipsum'.
3. "Views & Components" paragraph defining the layout structure (Header, Sidebar, Modals, Forms).
4. "Interactive States" - explicit instructions on hover states, empty states, loading skeletons, and validation errors.

Do NOT converse. Start directly with the prompt text.
\"\"\""""

new_generate = """        # Generate dynamic screen inventory string
        screen_list = "\\n".join(f"{i+1}. {s}" for i, s in enumerate(manifest.screen_inventory)) if manifest.screen_inventory else "1. HOME SCREEN\\n2. DASHBOARD"
        
        final_prompt = f\"\"\"You are the Ultimate AI GUI Generator Prompt Engineer.
You have successfully collected all project variables. Now you must generate the absolute perfect blueprint instructions for an AI Design Platform (like Figma Make or Stitch) to generate the UI exactly as specified.

YOUR OUTPUT REQUIREMENT:
Generate ONLY the comprehensive prompt text that the user will paste into their AI UI generation platform.
DO NOT WRITE ANY CODE OR FRAMEWORK INSTRUCTIONS. Focus ENTIRELY on design tokens, layouts, screen inventories, and UX states.

You MUST format your output EXACTLY mirroring the following structural format with ASCII boxes for the screens:

Generate a complete, high-fidelity app UI for "{manifest.app_name}" — {manifest.ui_style}.

🔹 APP OVERVIEW
• App Name: {manifest.app_name}
• Platform: {manifest.platform}
• Target Audience: {manifest.target_audience}
• Style: {manifest.ui_style}
• Primary Brand Color: {manifest.primary_color}

🔹 DESIGN SYSTEM
COLORS:
• Primary: {manifest.primary_color}
[Define Background, Surface, Border, Text Primary, Text Secondary, Success, Error]

TYPOGRAPHY:
[Define Headings, Body, Arabic support if applicable]

COMPONENTS:
[Define Buttons, Cards, Inputs, Icons based on: {manifest.design_system}]

🔹 SCREEN INVENTORY
{screen_list}

🔹 DETAILED SCREEN SPECIFICATIONS
[For EVERY screen in the Screen Inventory, create a detailed ASCII box template exactly like this:]
┌─────────────────────────────────────────────┐
│ 1. [SCREEN NAME]                            │
├─────────────────────────────────────────────┤
│ LAYOUT:                                     │
│ • [Layout instructions]                     │
│                                             │
│ CONTENT:                                    │
│ • [Component instructions]                  │
└─────────────────────────────────────────────┘

🔹 BOTTOM NAVIGATION (If applicable)
[Define tabs and active states]

🔹 GLOBAL COMPONENTS & PATTERNS
[Define LOADING STATES, EMPTY STATES, ERROR STATES, TOASTS]

🔹 RTL (ARABIC) SPECIFICATIONS
[Define RTL rules based on: {manifest.rtl_support}]

🔹 UX ENHANCEMENTS & MICRO-INTERACTIONS
[Define Haptics, Swipe behaviors, Transitions]

Do NOT converse. Output only the final blueprint prompt ready to be copy-pasted into Stitch/Figma.
\"\"\""""

text = text.replace(old_generate, new_generate)

with open("main.py", "w") as f:
    f.write(text)
