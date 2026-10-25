"""
Multimodal AI Engine for Construction Safety and Structural Diagnostics
Integrates Google Gemini (via google.genai or google.generativeai)
with high-fidelity Demonstration Fallback for 1-click cloud zero-setup testing.
"""

import os
import json
import re
import io
import warnings
from typing import Dict, Any, Optional, Tuple, List
from PIL import Image

warnings.filterwarnings("ignore", category=FutureWarning)

# Check for Gemini availability
HAVE_GENAI = False
try:
    from google import genai
    from google.genai import types
    HAVE_GENAI = True
except ImportError:
    pass

HAVE_GOOGLE_GENERATIVEAI = False
try:
    import google.generativeai as legacy_genai
    HAVE_GOOGLE_GENERATIVEAI = True
except ImportError:
    pass


PPE_SYSTEM_PROMPT = """You are a Principal Construction Safety Auditor certified in OSHA 1926 standards and Indian Standard IS 456 / IS 3786 / IS 2925.
Analyze the provided construction site photo thoroughly for PPE compliance and workplace hazards.

Return ONLY a valid JSON object strictly adhering to this JSON schema (no markdown fences, no explanatory text outside JSON):
{
  "safety_score": 58,
  "overall_status": "NON-COMPLIANT - IMMEDIATE ACTION REQUIRED",
  "worker_count_detected": 2,
  "ppe_detection": {
    "safety_helmets": {
      "detected": 1,
      "total_workers": 2,
      "compliance_pct": 50,
      "standard": "OSHA 1926.100 / IS 2925:1984",
      "status": "VIOLATION"
    },
    "high_visibility_vests": {
      "detected": 1,
      "total_workers": 2,
      "compliance_pct": 50,
      "standard": "OSHA 1926.201 / IS 15809:2017",
      "status": "VIOLATION"
    },
    "safety_footwear": {
      "detected": 1,
      "total_workers": 2,
      "compliance_pct": 50,
      "standard": "OSHA 1926.96 / IS 15298:2016",
      "status": "WARNING"
    },
    "fall_arrest_harnesses": {
      "detected": 0,
      "total_workers": 1,
      "compliance_pct": 0,
      "standard": "OSHA 1926.502 / IS 3521:1999",
      "status": "CRITICAL VIOLATION"
    },
    "eye_face_protection": {
      "detected": 1,
      "total_workers": 2,
      "compliance_pct": 50,
      "standard": "OSHA 1926.102",
      "status": "WARNING"
    }
  },
  "identified_hazards": [
    {
      "hazard": "Worker on elevated scaffold platform without personal fall arrest system (safety harness)",
      "severity": "Critical",
      "location": "Upper scaffolding staging tier",
      "osha_violation": "OSHA 1926.501(b)(1) Fall Protection Unprotected Sides & Edges",
      "indian_standard": "IS 3521:1999 Industrial Safety Harnesses",
      "corrective_remedy": "Issue Stop-Work notice immediately; attach dual-lanyard shock-absorbing harness to independent static lifeline."
    },
    {
      "hazard": "Worker operating in active perimeter zone without hard hat",
      "severity": "High",
      "location": "Scaffold working platform",
      "osha_violation": "OSHA 1926.100 Head Protection",
      "indian_standard": "IS 2925 Industrial Safety Helmets",
      "corrective_remedy": "Issue Type 1 Class E industrial helmet; enforce mandatory zero-tolerance hard hat policy."
    }
  ],
  "executive_summary": "Audited site image reveals acute fall and head impact risks. Immediate administrative intervention required."
}
"""

CRACK_SYSTEM_PROMPT = """You are a Senior Structural Forensic Engineer and Concrete Technologist specializing in IS 456:2000, ACI 224R, and BS 8110 standards.
Analyze the provided concrete/masonry wall image to diagnose structural cracking and material degradation.

Return ONLY a valid JSON object strictly adhering to this JSON schema (no markdown fences, no explanatory text outside JSON):
{
  "defect_type": "Structural Shear Crack",
  "confidence_score": 0.94,
  "severity_level": "Critical",
  "urgency_rating": "Immediate Shoring & Structural Remediation (within 24-48 hours)",
  "estimated_crack_width_mm": "3.5 - 6.0 mm",
  "crack_depth_estimate": "Through-member depth (~180mm), penetrating beyond clear cover into rebar shear zone",
  "orientation_propagation": "Diagonal 45-degree angle propagating from beam-column junction toward mid-span",
  "root_causes": [
    "Excessive principal tensile stress exceeding concrete tensile shear capacity (v_c < v_u per IS 456 Cl. 40)",
    "Inadequate transverse shear stirrup spacing or rebar yield during dynamic seismic/overloading",
    "Differential support settlement inducing unanticipated secondary bending shear"
  ],
  "engineering_repair_protocol": [
    "Stage 1: Install emergency temporary steel props/shoring to relieve beam gravity load.",
    "Stage 2: V-groove crack surface, install mechanical copper/plastic injection ports at 150mm intervals.",
    "Stage 3: Seal crack surface perimeter with thixotropic epoxy gel mastic (curing 24h).",
    "Stage 4: Low-pressure positive displacement injection of high-modulus, ultra-low viscosity structural epoxy resin (ASTM C881).",
    "Stage 5: Surface grinding and application of bidirectional Carbon Fiber Reinforced Polymer (CFRP) fabric wraps for shear strengthening."
  ],
  "estimated_repair_cost_inr": "₹65,000 - ₹1,20,000 (per linear span)",
  "is_456_citation": "IS 456:2000 Clause 40 (Design for Shear) & Clause 35.3.2 (Serviceability Limit State of Cracking)"
}
"""

def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Cleanly parse JSON from raw LLM output even if surrounded by markdown fences."""
    if not text:
        return None
    # Strip backticks
    cleaned = text.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if match:
        cleaned = match.group(1).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        # Try finding outermost { ... }
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(cleaned[start:end+1])
            except json.JSONDecodeError:
                return None
    return None

def analyze_ppe_image(
    image: Image.Image,
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash",
    force_demo: bool = False
) -> Dict[str, Any]:
    """
    Performs multimodal audit of construction site image for PPE safety.
    Gracefully falls back to high-fidelity demo engine if no API key or if API call fails.
    """
    if force_demo or not api_key:
        return get_demo_ppe_analysis()
        
    try:
        # Attempt Gemini 2.5/1.5 API call
        if HAVE_GENAI:
            client = genai.Client(api_key=api_key)
            # Convert image to bytes
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format="JPEG")
            img_bytes = img_byte_arr.getvalue()
            
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
                    PPE_SYSTEM_PROMPT
                ]
            )
            parsed = extract_json_from_text(response.text)
            if parsed:
                parsed["_source"] = f"Live Gemini Multimodal ({model_name})"
                return parsed
        elif HAVE_GOOGLE_GENERATIVEAI:
            legacy_genai.configure(api_key=api_key)
            model = legacy_genai.GenerativeModel(model_name)
            response = model.generate_content([PPE_SYSTEM_PROMPT, image])
            parsed = extract_json_from_text(response.text)
            if parsed:
                parsed["_source"] = f"Live Gemini Multimodal ({model_name})"
                return parsed
    except Exception as e:
        demo = get_demo_ppe_analysis()
        demo["_source"] = f"Demonstration Mode (Gemini API Notice: {str(e)[:90]}...)"
        return demo

    # If parsing failed, fallback gracefully
    demo = get_demo_ppe_analysis()
    demo["_source"] = "Demonstration Mode (Parsing fallback)"
    return demo

def analyze_crack_image(
    image: Image.Image,
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash",
    force_demo: bool = False
) -> Dict[str, Any]:
    """
    Performs multimodal concrete crack diagnostics.
    Gracefully falls back to high-fidelity demo engine if no API key or if API call fails.
    """
    if force_demo or not api_key:
        return get_demo_crack_analysis()
        
    try:
        if HAVE_GENAI:
            client = genai.Client(api_key=api_key)
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format="JPEG")
            img_bytes = img_byte_arr.getvalue()
            
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    types.Part.from_bytes(data=img_bytes, mime_type="image/jpeg"),
                    CRACK_SYSTEM_PROMPT
                ]
            )
            parsed = extract_json_from_text(response.text)
            if parsed:
                parsed["_source"] = f"Live Gemini Multimodal ({model_name})"
                return parsed
        elif HAVE_GOOGLE_GENERATIVEAI:
            legacy_genai.configure(api_key=api_key)
            model = legacy_genai.GenerativeModel(model_name)
            response = model.generate_content([CRACK_SYSTEM_PROMPT, image])
            parsed = extract_json_from_text(response.text)
            if parsed:
                parsed["_source"] = f"Live Gemini Multimodal ({model_name})"
                return parsed
    except Exception as e:
        demo = get_demo_crack_analysis()
        demo["_source"] = f"Demonstration Mode (Gemini API Notice: {str(e)[:90]}...)"
        return demo

    demo = get_demo_crack_analysis()
    demo["_source"] = "Demonstration Mode (Parsing fallback)"
    return demo

def generate_chat_response(
    messages: List[Dict[str, str]],
    api_key: Optional[str] = None,
    model_name: str = "gemini-2.5-flash",
    force_demo: bool = False
) -> str:
    """
    Multi-turn conversational assistant for construction site engineering.
    """
    system_instruction = (
        "You are 'SiteIntel AI', an expert Senior Construction Project Manager and Chartered Civil Structural Engineer. "
        "You have deep authority in IS 456:2000, IS 13920, OSHA 1926, CPWD Specifications, FIDIC Contract Clauses, "
        "concrete mix design (M25, M30, M40), curing regimes, and real estate valuation in India. "
        "Provide professional, structured, actionable engineering advice with references to standard clauses."
    )
    
    if force_demo or not api_key:
        return get_demo_chat_response(messages[-1]["content"])
        
    try:
        if HAVE_GENAI:
            client = genai.Client(api_key=api_key)
            # Format history
            formatted_contents = []
            for msg in messages:
                role = "user" if msg["role"] == "user" else "model"
                formatted_contents.append(f"{role.upper()}: {msg['content']}")
            prompt_str = system_instruction + "\n\n" + "\n".join(formatted_contents) + "\nASSISTANT:"
            response = client.models.generate_content(
                model=model_name,
                contents=prompt_str
            )
            return response.text
        elif HAVE_GOOGLE_GENERATIVEAI:
            legacy_genai.configure(api_key=api_key)
            model = legacy_genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system_instruction
            )
            # Format chat
            chat = model.start_chat(history=[])
            for msg in messages[:-1]:
                if msg["role"] == "user":
                    chat.send_message(msg["content"])
            last_resp = chat.send_message(messages[-1]["content"])
            return last_resp.text
    except Exception as e:
        return f"[Live Gemini Notice: Switched to Demonstration Mode ({str(e)[:60]}...)]\n\n" + get_demo_chat_response(messages[-1]["content"])

    return get_demo_chat_response(messages[-1]["content"])


# ==========================================
# HIGH-FIDELITY DEMONSTRATION FALLBACK DATA
# ==========================================

def get_demo_ppe_analysis() -> Dict[str, Any]:
    return {
        "safety_score": 62,
        "overall_status": "NON-COMPLIANT - IMMEDIATE ACTION REQUIRED",
        "worker_count_detected": 2,
        "ppe_detection": {
            "safety_helmets": {
                "detected": 1,
                "total_workers": 2,
                "compliance_pct": 50,
                "standard": "OSHA 1926.100 / IS 2925:1984",
                "status": "VIOLATION"
            },
            "high_visibility_vests": {
                "detected": 1,
                "total_workers": 2,
                "compliance_pct": 50,
                "standard": "OSHA 1926.201 / IS 15809:2017",
                "status": "VIOLATION"
            },
            "safety_footwear": {
                "detected": 1,
                "total_workers": 2,
                "compliance_pct": 50,
                "standard": "OSHA 1926.96 / IS 15298:2016",
                "status": "WARNING"
            },
            "fall_arrest_harnesses": {
                "detected": 0,
                "total_workers": 1,
                "compliance_pct": 0,
                "standard": "OSHA 1926.502 / IS 3521:1999",
                "status": "CRITICAL VIOLATION"
            },
            "eye_face_protection": {
                "detected": 1,
                "total_workers": 2,
                "compliance_pct": 50,
                "standard": "OSHA 1926.102",
                "status": "WARNING"
            }
        },
        "identified_hazards": [
            {
                "hazard": "Worker elevated on scaffolding tier (~3.2m above grade) lacking mandatory fall arrest harness & lanyard tie-off",
                "severity": "Critical",
                "location": "West Elevation Scaffolding Tower (Bay 2)",
                "osha_violation": "OSHA 1926.501(b)(1) - Unprotected sides and edges > 6ft",
                "indian_standard": "IS 3521:1999 & IS 2750 - Steel Scaffold Fall Arrest",
                "corrective_remedy": "Issue immediate Stop-Work directive. Supply Class-A full-body harness, anchor to overhead certified static lifeline before resuming work."
            },
            {
                "hazard": "Worker in active overhead crane swing radius without EN 397 / IS 2925 approved safety helmet",
                "severity": "High",
                "location": "Upper staging platform",
                "osha_violation": "OSHA 1926.100 - Head Protection against falling objects",
                "indian_standard": "IS 2925:1984 - Industrial Safety Helmets",
                "corrective_remedy": "Issue immediate safety helmet with chin strap. Escort off-site if non-compliance repeats."
            },
            {
                "hazard": "Absence of retro-reflective high-visibility vest in proximity to material staging area",
                "severity": "Medium",
                "location": "Scaffold working platform",
                "osha_violation": "OSHA 1926.201 - Signaling and High-Visibility Apparel",
                "indian_standard": "IS 15809:2017 - High-Visibility Warning Clothes",
                "corrective_remedy": "Distribute Class-2 fluorescent yellow-green vest with 360-degree reflective bands."
            },
            {
                "hazard": "Scaffold working deck lacking mid-rail and toe-board to prevent material dislodgement",
                "severity": "High",
                "location": "Scaffold working platform outer perimeter",
                "osha_violation": "OSHA 1926.451(g)(1) - Guardrail Systems & Toe-boards",
                "indian_standard": "IS 2750:1964 - Steel Scaffold Safety Standards",
                "corrective_remedy": "Fit 150mm kickboard/toe-board and intermediate horizontal guardrail at 530mm height."
            }
        ],
        "executive_summary": "Audit detected two active workers with an unacceptable 50% PPE compliance deficit. Most critically, an elevated worker is exposed to deadly fall hazards without safety harness arrest gear. Stop-Work protocol triggered for scaffold zone.",
        "_source": "Demonstration Fallback Engine (Zero API Key Mode)"
    }

def get_demo_crack_analysis() -> Dict[str, Any]:
    return {
        "defect_type": "Structural Shear Crack",
        "confidence_score": 0.95,
        "severity_level": "Critical",
        "urgency_rating": "Immediate Shoring & Structural Remediation (within 24-48 hours)",
        "estimated_crack_width_mm": "4.2 - 6.5 mm (Severe)",
        "crack_depth_estimate": "Full-depth shear fracture (~200mm), penetrating beyond tension reinforcement into compression zone",
        "orientation_propagation": "Diagonal 45-degree angle inclined from support column capital toward mid-span tensile zone",
        "root_causes": [
            "Diagonal tension failure: shear stress (τ_v) heavily exceeds maximum permissible shear stress (τ_cmax) defined in IS 456 Cl. 40.2.3.",
            "Sub-standard or displaced transverse shear stirrups (links) during concrete vibration.",
            "Differential settlement of the exterior foundation footing creating unanticipated support shear moments."
        ],
        "engineering_repair_protocol": [
            "Step 1: Emergency Structural Shoring - Immediately place heavy-duty Acrow props or structural steel towers to relieve gravitational loads on the affected bay.",
            "Step 2: Crack Preparation - Mechanically V-groove the crack profile to 20mm width x 20mm depth using an electric angle grinder with diamond disc.",
            "Step 3: Port Installation - Fix mechanical brass/nylon injection ports at intervals equal to member thickness (~150-200mm apart) along the fracture path.",
            "Step 4: Perimeter Sealing - Apply two-component thixotropic epoxy paste (ASTM C881 Type I/IV) over the crack face to contain injection pressure.",
            "Step 5: Pressure Grouting - Inject low-viscosity, solvent-free epoxy resin (viscosity < 250 mPa·s) starting from lowest port until clean resin discharges from the adjacent upper port.",
            "Step 6: Composite Strengthening - Bond two plies of unidirectional high-strength Carbon Fiber Reinforced Polymer (CFRP) fabric (300 gsm) impregnated with structural epoxy saturant to restore shear capacity."
        ],
        "estimated_repair_cost_inr": "₹75,000 - ₹1,40,000 (per linear span)",
        "is_456_citation": "IS 456:2000 Clause 40 (Design for Shear) & Clause 35.3.2 (Serviceability Limit State of Cracking)",
        "_source": "Demonstration Fallback Engine (Zero API Key Mode)"
    }

def get_demo_chat_response(query: str) -> str:
    q = query.lower()
    if "is 456" in q or "cover" in q or "concrete cover" in q:
        return (
            "### IS 456:2000 Concrete Cover Guidelines (Table 16 & Cl. 26.4)\n\n"
            "Under Indian Standard **IS 456:2000**, nominal concrete cover to meet durability requirements depends strictly on environmental exposure:\n\n"
            "| Exposure Condition | Minimum Nominal Cover | Structural Recommendation |\n"
            "| :--- | :--- | :--- |\n"
            "| **Mild** (Interior, sheltered) | **20 mm** | Slabs & internal columns |\n"
            "| **Moderate** (Sheltered from rain, underground) | **30 mm** | Footings in normal soil |\n"
            "| **Severe** (Direct rain, alternating wet/dry) | **45 mm** | Coastal structures, exterior frames |\n"
            "| **Very Severe** (Sea spray, corrosive fumes) | **50 mm** | Marine jetties, chemical plants |\n"
            "| **Extreme** (Tidal zone, abrasive contact) | **75 mm** | Submerged marine members |\n\n"
            "**Key Provision (Cl. 26.4.2)**: For longitudinal reinforcing bars in columns, cover shall never be less than 40 mm, nor less than the bar diameter. "
            "For footings, minimum cover must be **50 mm**."
        )
    elif "fall protection" in q or "osha" in q or "harness" in q:
        return (
            "### OSHA 1926.502 Fall Protection & Harness Mandates\n\n"
            "Under **OSHA Subpart M (1926.500 - 1926.503)** and **IS 3521:1999**:\n\n"
            "1. **Trigger Height**: Fall protection is mandatory for any employee working on a walking/working surface with an unprotected side or edge **6 feet (1.8 meters)** or more above a lower level.\n"
            "2. **Personal Fall Arrest System (PFAS)**:\n"
            "   - **Anchorages**: Must support at least 5,000 lbs (22.2 kN) per worker attached, or engineered with a safety factor of 2.0.\n"
            "   - **Body Wear**: Full-body harness only (body belts are strictly prohibited for fall arrest since 1998).\n"
            "   - **Maximum Deceleration Distance**: 3.5 feet (1.07 m).\n"
            "   - **Maximum Arrest Force**: 1,800 lbs (8 kN) when using full-body harness.\n"
            "3. **Dual-Lanyard 100% Tie-Off**: Workers traversing scaffolding or structural steel must maintain continuous anchorage via double-leg shock-absorbing lanyards."
        )
    elif "slump" in q or "m25" in q or "m30" in q or "curing" in q or "hot weather" in q:
        return (
            "### Concrete Technology: Temperature, Slump & IS 7861 Curing\n\n"
            "High ambient temperatures (>38°C) induce rapid chemical hydration kinetics in **M25 / M30 / M40 grade concrete**:\n\n"
            "1. **Slump Loss & Workability**:\n"
            "   - Slump loss increases by approximately 20-30 mm for every 10°C rise above 25°C due to accelerated hydration.\n"
            "   - *Remedy*: Introduce polycarboxylate ether (PCE) based superplasticizers with set-retarding admixtures (IS 9103) rather than adding unauthorized site water.\n"
            "2. **Water-Cement Ratio (w/c)**:\n"
            "   - Adding field water to restore slump degrades compressive strength exponentially (water-cement law) and leads to surface dusting and shrinkage cracking.\n"
            "3. **Curing Specifications (IS 456 Cl. 13.5)**:\n"
            "   - Minimum wet curing period is **7 days** for Ordinary Portland Cement (OPC), and **10-14 days** for blended cements (PPC, GGBS) or when subjected to dry/hot conditions."
        )
    elif "stop work" in q or "notice" in q:
        return (
            "### Formal Stop-Work Notice: Non-Compliant PPE / Safety Violation\n\n"
            "```text\n"
            "=========================================================================\n"
            "                         FORMAL STOP-WORK DIRECTIVE                      \n"
            "               PROJECT: Multimodal Construction Intelligence            \n"
            "               ISSUING AUTHORITY: Principal Safety & Quality Auditor    \n"
            "=========================================================================\n"
            "DATE / TIME: October 25, 2026 | 12:00 IST\n"
            "LOCATION: Sector Zone 4B (Elevation Scaffolding Tower, Bay 2)\n"
            "CONTRACTOR: Structural Framework & Formwork Works Division\n\n"
            "VIOLATION SUMMARY:\n"
            "- Immediate cessation of all work at elevation (>3.0m) due to lack of\n"
            "  Personal Fall Arrest Systems (IS 3521 / OSHA 1926.502).\n"
            "- Multiple personnel operating without protective hard hats (IS 2925).\n\n"
            "REQUIRED CORRECTIVE ACTION:\n"
            "1. Evacuate all personnel from scaffolding staging deck immediately.\n"
            "2. Install tested independent life-lines with 22.2 kN rated anchor points.\n"
            "3. Issue calibrated harnesses and helmets to all workers.\n"
            "4. Obtain written re-authorization from the Resident Safety Engineer.\n\n"
            "AUTHORIZED SIGNATORY: Senior HSE Superintendent\n"
            "=========================================================================\n"
            "```"
        )
    else:
        return (
            f"### Professional Site Engineering Analysis\n\n"
            f"Regarding your query on **'{query}'**:\n\n"
            f"Under standard construction management practice governed by **IS 456:2000** and **OSHA safety guidelines**:\n"
            f"1. **Technical Protocol**: Prioritize structural stability and life safety verification before executing specialized site works.\n"
            f"2. **Quality Assurance**: Maintain daily testing logs (slump tests, cube compressive strength at 7 & 28 days, weld ultrasonic testing).\n"
            f"3. **Cost & Risk Control**: Verify material consumption against structural BOQ allowances to maintain budget adherence within the calculated INR valuation parameters.\n\n"
            f"Feel free to ask for specific clause interpretations from IS 456, IS 13920, or OSHA 1926, or cost impact calculations!"
        )
