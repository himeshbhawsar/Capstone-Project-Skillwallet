"""
Weather-Aware Site Advisory Engine (Epic 5)
Provides actionable real-time safety protocols, crane operations limits,
concrete curing specifications under IS 456 / IS 7861, and supervisor checklists.
"""

from typing import Dict, Any, List

WEATHER_PROFILES: Dict[str, Dict[str, Any]] = {
    "High Wind (>45 km/h / Gale Warning)": {
        "status_level": "CRITICAL OPERATIONAL RESTRICTION",
        "badge_color": "#EF4444",
        "bg_color": "rgba(239, 68, 68, 0.12)",
        "wind_speed_range": "42 - 65 km/h",
        "crane_status": "MANDATORY STOP - JIB SLEWING FREED",
        "crane_details": (
            "Immediately halt all tower crane, mobile crawler, and boom lift operations. "
            "Release slew brake on tower cranes to allow 360° wind-vane mode (free slewing) to prevent structural tower overturning."
        ),
        "height_work_status": "SUSPENDED ABOVE 2 METERS",
        "height_work_details": (
            "Prohibit all exterior scaffolding, suspended gondola / cradle access, and roof sheeting works. "
            "Ensure loose shuttering ply, rebar ties, and metal decks are securely anchored or brought down to ground level."
        ),
        "concrete_protocol": (
            "Avoid high-rise concrete pumping; wind accelerations cause excessive moisture evaporation on freshly placed slabs, "
            "triggering plastic shrinkage cracking. Apply aliphatic alcohol evaporation retardant or moist curing blankets immediately."
        ),
        "electrical_safety": (
            "Inspect temporary power feeder poles, secure swaying overhead cable drops, and shut down non-essential exterior mast lights."
        ),
        "checklist": [
            "Release slew brakes on all tower cranes (enable wind-vane mode).",
            "Lower and secure all suspended cradles and man-baskets to ground.",
            "Fasten down loose corrugated sheets, GI pipes, and perimeter debris nets.",
            "Verify perimeter edge guardrails and safety nets comply with OSHA 1926.502.",
            "Issue site-wide radio broadcast instructing workers to clear high-rise open decks."
        ]
    },
    "Heavy Rain / Monsoon (>50 mm/day)": {
        "status_level": "HIGH WATER INGRESS & ELECTRICAL HAZARD",
        "badge_color": "#3B82F6",
        "bg_color": "rgba(59, 130, 246, 0.12)",
        "wind_speed_range": "15 - 35 km/h (Moderate gusting)",
        "crane_status": "RESTRICTED (OUTRIGGER INTEGRITY CHECK REQUIRED)",
        "crane_details": (
            "Mobile crane lifts permitted only after verified soil bearing capacity tests under outrigger mats. "
            "Soil saturation reduces load-bearing capacity by up to 50%."
        ),
        "height_work_status": "CAUTION - SLIP & FALL HAZARD",
        "height_work_details": (
            "Wet steel beams, slippery scaffold planks, and rebar mats increase slip hazards tenfold. "
            "Mandatory 100% tie-off using dual lanyards with shock absorbers. No external plastering or painting."
        ),
        "concrete_protocol": (
            "Per IS 456:2000, DO NOT pour concrete in open exposed areas without waterproof tarpaulin canopy protection. "
            "Excess rainwater alters water-cement (w/c) ratio, causing dramatic compressive strength degradation and surface washing."
        ),
        "electrical_safety": (
            "HIGH PRIORITY: Test all 30mA Earth Leakage Circuit Breakers (ELCB/RCCB). Elevate all junction boxes and cables "
            "on timber stands above water level. Deploy flameproof submersible pumps for basement and excavation dewatering."
        ),
        "checklist": [
            "Energize and monitor submersible dewatering pumps in basement sump pits.",
            "Check slope stability and shoring sheets in deep foundation trenches for mudslide risk.",
            "Verify 30mA ELCB tripping on all portable distribution boards (DBs).",
            "Store bulk cement bags and gypsum on raised pallets (min 300mm above finished floor).",
            "Provide rubber waterproof boots and rain gear to active logistics crews."
        ]
    },
    "Extreme Heat (>42°C / Heatwave Protocol)": {
        "status_level": "SEVERE HEAT STRESS & RAPID DESICCATION",
        "badge_color": "#F59E0B",
        "bg_color": "rgba(245, 158, 11, 0.12)",
        "wind_speed_range": "5 - 18 km/h",
        "crane_status": "NORMAL WITH CABIN AIR-CONDITIONING / CAB VENTILATION",
        "crane_details": (
            "Hydraulic fluid temperatures must be monitored to prevent seal degradation and line burst. "
            "Ensure crane cabin cooling is functional for operator alertness."
        ),
        "height_work_status": "RESTRICTED PEAK HOURS (12:00 PM - 3:30 PM)",
        "height_work_details": (
            "Shift strenuous steel tying and deck shuttering to early morning (6:00 AM - 11:00 AM) and evening shifts. "
            "Mandatory 15-minute shaded rest breaks every 45 minutes for crews working in direct solar radiation."
        ),
        "concrete_protocol": (
            "Strict adherence to IS 7861 (Part 1): Use chilled batching water or crushed ice flaking to keep fresh concrete "
            "temperature below 32°C. Extend wet burlap ponding curing to 14 days minimum. Avoid mid-day pours to eliminate thermal shock."
        ),
        "electrical_safety": (
            "Prevent generator and compressor overheating; maintain clear ventilation exhaust around portable DG sets."
        ),
        "checklist": [
            "Set up shaded hydration stations stocked with potable water and ORS electrolyte solution.",
            "Adjust working hours to split-shift schedule (avoiding 12:00 PM to 3:30 PM peak sun).",
            "Verify chilled water dosing at Ready Mix Concrete (RMC) batching plant.",
            "Pre-wet timber shuttering and steel rebar before concrete placement to prevent moisture absorption.",
            "Conduct morning toolbox talk on early heat exhaustion symptoms (dizziness, nausea, cramping)."
        ]
    },
    "Dense Fog / Poor Visibility (<50 meters)": {
        "status_level": "VISUAL IMPAIRMENT & COLLISION WARNING",
        "badge_color": "#8B5CF6",
        "bg_color": "rgba(139, 92, 246, 0.12)",
        "wind_speed_range": "0 - 8 km/h (Calm)",
        "crane_status": "RESTRICTED (BLIND LIFT PROTOCOLS ACTIVE)",
        "crane_details": (
            "No heavy lifting without direct two-way certified radio communication and dedicated spotters. "
            "Crane boom tip aviation strobe warning lights must remain illuminated continuously."
        ),
        "height_work_status": "RESTRICTED",
        "height_work_details": (
            "Mandatory Class 3 high-visibility jackets with 3M reflective tape for all site personnel. "
            "Prohibit heavy plant vehicular transit (dumpers, concrete transit mixers) without escort marshals."
        ),
        "concrete_protocol": (
            "Low ambient evaporation; curing proceeds favorably, but ensure adequate artificial illumination "
            "during screeding and surface power-troweling to prevent uneven finishes."
        ),
        "electrical_safety": (
            "Moisture condensation on cold outdoor electrical switchboards; verify IP65 enclosure sealing."
        ),
        "checklist": [
            "Turn on all site perimeter floodlights and crane warning beacon strobes.",
            "Assign dedicated banksmen / traffic marshals with high-vis batons at access gates.",
            "Require continuous radio communication between crane operators and riggers.",
            "Inspect safety access stair towers for condensation dew slip hazards."
        ]
    },
    "Normal / Fair Weather (24°C - 32°C, Clear)": {
        "status_level": "OPTIMAL CONSTRUCTION CONDITIONS",
        "badge_color": "#10B981",
        "bg_color": "rgba(16, 185, 129, 0.12)",
        "wind_speed_range": "10 - 20 km/h",
        "crane_status": "FULL CLEARANCE FOR TOWER & MOBILE CRANES",
        "crane_details": (
            "Perform scheduled pre-operational daily checklist (hoist limit switch, load moment indicator calibration, hook latch)."
        ),
        "height_work_status": "FULL CLEARANCE UNDER STANDARD OSHA PPE",
        "height_work_details": (
            "Standard fall arrest, hard hats, high-vis vests, and steel-toe boots required for all personnel."
        ),
        "concrete_protocol": (
            "Standard IS 456:2000 curing procedures: maintain continuous wet hessian or ponding curing for min 7 days (OPC) or 10 days (PPC/Slag cement)."
        ),
        "electrical_safety": (
            "Standard routine weekly inspection of distribution boards, earthing pits, and tool tagging."
        ),
        "checklist": [
            "Conduct standard 10-minute morning toolbox safety briefing.",
            "Verify all workers wear full PPE (Helmets, Vests, Steel-Toe Boots, Safety Glasses).",
            "Inspect scaffold tags (Green Tag = Safe to Use, Red Tag = Do Not Use).",
            "Monitor slump test and cube casting (min 6 cubes per 100m³ pour) for daily pours."
        ]
    }
}

def get_weather_protocol(condition_name: str) -> Dict[str, Any]:
    """Retrieve full advisory profile for selected weather condition."""
    return WEATHER_PROFILES.get(condition_name, WEATHER_PROFILES["Normal / Fair Weather (24°C - 32°C, Clear)"])
