"""
Real Estate Valuation & Construction Costing Engine (INR)
Supports Indian Standard calculations, material quantity estimation,
milestone tracking, and Pollinations AI 3D rendering generator.
"""

from typing import Dict, Any, List
import urllib.parse
from config import LOCATION_TIERS, MATERIAL_COEFFICIENTS_PER_1000_SQFT, CONSTRUCTION_MILESTONES

def format_inr(amount: float) -> str:
    """Format float into Indian Rupee denomination (Crores, Lakhs, Thousands)."""
    if amount is None or amount < 0:
        return "₹0.00"
    
    if amount >= 10_000_000:  # 1 Crore = 100 Lakhs = 10 Million
        crores = amount / 10_000_000
        return f"₹{crores:,.2f} Cr"
    elif amount >= 100_000:    # 1 Lakh = 100 Thousand
        lakhs = amount / 100_000
        return f"₹{lakhs:,.2f} L"
    elif amount >= 1_000:
        thousands = amount / 1_000
        return f"₹{thousands:,.2f} K"
    else:
        return f"₹{amount:,.2f}"

def calculate_project_valuation(
    structure_type: str,
    built_up_sqft: float,
    location_tier_name: str,
    specification_grade: str,
    completion_percentage: float
) -> Dict[str, Any]:
    """
    Computes CapEx, Remaining Cost, Asset Valuation, GDV, and Material Quantities.
    """
    tier_info = LOCATION_TIERS.get(location_tier_name, list(LOCATION_TIERS.values())[0])
    
    # 1. Base Construction Cost
    rate_per_sqft = tier_info["rates"].get(specification_grade, 2500)
    total_construction_budget = built_up_sqft * rate_per_sqft
    
    # Capital Expenditure Incurred
    capex_incurred = total_construction_budget * (completion_percentage / 100.0)
    cost_to_complete = total_construction_budget - capex_incurred
    
    # 2. Land Value & Gross Development Value (GDV)
    sale_rate_sqft = tier_info["sale_realization_rate"].get(specification_grade, 9000)
    projected_gdv = built_up_sqft * sale_rate_sqft
    
    # Imputed land value based on land_cost_ratio
    land_cost_ratio = tier_info["land_cost_ratio"]
    imputed_land_value = projected_gdv * land_cost_ratio
    
    # Current Market Asset Valuation (Imputed Land + Value of Construction Added + Stage Risk Discount Factor)
    # Stage risk premium decreases as completion rises
    risk_factor = 0.85 + (0.15 * (completion_percentage / 100.0))
    current_asset_valuation = (imputed_land_value + capex_incurred * 1.25) * risk_factor
    
    # Unrealized Developer Equity Value
    unrealized_equity = max(0.0, current_asset_valuation - capex_incurred)
    
    # 3. Material Quantities Estimation (IS 456 Benchmarks)
    area_multiplier = built_up_sqft / 1000.0
    steel_mt = area_multiplier * MATERIAL_COEFFICIENTS_PER_1000_SQFT["steel_mt"]
    cement_bags = int(area_multiplier * MATERIAL_COEFFICIENTS_PER_1000_SQFT["cement_bags"])
    cement_mt = (cement_bags * 50) / 1000.0
    coarse_agg_cft = area_multiplier * MATERIAL_COEFFICIENTS_PER_1000_SQFT["coarse_aggregate_cft"]
    coarse_agg_cum = coarse_agg_cft * 0.0283168  # convert CFT to m³
    sand_cft = area_multiplier * MATERIAL_COEFFICIENTS_PER_1000_SQFT["sand_msand_cft"]
    sand_cum = sand_cft * 0.0283168
    water_kl = (area_multiplier * MATERIAL_COEFFICIENTS_PER_1000_SQFT["water_litres"]) / 1000.0
    
    # 4. Milestone Progress Breakdown
    milestones: List[Dict[str, Any]] = []
    cumulative_pct = 0.0
    
    for ms in CONSTRUCTION_MILESTONES:
        share = ms["share_pct"]
        ms_budget = total_construction_budget * (share / 100.0)
        start_pct = cumulative_pct
        end_pct = cumulative_pct + share
        cumulative_pct = end_pct
        
        if completion_percentage >= end_pct:
            status = "Completed"
            progress_in_stage = 100.0
        elif completion_percentage <= start_pct:
            status = "Pending"
            progress_in_stage = 0.0
        else:
            status = "In Progress"
            progress_in_stage = ((completion_percentage - start_pct) / share) * 100.0
            
        stage_spent = ms_budget * (progress_in_stage / 100.0)
        
        milestones.append({
            "stage": ms["stage"],
            "share_pct": share,
            "budget_inr": ms_budget,
            "budget_formatted": format_inr(ms_budget),
            "spent_inr": stage_spent,
            "spent_formatted": format_inr(stage_spent),
            "status": status,
            "progress_pct": round(progress_in_stage, 1),
            "description": ms["description"]
        })
        
    return {
        "structure_type": structure_type,
        "built_up_sqft": built_up_sqft,
        "location_tier": location_tier_name,
        "specification_grade": specification_grade,
        "completion_percentage": completion_percentage,
        "rate_per_sqft": rate_per_sqft,
        "sale_rate_sqft": sale_rate_sqft,
        "total_construction_budget": total_construction_budget,
        "total_construction_budget_formatted": format_inr(total_construction_budget),
        "capex_incurred": capex_incurred,
        "capex_incurred_formatted": format_inr(capex_incurred),
        "cost_to_complete": cost_to_complete,
        "cost_to_complete_formatted": format_inr(cost_to_complete),
        "imputed_land_value": imputed_land_value,
        "imputed_land_value_formatted": format_inr(imputed_land_value),
        "current_asset_valuation": current_asset_valuation,
        "current_asset_valuation_formatted": format_inr(current_asset_valuation),
        "projected_gdv": projected_gdv,
        "projected_gdv_formatted": format_inr(projected_gdv),
        "unrealized_equity": unrealized_equity,
        "unrealized_equity_formatted": format_inr(unrealized_equity),
        "materials": {
            "steel_mt": round(steel_mt, 1),
            "cement_bags": cement_bags,
            "cement_mt": round(cement_mt, 1),
            "coarse_agg_cum": round(coarse_agg_cum, 1),
            "coarse_agg_cft": round(coarse_agg_cft, 0),
            "sand_cum": round(sand_cum, 1),
            "sand_cft": round(sand_cft, 0),
            "water_kl": round(water_kl, 1),
        },
        "milestones": milestones
    }

def generate_architectural_render_url(
    structure_type: str,
    architectural_style: str,
    location_tier: str,
    seed: int = 42
) -> Dict[str, str]:
    """
    Constructs an architectural prompt and returns a live Pollinations AI image URL.
    """
    prompt = (
        f"Hyper-realistic architectural 3D rendering of a luxury {structure_type}, "
        f"{architectural_style} style, located in modern metropolitan India, "
        f"golden hour warm cinematic lighting, dramatic facade with glass and steel louvers, "
        f"landscaped podium garden, reflections, wide angle shot, 8k resolution, Architectural Digest feature"
    )
    encoded_prompt = urllib.parse.quote(prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=640&seed={seed}&nologo=true&enhance=true"
    
    return {
        "prompt": prompt,
        "image_url": image_url
    }
