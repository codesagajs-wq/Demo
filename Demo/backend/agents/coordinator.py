import math
from typing import Dict, Any

class CoordinatorAgent:
    """Main coordinator orchestrating all agents"""
    
    def __init__(self):
        from .query_parser import QueryParserAgent
        from .data_agent import DataIntegrationAgent
        from .report_agent import ReportGenerationAgent
        from .analytics_agent import AnalyticsAgent
        from .workflow_agent import WorkflowAgent
        
        self.query_parser = QueryParserAgent()
        self.data_agent = DataIntegrationAgent()
        self.report_agent = ReportGenerationAgent()
        self.analytics_agent = AnalyticsAgent()
        self.workflow_agent = WorkflowAgent()

    def _clean_json(self, obj):
        """Recursively replace NaN/inf in dict/list with None for JSON serialization"""
        if isinstance(obj, dict):
            return {k: self._clean_json(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._clean_json(v) for v in obj]
        elif isinstance(obj, float):
            if math.isnan(obj) or math.isinf(obj):
                return None
            return obj
        else:
            return obj
    
    def process_user_query(self, user_query: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Main orchestration from natural language query"""
        
        result = {'status': 'processing', 'query': user_query}
        
        try:
            #Parse query
            parsed_request = self.query_parser.parse_query(user_query, user_context)
            result['parsed_request'] = parsed_request
            
            #Build workflow  
            workflow = self.workflow_agent.build_workflow(parsed_request)
            result['workflow'] = workflow
            
            #Fetch data
            data = self.data_agent.fetch_data(
                data_sources=parsed_request.get('data_sources', []),
                filters=parsed_request.get('filters', {})
            )
            result['data_sources_used'] = list(data.keys())
            result['records_fetched'] = {k: len(v) for k, v in data.items()}
            
            #Aggregate
            aggregated = self.data_agent.aggregate_data(data)
            result['aggregated_data'] = aggregated
            
            #Analytics
            anomalies = self.analytics_agent.detect_anomalies(data)
            insights = self.analytics_agent.generate_insights(data, aggregated)
            forecasts = self.analytics_agent.forecast_trends(data)
            
            result['anomalies'] = anomalies
            result['insights'] = insights
            result['forecasts'] = forecasts
            
            #Generate report
            report = self.report_agent.generate_report(
                report_focus=parsed_request.get('report_focus', 'General Report'),
                aggregated_data=aggregated,
                insights=insights,
                anomalies=anomalies,
                forecasts=forecasts
            )
            result['report'] = report
            result['status'] = 'completed'
        
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        
        return self._clean_json(result)
