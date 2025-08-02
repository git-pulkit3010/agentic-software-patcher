# backend/routers/explanation_router.py

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from schemas.explanation_schemas import (
    ExplanationRequest, ExplanationResponse, 
    PatchExplanationRequest, PatchExplanationResponse,
    ExplanationTemplatesResponse, ExplanationTemplate
)
from agents.explainer_agent import ExplainerAgent
from agents.audit_logger_agent import AuditLoggerAgent

router = APIRouter(prefix="/api/explanation", tags=["explanation"])

# Initialize agents
explainer_agent = ExplainerAgent()
audit_logger = AuditLoggerAgent()

@router.post("/patch-plan", response_model=ExplanationResponse)
async def generate_patch_plan_explanation(request: ExplanationRequest):
    """Generate comprehensive explanations for a patch plan"""
    try:
        patch_plan = request.patch_plan
        explanations = explainer_agent.generate_patch_plan_summary(patch_plan)
        
        # Log the explanation generation
        audit_logger.log_user_action(
            user_id="system",
            action="generate_explanation",
            resource_id=patch_plan.get("audit_id", "unknown"),
            details={"explanation_types": list(explanations.keys())}
        )
        
        return ExplanationResponse(
            patch_plan_id=patch_plan.get("audit_id", "unknown"),
            explanations=explanations,
            generated_at=patch_plan.get("plan_metadata", {}).get("generated_at"),
            total_patches=len(patch_plan.get("scheduled_patches", []))
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate explanation: {str(e)}")

@router.post("/specific-patch", response_model=PatchExplanationResponse)
async def explain_specific_patch(request: PatchExplanationRequest):
    """Generate detailed explanation for a specific patch"""
    try:
        patch = request.patch
        explanation = explainer_agent.explain_specific_patch(patch)
        
        return PatchExplanationResponse(
            cve_id=patch.get("cve_id", "unknown"),
            explanation=explanation,
            risk_score=patch.get("risk_score", 0),
            severity=patch.get("severity", "unknown")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to explain patch: {str(e)}")

@router.get("/templates", response_model=ExplanationTemplatesResponse)
async def get_explanation_templates():
    """Get available explanation templates and their descriptions"""
    templates = {
        "executive_summary": ExplanationTemplate(
            name="Executive Summary",
            description="High-level overview for business stakeholders",
            target_audience="C-level executives, business managers"
        ),
        "risk_analysis": ExplanationTemplate(
            name="Risk Analysis",
            description="Detailed security risk assessment and prioritization",
            target_audience="Security analysts, IT managers"
        ),
        "compliance_impact": ExplanationTemplate(
            name="Compliance Impact",
            description="Regulatory and compliance implications",
            target_audience="Compliance officers, auditors"
        ),
        "implementation_guide": ExplanationTemplate(
            name="Implementation Guide", 
            description="Technical implementation recommendations",
            target_audience="System administrators, DevOps engineers"
        ),
        "business_impact": ExplanationTemplate(
            name="Business Impact",
            description="Operational and business continuity analysis",
            target_audience="Business continuity managers, operations"
        )
    }
    
    return ExplanationTemplatesResponse(templates=templates)