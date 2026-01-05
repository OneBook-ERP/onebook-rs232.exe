"""
Waybridge Agent - Main Application
Reads weight data from serial port and sends to ERP system
"""

import sys
import signal
import time
from typing import Optional
from datetime import datetime

from config_manager import get_config, ConfigurationError
from logger import get_logger
from serial_reader import open_serial
from parser import parse_weight
from erp_client import get_erp_client

# Initialize logger
logger = get_logger()

# Global flag for graceful shutdown
running = True


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global running
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    running = False


def main():
    """Main application loop"""
    global running
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("=" * 60)
    logger.info("Waybridge Agent Starting...")
    logger.info("=" * 60)
    
    try:
        # Load configuration
        logger.info("Loading configuration...")
        config = get_config()
        
        # Log configuration (without sensitive data)
        logger.info(f"Serial Port: {config.get('serial.port')}")
        logger.info(f"Baud Rate: {config.get('serial.baudrate')}")
        logger.info(f"Weighbridge ID: {config.get('weighbridge.id')}")
        logger.info(f"ERP URL: {config.get('erp.url')}")
        
        token = config.get('erp.token', '')
        if token:
            logger.info(f"API Token: {'*' * 20} (configured)")
        else:
            logger.warning("API Token: Not configured")
        
    except ConfigurationError as e:
        logger.critical(f"Configuration error: {e}")
        logger.critical("Please check your config.json file")
        return 1
    except Exception as e:
        logger.critical(f"Unexpected error loading configuration: {e}", exc_info=True)
        return 1
    
    # Initialize ERP client
    try:
        logger.info("Initializing ERP client...")
        erp_client = get_erp_client()
        
        # Test connection (optional, can be disabled)
        if config.get('app.test_connection_on_start', False):
            logger.info("Testing ERP connection...")
            success, message = erp_client.test_connection()
            if not success:
                logger.warning(f"ERP connection test failed: {message}")
                logger.warning("Continuing anyway, will retry on actual data...")
        
    except Exception as e:
        logger.error(f"Error initializing ERP client: {e}", exc_info=True)
        logger.warning("Continuing without ERP connection...")
    
    # Open serial port
    ser = None
    try:
        logger.info("Opening serial port...")
        serial_config = config.get_section('serial')
        ser = open_serial(serial_config)
        logger.info(f"✓ Serial port {serial_config['port']} opened successfully")
        
    except Exception as e:
        logger.critical(f"Failed to open serial port: {e}", exc_info=True)
        logger.critical("Cannot continue without serial connection")
        return 1
    
    # Get weighbridge configuration
    wb_config = config.get_section('weighbridge')
    weighbridge_id = wb_config['id']
    precision = wb_config.get('precision', 2)
    unit = wb_config.get('unit', 'kg')
    
    logger.info("=" * 60)
    logger.info("Waybridge Agent Started Successfully")
    logger.info("Waiting for weight data...")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    # Statistics
    stats = {
        'total_readings': 0,
        'successful_sends': 0,
        'failed_sends': 0,
        'invalid_readings': 0,
        'start_time': datetime.now()
    }
    
    # Main loop
    try:
        while running:
            try:
                # Read from serial port
                raw = ser.readline().decode(errors='ignore').strip()
                
                if not raw:
                    continue
                
                logger.debug(f"RAW: {raw}")
                stats['total_readings'] += 1
                
                # Parse weight
                weight = parse_weight(raw)
                
                if weight is None:
                    logger.debug(f"Could not parse weight from: {raw}")
                    stats['invalid_readings'] += 1
                    continue
                
                # Round weight to precision
                weight = round(float(weight), precision)
                
                logger.info(f"📊 Weight Reading: {weight} {unit}")
                
                # Prepare payload
                payload = {
                    "weighbridge_id": weighbridge_id,
                    "weight": weight,
                    "unit": unit,
                    "raw": raw,
                    "timestamp": datetime.now().isoformat(),
                    "precision": precision
                }
                
                # Send to ERP
                success, error = erp_client.send(payload)
                
                if success:
                    stats['successful_sends'] += 1
                    logger.info(f"✓ Data sent to ERP successfully ({stats['successful_sends']}/{stats['total_readings']})")
                else:
                    stats['failed_sends'] += 1
                    logger.error(f"✗ Failed to send data to ERP: {error}")
                    logger.error(f"Failed sends: {stats['failed_sends']}/{stats['total_readings']}")
                
                # Log statistics periodically
                if stats['total_readings'] % 10 == 0:
                    log_statistics(stats)
                
            except KeyboardInterrupt:
                raise  # Re-raise to be caught by outer try-except
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
                time.sleep(1)  # Prevent tight loop on repeated errors
                
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        # Cleanup
        logger.info("Shutting down...")
        
        if ser:
            try:
                ser.close()
                logger.info("✓ Serial port closed")
            except Exception as e:
                logger.error(f"Error closing serial port: {e}")
        
        try:
            erp_client.close()
            logger.info("✓ ERP client closed")
        except Exception as e:
            logger.error(f"Error closing ERP client: {e}")
        
        # Final statistics
        log_statistics(stats, final=True)
        
        logger.info("=" * 60)
        logger.info("Waybridge Agent Stopped")
        logger.info("=" * 60)
    
    return 0


def log_statistics(stats: dict, final: bool = False):
    """
    Log statistics
    
    Args:
        stats: Statistics dictionary
        final: Whether this is the final statistics log
    """
    prefix = "FINAL STATISTICS" if final else "STATISTICS"
    
    runtime = datetime.now() - stats['start_time']
    success_rate = (stats['successful_sends'] / stats['total_readings'] * 100) if stats['total_readings'] > 0 else 0
    
    logger.info("-" * 60)
    logger.info(f"{prefix}:")
    logger.info(f"  Runtime: {runtime}")
    logger.info(f"  Total Readings: {stats['total_readings']}")
    logger.info(f"  Successful Sends: {stats['successful_sends']}")
    logger.info(f"  Failed Sends: {stats['failed_sends']}")
    logger.info(f"  Invalid Readings: {stats['invalid_readings']}")
    logger.info(f"  Success Rate: {success_rate:.1f}%")
    logger.info("-" * 60)


if __name__ == "__main__":
    sys.exit(main())
