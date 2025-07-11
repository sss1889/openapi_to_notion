from notion_client import Client
from typing import Dict, List, Any, Union
import os
import time
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()


class NotionAPIClient:
    def __init__(self, token: str = None):
        self.token = token or os.getenv('NOTION_TOKEN')
        if not self.token:
            raise ValueError("Notion token is required. Set NOTION_TOKEN environment variable or pass token parameter.")
        self.client = Client(auth=self.token)
    
    def create_endpoint_documentation(self, page_id: str, endpoints: List[Dict[str, Any]], include_errors: bool = False, batch_size: int = 5, verify_page: bool = False) -> None:
        # Normalize page ID format (add hyphens if needed)
        page_id = self._normalize_page_id(page_id)
        
        # Optional page verification
        if verify_page:
            try:
                page = self.client.pages.retrieve(page_id)
                print(f"Successfully connected to page: {page.get('properties', {}).get('title', {}).get('title', [{}])[0].get('plain_text', 'Untitled')}")
            except Exception as e:
                print(f"Error accessing page {page_id}: {e}")
                raise
        else:
            print(f"Connecting to Notion page: {page_id}")
        
        # Process endpoints in batches with progress bar
        total_blocks = []
        
        with tqdm(total=len(endpoints), desc="Processing endpoints") as pbar:
            for endpoint in endpoints:
                blocks = self._create_endpoint_blocks(endpoint, include_errors)
                total_blocks.extend(blocks)
                pbar.update(1)
        
        # Append blocks in batches to avoid hitting API limits
        print(f"\nUploading {len(total_blocks)} blocks to Notion...")
        self._append_blocks_in_batches(page_id, total_blocks, batch_size)
    
    def _create_endpoint_blocks(self, endpoint: Dict[str, Any], include_errors: bool = False) -> List[Dict[str, Any]]:
        blocks = []
        
        # エンドポイント名（H2見出し）
        endpoint_title = f"{endpoint['method']} {endpoint['path']}"
        
        blocks.append({
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": endpoint_title}
                }]
            }
        })
        
        # サマリー（通常のテキスト）
        if endpoint['summary']:
            blocks.append({
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": endpoint['summary']}
                    }]
                }
            })
        
        # 説明
        if endpoint['description']:
            blocks.append({
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": endpoint['description']}
                    }]
                }
            })
        
        # タグ
        if endpoint['tags']:
            blocks.append({
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": f"Tags: {', '.join(endpoint['tags'])}"},
                        "annotations": {"italic": True}
                    }]
                }
            })
        
        # パラメータ
        if endpoint['parameters']:
            blocks.append({
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "Parameters"}
                    }]
                }
            })
            
            param_text = self._format_parameters(endpoint['parameters'])
            if len(param_text) > 2000:
                blocks.append({
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": "Parameters (truncated due to size):"},
                            "annotations": {"italic": True}
                        }]
                    }
                })
                self._add_large_code_block(blocks, param_text, "json")
            else:
                blocks.append({
                    "type": "code",
                    "code": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": param_text}
                        }],
                        "language": "json"
                    }
                })
        
        # リクエストボディ
        if endpoint['request_body'] and endpoint['request_body'].get('content'):
            blocks.append({
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "Request Body"}
                    }]
                }
            })
            
            if endpoint['request_body'].get('description'):
                blocks.append({
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": endpoint['request_body']['description']}
                        }]
                    }
                })
            
            for media_type, content in endpoint['request_body']['content'].items():
                if content.get('schema'):
                    schema_text = self._simplify_schema(content['schema'])
                    # Notion has a 2000 character limit for code blocks
                    if len(schema_text) > 2000:
                        blocks.append({
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{
                                    "type": "text",
                                    "text": {"content": "Schema (truncated due to size):"},
                                    "annotations": {"italic": True}
                                }]
                            }
                        })
                        # Split large schema into multiple blocks
                        self._add_large_code_block(blocks, schema_text, "json")
                    else:
                        blocks.append({
                            "type": "code",
                            "code": {
                                "rich_text": [{
                                    "type": "text",
                                    "text": {"content": schema_text}
                                }],
                                "language": "json"
                            }
                        })
        
        # レスポンス
        if endpoint['responses']:
            blocks.append({
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": "Responses"}
                    }]
                }
            })
            
            for status_code, response in endpoint['responses'].items():
                # Skip error responses if not requested
                if not include_errors and status_code.startswith(('4', '5')):
                    continue
                blocks.append({
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": f"Status Code: {status_code}"},
                            "annotations": {"bold": True}
                        }]
                    }
                })
                
                if response.get('description'):
                    blocks.append({
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{
                                "type": "text",
                                "text": {"content": response['description']}
                            }]
                        }
                    })
                
                for media_type, content in response.get('content', {}).items():
                    if content.get('schema'):
                        schema_text = self._simplify_schema(content['schema'])
                        # Notion has a 2000 character limit for code blocks
                        if len(schema_text) > 2000:
                            blocks.append({
                                "type": "paragraph",
                                "paragraph": {
                                    "rich_text": [{
                                        "type": "text",
                                        "text": {"content": "Schema (truncated due to size):"},
                                        "annotations": {"italic": True}
                                    }]
                                }
                            })
                            # Split large schema into multiple blocks
                            self._add_large_code_block(blocks, schema_text, "json")
                        else:
                            blocks.append({
                                "type": "code",
                                "code": {
                                    "rich_text": [{
                                        "type": "text",
                                        "text": {"content": schema_text}
                                    }],
                                    "language": "json"
                                }
                            })
        
        # 区切り線
        blocks.append({"type": "divider", "divider": {}})
        
        return blocks
    
    def _format_parameters(self, parameters: List[Dict[str, Any]]) -> str:
        import json
        formatted_params = {}
        for param in parameters:
            param_name = param['name']
            param_type = self._get_simple_type(param.get('schema', {}))
            
            if not param.get('required', False):
                param_type = f"{param_type} | Optional"
            
            # Add location info (path, query, header)
            param_location = param.get('in', '')
            if param_location:
                param_type = f"{param_type} ({param_location})"
            
            formatted_params[param_name] = param_type
        
        return json.dumps(formatted_params, indent=2, ensure_ascii=False)
    
    def _get_simple_type(self, schema: Dict[str, Any]) -> str:
        schema_type = schema.get('type', 'any')
        
        if schema_type == 'string':
            if 'enum' in schema:
                return f"enum({', '.join(repr(v) for v in schema['enum'])})"
            return "string"
        elif schema_type == 'integer':
            return "integer"
        elif schema_type == 'number':
            return "number"
        elif schema_type == 'boolean':
            return "boolean"
        elif schema_type == 'array':
            items = schema.get('items', {})
            item_type = self._get_simple_type(items)
            return f"[{item_type}]"
        elif schema_type == 'object':
            return "object"
        else:
            return schema_type
    
    def _format_schema(self, schema: Dict[str, Any]) -> str:
        import json
        return json.dumps(schema, indent=2, ensure_ascii=False)
    
    def _simplify_schema(self, schema: Dict[str, Any]) -> str:
        import json
        simplified = self._simplify_schema_recursive(schema)
        return json.dumps(simplified, indent=2, ensure_ascii=False)
    
    def _simplify_schema_recursive(self, schema: Dict[str, Any], required_fields: List[str] = None) -> Union[Dict, str, List]:
        if required_fields is None:
            required_fields = schema.get('required', [])
        
        # Handle references
        if '$ref' in schema:
            return "reference"
        
        schema_type = schema.get('type', 'object')
        
        if schema_type == 'object':
            properties = schema.get('properties', {})
            result = {}
            for key, value in properties.items():
                field_type = self._simplify_schema_recursive(value, required_fields)
                if key not in required_fields:
                    if isinstance(field_type, str):
                        field_type = f"{field_type} | Optional"
                    elif isinstance(field_type, dict):
                        # Mark nested object as optional
                        field_type = {**field_type, "__optional__": True}
                result[key] = field_type
            return result
        
        elif schema_type == 'array':
            items = schema.get('items', {})
            item_type = self._simplify_schema_recursive(items, required_fields)
            return [item_type]
        
        elif schema_type == 'string':
            if 'enum' in schema:
                return f"enum({', '.join(repr(v) for v in schema['enum'])})"
            return "string"
        
        elif schema_type == 'number':
            return "number"
        
        elif schema_type == 'integer':
            return "integer"
        
        elif schema_type == 'boolean':
            return "boolean"
        
        else:
            return schema_type
    
    def _add_large_code_block(self, blocks: List[Dict[str, Any]], content: str, language: str) -> None:
        # Split content into chunks of 1900 characters (leaving some margin)
        max_length = 1900
        lines = content.split('\n')
        current_chunk = []
        current_length = 0
        
        for line in lines:
            line_length = len(line) + 1  # +1 for newline
            if current_length + line_length > max_length and current_chunk:
                # Add current chunk as a code block
                chunk_text = '\n'.join(current_chunk)
                blocks.append({
                    "type": "code",
                    "code": {
                        "rich_text": [{
                            "type": "text",
                            "text": {"content": chunk_text}
                        }],
                        "language": language
                    }
                })
                current_chunk = [line]
                current_length = line_length
            else:
                current_chunk.append(line)
                current_length += line_length
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            blocks.append({
                "type": "code",
                "code": {
                    "rich_text": [{
                        "type": "text",
                        "text": {"content": chunk_text}
                    }],
                    "language": language
                }
            })
    
    def _normalize_page_id(self, page_id: str) -> str:
        # Remove any existing hyphens
        page_id = page_id.replace('-', '')
        
        # Add hyphens in the correct positions for Notion API
        if len(page_id) == 32:
            return f"{page_id[:8]}-{page_id[8:12]}-{page_id[12:16]}-{page_id[16:20]}-{page_id[20:]}"
        return page_id
    
    def _append_blocks_to_page(self, page_id: str, blocks: List[Dict[str, Any]]) -> None:
        # Notion APIは一度に最大100ブロックまでしか追加できない
        max_blocks_per_request = 100
        
        for i in range(0, len(blocks), max_blocks_per_request):
            chunk = blocks[i:i + max_blocks_per_request]
            self.client.blocks.children.append(
                block_id=page_id,
                children=chunk
            )
    
    def _append_blocks_in_batches(self, page_id: str, blocks: List[Dict[str, Any]], batch_size: int) -> None:
        # Notion APIは一度に最大100ブロックまでしか追加できない
        max_blocks_per_request = 100
        
        # プログレスバーを表示
        with tqdm(total=len(blocks), desc="Uploading blocks") as pbar:
            for i in range(0, len(blocks), max_blocks_per_request):
                chunk = blocks[i:i + max_blocks_per_request]
                try:
                    self.client.blocks.children.append(
                        block_id=page_id,
                        children=chunk
                    )
                    pbar.update(len(chunk))
                    
                    # APIレート制限を避けるため少し待機
                    if i + max_blocks_per_request < len(blocks):
                        time.sleep(0.5)
                        
                except Exception as e:
                    print(f"\\nError uploading blocks {i}-{i+len(chunk)}: {e}")
                    # 失敗した場合は少し待って再試行
                    time.sleep(2)
                    try:
                        self.client.blocks.children.append(
                            block_id=page_id,
                            children=chunk
                        )
                        pbar.update(len(chunk))
                    except Exception as e2:
                        print(f"\\nFailed to upload blocks after retry: {e2}")
                        raise