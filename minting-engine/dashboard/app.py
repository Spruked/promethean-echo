from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_socketio import SocketIO, emit
import os
import sys
import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import system modules
from config.secure_config import config
from security.monitoring import metrics_collector, system_monitor, alert_manager
from security.error_handler import health_check, error_handler
from security.advanced_security import advanced_security, security_audit
from security.logging_config import security_logger, transaction_logger
from security.middleware import require_api_key, hash_sensitive_data

logger = logging.getLogger(__name__)

class DashboardApp:
    """Main dashboard application class"""
    
    def __init__(self):
        self.app = Flask(__name__, template_folder='templates', static_folder='static')
        self.app.config['SECRET_KEY'] = config.flask_secret_key
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Dashboard configuration
        self.dashboard_config = {
            'update_interval': 5,  # seconds
            'max_log_entries': 100,
            'refresh_rate': 1000,  # milliseconds
            'chart_data_points': 50
        }
        
        # Real-time data storage
        self.realtime_data = {
            'metrics': {},
            'logs': [],
            'alerts': [],
            'transactions': [],
            'system_status': {}
        }
        
        self.setup_routes()
        self.setup_websocket_handlers()
        self.start_background_tasks()
    
    def setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/')
        def dashboard():
            """Main dashboard page"""
            return render_template('dashboard.html', 
                                 config=self.get_dashboard_config())
        
        @self.app.route('/api/status')
        def api_status():
            """Get system status"""
            try:
                health_result = health_check()
                return jsonify({
                    'status': 'healthy' if health_result['status'] == 'healthy' else 'unhealthy',
                    'timestamp': datetime.utcnow().isoformat(),
                    'health_check': health_result,
                    'uptime': self.get_uptime()
                })
            except Exception as e:
                logger.error(f"Error getting system status: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/metrics')
        def api_metrics():
            """Get current metrics"""
            try:
                metrics = metrics_collector.get_metrics()
                return jsonify({
                    'timestamp': datetime.utcnow().isoformat(),
                    'metrics': metrics
                })
            except Exception as e:
                logger.error(f"Error getting metrics: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/alerts')
        def api_alerts():
            """Get current alerts"""
            try:
                alerts = alert_manager.get_active_alerts()
                return jsonify({
                    'timestamp': datetime.utcnow().isoformat(),
                    'alerts': alerts
                })
            except Exception as e:
                logger.error(f"Error getting alerts: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/audit')
        def api_audit():
            """Get audit information"""
            try:
                compliance_results = security_audit.run_compliance_checks()
                audit_log = security_audit.get_audit_log(50)
                
                return jsonify({
                    'timestamp': datetime.utcnow().isoformat(),
                    'compliance': compliance_results,
                    'audit_log': audit_log
                })
            except Exception as e:
                logger.error(f"Error getting audit info: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/transactions')
        def api_transactions():
            """Get transaction history"""
            try:
                # This would be implemented with actual transaction storage
                return jsonify({
                    'timestamp': datetime.utcnow().isoformat(),
                    'transactions': self.realtime_data['transactions'][-50:]  # Last 50
                })
            except Exception as e:
                logger.error(f"Error getting transactions: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/config')
        def api_config():
            """Get configuration information"""
            try:
                return jsonify({
                    'timestamp': datetime.utcnow().isoformat(),
                    'config': config.to_dict(),
                    'dashboard_config': self.dashboard_config
                })
            except Exception as e:
                logger.error(f"Error getting config: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/logs')
        def api_logs():
            """Get recent logs"""
            try:
                return jsonify({
                    'timestamp': datetime.utcnow().isoformat(),
                    'logs': self.realtime_data['logs'][-100:]  # Last 100
                })
            except Exception as e:
                logger.error(f"Error getting logs: {str(e)}")
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/config')
        def config_page():
            """Configuration management page"""
            return render_template('config.html', 
                                 config=config.to_dict(),
                                 dashboard_config=self.dashboard_config)
        
        @self.app.route('/monitoring')
        def monitoring_page():
            """Monitoring and metrics page"""
            return render_template('monitoring.html')
        
        @self.app.route('/security')
        def security_page():
            """Security audit page"""
            return render_template('security.html')
        
        @self.app.route('/transactions')
        def transactions_page():
            """Transaction history page"""
            return render_template('transactions.html')
        
        @self.app.route('/logs')
        def logs_page():
            """Logs viewer page"""
            return render_template('logs.html')
    
    def setup_websocket_handlers(self):
        """Setup WebSocket handlers for real-time updates"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            emit('connected', {'data': 'Connected to dashboard'})
            logger.info(f"Dashboard client connected: {request.sid}")
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            logger.info(f"Dashboard client disconnected: {request.sid}")
        
        @self.socketio.on('request_update')
        def handle_request_update():
            """Handle request for data update"""
            self.send_realtime_update()
        
        @self.socketio.on('request_metrics')
        def handle_request_metrics():
            """Handle request for metrics"""
            try:
                metrics = metrics_collector.get_metrics()
                emit('metrics_update', {'metrics': metrics})
            except Exception as e:
                logger.error(f"Error sending metrics: {str(e)}")
                emit('error', {'message': str(e)})
    
    def start_background_tasks(self):
        """Start background tasks for real-time updates"""
        
        def update_realtime_data():
            """Background task to update real-time data"""
            while True:
                try:
                    # Update metrics
                    self.realtime_data['metrics'] = metrics_collector.get_metrics()
                    
                    # Update alerts
                    self.realtime_data['alerts'] = alert_manager.get_active_alerts()
                    
                    # Update system status
                    self.realtime_data['system_status'] = health_check()
                    
                    # Send update to connected clients
                    self.send_realtime_update()
                    
                    time.sleep(self.dashboard_config['update_interval'])
                    
                except Exception as e:
                    logger.error(f"Error in background update task: {str(e)}")
                    time.sleep(self.dashboard_config['update_interval'])
        
        # Start background thread
        update_thread = threading.Thread(target=update_realtime_data)
        update_thread.daemon = True
        update_thread.start()
    
    def send_realtime_update(self):
        """Send real-time update to all connected clients"""
        try:
            update_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'metrics': self.realtime_data['metrics'],
                'alerts': self.realtime_data['alerts'],
                'system_status': self.realtime_data['system_status']
            }
            
            self.socketio.emit('realtime_update', update_data)
            
        except Exception as e:
            logger.error(f"Error sending real-time update: {str(e)}")
    
    def get_dashboard_config(self):
        """Get dashboard configuration"""
        return {
            'title': 'Prometheus NFT Minting Engine Dashboard',
            'version': '1.0.0',
            'update_interval': self.dashboard_config['update_interval'],
            'refresh_rate': self.dashboard_config['refresh_rate'],
            'environment': config.flask_env,
            'network': config.network
        }
    
    def get_uptime(self):
        """Get system uptime"""
        try:
            uptime_seconds = (datetime.utcnow() - system_monitor.metrics.start_time).total_seconds()
            return {
                'seconds': uptime_seconds,
                'human_readable': str(timedelta(seconds=int(uptime_seconds)))
            }
        except:
            return {'seconds': 0, 'human_readable': '0:00:00'}
    
    def run(self, host='127.0.0.1', port=5001, debug=False):
        """Run the dashboard application"""
        logger.info(f"Starting Prometheus NFT Dashboard on {host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=debug)

# Create global dashboard instance
dashboard_app = DashboardApp()

if __name__ == '__main__':
    dashboard_app.run(debug=True)
