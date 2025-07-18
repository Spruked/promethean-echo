from flask import request, jsonify, g
import logging
import time
import hashlib
from functools import wraps
from datetime import datetime, timedelta
import jwt
import os

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """Security middleware for Flask application"""
    
    def __init__(self, app=None):
        self.app = app
        self.failed_attempts = {}
        self.blocked_ips = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security middleware with Flask app"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Run before each request"""
        g.start_time = time.time()
        
        # Check for blocked IPs
        client_ip = self.get_client_ip()
        if self.is_ip_blocked(client_ip):
            logger.warning(f"Blocked IP {client_ip} attempted access")
            return jsonify({"error": "Access denied"}), 403
        
        # Log request
        self.log_request()
        
        # Add security headers
        self.add_security_headers()
    
    def after_request(self, response):
        """Run after each request"""
        # Calculate response time
        response_time = time.time() - g.start_time
        
        # Log response
        self.log_response(response, response_time)
        
        # Add security headers to response
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'"
        
        return response
    
    def get_client_ip(self):
        """Get client IP address"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr
    
    def is_ip_blocked(self, ip):
        """Check if IP is blocked"""
        if ip in self.blocked_ips:
            block_time = self.blocked_ips[ip]
            # Block for 1 hour
            if datetime.now() - block_time < timedelta(hours=1):
                return True
            else:
                del self.blocked_ips[ip]
        return False
    
    def block_ip(self, ip):
        """Block an IP address"""
        self.blocked_ips[ip] = datetime.now()
        logger.warning(f"IP {ip} has been blocked")
    
    def record_failed_attempt(self, ip):
        """Record failed authentication attempt"""
        if ip not in self.failed_attempts:
            self.failed_attempts[ip] = []
        
        self.failed_attempts[ip].append(datetime.now())
        
        # Remove attempts older than 1 hour
        cutoff_time = datetime.now() - timedelta(hours=1)
        self.failed_attempts[ip] = [
            attempt for attempt in self.failed_attempts[ip] 
            if attempt > cutoff_time
        ]
        
        # Block if too many failed attempts
        if len(self.failed_attempts[ip]) >= 5:
            self.block_ip(ip)
    
    def log_request(self):
        """Log incoming request"""
        logger.info(f"Request: {request.method} {request.path} from {self.get_client_ip()}")
    
    def log_response(self, response, response_time):
        """Log outgoing response"""
        logger.info(f"Response: {response.status_code} in {response_time:.3f}s")
    
    def add_security_headers(self):
        """Add security headers to request context"""
        pass

def require_api_key(f):
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        expected_key = os.getenv('API_KEY')
        
        if not expected_key:
            logger.warning("API_KEY not configured")
            return jsonify({"error": "API authentication not configured"}), 500
        
        if not api_key:
            return jsonify({"error": "API key required"}), 401
        
        if api_key != expected_key:
            # Record failed attempt
            security_middleware = SecurityMiddleware()
            security_middleware.record_failed_attempt(security_middleware.get_client_ip())
            return jsonify({"error": "Invalid API key"}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def generate_api_key():
    """Generate a secure API key"""
    import secrets
    return secrets.token_urlsafe(32)

def hash_sensitive_data(data):
    """Hash sensitive data for logging"""
    return hashlib.sha256(data.encode()).hexdigest()[:16]

# Global middleware instance
security_middleware = SecurityMiddleware()
