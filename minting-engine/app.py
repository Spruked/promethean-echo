from flask import Flask, jsonify, request, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import json
from datetime import datetime
import os
import sys
import uuid
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import configuration and security modules
from config.secure_config import config
from security.input_validator import validate_nft_minting_request, ValidationError
from security.middleware import SecurityMiddleware, require_api_key, hash_sensitive_data
from security.logging_config import init_logging, security_logger, transaction_logger
from security.error_handler import (
    retry_with_backoff, handle_web3_errors, handle_ipfs_errors, 
    safe_execute, health_check, error_handler
)
from security.monitoring import (
    metrics_collector, system_monitor, performance_monitor, alert_manager
)
from security.advanced_security import advanced_security, rate_limiter, security_audit

# Import business logic modules
from ai_module.metadata_generator import generate_metadata
from ipfs_uploader.ipfs_upload import upload_to_ipfs
from minting_engine.mint_nft import mint_nft

# Initialize logging
init_logging()
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = config.flask_secret_key

# Initialize security middleware
security_middleware = SecurityMiddleware(app)

# Initialize rate limiter with custom key function
def get_rate_limit_key():
    """Custom rate limit key function"""
    api_key = request.headers.get('X-API-Key')
    if api_key:
        return f"api_key:{hash_sensitive_data(api_key)}"
    return f"ip:{get_remote_address()}"

limiter = Limiter(
    app,
    key_func=get_rate_limit_key,
    default_limits=[f"{config.rate_limit_requests_per_minute} per minute"],
    storage_uri="memory://"
)

# Start system monitoring
system_monitor.start_monitoring()

# Performance monitoring decorator
def monitor_performance(endpoint_name):
    """Decorator to monitor endpoint performance"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            request_id = str(uuid.uuid4())
            
            try:
                # Record request
                performance_monitor.record_api_call(
                    endpoint_name, 
                    request.method, 
                    200,  # Will be updated in finally block
                    0     # Will be updated in finally block
                )
                
                result = func(*args, **kwargs)
                return result
                
            except Exception as e:
                logger.error(f"Error in {endpoint_name}: {str(e)}", extra={
                    'request_id': request_id,
                    'endpoint': endpoint_name
                })
                raise
                
            finally:
                duration = time.time() - start_time
                status_code = getattr(result, 'status_code', 200) if 'result' in locals() else 500
                
                performance_monitor.record_api_call(
                    endpoint_name,
                    request.method,
                    status_code,
                    duration
                )
        
        return wrapper
    return decorator

@app.errorhandler(429)
def ratelimit_handler(e):
    """Handle rate limit exceeded"""
    ip = get_remote_address()
    security_logger.log_suspicious_activity(
        'rate_limit_exceeded',
        ip,
        {'limit': str(e.description), 'endpoint': request.endpoint}
    )
    return jsonify(error="Rate limit exceeded", message=str(e.description)), 429

@app.errorhandler(400)
def bad_request(e):
    """Handle bad requests"""
    return jsonify(error="Bad request", message=str(e)), 400

@app.errorhandler(500)
def internal_error(e):
    """Handle internal errors"""
    logger.error(f"Internal server error: {str(e)}")
    return jsonify(error="Internal server error"), 500

@app.route("/")
@monitor_performance("root")
def home():
    """Root endpoint"""
    return jsonify({
        "status": "Prometheus NFT Minting API running",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "security": "Enhanced"
    })

@app.route("/health")
@monitor_performance("health")
def health():
    """Enhanced health check endpoint"""
    health_result = safe_execute(health_check)
    
    return jsonify({
        "status": "healthy" if health_result['success'] else "unhealthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "config": config.to_dict(),
        "health_check": health_result,
        "metrics": metrics_collector.get_metrics(),
        "alerts": alert_manager.get_active_alerts()
    })

@app.route("/metrics")
@require_api_key
@monitor_performance("metrics")
def metrics():
    """Metrics endpoint for monitoring"""
    return jsonify({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metrics": metrics_collector.get_metrics(),
        "alerts": alert_manager.get_active_alerts(),
        "error_stats": error_handler.get_error_stats()
    })

@app.route("/security/audit")
@require_api_key
@monitor_performance("security_audit")
def security_audit_endpoint():
    """Security audit endpoint"""
    compliance_results = security_audit.run_compliance_checks()
    audit_log = security_audit.get_audit_log(50)
    
    return jsonify({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "compliance": compliance_results,
        "audit_log": audit_log
    })

@app.route("/mint", methods=["POST"])
@require_api_key
@limiter.limit("5 per minute")  # Stricter limit for minting
@monitor_performance("mint")
def mint_nft_endpoint():
    """Secure NFT minting endpoint with comprehensive error handling"""
    request_id = str(uuid.uuid4())
    ip = get_remote_address()
    
    try:
        # Validate content type
        if not request.is_json:
            abort(400, description="Content-Type must be application/json")
        
        # Get request data
        data = request.get_json()
        if not data:
            abort(400, description="No JSON data provided")
        
        logger.info(f"Received minting request from IP: {ip}", extra={
            'request_id': request_id,
            'ip_address': ip
        })
        
        # Log transaction request
        transaction_logger.log_mint_request(request_id, ip, data)
        
        # Advanced rate limiting
        if not rate_limiter.token_bucket_allow(f"mint_{ip}", capacity=10, refill_rate=0.1):
            security_logger.log_suspicious_activity(
                'mint_rate_limit_exceeded',
                ip,
                {'request_id': request_id}
            )
            return jsonify({"error": "Minting rate limit exceeded"}), 429
        
        # Validate input data
        validated_data = validate_nft_minting_request(data)
        
        # Generate metadata with retry logic
        @retry_with_backoff(max_retries=3)
        def generate_metadata_with_retry():
            return generate_metadata(
                title=validated_data['title'],
                description=validated_data['description'],
                author=validated_data.get('author', 'Unknown'),
                tags=validated_data.get('tags', [])
            )
        
        metadata = generate_metadata_with_retry()
        
        # Upload to IPFS with retry and error handling
        @retry_with_backoff(max_retries=3)
        @handle_ipfs_errors
        def upload_to_ipfs_with_retry():
            return upload_to_ipfs(metadata)
        
        logger.info("Uploading metadata to IPFS...", extra={'request_id': request_id})
        ipfs_uri = upload_to_ipfs_with_retry()
        
        # Log IPFS upload
        transaction_logger.log_ipfs_upload(request_id, ipfs_uri.split('/')[-1], len(metadata))
        
        # Mint NFT with retry and error handling
        @retry_with_backoff(max_retries=2)
        @handle_web3_errors
        def mint_nft_with_retry():
            recipient = validated_data.get('recipient_address', config.account_address)
            return mint_nft(ipfs_uri, recipient)
        
        logger.info("Minting NFT on blockchain...", extra={'request_id': request_id})
        
        mint_start_time = time.time()
        tx_receipt = mint_nft_with_retry()
        mint_duration = time.time() - mint_start_time
        
        # Record blockchain transaction metrics
        performance_monitor.record_blockchain_transaction(
            'mint_nft',
            True,
            tx_receipt.gasUsed,
            mint_duration
        )
        
        # Log successful mint
        transaction_logger.log_mint_success(
            request_id,
            tx_receipt.transactionHash.hex(),
            tx_receipt.get('tokenId', 0),  # Would need to parse from logs
            validated_data.get('recipient_address', config.account_address)
        )
        
        # Increment success counter
        metrics_collector.increment_counter('nft.minted.success')
        
        response = {
            "success": True,
            "request_id": request_id,
            "transaction_hash": tx_receipt.transactionHash.hex(),
            "block_number": tx_receipt.blockNumber,
            "gas_used": tx_receipt.gasUsed,
            "ipfs_uri": ipfs_uri,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        logger.info(f"Successfully minted NFT: {tx_receipt.transactionHash.hex()}", extra={
            'request_id': request_id,
            'transaction_hash': tx_receipt.transactionHash.hex()
        })
        
        return jsonify(response), 201
        
    except ValidationError as e:
        logger.warning(f"Validation error: {str(e)}", extra={'request_id': request_id})
        metrics_collector.increment_counter('nft.minted.validation_error')
        return jsonify({"error": "Validation failed", "message": str(e)}), 400
    
    except Exception as e:
        logger.error(f"Minting error: {str(e)}", extra={'request_id': request_id})
        
        # Log mint failure
        transaction_logger.log_mint_failure(
            request_id,
            str(e),
            {'error_type': type(e).__name__}
        )
        
        # Record error in handler
        error_handler.record_error(type(e).__name__, 'mint_nft')
        
        # Increment error counter
        metrics_collector.increment_counter('nft.minted.error', tags={
            'error_type': type(e).__name__
        })
        
        return jsonify({"error": "Minting failed", "message": "Internal server error"}), 500

@app.before_request
def before_request():
    """Enhanced before request handler"""
    # Check alerts
    alert_manager.check_alerts()
    
    # Log security events
    security_audit.log_security_event(
        'api_request',
        {
            'endpoint': request.endpoint,
            'method': request.method,
            'ip': get_remote_address(),
            'user_agent': request.headers.get('User-Agent', '')
        }
    )

if __name__ == "__main__":
    # Security check for production
    if config.flask_env == 'production':
        if config.flask_secret_key == 'dev-secret-key-change-in-production':
            logger.error("Production detected with default secret key! Please set FLASK_SECRET_KEY environment variable.")
            sys.exit(1)
        
        # Additional production security checks
        compliance_results = security_audit.run_compliance_checks()
        if compliance_results['failed'] > 0:
            logger.error(f"Security compliance failed: {compliance_results['failed']} checks failed")
            for check in compliance_results['checks']:
                if not check['passed']:
                    logger.error(f"Failed compliance check: {check['name']} - {check['description']}")
            sys.exit(1)
    
    logger.info("Starting Prometheus NFT Minting API with enhanced security")
    
    app.run(
        host="0.0.0.0", 
        port=5000,
        debug=(config.flask_env == 'development'),
        threaded=True
    )
