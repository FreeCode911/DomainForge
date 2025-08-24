import aiohttp
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger('cloudflare')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='cloudflare.log', encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
API_BASE_URL = "https://api.cloudflare.com/client/v4"

async def create_subdomain(domain, record_type, record_content, proxy_status, additional_features):
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        try:
            # Get the zone ID for the domain
            async with session.get(f"{API_BASE_URL}/zones?name={domain}", headers=headers) as response:
                zones = await response.json()
                if not zones["success"]:
                    logger.error(f"Failed to get zone ID for domain {domain}: {zones['errors']}")
                    return False, f"Failed to get zone ID for domain {domain}"
                zone_id = zones["result"][0]["id"]
            
            # Create the DNS record
            subdomain, content = record_content.split(",")
            data = {
                "type": record_type,
                "name": subdomain,
                "content": content,
                "proxied": proxy_status
            }
            
            # Add additional features to the data
            for feature, value in additional_features.items():
                data[feature] = value
            
            async with session.post(f"{API_BASE_URL}/zones/{zone_id}/dns_records", headers=headers, json=data) as response:
                result = await response.json()
                if not result["success"]:
                    logger.error(f"Failed to create DNS record: {result['errors']}")
                    return False, f"Failed to create DNS record: {result['errors']}"
                logger.info(f"Successfully created DNS record for {subdomain}")
                return True, f"Successfully created DNS record for {subdomain}"

        except Exception as e:
            logger.error(f"An error occurred while creating subdomain: {str(e)}")
            return False, f"An error occurred: {str(e)}"

async def get_user_subdomains(user_id):
    # This function is not implemented as we're using local JSON storage
    # You can implement this if you want to fetch subdomains from Cloudflare directly
    pass

async def delete_subdomain(domain):
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }
        
        try:
            # Get the zone ID for the domain
            zone_name = '.'.join(domain.split('.')[-2:])
            async with session.get(f"{API_BASE_URL}/zones?name={zone_name}", headers=headers) as response:
                zones = await response.json()
                if not zones["success"] or not zones["result"]:
                    logger.error(f"No zones found for domain {zone_name}")
                    return False
                zone_id = zones["result"][0]["id"]

            # Get the DNS record ID
            async with session.get(f"{API_BASE_URL}/zones/{zone_id}/dns_records?name={domain}", headers=headers) as response:
                records = await response.json()
                if not records["success"] or not records["result"]:
                    logger.error(f"No DNS record found for domain {domain}")
                    return False
                record_id = records["result"][0]["id"]

            # Delete the DNS record
            async with session.delete(f"{API_BASE_URL}/zones/{zone_id}/dns_records/{record_id}", headers=headers) as response:
                result = await response.json()
                if not result["success"]:
                    logger.error(f"Failed to delete DNS record for {domain}: {result['errors']}")
                    return False
                logger.info(f"Successfully deleted DNS record for {domain}")
                return True

        except Exception as e:
            logger.error(f"An error occurred while deleting subdomain: {str(e)}")
            return False

async def toggle_proxy_status(domain):
    async with aiohttp.ClientSession() as session:
        headers = {
            "Authorization": f"Bearer {API_TOKEN}",
            "Content-Type": "application/json"
        }

        try:
            # Get the zone ID for the domain
            zone_name = '.'.join(domain.split('.')[-2:])
            async with session.get(f"{API_BASE_URL}/zones?name={zone_name}", headers=headers) as response:
                zones = await response.json()
                if not zones["success"] or not zones["result"]:
                    logger.error(f"No zones found for domain {zone_name}")
                    return False, "No zones found for domain."
                zone_id = zones["result"][0]["id"]

            # Get the DNS record ID and current proxy status
            async with session.get(f"{API_BASE_URL}/zones/{zone_id}/dns_records?name={domain}", headers=headers) as response:
                records = await response.json()
                if not records["success"] or not records["result"]:
                    logger.error(f"No DNS record found for domain {domain}")
                    return False, "No DNS record found for domain."
                record_id = records["result"][0]["id"]
                current_proxied = records["result"][0]["proxied"]

            # Toggle the proxy status
            new_proxied = not current_proxied

            data = {
                "proxied": new_proxied
            }

            async with session.patch(f"{API_BASE_URL}/zones/{zone_id}/dns_records/{record_id}", headers=headers, json=data) as response:
                result = await response.json()
                if not result["success"]:
                    logger.error(f"Failed to toggle proxy status for {domain}: {result['errors']}")
                    return False, f"Failed to toggle proxy status: {result['errors']}"

                logger.info(f"Successfully toggled proxy status for {domain} to {new_proxied}")
                return True, f"Proxy status toggled to { 'enabled' if new_proxied else 'disabled' }."

        except Exception as e:
            logger.error(f"An error occurred while toggling proxy status: {str(e)}")
            return False, f"An error occurred: {str(e)}"
