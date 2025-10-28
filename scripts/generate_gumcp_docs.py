import asyncio
import os
import json
import sys
from datetime import datetime
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Gumloop user ID from environment
GUMCP_CREDENTIALS = os.getenv("GUMCP_CREDENTIALS")

if not GUMCP_CREDENTIALS:
    print("ERROR: GUMCP_CREDENTIALS environment variable not set.")
    print("Please set it to use guMCP integrations.")
    exit(1)


def read_integrations_list():
    """Read available integrations from gumcp_list.txt"""
    try:
        with open("resources/gumcp_docs/gumcp_list.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()

        integrations = []
        for line in lines:
            # Remove comments and empty lines, strip whitespace and '- '
            line = line.strip()
            if line and not line.startswith("#"):
                if line.startswith("- "):
                    line = line[2:]  # Remove '- ' prefix
                integrations.append(line)

        return integrations
    except FileNotFoundError:
        print(
            "ERROR: gumcp_list.txt not found. Please create it with available integrations."
        )
        return []
    except Exception as e:
        print(f"Error reading gumcp_list.txt: {e}")
        return []


def generate_documentation(tools: list, integration_name: str) -> str:
    """Generate formatted documentation for discovered tools"""
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    doc = f"# {integration_name.title()} guMCP Tools Documentation\n\n"
    doc += f"*Generated on: {current_date}*\n\n"
    doc += f"## Available Tools ({len(tools)} total)\n\n"

    for i, tool in enumerate(tools, 1):
        doc += f"### {i}. {tool.name}\n"
        doc += f"- **Description**: {tool.description}\n"
        doc += f"- **Parameters Schema**:\n"
        doc += f"```json\n"
        doc += f"{json.dumps(tool.args, indent=2)}\n"
        doc += f"```\n\n"

    return doc


async def discover_and_document_tools(integration_name: str, user_id: str):
    """Discover tools and generate documentation file"""
    try:
        print(f"Discovering {integration_name} guMCP tools for user: {user_id}")

        # Initialize guMCP client
        client = MultiServerMCPClient(
            {
                integration_name: {
                    "transport": "streamable_http",
                    "url": f"https://mcp.gumloop.com/{integration_name}/{user_id}/mcp",
                }
            }
        )

        # Get all available tools
        tools = await client.get_tools()

        print(f"\n=== Found {len(tools)} {integration_name} guMCP Tools ===\n")

        for i, tool in enumerate(tools, 1):
            print(f"{i}. Tool Name: {tool.name}")
            print(f"   Description: {tool.description}")
            print(f"   Args Schema: {json.dumps(tool.args, indent=2)}")
            print("-" * 80)

        # Generate documentation
        documentation = generate_documentation(tools, integration_name)

        # Write to file
        output_file = f"resources/gumcp_docs/gumcp_{integration_name}_docs.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(documentation)

        print(f"\nDocumentation generated: {output_file}")
        return tools

    except Exception as e:
        print(f"Error discovering tools for {integration_name}: {e}")
        return []


async def main():
    """Main function to discover all integrations from gumcp_list.txt"""
    integrations = read_integrations_list()

    if not integrations:
        print("No integrations found in gumcp_list.txt")
        return

    print(
        f"Found {len(integrations)} integrations to document: {', '.join(integrations)}"
    )

    # Handle command line arguments
    if len(sys.argv) > 1:
        selected_integration = sys.argv[1]
        if selected_integration in integrations:
            print(f"Selected integration: {selected_integration}")
            await discover_and_document_tools(selected_integration, GUMCP_CREDENTIALS)
        else:
            print(
                f"Integration '{selected_integration}' not found. Available: {', '.join(integrations)}"
            )
    else:
        # Generate documentation for all integrations by default
        print(f"Generating documentation for all integrations...")
        for integration in integrations:
            await discover_and_document_tools(integration, GUMCP_CREDENTIALS)


# Run the discovery and documentation
if __name__ == "__main__":
    asyncio.run(main())
