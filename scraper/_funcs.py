import os
import yaml

def load_config(file_path=None):
    """Load configuration from environment variables if available; otherwise, load from YAML file."""
    if file_path:
        with open(file_path, "r") as file:
            return yaml.safe_load(file)
        
    config_keys = [
        "BOOKING_URL", "SPORTS_URL", "FITNESS_URL", 
        "EMAIL", "DISCORD_POSTS", "DISCORD_LOGS", "DISCORD_UID"
    ]
    config = {key: os.getenv(key) for key in config_keys}
    
    if None in config.values():
        raise ValueError("Missing environment variables for configuration.")
    
    return config


