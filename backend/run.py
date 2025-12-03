import os
import time
from dotenv import load_dotenv
from app import create_app


load_dotenv()


config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1', 'yes')
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', os.environ.get('PORT', 5000)))
    
    app.run(debug=debug_mode, host=host, port=port)
