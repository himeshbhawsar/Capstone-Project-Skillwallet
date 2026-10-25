"""
Configuration and Domain Knowledge Constants
Platform ID: 6ac4c98d1dcde6d7857c1642
Multimodal Construction Intelligence Platform
"""

PLATFORM_META = {
    "name": "Multimodal Construction Intelligence Platform",
    "capstone_id": "Skill Wallet Capstone Project 1",
    "platform_id": "6ac4c98d1dcde6d7857c1642",
    "version": "2.4.0-Production",
    "category": "Generative AI | Real Estate Decision Support",
}

# Supported Gemini Models
AVAILABLE_MODELS = [
    "gemini-2.5-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

# Standards Reference
STANDARDS = {
    "OSHA": {
        "helmets": "OSHA 1926.100 (Head Protection in Construction)",
        "eye_face": "OSHA 1926.102 (Eye and Face Protection)",
        "vests": "OSHA 1926.201 / ANSI 107 (High-Visibility Safety Apparel)",
        "boots": "OSHA 1926.96 / ASTM F2413 (Foot Protection - Protective Footwear)",
        "harnesses": "OSHA 1926.502 (Fall Protection Systems Criteria and Practices)",
        "scaffolding": "OSHA 1926.451 (General Requirements for Scaffolds)",
        "electrical": "OSHA 1926.404 (Wiring Design and Protection / GFCI)",
        "cranes": "OSHA 1926.1400 (Cranes and Derricks in Construction)",
    },
    "INDIAN_STANDARDS": {
        "concrete": "IS 456:2000 (Plain and Reinforced Concrete - Code of Practice)",
        "safety_code": "IS 3786:1983 (Method for Computation of Frequency & Severity Rates)",
        "helmets": "IS 2925:1984 (Specification for Industrial Safety Helmets)",
        "harnesses": "IS 3521:1999 (Industrial Safety Belts and Harnesses)",
        "vests": "IS 15809:2017 (High Visibility Warning Clothes)",
        "footwear": "IS 15298:2016 (Personal Protective Equipment - Safety Footwear)",
        "scaffolding": "IS 2750:1964 (Specification for Steel Scaffoldings)",
        "weather_concreting": "IS 7861 (Part 1: Extreme Hot Weather, Part 2: Cold Weather)",
    }
}

# Real Estate & Construction Costing Benchmarks (INR / sq.ft)
LOCATION_TIERS = {
    "Tier 1 (Metro: Mumbai, Delhi-NCR, Bengaluru, Hyderabad)": {
        "tier_key": "tier1",
        "land_cost_ratio": 0.45,  # Land represents ~45% of total asset valuation
        "rates": {
            "Budget / Standard": 2100,
            "Premium Quality": 3200,
            "Ultra-Luxury / High-Rise": 4800,
        },
        "sale_realization_rate": {
            "Budget / Standard": 8500,
            "Premium Quality": 14500,
            "Ultra-Luxury / High-Rise": 24000,
        }
    },
    "Tier 2 (Growth Hubs: Pune, Chennai, Kolkata, Ahmedabad)": {
        "tier_key": "tier2",
        "land_cost_ratio": 0.35,
        "rates": {
            "Budget / Standard": 1850,
            "Premium Quality": 2700,
            "Ultra-Luxury / High-Rise": 3900,
        },
        "sale_realization_rate": {
            "Budget / Standard": 6200,
            "Premium Quality": 9800,
            "Ultra-Luxury / High-Rise": 16500,
        }
    },
    "Tier 3 (Emerging: Jaipur, Lucknow, Indore, Kochi, Coimbatore)": {
        "tier_key": "tier3",
        "land_cost_ratio": 0.25,
        "rates": {
            "Budget / Standard": 1600,
            "Premium Quality": 2250,
            "Ultra-Luxury / High-Rise": 3200,
        },
        "sale_realization_rate": {
            "Budget / Standard": 4500,
            "Premium Quality": 6800,
            "Ultra-Luxury / High-Rise": 10500,
        }
    }
}

STRUCTURE_TYPES = [
    "Residential High-Rise Apartment",
    "Commercial Grade-A Office Complex",
    "Industrial Pre-Engineered Warehouse",
    "Gated Luxury Villa Community",
    "Institutional & Educational Campus"
]

# Material Consumption Coefficients per 1,000 sq.ft of built-up area (IS 456 estimates)
MATERIAL_COEFFICIENTS_PER_1000_SQFT = {
    "steel_mt": 3.8,               # Metric Tonnes of reinforcement steel (Fe500/Fe550D)
    "cement_bags": 410,             # 50kg bags (PPC / OPC 53 grade)
    "coarse_aggregate_cft": 1350,   # Cubic feet (20mm & 10mm crushed stone)
    "sand_msand_cft": 1850,         # Cubic feet of Manufactured Sand (M-Sand)
    "water_litres": 22000,          # Litres for mixing and 28-day curing
}

# Milestone Breakdown Percentages
CONSTRUCTION_MILESTONES = [
    {"stage": "Substructure & Deep Foundation", "share_pct": 18, "description": "Excavation, piling, raft footing, retaining walls & waterproof membrane"},
    {"stage": "Plinth & Lower Basement Slab", "share_pct": 12, "description": "Backfilling, plinth beams, drainage trenches, damp-proof course"},
    {"stage": "Superstructure RCC Framework", "share_pct": 32, "description": "Columns, shear walls, beams, post-tensioned slabs & staircases"},
    {"stage": "Masonry, AAC Blocks & MEP Rough-in", "share_pct": 16, "description": "Internal partitioning, electrical conduits, plumbing risers, HVAC ducts"},
    {"stage": "Plastering, Flooring & Internal Finishes", "share_pct": 14, "description": "Gypsum plaster, vitrified tiles, joinery, glazing, painting primer"},
    {"stage": "External Façade, Elevators & Handover (OC)", "share_pct": 8, "description": "Curtain glazing, testing & commissioning, fire NOC, Occupancy Certificate"}
]

# Crack Diagnostics Taxonomy
CRACK_TYPES = {
    "Structural Shear Crack": {
        "severity": "Critical",
        "description": "Diagonal 45-degree fracture indicating principal tension failure in RCC beams or shear walls.",
        "repair": "Structural epoxy injection (pressure grouting) combined with carbon fiber (CFRP) composite wrapping or steel jacketing.",
        "urgency": "Immediate Evacuation & Shoring (within 12-24h)"
    },
    "Settlement Crack": {
        "severity": "High",
        "description": "Stepped diagonal cracks extending through foundation/masonry due to differential soil consolidation or subgrade shear.",
        "repair": "Foundation underpinning, micropiling, chemical compaction grouting, followed by flexible poly-sulfide joint sealing.",
        "urgency": "Urgent Structural Engineering Review (within 48h)"
    },
    "Thermal Expansion / Contraction": {
        "severity": "Medium",
        "description": "Cyclic movement cracks along parapet walls, roof slab junctions, or expansion joints lacking movement allowance.",
        "repair": "Elastomeric polyurethane (PU) sealant injection with backing rod, followed by solar reflective thermal barrier coating.",
        "urgency": "Scheduled Maintenance (within 2-4 weeks)"
    },
    "Plastic Shrinkage Hairline Crack": {
        "severity": "Low",
        "description": "Superficial fine cracks (<0.3mm width) resulting from rapid moisture evaporation during initial concrete setting.",
        "repair": "Crystalline waterproofing slurry penetration or micro-fine cementitious slurry sealing.",
        "urgency": "Monitor & Routine Surface Sealing"
    },
    "Spalling & Delamination (Rebar Corrosion)": {
        "severity": "High",
        "description": "Concrete cover detachment caused by internal expansive stress from rebar rust carbonation or chloride attack.",
        "repair": "Chipping loose concrete, sandblasting rusted rebar, zinc-rich anti-corrosion primer application, and polymer-modified mortar (PMM) build-up.",
        "urgency": "Urgent Remediation (within 7 days)"
    }
}
