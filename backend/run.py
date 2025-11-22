import os
import time
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env file
load_dotenv()

if __name__ == '__main__':
    # Get config from environment, default to 'development'
    config_name = os.environ.get('FLASK_ENV', 'development')
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1', 'yes')
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    # Retry loop for database connection
    max_retries = 30
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            app = create_app(config_name)
            break
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Failed to create app (attempt {attempt + 1}/{max_retries}): {e}")
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed to create app after {max_retries} attempts")
                raise
    
    app.run(debug=debug_mode, host=host, port=port)
