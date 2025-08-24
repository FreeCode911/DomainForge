# DomainForge v1.1

<!-- Add project badges here -->
<!-- Example: [![Build Status](https://travis-ci.org/your-username/domainforge.svg?branch=main)](https://travis-ci.org/your-username/domainforge) -->

<p align="center">
  <img src="https://github.com/FreeCode911/DomainForge/blob/main/views/ultra_realistic_1726222400.png?raw=true" alt="DomainForge Logo" width="200"/>
</p>

<!-- Add a short GIF showing the bot in action here -->
<!-- Example: <p align="center"><img src="path/to/animated_gif.gif" alt="DomainForge Demo" width="400"/></p> -->

## Project Summary

DomainForge is a powerful and user-friendly Discord bot designed to streamline Cloudflare subdomain management directly from your Discord server. It empowers users to effortlessly create, manage, and organize subdomains, while providing administrators with robust control and monitoring capabilities. Say goodbye to tedious manual processes and embrace a seamless, Discord-integrated DNS management experience!

## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Commands](#commands)
- [Setup for Development](#setup-for-development)
  - [Environment Variables](#environment-variables)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Features

- **Easy Subdomain Creation**: Set up new subdomains with simple Discord commands, specifying the record type (A, CNAME, TXT, etc.).
- **Role-Based Permissions**: Control who can create subdomains using Discord roles for enhanced security.
- **Centralized Management**: Manage subdomains and admin settings from a single, interactive command.
- **Cloudflare Integration**: Seamless connection with Cloudflare for reliable DNS management.

## Getting Started

### Prerequisites

- A Discord server where you have administrative privileges.
- A Cloudflare account with a domain you want to manage.

### Installation

1.  [Invite DomainForge](https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=2147483648&scope=bot%20applications.commands) to your Discord server.
2.  Use the `/create_subdomain` command to start creating subdomains.
3.  Follow the interactive prompts to specify domain, record type, and other details.

## Commands

- `/create_subdomain`: Start the subdomain creation process (specify record type).
- `/manage_subdomain`: Manage a specified subdomain.
- `/admin_manage`: (Admin only) Access administrative functions.
- `/whois`: (Admin only) Look up the owner of a specific subdomain.
- `/request_subdomain_role`: Request the subdomain creation role.

## Setup for Development

1.  Clone this repository:

    ```bash
    git clone https://github.com/your-username/domainforge.git
    ```

2.  Install dependencies:

    ```bash
    cd domainforge
    pip install -r requirements.txt
    ```

### Environment Variables

3.  Set up your `.env` file with the following variables:

    ```env
    # Create a .env file in the same directory as bot.py
    # Add the following variables to the .env file:

    # Discord Bot Token: Obtain this from the Discord Developer Portal (https://discord.com/developers/applications)
    DISCORD_BOT_TOKEN=Your Discord bot token

    # Cloudflare API Token: Generate a token with Edit zone DNS permission (Permissions - Zone.DNS,Zone.DNS) ( Resources - All zones ) at https://dash.cloudflare.com/profile/api-tokens
    CLOUDFLARE_API_TOKEN=Your Cloudflare API token

    # Comma-separated list of role IDs that can create subdomains. To get a role ID, enable developer mode in Discord (Settings > Advanced) and right-click the role and select "Copy ID"
    SUBDOMAIN_CREATION_ROLES=Comma-separated list of role IDs that can create subdomains

    # The channel ID where subdomain role requests are sent. To get a channel ID, enable developer mode in Discord (Settings > Advanced) and right-click the channel and select "Copy ID"
    ADMIN_CHANNEL_ID=The channel ID where subdomain role requests are sent
    ```

4.  Run the bot:

    ```bash
    python bot.py
    ```

## Contributing

We welcome contributions to DomainForge! Please feel free to submit issues, fork the repository and send pull requests!

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Support

If you need help or have any questions, please join our [support server](https://discord.gg/your-support-server-invite).

---

<p align="center">
Made with ❤ by LegendYt4k
</p>
