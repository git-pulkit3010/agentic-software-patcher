# backend/agents/explainer_agent.py

import json
from typing import Dict, List, Any
from agents.llm_reasoner import LLMReasoningAgent

class ExplainerAgent:
    def __init__(self):
        self.llm_reasoner = LLMReasoningAgent()
    
    def generate_patch_plan_summary(self, patch_plan: Dict[str, Any]) -> Dict[str, str]:
        """Generate comprehensive explanations for a patch plan"""
        
        # Extract key information
        scheduled_patches = patch_plan.get("scheduled_patches", [])
        metadata = patch_plan.get("plan_metadata", {})
        compliance_summary = metadata.get("compliance_summary", {})
        
        # Generate different types of explanations
        explanations = {
            "executive_summary": self._generate_executive_summary(patch_plan),
            "risk_analysis": self._generate_risk_analysis(scheduled_patches),
            "compliance_impact": self._generate_compliance_explanation(compliance_summary),
            "implementation_guide": self._generate_implementation_guide(scheduled_patches),
            "business_impact": self._generate_business_impact(patch_plan)
        }
        
        return explanations
    
    def _generate_executive_summary(self, patch_plan: Dict) -> str:
        """Generate executive summary using LLM"""
        scheduled_patches = patch_plan.get("scheduled_patches", [])
        metadata = patch_plan.get("plan_metadata", {})
        
        # Prepare context for LLM
        context = f"""
        Patch Plan Overview:
        - Total Patches: {len(scheduled_patches)}
        - Generated: {metadata.get('generated_at', 'Unknown')}
        - Audit ID: {patch_plan.get('audit_id', 'N/A')}
        
        High-Level Statistics:
        - High Risk Patches: {len([p for p in scheduled_patches if p.get('risk_score', 0) >= 70])}
        - Critical Severity: {len([p for p in scheduled_patches if p.get('severity') == 'critical'])}
        - Production Systems: {len([p for p in scheduled_patches if p.get('target_system', {}).get('environment') == 'production'])}
        
        Compliance Frameworks: {metadata.get('compliance_summary', {}).get('frameworks_involved', [])}
        """
        
        prompt = f"""
        You are a cybersecurity executive assistant. Create a concise executive summary (2-3 paragraphs) 
        for the following patch plan. Focus on business impact, risk mitigation, and key decisions needed.
        
        {context}
        
        Write in professional, executive-level language that non-technical stakeholders can understand.
        """
        
        return self.llm_reasoner.run(prompt)
    
    def _generate_risk_analysis(self, scheduled_patches: List[Dict]) -> str:
        """Generate risk analysis explanation"""
        
        # Analyze risk distribution
        risk_stats = {
            "critical": len([p for p in scheduled_patches if p.get("risk_score", 0) >= 90]),
            "high": len([p for p in scheduled_patches if 70 <= p.get("risk_score", 0) < 90]),
            "medium": len([p for p in scheduled_patches if 40 <= p.get("risk_score", 0) < 70]),
            "low": len([p for p in scheduled_patches if p.get("risk_score", 0) < 40])
        }
        
        # Get examples of high-risk patches
        high_risk_patches = [p for p in scheduled_patches if p.get("risk_score", 0) >= 70][:3]
        
        context = f"""
        Risk Distribution:
        - Critical Risk (90+): {risk_stats['critical']} patches
        - High Risk (70-89): {risk_stats['high']} patches  
        - Medium Risk (40-69): {risk_stats['medium']} patches
        - Low Risk (<40): {risk_stats['low']} patches
        
        High Risk Patch Examples:
        """
        
        for patch in high_risk_patches:
            context += f"""
        - CVE: {patch.get('cve_id', 'N/A')}
          Risk Score: {patch.get('risk_score', 0)}
          Severity: {patch.get('severity', 'unknown')}
          Target: {patch.get('target_system', {}).get('name', 'Unknown')}
        """
        
        prompt = f"""
        You are a cybersecurity risk analyst. Explain the risk profile of this patch plan in detail.
        Focus on the most concerning vulnerabilities and potential impacts if patches are delayed.
        
        {context}
        
        Provide actionable insights about risk prioritization and mitigation strategies.
        """
        
        return self.llm_reasoner.run(prompt)
    
    def _generate_compliance_explanation(self, compliance_summary: Dict) -> str:
        """Generate compliance impact explanation"""
        
        frameworks = compliance_summary.get("frameworks_involved", [])
        docs_required = compliance_summary.get("patches_requiring_documentation", 0)
        
        if not frameworks:
            return "No specific compliance frameworks identified for this patch plan."
        
        context = f"""
        Compliance Requirements:
        - Applicable Frameworks: {', '.join(frameworks)}
        - Patches Requiring Documentation: {docs_required}
        - Total Compliance Requirements: {compliance_summary.get('total_compliance_requirements', 0)}
        """
        
        prompt = f"""
        You are a compliance specialist. Explain the compliance implications of this patch plan.
        Detail what documentation and processes are required for each framework.
        
        {context}
        
        Focus on regulatory requirements, timelines, and documentation needs.
        """
        
        return self.llm_reasoner.run(prompt)
    
    def _generate_implementation_guide(self, scheduled_patches: List[Dict]) -> str:
        """Generate implementation guidance"""
        
        # Group patches by timeline
        immediate = [p for p in scheduled_patches if p.get("risk_score", 0) >= 80]
        near_term = [p for p in scheduled_patches if 60 <= p.get("risk_score", 0) < 80]
        planned = [p for p in scheduled_patches if p.get("risk_score", 0) < 60]
        
        context = f"""
        Implementation Timeline:
        - Immediate (24-48 hours): {len(immediate)} critical patches
        - Near-term (1-2 weeks): {len(near_term)} high priority patches  
        - Planned (2-4 weeks): {len(planned)} standard patches
        
        Environment Distribution:
        - Production patches: {len([p for p in scheduled_patches if p.get('target_system', {}).get('environment') == 'production'])}
        - Staging patches: {len([p for p in scheduled_patches if p.get('target_system', {}).get('environment') == 'staging'])}
        - Development patches: {len([p for p in scheduled_patches if p.get('target_system', {}).get('environment') == 'development'])}
        """
        
        prompt = f"""
        You are a systems administrator. Provide practical implementation guidance for this patch plan.
        Include rollback strategies, testing recommendations, and coordination requirements.
        
        {context}
        
        Focus on operational considerations and best practices for safe deployment.
        """
        
        return self.llm_reasoner.run(prompt)
    
    def _generate_business_impact(self, patch_plan: Dict) -> str:
        """Generate business impact analysis"""
        
        scheduled_patches = patch_plan.get("scheduled_patches", [])
        
        # Calculate business metrics
        production_patches = len([p for p in scheduled_patches 
                                if p.get('target_system', {}).get('environment') == 'production'])
        
        critical_systems = len([p for p in scheduled_patches 
                              if p.get('target_system', {}).get('criticality') == 'critical'])
        
        context = f"""
        Business Impact Metrics:
        - Production Systems Affected: {production_patches}
        - Critical Systems Affected: {critical_systems}
        - Total Patches: {len(scheduled_patches)}
        - Estimated Maintenance Windows: {len(set(p.get('target_system', {}).get('id', '') for p in scheduled_patches))}
        """
        
        prompt = f"""
        You are a business continuity analyst. Analyze the business impact of this patch plan.
        Consider service availability, user impact, and operational disruption.
        
        {context}
        
        Provide recommendations for minimizing business disruption while maintaining security.
        """
        
        return self.llm_reasoner.run(prompt)
    
    def explain_specific_patch(self, patch: Dict[str, Any]) -> str:
        """Generate detailed explanation for a specific patch"""
        
        context = f"""
        Patch Details:
        - CVE ID: {patch.get('cve_id', 'N/A')}
        - Risk Score: {patch.get('risk_score', 0)}
        - Severity: {patch.get('severity', 'unknown')}
        - Target System: {patch.get('target_system', {}).get('name', 'Unknown')}
        - Environment: {patch.get('target_system', {}).get('environment', 'unknown')}
        - Scheduled Time: {patch.get('scheduled_time', 'TBD')}
        - Estimated Duration: {patch.get('estimated_duration', 'Unknown')}
        - LLM Reasoning: {patch.get('llm_reasoning', 'Not available')}
        """
        
        prompt = f"""
        You are a cybersecurity analyst. Provide a detailed explanation of this specific patch,
        including why it's important, potential risks of not applying it, and implementation considerations.
        
        {context}
        
        Make it understandable for both technical and non-technical stakeholders.
        """
        
        return self.llm_reasoner.run(prompt)