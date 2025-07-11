#!/usr/bin/env python3
import argparse
import sys
from openapi_parser import OpenAPIParser
from notion_client import NotionAPIClient
import logging


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def main():
    logger = setup_logging()
    
    parser = argparse.ArgumentParser(
        description='Convert OpenAPI YAML specification to Notion page documentation'
    )
    parser.add_argument(
        '--openapi',
        required=True,
        help='Path to OpenAPI YAML file'
    )
    parser.add_argument(
        '--notion-page-id',
        required=True,
        help='Notion page ID where the documentation will be created'
    )
    parser.add_argument(
        '--notion-token',
        help='Notion integration token (can also be set via NOTION_TOKEN env variable)'
    )
    
    args = parser.parse_args()
    
    try:
        logger.info(f"Loading OpenAPI specification from: {args.openapi}")
        openapi_parser = OpenAPIParser(args.openapi)
        endpoints = openapi_parser.get_endpoints()
        logger.info(f"Found {len(endpoints)} endpoints")
        
        logger.info("Connecting to Notion API")
        notion_client = NotionAPIClient(token=args.notion_token)
        
        logger.info(f"Creating documentation in Notion page: {args.notion_page_id}")
        notion_client.create_endpoint_documentation(args.notion_page_id, endpoints)
        
        logger.info("Documentation created successfully!")
        
    except FileNotFoundError:
        logger.error(f"OpenAPI file not found: {args.openapi}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()