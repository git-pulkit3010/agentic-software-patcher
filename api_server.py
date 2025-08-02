# backend/api_server.py - Enhanced for Phase 3

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import json
import os
from pymongo import MongoClient

# Import Phase 3 routers
from routers.approval_router import router as approval_router
from routers.explanation_router import router as explanation_router

# Import Phase 3 agents
from agents.human_approval_agent import HumanApprovalAgent
from agents.explainer_agent import ExplainerAgent
from agents.audit_logger_agent import AuditLoggerAgent

app = FastAPI(
    title="Agentic Patch Management System",
    description="Phase 3 - Human Approval & Explanation System",
    version="3.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["mydatabase"]
collection = db["patch_plans"]

# Initialize Phase 3 agents
approval_agent = HumanApprovalAgent()
explainer_agent = ExplainerAgent()
audit_logger = AuditLoggerAgent()

# Include Phase 3 routers
app.include_router(approval_router)
app.include_router(explanation_router)

# Existing Pydantic model
class PatchPlan(BaseModel):
    patch_plan: Dict[str, Any]

# Enhanced patch plan endpoint with automatic approval request creation
@app.post("/patch-plan")
async def receive_patch_plan(plan: PatchPlan):
    try:
        os.makedirs("data/received_plans", exist_ok=True)
        filename = os.path.join("data/received_plans", "patch_plan_received.json")
        
        # Save the posted patch plan JSON
        with open(filename, "w") as f:
            json.dump(plan.patch_plan, f, indent=2)
        
        # Load saved data to MongoDB
        with open(filename, 'r') as file:
            document = json.loads(file.read())
        collection.insert_one(document)
        
        # Log patch plan generation
        audit_logger.log_patch_plan_generation(plan.patch_plan)
        
        # Automatically create approval request for the patch plan
        approval_id = approval_agent.create_approval_request(
            patch_plan=plan.patch_plan,
            requester="automated_system"
        )
        
        print(f"✅ Patch plan received and approval request created: {approval_id}")
        
        return {
            "message": "Patch plan received, saved locally, stored in MongoDB, and approval request created",
            "filename": filename,
            "approval_id": approval_id,
            "patch_plan_id": plan.patch_plan.get("audit_id", "unknown")
        }
        
    except Exception as e:
        print(f"❌ Error processing patch plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# New endpoint to get system status
@app.get("/system/status")
async def get_system_status():
    """Get overall system status including agent health"""
    try:
        # Check approval agent
        approval_stats = approval_agent.get_approval_statistics()
        
        # Check audit logger
        audit_stats = audit_logger.get_decision_statistics(7)  # Last 7 days
        
        # Test MongoDB connection
        try:
            client.admin.command('ping')
            mongodb_status = "connected"
        except:
            mongodb_status = "disconnected"
        
        return {
            "status": "healthy",
            "phase": "3.0 - Human Approval & Explanation",
            "agents": {
                "approval_agent": "online",
                "explainer_agent": "online", 
                "audit_logger": "online"
            },
            "statistics": {
                "approvals": approval_stats,
                "recent_decisions": audit_stats
            },
            "database": {
                "mongodb": mongodb_status
            }
        }
        
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "3.0.0",
        "phase": "Human Approval & Explanation System"
    }

# Root endpoint with system information
@app.get("/")
async def root():
    return {
        "message": "Agentic Patch Management System - Phase 3",
        "version": "3.0.0",
        "features": [
            "Human Approval Workflows",
            "LLM-Powered Explanations", 
            "Enhanced Audit Logging",
            "React-based UI",
            "Real-time Status Updates"
        ],
        "endpoints": {
            "approvals": "/api/approval",
            "explanations": "/api/explanation",
            "patch_plans": "/patch-plan",
            "system_status": "/system/status"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)