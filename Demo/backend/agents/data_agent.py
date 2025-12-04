from typing import Dict, Any
import pandas as pd
from mock_data.mock_apis import MockERPSystem, MockCRMSystem, MockBusinessTransactions
from mock_data.data_generator import DataGenerator

class DataIntegrationAgent:
    """Agent responsible for fetching and aggregating linked ERP, CRM, and transaction data"""
    
    def __init__(self):
        crm_df = DataGenerator.generate_crm_data(num_customers=100)

        self.crm = MockCRMSystem(crm_df)
        self.erp = MockERPSystem(crm_df)
        self.transactions = MockBusinessTransactions(crm_df)
    
    def fetch_data(self, data_sources: list, filters: Dict[str, Any]) -> Dict[str, pd.DataFrame]:
        """Fetch data from specified sources with filters"""
        data = {}
        clean_filters = {k: v for k, v in filters.items() if v is not None}
        
        for source in data_sources:
            if source == 'erp_sales':
                data['sales_transactions'] = self.erp.get_sales_transactions(clean_filters)
            elif source == 'erp_financial':
                data['financial_records'] = self.erp.get_financial_records(clean_filters)
            elif source == 'erp_inventory':
                data['inventory'] = self.erp.get_inventory_data(clean_filters)
            elif source == 'crm_customers':
                data['customers'] = self.crm.get_customer_data(clean_filters)
            elif source == 'crm_opportunities':
                data['opportunities'] = self.crm.get_opportunities(clean_filters)
            elif source == 'transactions':
                data['business_transactions'] = self.transactions.get_transactions(clean_filters)
        
        return data

    def aggregate_data(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """Aggregate data for reporting"""
        aggregated = {}
        
        if 'sales_transactions' in data:
            df = data['sales_transactions']
            aggregated['sales_summary'] = {
                'total_revenue': float(df['total'].sum()),
                'total_transactions': len(df),
                'avg_transaction': float(df['total'].mean()) if len(df) > 0 else 0,
                'top_product': df.groupby('product')['total'].sum().idxmax() if len(df) > 0 else 'N/A',
                'top_region': df.groupby('region')['total'].sum().idxmax() if len(df) > 0 else 'N/A',
                'total_quantity': int(df['quantity'].sum())
            }
        
        if 'customers' in data:
            df = data['customers']
            aggregated['crm_summary'] = {
                'total_customers': len(df),
                'total_deal_value': float(df['deal_value'].sum()),
                'avg_deal_value': float(df['deal_value'].mean()) if len(df) > 0 else 0,
                'conversion_rate': float((len(df[df['stage'] == 'Closed Won']) / len(df)) * 100) if len(df) > 0 else 0,
                'top_industry': df.groupby('industry')['deal_value'].sum().idxmax() if len(df) > 0 else 'N/A'
            }
        
        if 'financial_records' in data:
            df = data['financial_records']
            aggregated['financial_summary'] = {
                'total_revenue': float(df['revenue'].sum()),
                'total_expenses': float(df['expenses'].sum()),
                'total_profit': float(df['profit'].sum()),
                'avg_profit_margin': float(df['profit_margin'].mean()) if len(df) > 0 else 0
            }
        
        if 'business_transactions' in data:
            df = data['business_transactions']
            aggregated['transaction_summary'] = {
                'total_transactions': len(df),
                'completed': len(df[df['status'] == 'Completed']),
                'pending': len(df[df['status'] == 'Pending']),
                'total_amount': float(df['amount'].sum())
            }
        
        return aggregated
