import requests
import json
from typing import Dict, Any, Optional


class NewAPIClient:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config.get('name', 'Unknown')
        self.url = config['url'].rstrip('/') + '/chat/completions'
        self.api_key = config['api_key']
        self.model = config['model']
        self.max_tokens = config.get('max_tokens', 100)
        self.temperature = config.get('temperature', 0.7)
        
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
        }

    def _parse_sse_response(self, text: str) -> Dict[str, Any]:
        """解析 SSE 流式响应，合并所有 chunk 的内容"""
        content_parts = []
        model = self.model
        usage = None
        
        for line in text.split('\n'):
            line = line.strip()
            if not line or not line.startswith('data:'):
                continue
            
            data_str = line[5:].strip()
            if data_str == '[DONE]':
                break
            
            try:
                chunk = json.loads(data_str)
                if 'model' in chunk:
                    model = chunk['model']
                if 'usage' in chunk and chunk['usage']:
                    usage = chunk['usage']
                if 'choices' in chunk and chunk['choices']:
                    delta = chunk['choices'][0].get('delta', {})
                    if 'content' in delta and delta['content']:
                        content_parts.append(delta['content'])
            except json.JSONDecodeError:
                continue
        
        if not content_parts:
            raise ValueError("No content found in SSE response")
        
        return {
            'content': ''.join(content_parts),
            'model': model,
            'usage': usage or {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0}
        }

    def send_request(self, prompt: str) -> Optional[Dict[str, Any]]:
        try:
            payload = {
                'model': self.model,
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': self.max_tokens,
                'temperature': self.temperature,
                'stream': False
            }
            
            response = requests.post(
                self.url,
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                response_text = response.text
                
                if response_text.startswith('data:'):
                    try:
                        parsed = self._parse_sse_response(response_text)
                        return {
                            'success': True,
                            'api_name': self.name,
                            'prompt': prompt,
                            'response': parsed['content'],
                            'usage': parsed['usage'],
                            'model': parsed['model']
                        }
                    except Exception as sse_err:
                        return {
                            'success': False,
                            'api_name': self.name,
                            'prompt': prompt,
                            'error': f"SSE parse error: {sse_err}. Raw: {response_text[:300]}"
                        }
                
                try:
                    data = response.json()
                except Exception as json_err:
                    raw_text = response_text[:500] if response_text else "(empty response)"
                    return {
                        'success': False,
                        'api_name': self.name,
                        'prompt': prompt,
                        'error': f"JSON parse error: {json_err}. Raw response: {raw_text}"
                    }
                
                usage = data.get('usage', {})
                if not usage:
                    usage = {
                        'prompt_tokens': 0,
                        'completion_tokens': 0,
                        'total_tokens': 0
                    }
                
                return {
                    'success': True,
                    'api_name': self.name,
                    'prompt': prompt,
                    'response': data['choices'][0]['message']['content'],
                    'usage': usage,
                    'model': data.get('model', self.model)
                }
            else:
                error_detail = ""
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        err = error_data['error']
                        error_detail = err.get('message', '') or err.get('msg', '') or str(err)
                    else:
                        error_detail = response.text[:300]
                except:
                    error_detail = response.text[:300] if response.text else "(empty response)"
                
                return {
                    'success': False,
                    'api_name': self.name,
                    'prompt': prompt,
                    'error': f"HTTP {response.status_code}: {error_detail}"
                }
        
        except requests.exceptions.SSLError as e:
            return {
                'success': False,
                'api_name': self.name,
                'prompt': prompt,
                'error': f"SSL Error: {str(e)}"
            }
        except requests.exceptions.Timeout as e:
            return {
                'success': False,
                'api_name': self.name,
                'prompt': prompt,
                'error': f"Timeout: {str(e)}"
            }
        except requests.exceptions.ConnectionError as e:
            return {
                'success': False,
                'api_name': self.name,
                'prompt': prompt,
                'error': f"Connection Error: {str(e)}"
            }
        except Exception as e:
            return {
                'success': False,
                'api_name': self.name,
                'prompt': prompt,
                'error': f"{type(e).__name__}: {str(e)}"
            }
