# Waybridge Agent

**Production-ready agent for reading weight data from weighbridge serial ports and transmitting to ERP systems.**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## 🌟 Features

- ✅ **Real-time Weight Capture** - Continuous reading from serial weighbridge
- 🔐 **Secure Authentication** - Token-based API authentication
- 🔄 **Auto-Retry Logic** - Configurable retry attempts with exponential backoff
- 📊 **Statistics Tracking** - Real-time monitoring of success/failure rates
- 🎨 **GUI Configuration** - User-friendly settings interface
- 📝 **Comprehensive Logging** - Colored console output + rotating file logs
- ⚙️ **Flexible Configuration** - JSON-based config with validation
- 🛡️ **Error Handling** - Graceful degradation and recovery
- 📦 **Import/Export Config** - Easy backup and sharing of settings
- 🔌 **Connection Testing** - Verify settings before deployment

## 📋 Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Configuration Reference](#configuration-reference)
- [API Integration](#api-integration)
- [Logging](#logging)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [License](#license)

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- Serial port access (for weighbridge connection)
- Network access to ERP system

### Steps

1. **Clone or download the repository**
   ```bash
   cd waybridge_agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation**
   ```bash
   python -c "import serial, requests; print('Dependencies OK')"
   ```

## ⚙️ Configuration

### Option 1: GUI Configuration (Recommended)

Launch the settings interface:

```bash
python settings_gui.py
```

The GUI provides:
- ✅ Visual configuration of all settings
- ✅ Connection testing
- ✅ Import/Export functionality
- ✅ Reset to defaults
- ✅ Input validation

### Option 2: Manual Configuration

Edit `config.json` directly:

```json
{
  "serial": {
    "port": "COM3",
    "baudrate": 9600,
    "timeout": 1,
    "bytesize": 8,
    "parity": "N",
    "stopbits": 1
  },
  "erp": {
    "url": "http://your-erp-server.com/api/method/waybridge",
    "token": "your-api-key:your-api-secret",
    "timeout": 10,
    "retry_attempts": 3,
    "retry_delay": 2
  },
  "weighbridge": {
    "id": "WB-01",
    "unit": "kg",
    "precision": 2
  },
  "logging": {
    "level": "INFO",
    "file": "waybridge_agent.log",
    "max_size_mb": 10,
    "backup_count": 5
  },
  "app": {
    "version": "1.0.0",
    "auto_start": false,
    "minimize_to_tray": false
  }
}
```

## 🎯 Usage

### Quick Start

```bash
python main.py
```

### Using the Launcher

```bash
python launcher.py
```

The launcher provides options to:
- ⚙️ Configure settings
- ▶️ Start the agent
- ❌ Exit

### Command Line Options

```bash
# Start with custom config file
python main.py --config custom_config.json

# Test configuration without starting
python main.py --test-config

# Verbose logging
python main.py --verbose
```

## 📖 Configuration Reference

### Serial Port Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `port` | string | `"COM3"` | Serial port identifier (COM3, /dev/ttyUSB0, etc.) |
| `baudrate` | integer | `9600` | Communication speed (300-115200) |
| `timeout` | integer | `1` | Read timeout in seconds |
| `bytesize` | integer | `8` | Number of data bits |
| `parity` | string | `"N"` | Parity checking (N/E/O) |
| `stopbits` | integer | `1` | Number of stop bits |

### ERP Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `url` | string | `""` | **Required** - ERP API endpoint URL |
| `token` | string | `""` | API authentication token (format: `key:secret`) |
| `timeout` | integer | `10` | HTTP request timeout in seconds |
| `retry_attempts` | integer | `3` | Number of retry attempts on failure |
| `retry_delay` | integer | `2` | Delay between retries in seconds |

### Weighbridge Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | string | `"WB-01"` | **Required** - Unique weighbridge identifier |
| `unit` | string | `"kg"` | Weight unit (kg/lb/ton/g) |
| `precision` | integer | `2` | Decimal places for weight values |

### Logging Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `level` | string | `"INFO"` | Log level (DEBUG/INFO/WARNING/ERROR/CRITICAL) |
| `file` | string | `"waybridge_agent.log"` | Log file path |
| `max_size_mb` | integer | `10` | Maximum log file size in MB |
| `backup_count` | integer | `5` | Number of backup log files to keep |

## 🔌 API Integration

### Generating API Token (Frappe/ERPNext)

1. Log in to your ERPNext instance
2. Go to **User Menu** → **API Access**
3. Click **Generate Keys**
4. Copy the API Key and API Secret
5. Format as: `api_key:api_secret`
6. Paste into the settings GUI or config file

Example:
```
abc123def456ghi789:xyz987uvw654rst321
```

### Expected API Endpoint

The agent sends POST requests to your configured endpoint with the following payload:

```json
{
  "weighbridge_id": "WB-01",
  "weight": 1234.56,
  "unit": "kg",
  "raw": "raw serial data",
  "timestamp": "2026-01-05T12:30:45.123456",
  "precision": 2
}
```

### API Response

Expected successful response:

```json
{
  "message": "success",
  "data": {
    "id": "WEIGHT-001",
    "status": "recorded"
  }
}
```

## 📝 Logging

### Log Levels

- **DEBUG** - Detailed diagnostic information
- **INFO** - General informational messages
- **WARNING** - Warning messages for potentially harmful situations
- **ERROR** - Error messages for serious problems
- **CRITICAL** - Critical messages for very serious errors

### Log Files

Logs are automatically rotated when they reach the configured size:

- `waybridge_agent.log` - Current log file
- `waybridge_agent.log.1` - Previous log file
- `waybridge_agent.log.2` - Older log file
- ... (up to `backup_count` files)

### Console Output

Console logs include colored output for easy reading:

- 🔵 **DEBUG** - Cyan
- 🟢 **INFO** - Green
- 🟡 **WARNING** - Yellow
- 🔴 **ERROR** - Red
- 🟣 **CRITICAL** - Magenta

## 🔧 Troubleshooting

### Serial Port Issues

**Problem**: `Serial port not found` or `Permission denied`

**Solutions**:
- Verify the COM port number in Device Manager (Windows) or `ls /dev/tty*` (Linux)
- Ensure no other application is using the port
- On Linux, add user to `dialout` group: `sudo usermod -a -G dialout $USER`
- Check cable connections

### Connection Errors

**Problem**: `Connection failed` or `Timeout`

**Solutions**:
- Verify ERP server is running and accessible
- Check firewall settings
- Test URL in browser or with `curl`
- Verify network connectivity: `ping your-server.com`
- Check proxy settings if behind corporate firewall

### Authentication Errors

**Problem**: `401 Unauthorized` or `403 Forbidden`

**Solutions**:
- Verify API token is correct
- Check token format: `api_key:api_secret`
- Ensure user has proper permissions in ERP
- Regenerate API keys if expired

### Data Not Parsing

**Problem**: Weight values not being extracted from serial data

**Solutions**:
- Check `parser.py` logic matches your weighbridge format
- Enable DEBUG logging to see raw serial data
- Verify baud rate and serial settings match weighbridge
- Contact weighbridge manufacturer for data format specification

### High Failure Rate

**Problem**: Many failed sends in statistics

**Solutions**:
- Increase `retry_attempts` in config
- Increase `timeout` value
- Check ERP server performance and logs
- Verify network stability
- Review ERP endpoint implementation

## 🛠️ Development

### Project Structure

```
waybridge_agent/
├── main.py                 # Main application entry point
├── config_manager.py       # Configuration management
├── logger.py              # Logging configuration
├── erp_client.py          # ERP communication client
├── serial_reader.py       # Serial port reader
├── parser.py              # Weight data parser
├── settings_gui.py        # Settings GUI
├── launcher.py            # Application launcher
├── config.json            # Configuration file
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── waybridge_agent.log   # Log file (generated)
```

### Running Tests

```bash
# Test configuration loading
python config_manager.py

# Test logger
python logger.py

# Test ERP client
python erp_client.py

# Test settings GUI
python settings_gui.py
```

### Building Executable

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller main.spec
```

The executable will be in the `dist/` folder.

### Code Quality

```bash
# Format code
black *.py

# Lint code
pylint *.py

# Type checking
mypy *.py
```

## 📊 Statistics and Monitoring

The agent tracks and logs statistics:

- **Total Readings** - Number of weight readings captured
- **Successful Sends** - Number of successful transmissions
- **Failed Sends** - Number of failed transmissions
- **Invalid Readings** - Number of unparseable readings
- **Success Rate** - Percentage of successful transmissions
- **Runtime** - Total running time

Statistics are logged every 10 readings and on shutdown.

## 🔒 Security Best Practices

1. **Protect API Tokens** - Never commit tokens to version control
2. **Use HTTPS** - Always use HTTPS endpoints in production
3. **Restrict Permissions** - Use API tokens with minimal required permissions
4. **Regular Updates** - Keep dependencies updated for security patches
5. **Log Review** - Regularly review logs for suspicious activity
6. **Backup Config** - Keep encrypted backups of configuration

## 📄 License

[Your License Here - e.g., MIT License]

## 🤝 Support

For issues, questions, or contributions:

- **Issues**: [GitHub Issues](your-repo-url/issues)
- **Email**: support@yourcompany.com
- **Documentation**: [Wiki](your-repo-url/wiki)

## 🙏 Acknowledgments

- Built for integration with Frappe/ERPNext
- Uses PySerial for serial communication
- Uses Requests for HTTP communication

---

**Version**: 1.0.0  
**Last Updated**: 2026-01-05  
**Maintained by**: [Your Name/Organization]
