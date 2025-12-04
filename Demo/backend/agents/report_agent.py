from typing import Dict, Any
import json

from .llm import get_llm
from typing import Dict, Any
import json

class ReportGenerationAgent:

    def generate_report(self, 
                       report_focus: str,
                       aggregated_data: Dict[str, Any],
                       insights: list,
                       anomalies: list,
                       forecasts: Dict[str, Any]) -> str:
        
        prompt = f"""Generate a professional business report based on this data:

Report Focus: {report_focus}

Data Summary:
{json.dumps(aggregated_data, indent=2)}

Key Insights:
{chr(10).join(f'- {insight}' for insight in insights)}

Anomalies Detected:
{json.dumps(anomalies, indent=2) if anomalies else 'None'}

Forecasts:
{json.dumps(forecasts, indent=2) if forecasts else 'None'}

Generate the report with:
1. Executive Summary
2. Key Findings
3. Detailed Analysis
4. Anomalies & Alerts
5. Recommendations
6. Future Outlook
"""

        try:
            llm = get_llm()
            response = llm.invoke([
                {"role": "user", "content": prompt}
            ])

            return response.content

        except Exception as e:
            return f"Error generating report: {str(e)}"
