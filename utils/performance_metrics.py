"""
Performance metrics tracking utility.
"""
import time
import functools
import logging

logger = logging.getLogger(__name__)

# Dictionary to store performance metrics
performance_data = {
    'total_requests': 0,
    'total_processing_time': 0,
    'successful_requests': 0,
    'failed_requests': 0,
    'avg_processing_time': 0,
    'requests_by_endpoint': {},
    'processing_times': []
}