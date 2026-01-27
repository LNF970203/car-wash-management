import boto3
from datetime import datetime, timedelta
import os
from typing import Dict, List, Optional, Union, Any
import pandas as pd
import streamlit as st

# Type alias for DynamoDB item
dynamodb_item = Dict[str, Any]


os.environ["AWS_ACCESS_KEY_ID"] = st.secrets["aws"]["AWS_ACCESS_KEY"]
os.environ["AWS_SECRET_ACCESS_KEY"] = st.secrets["aws"]["AWS_SECRET_KEY"]
os.environ["AWS_REGION"] = st.secrets["aws"]["REGION_NAME"]
os.environ["ENV"] = st.secrets["aws"]["ENV"]


def add_record(
    table_name: str,
    sale_id: str,
    vehicle_number: str,
    service_date: str,
    services: List[str],
    price: float,
    status: str,
    customer_name: Optional[str],
    contact_number: Optional[str],
    service_description: Optional[str]  
) -> Dict:
    """
    Add a new record to the specified DynamoDB table.
    
    Args:
        table_name (str): Name of the DynamoDB table
        sale_id (str): User ID associated with the record
        vehicle_number (str): URL of the image
        service_date (str): Service date
        services (List[str]): Services conducted
        price (float): Price of the service
        status (str): Status of the sale
        customer_name (str[Optional]): Customer name
        contact_number (str[Optional]): Customer contact number
        service_description (str[Optional]): Service description

    Returns:
        Dict: The response from DynamoDB with success/error information
    """
    # Initialize AWS session and DynamoDB resource
    session = boto3.Session(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    
    dynamodb = session.resource('dynamodb')
    table = dynamodb.Table(table_name)
    
    # Prepare the item
    item = {
        'sale_id': sale_id,
        'vehicle_number': vehicle_number,
        'service_date': service_date or datetime.utcnow().isoformat(),
        'services': services,
        'price': price,
        'status': status,
        'customer_name': customer_name,
        'contact_number': contact_number,
        'service_description': service_description,
    }
    
    try:
        # Put the item in the table
        response = table.put_item(Item=item)
        return {
            'success': True,
            'message': 'Record added successfully',
            'item': item,
            'response': response
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error adding record: {str(e)}',
            'item': item
        }

        
def get_recent_records(table_name: str, start_date: str, end_date: str, gsi_name: str = 'CreationDateIndex') -> Dict[str, Union[bool, str, pd.DataFrame]]:
    """
    Fetch records from the DynamoDB table that were created within the specified number of days.
    
    Args:
        table_name (str): Name of the DynamoDB table
        days (int, optional): Number of days to look back. Defaults to 14 (2 weeks).
        gsi_name (str, optional): Name of the Global Secondary Index on creation_date.
                                 Defaults to 'CreationDateIndex'.
        
    Returns:
        Dict: A dictionary containing:
            - success (bool): Whether the operation was successful
            - message (str): Status message
            - data (pd.DataFrame): DataFrame containing the records, or None if there was an error
    """
    try:
        # Initialize AWS session and DynamoDB resource
        session = boto3.Session(
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        
        dynamodb = session.resource('dynamodb')
        table = dynamodb.Table(table_name)
        
        # Use query on the GSI for creation_date
        response = table.query(
            IndexName=gsi_name,
            KeyConditionExpression='#pk = :pk_value AND #cd BETWEEN :start_date AND :end_date',
            ExpressionAttributeNames={
                '#pk': 'status',  # The partition key of the GSI
                '#cd': 'service_date'  # The sort key of the GSI
            },
            ExpressionAttributeValues={
                ':pk_value': 'success',
                ':start_date': start_date,
                ':end_date': end_date
            },
            ScanIndexForward=False  # Sort in descending order (newest first)
        )
        
        items = response.get('Items', [])
        
        # Handle pagination if there are more items
        while 'LastEvaluatedKey' in response:
            response = table.query(
                IndexName=gsi_name,
                KeyConditionExpression='#pk = :pk_value AND #cd BETWEEN :start_date AND :end_date',
                ExpressionAttributeNames={
                    '#pk': 'status',
                    '#cd': 'service_date'
                },
                ExpressionAttributeValues={
                    ':pk_value': 'success',
                    ':start_date': start_date,
                    ':end_date': end_date
                },
                ExclusiveStartKey=response['LastEvaluatedKey'],
                ScanIndexForward=False
            )
            items.extend(response.get('Items', []))
        
        if not items:
            return {
                'success': True,
                'message': 'No records found in the specified date range',
                'data': pd.DataFrame()
            }
        
        # Convert to DataFrame
        df = pd.DataFrame(items)
        
        # Convert service_date to datetime and sort
        if 'service_date' in df.columns:
            df['service_date'] = pd.to_datetime(df['service_date'])
            df = df.sort_values('service_date', ascending=False)
        
        return {
            'success': True,
            'message': f'Successfully retrieved {len(df)} records',
            'data': df
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f'Error fetching records: {str(e)}',
            'data': None
        }