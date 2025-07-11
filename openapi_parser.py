import yaml
from typing import Dict, List, Any
import json


class OpenAPIParser:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.spec = self._load_spec()
        
    def _load_spec(self) -> Dict[str, Any]:
        with open(self.file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    
    def get_endpoints(self) -> List[Dict[str, Any]]:
        endpoints = []
        paths = self.spec.get('paths', {})
        
        for path, path_item in paths.items():
            for method, operation in path_item.items():
                if method in ['get', 'post', 'put', 'delete', 'patch', 'options', 'head']:
                    endpoint = self._parse_endpoint(path, method, operation)
                    endpoints.append(endpoint)
        
        return endpoints
    
    def _parse_endpoint(self, path: str, method: str, operation: Dict[str, Any]) -> Dict[str, Any]:
        endpoint = {
            'path': path,
            'method': method.upper(),
            'summary': operation.get('summary', ''),
            'description': operation.get('description', ''),
            'operation_id': operation.get('operationId', ''),
            'tags': operation.get('tags', []),
            'parameters': self._parse_parameters(operation.get('parameters', [])),
            'request_body': self._parse_request_body(operation.get('requestBody', {})),
            'responses': self._parse_responses(operation.get('responses', {}))
        }
        
        return endpoint
    
    def _parse_parameters(self, parameters: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        parsed_params = []
        for param in parameters:
            if '$ref' in param:
                param = self._resolve_ref(param['$ref'])
            
            parsed_param = {
                'name': param.get('name', ''),
                'in': param.get('in', ''),
                'required': param.get('required', False),
                'description': param.get('description', ''),
                'schema': param.get('schema', {})
            }
            parsed_params.append(parsed_param)
        
        return parsed_params
    
    def _parse_request_body(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        if not request_body:
            return {}
        
        if '$ref' in request_body:
            request_body = self._resolve_ref(request_body['$ref'])
        
        content = request_body.get('content', {})
        parsed_body = {
            'description': request_body.get('description', ''),
            'required': request_body.get('required', False),
            'content': {}
        }
        
        for media_type, media_type_obj in content.items():
            schema = media_type_obj.get('schema', {})
            if '$ref' in schema:
                schema = self._resolve_ref(schema['$ref'])
            parsed_body['content'][media_type] = {
                'schema': schema,
                'example': media_type_obj.get('example', {})
            }
        
        return parsed_body
    
    def _parse_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        parsed_responses = {}
        
        for status_code, response in responses.items():
            if '$ref' in response:
                response = self._resolve_ref(response['$ref'])
            
            parsed_response = {
                'description': response.get('description', ''),
                'content': {}
            }
            
            content = response.get('content', {})
            for media_type, media_type_obj in content.items():
                schema = media_type_obj.get('schema', {})
                if '$ref' in schema:
                    schema = self._resolve_ref(schema['$ref'])
                parsed_response['content'][media_type] = {
                    'schema': schema,
                    'example': media_type_obj.get('example', {})
                }
            
            parsed_responses[status_code] = parsed_response
        
        return parsed_responses
    
    def _resolve_ref(self, ref: str) -> Dict[str, Any]:
        parts = ref.split('/')
        if parts[0] != '#':
            raise ValueError(f"External references not supported: {ref}")
        
        current = self.spec
        for part in parts[1:]:
            current = current.get(part, {})
        
        return current
    
    def format_schema_as_json(self, schema: Dict[str, Any]) -> str:
        return json.dumps(schema, indent=2, ensure_ascii=False)