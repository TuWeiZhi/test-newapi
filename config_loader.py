import yaml
from pathlib import Path
from typing import Dict, Any


class ConfigLoader:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"配置文件不存在: {self.config_path}\n"
                f"请复制 config.yaml.example 为 config.yaml 并填写配置"
            )
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        self._validate_config(config)
        return config

    def _validate_config(self, config: Dict[str, Any]) -> None:
        if 'apis' not in config:
            raise ValueError("配置文件缺少 'apis' 部分")
        
        if not isinstance(config['apis'], list) or len(config['apis']) == 0:
            raise ValueError("apis 必须是非空列表")
        
        required_fields = ['name', 'url', 'api_key', 'model']
        for idx, api_config in enumerate(config['apis']):
            for field in required_fields:
                if field not in api_config:
                    raise ValueError(f"apis[{idx}] 缺少必需字段: {field}")
        
        if 'request_strategies' not in config:
            raise ValueError("配置文件缺少 'request_strategies' 部分")

    def get_apis_config(self) -> list:
        apis = self.config.get('apis', [])
        return [api for api in apis if api.get('enabled', True)]

    def get_strategies_config(self) -> list:
        return self.config.get('request_strategies', [])

    def get_logging_config(self) -> Dict[str, Any]:
        return self.config.get('logging', {
            'path': './logs',
            'level': 'INFO',
            'format': '%(asctime)s - %(levelname)s - %(message)s'
        })
