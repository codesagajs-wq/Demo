# from typing import TypedDict, Annotated
# from langgraph.graph import StateGraph, END
# import operator

# class WorkflowState(TypedDict):
#     request: dict
#     data: dict
#     aggregated: dict
#     anomalies: list
#     insights: list
#     forecasts: dict
#     report: str
#     workflow: dict
#     status: str
#     errors: Annotated[list, operator.add]

# def create_workflow_graph(coordinator):
#     """Create LangGraph workflow"""
    
#     def fetch_data_node(state: WorkflowState):
#         data = coordinator.data_agent.fetch_data(
#             report_type=state['request'].get('report_type', 'sales'),
#             filters=state['request'].get('filters', {})
#         )
#         return {'data': data}
    
#     def aggregate_node(state: WorkflowState):
#         aggregated = coordinator.data_agent.aggregate_data(state['data'])
#         return {'aggregated': aggregated}
    
#     def analytics_node(state: WorkflowState):
#         anomalies = coordinator.analytics_agent.detect_anomalies(state['data'])
#         insights = coordinator.analytics_agent.generate_insights(state['data'], state['aggregated'])
#         forecasts = coordinator.analytics_agent.forecast_trends(state['data'])
#         return {
#             'anomalies': anomalies,
#             'insights': insights,
#             'forecasts': forecasts
#         }
    
#     def workflow_build_node(state: WorkflowState):
#         workflow = coordinator.workflow_agent.build_workflow(state['request'])
#         return {'workflow': workflow}
    
#     def report_gen_node(state: WorkflowState):
#         report = coordinator.report_agent.generate_report(
#             report_type=state['request'].get('report_type', 'sales'),
#             aggregated_data=state['aggregated'],
#             insights=state['insights'],
#             anomalies=state['anomalies'],
#             forecasts=state['forecasts']
#         )
#         return {'report': report, 'status': 'completed'}
    
#     # Build graph
#     workflow = StateGraph(WorkflowState)
    
#     workflow.add_node("fetch_data", fetch_data_node)
#     workflow.add_node("aggregate", aggregate_node)
#     workflow.add_node("analytics", analytics_node)
#     workflow.add_node("build_workflow", workflow_build_node)
#     workflow.add_node("generate_report", report_gen_node)
    
#     workflow.set_entry_point("fetch_data")
#     workflow.add_edge("fetch_data", "aggregate")
#     workflow.add_edge("aggregate", "analytics")
#     workflow.add_edge("analytics", "build_workflow")
#     workflow.add_edge("build_workflow", "generate_report")
#     workflow.add_edge("generate_report", END)
    
#     return workflow.compile()