import random
from typing import Optional
from .base_strategy import BaseStrategy


class RandomQuestionStrategy(BaseStrategy):
    def generate_prompt(self) -> Optional[str]:
        try:
            config = self.config.get('config', {})
            templates = config.get('question_templates', [])
            variables = config.get('variables', )
            
            if not templates:
                return None
            
            template = random.choice(templates)
            
            prompt = template
            for var_name, var_values in variables.items():
                if f'{{{var_name}}}' in template:
                    if isinstance(var_values, list) and len(var_values) == 2:
                        value = random.randint(var_values[0], var_values[1])
                    elif isinstance(var_values, list):
                        value = random.choice(var_values)
                    else:
                        value = var_values
                    
                    prompt = prompt.replace(f'{{{var_name}}}', str(value))
            
            return prompt
        
        except Exception as e:
            return None
