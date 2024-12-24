"""
Webhook Handler for Voice Agent Discovery System

This Flask application handles incoming webhooks from the Hamming API service,
processing call status updates and recording availability notifications.

Features:
    - Receives POST requests with call status data
    - Logs incoming webhook data
    - Processes call status and recording availability
    - Returns appropriate HTTP responses

Usage:
    Run directly with: python webhook.py
    Or use with a WSGI server for production deployment
"""

from flask import Flask, request
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Handle incoming webhook requests from the Hamming API.

    Processes POST requests containing call status updates and recording
    availability notifications. Logs the incoming data and returns
    appropriate responses.

    Request Format:
        Expected JSON payload:
        {
            "id": "call_123",           # Unique call identifier
            "status": "completed",      # Call status
            "recording_available": true  # Recording availability flag
        }

    Returns:
        tuple: (response_dict, http_status_code)
            Success: ({'success': True}, 200)
            Error: ({'error': error_message}, 500)

    Raises:
        No exceptions are raised; all errors are caught and returned
        as 500 responses

    Example:
        POST /webhook
        {
            "id": "call_123",
            "status": "completed",
            "recording_available": true
        }
        
        Response:
        {
            "success": true
        }
    """
    try:
        data = request.json
        logger.info(f"Received webhook data: {data}")
        
        # Process webhook data
        call_id = data.get('id')
        status = data.get('status')
        recording_available = data.get('recording_available')
        
        # You might want to store this information or trigger other processes
        # For example, you could use a queue or database to store call status
        
        return {'success': True}, 200
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return {'error': str(e)}, 500

if __name__ == '__main__':
    # Run on port 5000 by default
    app.run(debug=True)