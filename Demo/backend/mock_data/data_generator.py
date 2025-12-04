from faker import Faker
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

fake = Faker()

class DataGenerator:
    """Generate interlinked mock data for 2025"""
    
    @staticmethod
    def generate_crm_data(num_customers=50):
        """Generate CRM customers"""
        data = []
        for _ in range(num_customers):
            last_contact = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 364))
            data.append({
                'customer_id': fake.uuid4(),
                'company_name': fake.company(),
                'contact_person': fake.name(),
                'email': fake.email(),
                'phone': fake.phone_number(),
                'industry': random.choice(['Technology', 'Finance', 'Healthcare', 'Retail', 'Manufacturing']),
                'deal_value': round(random.uniform(10000, 500000), 2),
                'stage': random.choice(['Lead', 'Qualified', 'Proposal', 'Negotiation', 'Closed Won', 'Closed Lost']),
                'last_contact': last_contact,
                'account_manager': fake.name()
            })
        return pd.DataFrame(data)

    @staticmethod
    def generate_sales_data(crm_df, num_records=200):
        """Generate sales transactions linked to CRM customers"""
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 12, 31)
        num_days = (end_date - start_date).days + 1

        data = []
        for _ in range(num_records):
            customer = crm_df.sample(1).iloc[0]
            date = start_date + timedelta(days=random.randint(0, num_days - 1))
            quantity = random.randint(1, 100)
            unit_price = round(random.uniform(10, 1000), 2)

            data.append({
                'transaction_id': fake.uuid4(),
                'date': date,
                'customer': customer['company_name'],
                'customer_id': customer['customer_id'],
                'industry': customer['industry'],
                'product': random.choice(['Product A','Product B','Product C','Product D','Product E']),
                'quantity': quantity,
                'unit_price': unit_price,
                'total': quantity*unit_price,
                'region': random.choice(['North','South','East','West','Central']),
                'sales_rep': customer['account_manager'],
                'status': random.choice(['Completed','Pending','Shipped'])
            })
        return pd.DataFrame(data)

    @staticmethod
    def generate_financial_data(num_records=12):
        """Generate monthly financials for 2025"""
        data = []
        for month in range(1, 13):
            date = datetime(2025, month, 1)
            revenue = random.uniform(800000, 1500000)
            expenses = revenue * random.uniform(0.6, 0.8)
            data.append({
                'month': date.strftime('%Y-%m'),
                'revenue': round(revenue,2),
                'expenses': round(expenses,2),
                'profit': round(revenue-expenses,2),
                'profit_margin': round(((revenue-expenses)/revenue)*100,2)
            })
        return pd.DataFrame(data)

    @staticmethod
    def generate_inventory_data(num_records=50):
        data = []
        for _ in range(num_records):
            data.append({
                'product_id': fake.uuid4(),
                'product_name': fake.word().capitalize() + ' ' + random.choice(['Pro','Plus','Elite','Basic']),
                'category': random.choice(['Electronics','Furniture','Supplies','Equipment']),
                'quantity_on_hand': random.randint(0,500),
                'reorder_level': random.randint(50,100),
                'unit_cost': round(random.uniform(10,200),2),
                'warehouse': random.choice(['Warehouse A','Warehouse B','Warehouse C'])
            })
        return pd.DataFrame(data)

    @staticmethod
    def generate_opportunities(crm_df, num_records=80):
        """Generate opportunities linked to CRM customers"""
        data = []
        for _ in range(num_records):
            customer = crm_df.sample(1).iloc[0]
            close_date = datetime(2025, 1, 1) + timedelta(days=random.randint(0, 364))
            data.append({
                'opportunity_id': fake.uuid4(),
                'customer': customer['company_name'],
                'customer_id': customer['customer_id'],  # link key
                'opportunity_name': fake.catch_phrase(),
                'value': round(random.uniform(50000, 1000000), 2),
                'stage': random.choice(['Prospecting','Qualification','Proposal','Negotiation','Closed Won']),
                'probability': random.choice([10,25,50,75,90,100]),
                'close_date': close_date,
                'owner': customer['account_manager']
            })
        return pd.DataFrame(data)

    @staticmethod
    def generate_business_transactions(crm_df, num_records=150):
        """Generate business transactions linked to customers"""
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 12, 31)
        num_days = (end_date - start_date).days + 1
        data = []

        for _ in range(num_records):
            customer = crm_df.sample(1).iloc[0]
            date = start_date + timedelta(days=random.randint(0, num_days-1))
            data.append({
                'transaction_id': fake.uuid4(),
                'date': date,
                'customer': customer['company_name'],
                'customer_id': customer['customer_id'],
                'industry': customer['industry'],
                'type': random.choice(['Purchase','Sale','Refund','Payment']),
                'amount': round(random.uniform(100,50000),2),
                'status': random.choice(['Completed','Pending','Failed','Processing']),
                'reference': fake.bothify(text='TXN-####-????'),
                'description': fake.sentence()
            })
        return pd.DataFrame(data)