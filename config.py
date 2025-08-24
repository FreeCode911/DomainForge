import os
from dotenv import load_dotenv

load_dotenv()

# Core Settings
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "!")  # Default to "!"

# Admin Settings
ADMIN_USER_IDS = [int(user_id) for user_id in os.getenv("ADMIN_USER_IDS", "").split(",") if user_id]
ADMIN_ROLE_IDS = [int(role_id) for role_id in os.getenv("ADMIN_ROLE_IDS", "").split(",") if role_id]

# Feature Flags
ENABLE_SUBDOMAIN_CREATION = os.getenv("ENABLE_SUBDOMAIN_CREATION", "True").lower() == "true"
ENABLE_PROXY_TOGGLE = os.getenv("ENABLE_PROXY_TOGGLE", "True").lower() == "true"
SUBDOMAIN_CREATION_ROLES = [int(role_id) for role_id in os.getenv("SUBDOMAIN_CREATION_ROLES", "").split(",") if role_id]
ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID", 0))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Cloudflare Settings
DOMAINS = ["lykcloud.com", "example.org", "example.net"]
RECORD_TYPES = ["A", "AAAA", "CNAME", "TXT"]

# Define the features for each record type
RECORD_FEATURES = {
    "SRV": ["priority", "weight", "port", "target" ],
    # Add more record types and their features as needed
}