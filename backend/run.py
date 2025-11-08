"""
Application entry point.

Run this file to start the Flask development server.
"""

import os
from app import create_app

# Get environment from environment variable
env = os.getenv('FLASK_ENV', 'development')

# Create app using factory
app = create_app(env)

if __name__ == '__main__':
    # Run development server
    # Using port 5001 to avoid conflicts with other projects
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=app.config['DEBUG']
    )
