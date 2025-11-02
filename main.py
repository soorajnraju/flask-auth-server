#!/usr/bin/env python3
"""
Main application entry point for the Enterprise Authorization Server.
"""

from app import create_app

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)