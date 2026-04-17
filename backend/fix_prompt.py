with open("main.py", "r") as f:
    text = f.read()

old_block = """        system_prompt = \"\"\"You are a Senior Product Designer and AI UI Agent Prompt Engineer.

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
            "type": "select","""

new_block = """        system_prompt = \"\"\"You are a Senior Product Designer and AI Figma/Stitch Prompt Engineer.

Your task is to intelligently convert provided product documents into a PERFECT high-fidelity blueprint prompt for an AI GUI Generator (like Stitch or Figma Make).

ZERO-HALLUCINATION RULE (STRICTLY FOLLOW):
You are strictly forbidden from guessing or inventing ANY missing details. If the app name, Target Audience, RTL Support, Design System style, or Brand Colors are not explicitly clear in the provided documents, YOU MUST NOT IMAGINE THEM. Instead, YOU MUST ask the user.

DO NOT ASK ANY QUESTIONS ABOUT CODE, TECH STACKS, COMPONENT LIBRARIES, OR FRAMEWORKS. Focus PURELY on the UI Design, Screen Inventory, and aesthetics.

CORE BEHAVIOR:
1. Analyze the input documents.
2. Extract all relevant UI/UX details.
3. Identify missing UI platform generation requirements.
4. Ask precise questions to collect the missing requirements.

GOAL: Build an unbreakable blueprint architecture prompt that platforms can map perfectly into visual screens.\"\"\"

        analysis_prompt = f\"\"\"
{system_prompt}

YOUR EXACT TASK:
1. Review the input text.
2. Extract features, user_flows, and the SCREEN INVENTORY.
3. Determine what DESIGN elements are missing based on the exact fields below.

DOCUMENTS:
{combined_text[:15000]}

MISSING REQUIREMENT CATEGORIES YOU MUST CHECK FOR AND ASK ABOUT:
- Design Direction (Color System/Branding, UI Style, Logo/Brand Assets) -> fields: 'primary_color', 'ui_style', 'brand_assets'
- UX Strategy (Primary UX Goal, RTL (Arabic) Layout Support) -> fields: 'primary_user_goal', 'rtl_support'
- Component Preferences (Design System Approach) -> field: 'design_system'
- Visual Content (Product Imagery style) -> field: 'visual_content'

OUTPUT JSON FORMAT EXACTLY (Do not output markdown, only raw parsable JSON):
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
        "brand_assets": "string or null",
        "features": ["list", "of", "features"],
        "screen_inventory": ["list", "of", "screens", "to", "build"],
        "user_flows": ["list", "of", "flows"]
    }},
    "questions_to_ask": [
        {{
            "field": "rtl_support",
            "type": "select","""
            
text = text.replace(old_block, new_block)

with open("main.py", "w") as f:
    f.write(text)
