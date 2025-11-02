#!/usr/bin/env python3
"""
Simple Flask app to test if the basic setup works.
"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'Server is running'})

@app.route('/test')
def test():
    return jsonify({'message': 'Test endpoint working'})

if __name__ == '__main__':
    print("Starting simple Flask test server...")
    app.run(debug=True, host='127.0.0.1', port=5002)