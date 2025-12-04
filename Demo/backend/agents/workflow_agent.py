from typing import Dict, Any
from datetime import datetime
import json

from .llm import get_llm

class WorkflowAgent:

    def build_workflow(self, parsed_request: Dict[str, Any]) -> Dict[str, Any]:
        """Build workflow based on parsed user request"""
        
        prompt = f"""Design an appropriate approval workflow for this request:

Report Type: {parsed_request.get('report_type', 'custom')}
Report Focus: {parsed_request.get('report_focus', 'General')}
Requestor: {parsed_request.get('requestor', 'User')} ({parsed_request.get('user_role', 'Unknown')})
Department: {parsed_request.get('department', 'General')}
Urgency: {parsed_request.get('urgency', 'normal')}
Value Impact: {parsed_request.get('value_impact', 'medium')}

Rules:
- Sales reports: Manager → Director
- Financial reports: Manager → Finance Head → CFO  
- Executive reports: Director → VP → C-Level
- Simple reports: Single manager approval
- High urgency: Parallel approvals where possible
- High value: Additional stakeholder reviews

Return ONLY valid JSON:
{{
  "name": "workflow name",
  "stages": [
    {{
      "id": "stage_1",
      "name": "stage name",
      "approvers": ["role"],
      "type": "sequential|parallel",
      "requires": "single|any_one|all",
      "timeout_hours": 24
    }}
  ],
  "notifications": {{
    "on_submit": true,
    "on_approval": true,
    "on_rejection": true
  }},
  "reason": "Brief explanation"
}}"""

        try:
            llm = get_llm()

            response = llm.invoke([
                {"role": "user", "content": prompt}
            ])

            response_text = response.content.strip()
            response_text = (
                response_text.replace("```json", "")
                             .replace("```", "")
                             .strip()
            )

            workflow = json.loads(response_text)

            workflow["created_at"] = datetime.now().isoformat()
            workflow["status"] = "pending"

            return workflow
            
        except Exception:
            return {
                "name": "Standard Approval Workflow",
                "stages": [{
                    "id": "stage_1",
                    "name": "Manager Review",
                    "approvers": ["Manager"],
                    "type": "sequential",
                    "requires": "single",
                    "timeout_hours": 24
                }],
                "notifications": {
                    "on_submit": True,
                    "on_approval": True,
                    "on_rejection": True
                },
                "reason": "Default workflow",
                "created_at": datetime.now().isoformat(),
                "status": "pending"
            }
