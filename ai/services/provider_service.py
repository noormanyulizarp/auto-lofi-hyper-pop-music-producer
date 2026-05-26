import httpx
import asyncio
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from loguru import logger

from ..config.provider_config import provider_config
from ..models.responses import TaskStatus

class ProviderService:
    """Custom provider service using PicoClaw's configuration"""
    
    def __init__(self):
        self.config = provider_config
        self.models = self.config.MODELS
        self.active_models = {}
        self.client = httpx.AsyncClient(
            timeout=self.config.TIMEOUT_SECONDS
        )
        
    async def initialize(self):
        """Initialize provider service and check model availability"""
        logger.info("Initializing provider service with PicoClaw configuration")
        
        # Check all models availability
        for model_name, model_config in self.models.items():
            try:
                is_available = await self._check_model_availability(model_config)
                self.active_models[model_name] = {
                    **model_config,
                    "available": is_available,
                    "last_check": datetime.utcnow()
                }
                logger.info(f"Model {model_name}: {'✅ Available' if is_available else '❌ Unavailable'}")
            except Exception as e:
                logger.error(f"Failed to check model {model_name}: {str(e)}")
                self.active_models[model_name] = {
                    **model_config,
                    "available": False,
                    "last_check": datetime.utcnow(),
                    "error": str(e)
                }
    
    async def call_model(
        self, 
        model_name: str, 
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        """Call a specific model with fallback support"""
        
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")
        
        model_config = self.models[model_name]
        
        # Try the requested model first
        try:
            result = await self._make_api_call(model_config, messages, **kwargs)
            logger.info(f"Successfully called model: {model_name}")
            return result
            
        except Exception as e:
            logger.warning(f"Model {model_name} failed: {str(e)}")
            
            # Try fallback models if enabled
            if self.config.FALLBACK_ENABLED and model_config.get("fallbacks"):
                for fallback_model in model_config["fallbacks"]:
                    try:
                        logger.info(f"Trying fallback model: {fallback_model}")
                        fallback_config = self.models[fallback_model]
                        result = await self._make_api_call(fallback_config, messages, **kwargs)
                        logger.info(f"Successfully used fallback: {fallback_model}")
                        return {
                            **result,
                            "fallback_used": fallback_model,
                            "original_model": model_name
                        }
                    except Exception as fallback_error:
                        logger.warning(f"Fallback {fallback_model} also failed: {str(fallback_error)}")
                        continue
            
            # If all fallbacks failed, raise original error
            raise Exception(f"All models failed for {model_name}. Last error: {str(e)}")
    
    async def get_best_model_for_task(self, task_type: str) -> str:
        """Get the best model for a specific task type"""
        
        task_model_mapping = {
            "music_generation": "openrouter-glm-air",
            "lyrical_composition": "openrouter-cobuddy", 
            "music_theory": "openrouter-trinity-thinking",
            "pattern_recognition": "openrouter-nemotron-30b",
            "quick_ideas": "openrouter-nemotron-9b",
            "deep_analysis": "openrouter-nemotron-120b",
            "general": "openrouter-gpt-oss-20b",
            "long_form": "openrouter-gpt-oss-120b"
        }
        
        preferred_model = task_model_mapping.get(task_type, self.config.DEFAULT_MODEL)
        
        # Check if preferred model is available
        if preferred_model in self.active_models and self.active_models[preferred_model].get("available"):
            return preferred_model
        
        # Find first available model
        for model_name, model_info in self.active_models.items():
            if model_info.get("available"):
                return model_name
        
        # If no models available, return default anyway
        return preferred_model
    
    async def call_model_by_task(
        self, 
        task_type: str, 
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        """Call the best model for a specific task"""
        model_name = await self.get_best_model_for_task(task_type)
        return await self.call_model(model_name, messages, **kwargs)
    
    async def _make_api_call(
        self, 
        model_config: Dict[str, Any], 
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Dict[str, Any]:
        """Make actual API call to the model"""
        
        # Prepare headers
        headers = {
            "Authorization": f"Bearer {self.config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://auto-music-producer.local",  # OpenRouter requires this
            "X-Title": "Auto Music Producer"
        }
        
        # Prepare request payload
        payload = {
            "model": model_config["model"],
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", model_config.get("max_tokens", 2048)),
            "temperature": kwargs.get("temperature", model_config.get("temperature", 0.7)),
            **kwargs
        }
        
        # Make API call
        response = await self.client.post(
            f"{model_config['api_base']}/chat/completions",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            error_text = response.text
            logger.error(f"API call failed: {response.status_code} - {error_text}")
            raise Exception(f"API call failed: {response.status_code} - {error_text}")
        
        result = response.json()
        
        # Extract and return the response text
        return {
            "model": model_config["model"],
            "model_name": list(self.models.keys())[list(self.models.values()).index(model_config)],
            "content": result["choices"][0]["message"]["content"],
            "usage": result.get("usage", {}),
            "timestamp": datetime.utcnow().isoformat(),
            "provider": model_config["provider"],
            "specialty": model_config.get("specialty", "general")
        }
    
    async def _check_model_availability(self, model_config: Dict[str, Any]) -> bool:
        """Check if a model is available"""
        try:
            # Simple test call to check availability
            test_messages = [{"role": "user", "content": "Hello"}]
            
            headers = {
                "Authorization": f"Bearer {self.config.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model_config["model"],
                "messages": test_messages,
                "max_tokens": 10,
                "temperature": 0.7
            }
            
            response = await self.client.post(
                f"{model_config['api_base']}/chat/completions",
                headers=headers,
                json=payload
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.warning(f"Model availability check failed: {str(e)}")
            return False
    
    async def get_model_status(self) -> Dict[str, Any]:
        """Get status of all models"""
        return {
            "total_models": len(self.models),
            "active_models": len([m for m in self.active_models.values() if m.get("available")]),
            "models": {
                name: {
                    "available": info.get("available", False),
                    "specialty": info.get("specialty", "general"),
                    "model": info.get("model", "unknown"),
                    "last_check": info.get("last_check").isoformat() if info.get("last_check") else None
                }
                for name, info in self.active_models.items()
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    async def call_web_search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Call GLM web search service"""
        try:
            # Implementation for web search using MCP-style call
            payload = {
                "query": query,
                "max_results": max_results
            }
            
            headers = {
                "Authorization": self.config.GLM_API_TOKEN,
                "Content-Type": "application/json"
            }
            
            response = await self.client.post(
                self.config.GLM_WEB_SEARCH_URL,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "query": query
                }
            else:
                logger.error(f"Web search failed: {response.status_code}")
                return {
                    "success": False,
                    "error": f"Web search failed: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Web search error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def call_web_reader(self, url: str) -> Dict[str, Any]:
        """Call GLM web reader service"""
        try:
            payload = {
                "url": url
            }
            
            headers = {
                "Authorization": self.config.GLM_API_TOKEN,
                "Content-Type": "application/json"
            }
            
            response = await self.client.post(
                self.config.GLM_WEB_READER_URL,
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "data": response.json(),
                    "url": url
                }
            else:
                logger.error(f"Web reader failed: {response.status_code}")
                return {
                    "success": False,
                    "error": f"Web reader failed: {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"Web reader error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# Global service instance
provider_service = ProviderService()