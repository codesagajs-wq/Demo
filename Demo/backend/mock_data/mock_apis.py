import pandas as pd
import random
from datetime import datetime, timedelta
from .data_generator import DataGenerator

class MockERPSystem:
    def __init__(self, crm_df: pd.DataFrame):
        self.generator = DataGenerator()
        self.crm_df = crm_df
        self._cache = {}

    def get_sales_transactions(self, filters=None):
        if 'sales' not in self._cache:
            self._cache['sales'] = self.generator.generate_sales_data(self.crm_df,num_records=200)
            
            self._cache['sales']['customer_id'] = random.choices(self.crm_df['customer_id'], k=len(self._cache['sales']))
        df = self._cache['sales'].copy()
        if filters:
            if 'industry' in filters:
                df = df[df['customer_id'].isin(
                    self.crm_df[self.crm_df['industry'].str.lower() == filters['industry'].lower()]['customer_id']
                )]
            if 'date_from' in filters:
                df = df[df['date'] >= pd.to_datetime(filters['date_from'])]
            if 'date_to' in filters:
                df = df[df['date'] <= pd.to_datetime(filters['date_to'])]
        return df

    def get_financial_records(self, filters=None):
        if 'financial' not in self._cache:
            self._cache['financial'] = self.generator.generate_financial_data(num_records=12)
        return self._cache['financial'].copy()

    def get_inventory_data(self, filters=None):
        if 'inventory' not in self._cache:
            self._cache['inventory'] = self.generator.generate_inventory_data(num_records=50)
        return self._cache['inventory'].copy()


class MockCRMSystem:
    def __init__(self, crm_df: pd.DataFrame):
        self.generator = DataGenerator()
        self.crm_df = crm_df
        self._cache = {'customers': crm_df.copy(), 'opportunities': self.generator.generate_opportunities(self.crm_df,80)}

    def get_customer_data(self, filters=None):
        df = self._cache['customers'].copy()
        if filters:
            if 'industry' in filters:
                df = df[df['industry'].str.lower() == filters['industry'].lower()]
        return df

    def get_opportunities(self, filters=None):
        df = self._cache['opportunities'].copy()
        if filters:
            if 'industry' in filters:
                df = df[df['customer'].isin(
                    self.crm_df[self.crm_df['industry'].str.lower() == filters['industry'].lower()]['company_name']
                )]
        return df


class MockBusinessTransactions:
    def __init__(self, crm_df: pd.DataFrame):
        self.generator = DataGenerator()
        self.crm_df = crm_df
        self._cache = {'transactions': self.generator.generate_business_transactions(self.crm_df,150)}

    def get_transactions(self, filters=None):
        df = self._cache['transactions'].copy()
        if filters:
            if 'industry' in filters:
                df = df[df['customer_id'].isin(
                    self.crm_df[self.crm_df['industry'].str.lower() == filters['industry'].lower()]['customer_id']
                )]
        return df
