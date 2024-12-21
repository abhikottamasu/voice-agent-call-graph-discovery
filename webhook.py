from flask import Flask, request
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
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