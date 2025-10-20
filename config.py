import os
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class with settings loaded from environment variables."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', '')
    
    # Database settings
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'invites.db')
    
    # Plex settings
    PLEX_TOKEN = os.getenv('PLEX_TOKEN', '')
    PLEX_SERVER_NAME = os.getenv('PLEX_SERVER_NAME', '')
    
    # Admin credentials
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', '')
    ADMIN_PASSWORD_HASH = os.getenv('ADMIN_PASSWORD_HASH', '')
    
    # Optional invite code
    INVITE_CODE = os.getenv('INVITE_CODE', '')
    
    # Configuration file path
    CONFIG_FILE = 'config.json'
    
    @staticmethod
    def get_library_config():
        """Get the list of libraries to share from config.json."""
        config_path = Path(Config.CONFIG_FILE)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    return data.get('shared_libraries', [])
            except json.JSONDecodeError as e:
                # Log warning and backup corrupt file
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Corrupt config.json file: {str(e)}. Creating backup and returning empty list.")
                
                # Create backup of corrupt file
                backup_path = config_path.with_suffix('.json.bak')
                try:
                    import shutil
                    shutil.copy(config_path, backup_path)
                    logger.info(f"Backed up corrupt config to {backup_path}")
                except Exception as backup_error:
                    logger.error(f"Failed to backup corrupt config: {str(backup_error)}")
                
                return []
        return []
    
    @staticmethod
    def set_library_config(libraries):
        """Update the list of libraries to share in config.json."""
        config_path = Path(Config.CONFIG_FILE)
        data = {'shared_libraries': libraries}
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @staticmethod
    def validate_config():
        """Validate that all required configuration is present."""
        required_vars = {
            'SECRET_KEY': Config.SECRET_KEY,
            'PLEX_TOKEN': Config.PLEX_TOKEN,
            'PLEX_SERVER_NAME': Config.PLEX_SERVER_NAME,
            'ADMIN_USERNAME': Config.ADMIN_USERNAME,
            'ADMIN_PASSWORD_HASH': Config.ADMIN_PASSWORD_HASH
        }
        missing = [var for var, value in required_vars.items() if not value]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

