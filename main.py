#!/usr/bin/env python3
import sys
from pathlib import Path
from config_loader import ConfigLoader
from newapi_client import NewAPIClient
from logger import APILogger
from strategies import NewsStrategy, WebpageStrategy, RandomQuestionStrategy


def create_strategy(strategy_config):
    strategy_type = strategy_config.get('type')
    
    if strategy_type == 'news':
        return NewsStrategy(strategy_config)
    elif strategy_type == 'webpage':
        return WebpageStrategy(strategy_config)
    elif strategy_type == 'random_question':
        return RandomQuestionStrategy(strategy_config)
    else:
        return None


def run_keeper_task():
    config_loader = ConfigLoader('config.yaml')
    logger = APILogger(config_loader.get_logging_config())
    
    logger.log_info("=" * 50)
    logger.log_info("NewAPI Keeper Started")
    logger.log_info("=" * 50)
    
    apis_config = config_loader.get_apis_config()
    if not apis_config:
        logger.log_error("No enabled APIs found in configuration")
        return
    
    logger.log_info(f"Found {len(apis_config)} enabled API(s)")
    
    strategies_config = config_loader.get_strategies_config()
    strategies_config.sort(key=lambda x: x.get('priority', 999))
    
    prompt = None
    used_strategy = None
    
    for strategy_config in strategies_config:
        if not strategy_config.get('enabled', True):
            continue
        
        strategy = create_strategy(strategy_config)
        if not strategy:
            continue
        
        strategy_type = strategy_config.get('type')
        logger.log_info(f"Trying strategy: {strategy_type}")
        
        try:
            prompt = strategy.generate_prompt()
            if prompt:
                used_strategy = strategy_type
                logger.log_info(f"Strategy {strategy_type} succeeded")
                break
            else:
                logger.log_strategy_failure(strategy_type, "No prompt generated")
        except Exception as e:
            logger.log_strategy_failure(strategy_type, str(e))
    
    if not prompt:
        logger.log_error("All strategies failed, no prompt generated")
        return
    
    logger.log_info(f"Generated prompt using strategy: {used_strategy}")
    logger.log_info("=" * 50)
    
    success_count = 0
    failed_count = 0
    
    for api_config in apis_config:
        api_name = api_config.get('name', 'Unknown')
        logger.log_info(f"Sending request to API: {api_name}")
        
        try:
            client = NewAPIClient(api_config)
            result = client.send_request(prompt)
            logger.log_request(used_strategy, result)
            
            if result.get('success'):
                success_count += 1
            else:
                failed_count += 1
        except Exception as e:
            logger.log_error(f"Failed to send request to {api_name}: {str(e)}")
            failed_count += 1
    
    logger.log_info("=" * 50)
    logger.log_info(f"Summary: {success_count} succeeded, {failed_count} failed")
    logger.log_info("=" * 50)


def main():
    try:
        run_keeper_task()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
