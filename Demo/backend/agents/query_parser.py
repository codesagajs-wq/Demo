from typing import Dict, Any
import json

from .llm import get_llm

class QueryParserAgent:
    """Agent that parses user natural language queries into structured requests"""
    
    def parse_query(self, user_query: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Parse natural language query into structured request"""
        
        prompt = f"""Parse this user query into a structured report request.

User Query: "{user_query}"

User Context:
- Name: {user_context.get('full_name', 'Unknown')}
- Department: {user_context.get('department', 'Unknown')}
- Role: {user_context.get('role', 'Unknown')}

Assume the **current reporting year is 2025**. 
Any quarter references (Q1, Q2, Q3, Q4) should map to 2025 dates.

Available Data Sources:
1. ERP System: sales_transactions, financial_records, inventory_data
2. CRM System: customer_data, opportunities
3. Business Transactions: transaction_logs

Determine:
1. What data sources are needed
2. What filters should be applied
3. What type of report this is
4. Urgency level
5. Business value impact

Return ONLY valid JSON (no markdown):
{{
  "report_type": "sales|financial|crm|executive|custom",
  "data_sources": ["erp_sales", "crm_customers", "transactions"],
  "filters": {{
    "date_from": "YYYY-MM-DD or null",
    "date_to": "YYYY-MM-DD or null",
    "region": "region name or null",
    "product": "product name or null",
    "industry": "industry or null",
    "min_amount": number or null,
    "transaction_type": "type or null"
  }},
  "urgency": "low|normal|high",
  "value_impact": "low|medium|high",
  "report_focus": "brief description of what user wants to know",
  "interpretation": "explain what the user is asking for"
}}
"""

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

            parsed_request = json.loads(response_text)

            parsed_request['requestor'] = user_context.get('full_name', 'Unknown')
            parsed_request['department'] = user_context.get('department', 'Unknown')
            parsed_request['user_role'] = user_context.get('role', 'Unknown')

            return parsed_request
            
        except Exception:
            return {
                "report_type": "custom",
                "data_sources": ["erp_sales"],
                "filters": {},
                "urgency": "normal",
                "value_impact": "medium",
                "report_focus": user_query,
                "interpretation": "General report request",
                "requestor": user_context.get('full_name', 'Unknown'),
                "department": user_context.get('department', 'Unknown'),
                "user_role": user_context.get('role', 'Unknown')
            }
