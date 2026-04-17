import re

with open("main.py", "r") as f:
    text = f.read()

# Extraction Prompt
old_ext_prompt = """        extraction_prompt = f\"\"\"
Extract specific project details from the document text.
Return ONLY the JSON with extracted values (use null if not found):

{{
    "app_name": "app name or null",
    "target_audience": "target audience or null",
    "platform": "platform or null",
    "primary_color": "primary color or null",
    "ui_style": "ui style or null",
    "navigation_pattern": "navigation pattern or null",
    "inspiration_apps": ["..."]
}}

Document text:
{combined_text[:8000]}
\"\"\""""

new_ext_prompt = """        extraction_prompt = f\"\"\"
Extract specific project details from the document text.
Return ONLY the JSON with extracted values (use null if not found). Do NOT guess.

{{
    "app_name": "app name or null",
    "target_audience": "target audience or null",
    "platform": "platform or null",
    "primary_color": "primary color or null",
    "ui_style": "ui style or null",
    "navigation_pattern": "navigation pattern or null",
    "tech_stack": "mentioned tech stack or null",
    "component_library": "mentioned component library or null",
    "icon_set": "mentioned icon set or null"
}}

Document text:
{combined_text[:8000]}
\"\"\""""

text = text.replace(old_ext_prompt, new_ext_prompt)

# Extraction Manifest mapping
old_ext_map = """            # Update manifest
            state.manifest.app_name = extracted.get("app_name")
            state.manifest.target_audience = extracted.get("target_audience")
            state.manifest.platform = extracted.get("platform")
            state.manifest.primary_color = extracted.get("primary_color")
            state.manifest.ui_style = extracted.get("ui_style")
            state.manifest.navigation_pattern = extracted.get("navigation_pattern")
            state.manifest.inspiration_apps = extracted.get("inspiration_apps", [])"""

new_ext_map = """            # Update manifest
            state.manifest.app_name = extracted.get("app_name")
            state.manifest.target_audience = extracted.get("target_audience")
            state.manifest.platform = extracted.get("platform")
            state.manifest.primary_color = extracted.get("primary_color")
            state.manifest.ui_style = extracted.get("ui_style")
            state.manifest.navigation_pattern = extracted.get("navigation_pattern")
            state.manifest.tech_stack = extracted.get("tech_stack")
            state.manifest.component_library = extracted.get("component_library")
            state.manifest.icon_set = extracted.get("icon_set")"""

text = text.replace(old_ext_map, new_ext_map)


old_final_prompt = """        # Use the user's proven system prompt for final generation
        final_prompt = f\"\"\"You are a Senior Product Designer, UX Architect, Interaction Designer, and AI Prompt Engineer.

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
- Is optimized for production-ready UI generation

---

INPUT DOCUMENT ANALYSIS:

App Type: {manifest.app_type or 'eCommerce'}
Features: {', '.join(manifest.features[:10]) if manifest.features else 'Not specified'}
User Flows: {', '.join(manifest.user_flows[:5]) if manifest.user_flows else 'Not specified'}
Platform: {manifest.platform or 'Mobile'}
Target Audience: {manifest.target_audience or 'Not specified'}

---

EXTRACTED MANIFEST:

App Name: {manifest.app_name or 'Not specified'}
Primary Color: {manifest.primary_color or '#6366F1'}
UI Style: {manifest.ui_style or 'Modern'}
Navigation Pattern: {manifest.navigation_pattern or 'Bottom Navigation'}
Primary User Goal: {manifest.primary_user_goal or 'Fast task completion'}

---

STEP 4: GENERATE FINAL STITCH PROMPT

After receiving all required inputs, generate a CLEAN, STRUCTURED, and Stitch-optimized prompt.

### App Overview
- App name: {manifest.app_name or 'App Name'}
- Platform: {manifest.platform or 'Mobile'}
- UI style: {manifest.ui_style or 'Modern'}
- UX goal: {manifest.primary_user_goal or 'Conversion'}

### Screens (DYNAMIC GENERATION)

Generate screens ONLY based on extracted features:
{features_list}

### Per Screen Include:

For each screen, include:
- Screen name
- Purpose
- Layout (Header, Body, Footer)
- UI components
- Key elements (data/content)
- CTA actions
- Navigation behavior

### UX DESIGN (VERY IMPORTANT):

Define key user flows step-by-step:
{flows_list}

Reduce friction and cognitive load
Optimize for primary business goal
Add smart UX improvements where needed

### PROTOTYPE FLOW:

Define screen-to-screen interaction:
- Navigation paths (e.g., Screen A → Screen B)
- Trigger actions (tap, swipe, CTA click)
- Back navigation behavior
- Modal and bottom sheet interactions

### COMPONENT SYSTEM:

Identify reusable components:
- Cards, buttons, inputs, etc.
- Define variants and usage patterns

### STATES:

- Loading (skeleton UI)
- Empty states
- Error states

### INTERACTIONS:

- Micro-interactions (button feedback, animations)
- Transitions between screens
- Visual feedback for user actions

### DESIGN SYSTEM:

Color palette: Primary {manifest.primary_color or '#6366F1'}, with complementary colors
Typography: Modern sans-serif (Inter/Roboto)
Spacing system: 8pt grid
Border radius: 8-12px for friendly feel
Elevation / shadows: Subtle for cards, stronger for modals

### UX ENHANCEMENTS:

Add best practices based on app type ({manifest.app_type or 'eCommerce'})
Suggest improvements beyond given data
Strengthen weak or missing flows

---

OUTPUT RULES:

Output ONLY the final Stitch prompt
No explanations or analysis
Keep it clean, structured, and readable
Ensure it is directly usable in Stitch

---

FINAL QUALITY CHECK:

✅ All features are included
✅ No unnecessary assumptions
✅ Missing gaps handled intelligently
✅ UX is optimized
✅ Prototype flow is clearly defined
✅ UI is modern and production-ready
✅ Prompt is optimized for Stitch AI
\"\"\""""

new_final_prompt = """        final_prompt = f\"\"\"You are the Ultimate AI GUI Generator Prompt Engineer.
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

text = text.replace(old_final_prompt, new_final_prompt)

with open("main.py", "w") as f:
    f.write(text)
