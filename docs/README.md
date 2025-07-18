# Prometheus NFT Minting Engine (Alpha)

A secure, full-stack NFT minting system with AI-generated metadata, IPFS storage, and blockchain integration. Built for Prometheus Prime and SPRUKED AI.

## 🔒 Security Features

- **Environment-based Configuration**: No hardcoded secrets
- **Input Validation**: Comprehensive sanitization and validation
- **Rate Limiting**: Protection against abuse
- **API Key Authentication**: Secure API access
- **Security Headers**: OWASP recommended headers
- **IP Blocking**: Automatic blocking of suspicious IPs
- **Audit Logging**: Comprehensive request/response logging

## � Dashboard Features

- **Real-time Monitoring**: Live metrics and system status
- **Security Audit**: Threat detection and compliance checking
- **Configuration Management**: Runtime settings and environment variables
- **Performance Tracking**: Resource usage and response times
- **Alert System**: Configurable notifications and thresholds

## �🚀 Quick Start

### 1. Security Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run security setup
python security_setup.py setup

# Validate configuration
python security_setup.py validate

# Check dependencies
python security_setup.py check
```

### 2. Start Dashboard

```bash
# Option 1: Using startup script (recommended)
python start_dashboard.py

# Option 2: Manual start
python dashboard/app.py
```

The dashboard will open automatically at http://localhost:5001

### 3. Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Update the `.env` file with your actual values:
- Network RPC URL
- Wallet private key and address
- Web3.Storage token
- Contract address

### 4. Deploy Contract

```bash
cd contract_deployer
npm install
npx hardhat run scripts/deploy.js --network your-network
```

### 4. Run the Application

```bash
python app.py
```

## 🔧 API Endpoints

### Health Check
```
GET /health
```

### Mint NFT
```
POST /mint
Content-Type: application/json
X-API-Key: your-api-key

{
  "title": "Knowledge NFT Title",
  "description": "Detailed description of the knowledge",
  "tags": ["ai", "knowledge", "nft"],
  "author": "Author Name",
  "recipient_address": "0x..." (optional)
}
```

## 🛡️ Security Best Practices

### Environment Variables
- Never commit `.env` files
- Use strong, unique API keys
- Rotate keys regularly
- Use different keys for different environments

### Network Security
- Use HTTPS in production
- Implement proper firewall rules
- Monitor for suspicious activity
- Keep dependencies updated

### Wallet Security
- Use hardware wallets for production
- Implement multi-signature wallets
- Never share private keys
- Use separate wallets for different purposes

## 📁 Project Structure

```
Alpha mint engine/
├── app.py                     # Main Flask application
├── security_setup.py          # Security configuration script
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
├── ai_module/                # AI metadata generation
├── config/                   # Configuration management
│   └── secure_config.py      # Secure config loader
├── security/                 # Security modules
│   ├── input_validator.py    # Input validation
│   └── middleware.py         # Security middleware
├── minting_engine/           # NFT minting logic
├── ipfs_uploader/            # IPFS integration
├── contracts/                # Smart contracts
├── frontend/                 # React frontend
└── docs/                     # Documentation
```

## 🔍 Security Validation

The system includes comprehensive validation:

- **Input Sanitization**: All user inputs are sanitized
- **Address Validation**: Ethereum addresses are validated
- **Rate Limiting**: API endpoints are rate-limited
- **Authentication**: API key required for minting
- **Logging**: All requests and responses are logged

## 🚨 Security Warnings

⚠️ **Never commit sensitive data to version control**
⚠️ **Use different keys for development and production**
⚠️ **Regularly audit your security settings**
⚠️ **Monitor for unusual activity**

## 📊 Monitoring

The system logs:
- All API requests and responses
- Failed authentication attempts
- Blocked IP addresses
- Transaction details
- Error conditions

## 🔄 Updates and Maintenance

- Regularly update dependencies
- Monitor security advisories
- Review access logs
- Update API keys periodically
- Test backup and recovery procedures

## 🆘 Support

For security issues, please contact the development team immediately.

Created by Bryan Spruk. This is IP with teeth. 🔥

---

**Security Notice**: This system handles cryptocurrency transactions and sensitive data. Please review all security measures before deploying to production.