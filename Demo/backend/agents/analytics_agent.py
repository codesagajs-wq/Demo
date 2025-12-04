import pandas as pd
import numpy as np
from typing import Dict, Any, List
from .llm import get_llm

class AnalyticsAgent:
    """Agent for predictive analytics, anomaly detection, and insights"""
    
    def detect_anomalies(self, data: Dict[str, pd.DataFrame]) -> List[Dict[str, Any]]:
        anomalies = []
        
        if 'sales_transactions' in data:
            df = data['sales_transactions']
            if len(df) > 0:
                mean_total = df['total'].mean()
                std_total = df['total'].std()
                threshold = mean_total + (3 * std_total)
                high_transactions = df[df['total'] > threshold]
                
                if len(high_transactions) > 0:
                    anomalies.append({
                        'type': 'high_value_transaction',
                        'severity': 'medium',
                        'count': len(high_transactions),
                        'message': f'Detected {len(high_transactions)} unusually high-value transactions',
                        'max_value': float(high_transactions['total'].max())
                    })
        
        if 'financial_records' in data:
            df = data['financial_records']
            if len(df) > 1:
                avg_margin = df['profit_margin'].mean()
                recent_margin = df.iloc[0]['profit_margin']
                
                if recent_margin < avg_margin * 0.8:
                    anomalies.append({
                        'type': 'profit_margin_drop',
                        'severity': 'high',
                        'message': f'Profit margin dropped to {recent_margin:.2f}% (avg: {avg_margin:.2f}%)',
                        'recent_value': float(recent_margin),
                        'average_value': float(avg_margin)
                    })
        
        return anomalies
    
    def generate_insights(self, data: Dict[str, pd.DataFrame], aggregated: Dict[str, Any]) -> List[str]:
        insights = []
        
        if 'sales_summary' in aggregated:
            summary = aggregated['sales_summary']
            insights.append(f"Top performing product is {summary['top_product']}")
            insights.append(f"Top performing region is {summary['top_region']}")
            insights.append(f"Average transaction value is ${summary['avg_transaction']:,.2f}")
        
        if 'crm_summary' in aggregated:
            summary = aggregated['crm_summary']
            insights.append(f"Deal conversion rate is {summary['conversion_rate']:.1f}%")
            insights.append(f"{summary['top_industry']} sector has highest deal values")
        
        if 'financial_summary' in aggregated:
            summary = aggregated['financial_summary']
            margin = (summary['total_profit'] / summary['total_revenue']) * 100
            insights.append(f"Overall profit margin is {margin:.1f}%")
        
        return insights
    
    def forecast_trends(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        forecasts = {}
        
        if 'sales_transactions' in data:
            df = data['sales_transactions']
            if len(df) > 7:
                sales_by_date = df.groupby('date')['total'].sum().sort_index()
                recent_trend = sales_by_date.tail(7).mean()
                previous_trend = sales_by_date.head(7).mean()
                growth_rate = ((recent_trend - previous_trend) / previous_trend) * 100 if previous_trend > 0 else 0
                
                forecasts['sales_trend'] = {
                    'direction': 'up' if growth_rate > 0 else 'down',
                    'growth_rate': round(float(growth_rate), 2),
                    'prediction': 'Sales are trending upward' if growth_rate > 0 else 'Sales are declining'
                }
        
        return forecasts