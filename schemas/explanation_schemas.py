# backend/schemas/explanation_schemas.py

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional

class ExplanationRequest(BaseModel):
    patch_plan: Dict[str, Any] = Field(..., description="Complete patch plan to explain")

class PatchExplanationRequest(BaseModel):
    patch: Dict[str, Any] = Field(..., description="Specific patch to explain")

class ExplanationResponse(BaseModel):
    patch_plan_id: str = Field(..., description="ID of the explained patch plan")
    explanations: Dict[str, str] = Field(..., description="Generated explanations by type")
    generated_at: Optional[str] = Field(None, description="When the plan was generated")
    total_patches: int = Field(..., description="Total number of patches in the plan")

class PatchExplanationResponse(BaseModel):
    cve_id: str = Field(..., description="CVE ID of the explained patch")
    explanation: str = Field(..., description="Detailed explanation of the patch")
    risk_score: int = Field(..., description="Risk score of the patch")
    severity: str = Field(..., description="Severity level of the patch")

class ExplanationTemplate(BaseModel):
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="What this template explains")
    target_audience: str = Field(..., description="Intended audience for this explanation")

class ExplanationTemplatesResponse(BaseModel):
    templates: Dict[str, ExplanationTemplate] = Field(..., description="Available explanation templates")