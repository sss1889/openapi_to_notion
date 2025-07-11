from notion_client import Client
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

load_dotenv()


class NotionAPIClient:
    def __init__(self, token: str = None):
        self.token = token or os.getenv('NOTION_TOKEN')
        if not self.token:
            raise ValueError("Notion token is required. Set NOTION_TOKEN environment variable or pass token parameter.")
        self.client = Client(auth=self.token)
    
    def create_endpoint_documentation(self, page_id: str, endpoints: List[Dict[str, Any]]) -> None:
        for endpoint in endpoints:
            blocks = self._create_endpoint_blocks(endpoint)
            self._append_blocks_to_page(page_id, blocks)
    
    def _create_endpoint_blocks(self, endpoint: Dict[str, Any]) -> List[Dict[str, Any]]:
        blocks = []
        
        # エンドポイント名（H2見出し）
        endpoint_title = f"{endpoint['method']} {endpoint['path']}"
        if endpoint['summary']:
            endpoint_title += f" - {endpoint['summary']}"
        
        blocks.append({
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{
                    "type": "text",
                    "text": {"content": endpoint_title}
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
                    blocks.append({
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{
                                "type": "text",
                                "text": {"content": f"Content-Type: {media_type}"},
                                "annotations": {"bold": True}
                            }]
                        }
                    })
                    
                    schema_text = self._format_schema(content['schema'])
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
                        blocks.append({
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{
                                    "type": "text",
                                    "text": {"content": f"Content-Type: {media_type}"},
                                    "annotations": {"italic": True}
                                }]
                            }
                        })
                        
                        schema_text = self._format_schema(content['schema'])
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
        formatted_params = []
        for param in parameters:
            formatted_param = {
                "name": param['name'],
                "in": param['in'],
                "required": param['required'],
                "description": param['description'],
                "schema": param['schema']
            }
            formatted_params.append(formatted_param)
        return json.dumps(formatted_params, indent=2, ensure_ascii=False)
    
    def _format_schema(self, schema: Dict[str, Any]) -> str:
        import json
        return json.dumps(schema, indent=2, ensure_ascii=False)
    
    def _append_blocks_to_page(self, page_id: str, blocks: List[Dict[str, Any]]) -> None:
        # Notion APIは一度に最大100ブロックまでしか追加できない
        max_blocks_per_request = 100
        
        for i in range(0, len(blocks), max_blocks_per_request):
            chunk = blocks[i:i + max_blocks_per_request]
            self.client.blocks.children.append(
                block_id=page_id,
                children=chunk
            )