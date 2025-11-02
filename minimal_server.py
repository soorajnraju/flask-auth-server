#!/usr/bin/env python3
"""
Minimal Flask server to verify setup works.
"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        'message': 'Enterprise Authorization Server is running!',
        'status': 'success'
    })

@app.route('/health')
def health():
    return jsonify({
        'success': True,
        'message': 'Server is healthy',
        'version': '1.0.0'
    })

@app.route('/test')
def test():
    return jsonify({
        'message': 'Test endpoint working',
        'timestamp': '2025-11-02'
    })

if __name__ == '__main__':
    print("🚀 Starting Minimal Authorization Server...")
    print("📍 Server will be available at: http://127.0.0.1:5001")
    print("📍 Health check: http://127.0.0.1:5001/health")
    app.run(debug=True, host='127.0.0.1', port=5001)