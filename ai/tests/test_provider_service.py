# Unit Tests for Provider Service
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from tests.fixtures import (
    mock_provider_service,
    mock_openrouter_client
)
from tests.mocks import (
    MockOpenRouterClient, 
    mock_openrouter,
    MockGLMClient,
    mock_glm
)
from tests.assertions import (
    assert_success_response,
    assert_error_response,
    assert_valid_provider_status,
    assert_valid_routing_response
)

# Import the service class
from ai.services.provider_service import ProviderService


class TestProviderService:
    """Test suite for Provider Service."""
    
    @pytest.fixture
    def provider_service(self, mock_openrouter_client):
        """Create a Provider Service instance with mocked dependencies."""
        with mock_openrouter():
            service = ProviderService()
            service.openrouter_client = mock_openrouter_client
            service.glm_search_client = MockGLMClient()
            service.glm_reader_client = MockGLMClient()
            return service
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_provider_status_success(self, provider_service):
        """Test successful provider status retrieval."""
        result = await provider_service.get_provider_status()
        
        assert_success_response(result)
        assert_valid_provider_status(result)
        
        # Validate structure
        assert "providers" in result
        assert "total_providers" in result
        assert "available_providers" in result
        
        # Validate that we have provider information
        providers = result["providers"]
        assert isinstance(providers, dict)
        assert len(providers) > 0
        
        # Validate individual provider info
        for provider_name, provider_info in providers.items():
            assert "status" in provider_info
            assert "models" in provider_info
            assert "latency" in provider_info
            assert "success_rate" in provider_info
            
            assert provider_info["status"] in ["available", "unavailable", "degraded"]
            assert isinstance(provider_info["models"], list)
            assert len(provider_info["models"]) > 0
            assert provider_info["latency"] >= 0
            assert 0.0 <= provider_info["success_rate"] <= 1.0
        
        # Validate counts
        assert result["total_providers"] == len(providers)
        assert 0 <= result["available_providers"] <= result["total_providers"]
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_route_to_provider_success(self, provider_service):
        """Test successful provider routing."""
        task_data = {
            "task_type": "music_theory",
            "prompt": "Explain chord progressions",
            "model_preference": "fast",
            "complexity": "simple"
        }
        
        result = await provider_service.route_to_provider(task_data)
        
        assert_success_response(result)
        assert_valid_routing_response(result)
        
        # Validate response structure
        assert "provider" in result
        assert "model" in result
        assert "response" in result
        assert "latency" in result
        assert "tokens_used" in result
        
        # Validate values
        assert result["provider"] in ["anthropic", "openai", "google", "mistral", "cohere", "perplexity"]
        assert result["model"] in ["claude-3-sonnet", "gpt-4", "gemini-pro", "mixtral", "command", "pplx"]
        assert isinstance(result["response"], str)
        assert len(result["response"]) > 0
        assert result["latency"] >= 0
        assert result["tokens_used"] > 0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_route_to_provider_with_preference(self, provider_service):
        """Test provider routing with specific provider preference."""
        task_data = {
            "task_type": "creative_content",
            "prompt": "Generate a creative story",
            "provider_preference": "anthropic",
            "model_preference": "claude-3-sonnet"
        }
        
        result = await provider_service.route_to_provider(task_data)
        
        assert_success_response(result)
        
        # Should respect provider preference
        assert result["provider"] == "anthropic"
        assert result["model"] == "claude-3-sonnet"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_route_to_provider_fallback(self, provider_service):
        """Test provider routing with fallback when preferred provider is unavailable."""
        # Mock preferred provider as unavailable
        provider_service.provider_status = {
            "anthropic": {"status": "unavailable"},
            "openai": {"status": "available"},
            "google": {"status": "available"}
        }
        
        task_data = {
            "task_type": "creative_content",
            "prompt": "Generate creative content",
            "provider_preference": "anthropic"  # Preferred but unavailable
        }
        
        result = await provider_service.route_to_provider(task_data)
        
        assert_success_response(result)
        
        # Should fall back to available provider
        assert result["provider"] in ["openai", "google"]
        assert result["provider"] != "anthropic"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_test_model_routing_success(self, provider_service):
        """Test successful model routing testing."""
        result = await provider_service.test_model_routing()
        
        assert_success_response(result)
        
        # Validate structure
        assert "routing_results" in result
        assert "routing_accuracy" in result
        
        # Validate routing results
        routing_results = result["routing_results"]
        assert isinstance(routing_results, list)
        assert len(routing_results) > 0
        
        # Each routing result should have required fields
        for routing_result in routing_results:
            assert "task_type" in routing_result
            assert "selected_provider" in routing_result
            assert "selected_model" in routing_result
            assert "confidence" in routing_result
            
            assert routing_result["confidence"] >= 0.0
            assert routing_result["confidence"] <= 1.0
        
        # Validate routing accuracy
        routing_accuracy = result["routing_accuracy"]
        assert 0.0 <= routing_accuracy <= 1.0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_provider_models_success(self, provider_service):
        """Test successful provider models retrieval."""
        result = await provider_service.get_provider_models("anthropic")
        
        assert_success_response(result)
        
        # Validate structure
        assert "provider" in result
        assert "models" in result
        assert "capabilities" in result
        
        # Validate provider
        assert result["provider"] == "anthropic"
        
        # Validate models
        models = result["models"]
        assert isinstance(models, list)
        assert len(models) > 0
        
        # Each model should have required fields
        for model in models:
            assert "name" in model
            assert "capabilities" in model
            assert "max_tokens" in model
            assert "context_window" in model
            
            assert isinstance(model["name"], str)
            assert isinstance(model["capabilities"], list)
            assert model["max_tokens"] > 0
            assert model["context_window"] > 0
        
        # Validate capabilities
        capabilities = result["capabilities"]
        assert isinstance(capabilities, list)
        assert len(capabilities) > 0
        for capability in capabilities:
            assert isinstance(capability, str)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_provider_models_invalid_provider(self, provider_service):
        """Test provider models retrieval with invalid provider."""
        result = await provider_service.get_provider_models("invalid_provider")
        
        assert_error_response(result)
        assert result["error"]["status_code"] == 404
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_estimate_request_cost_success(self, provider_service):
        """Test successful request cost estimation."""
        request_data = {
            "provider": "anthropic",
            "model": "claude-3-sonnet",
            "prompt_tokens": 100,
            "max_completion_tokens": 500
        }
        
        result = await provider_service.estimate_request_cost(request_data)
        
        assert_success_response(result)
        
        # Validate structure
        assert "estimated_cost" in result
        assert "currency" in result
        assert "cost_breakdown" in result
        
        # Validate cost
        assert result["estimated_cost"] >= 0
        assert result["currency"] == "USD"
        
        # Validate cost breakdown
        cost_breakdown = result["cost_breakdown"]
        assert "input_tokens_cost" in cost_breakdown
        assert "output_tokens_cost" in cost_breakdown
        assert "total_cost" in cost_breakdown
        
        assert cost_breakdown["input_tokens_cost"] >= 0
        assert cost_breakdown["output_tokens_cost"] >= 0
        assert cost_breakdown["total_cost"] >= 0
        assert (cost_breakdown["input_tokens_cost"] + cost_breakdown["output_tokens_cost"] == 
                cost_breakdown["total_cost"])
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_estimate_request_cost_invalid_model(self, provider_service):
        """Test request cost estimation with invalid model."""
        request_data = {
            "provider": "anthropic",
            "model": "invalid_model",
            "prompt_tokens": 100,
            "max_completion_tokens": 500
        }
        
        result = await provider_service.estimate_request_cost(request_data)
        
        assert_error_response(result)
        assert result["error"]["status_code"] == 400
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_provider_performance_metrics_success(self, provider_service):
        """Test successful provider performance metrics retrieval."""
        result = await provider_service.get_provider_performance_metrics()
        
        assert_success_response(result)
        
        # Validate structure
        assert "metrics" in result
        assert "summary" in result
        
        # Validate metrics
        metrics = result["metrics"]
        assert isinstance(metrics, dict)
        assert len(metrics) > 0
        
        # Each provider should have metrics
        for provider_name, provider_metrics in metrics.items():
            assert "avg_latency" in provider_metrics
            assert "success_rate" in provider_metrics
            assert "error_rate" in provider_metrics
            assert "total_requests" in provider_metrics
            assert "last_24h_requests" in provider_metrics
            
            assert provider_metrics["avg_latency"] >= 0
            assert 0.0 <= provider_metrics["success_rate"] <= 1.0
            assert 0.0 <= provider_metrics["error_rate"] <= 1.0
            assert (provider_metrics["success_rate"] + provider_metrics["error_rate"] == 1.0)
            assert provider_metrics["total_requests"] >= 0
            assert provider_metrics["last_24h_requests"] >= 0
        
        # Validate summary
        summary = result["summary"]
        assert "total_providers" in summary
        assert "available_providers" in summary
        assert "avg_latency_all" in summary
        assert "overall_success_rate" in summary
        
        assert summary["total_providers"] == len(metrics)
        assert 0 <= summary["available_providers"] <= summary["total_providers"]
        assert summary["avg_latency_all"] >= 0
        assert 0.0 <= summary["overall_success_rate"] <= 1.0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_optimize_provider_selection_success(self, provider_service):
        """Test successful provider selection optimization."""
        optimization_data = {
            "task_types": ["music_theory", "creative_content", "technical_analysis"],
            "priority_factors": ["speed", "quality", "cost"],
            "constraints": {
                "max_latency": 2.0,
                "min_success_rate": 0.95,
                "max_cost_per_request": 0.01
            }
        }
        
        result = await provider_service.optimize_provider_selection(optimization_data)
        
        assert_success_response(result)
        
        # Validate structure
        assert "optimization_results" in result
        assert "recommended_configurations" in result
        assert "performance_projections" in result
        
        # Validate optimization results
        opt_results = result["optimization_results"]
        assert isinstance(opt_results, dict)
        assert len(opt_results) > 0
        
        # Each task type should have optimization results
        for task_type, task_result in opt_results.items():
            assert "best_provider" in task_result
            assert "best_model" in task_result
            assert "expected_performance" in task_result
            assert "cost_efficiency" in task_result
            
            assert task_result["expected_performance"]["latency"] >= 0
            assert 0.0 <= task_result["expected_performance"]["success_rate"] <= 1.0
            assert task_result["cost_efficiency"] >= 0
        
        # Validate recommended configurations
        configurations = result["recommended_configurations"]
        assert isinstance(configurations, list)
        assert len(configurations) > 0
        
        for config in configurations:
            assert "provider" in config
            assert "model" in config
            assert "task_types" in config
            assert "priority" in config
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_test_provider_connectivity_success(self, provider_service):
        """Test successful provider connectivity testing."""
        result = await provider_service.test_provider_connectivity()
        
        assert_success_response(result)
        
        # Validate structure
        assert "connectivity_results" in result
        assert "summary" in result
        
        # Validate connectivity results
        connectivity_results = result["connectivity_results"]
        assert isinstance(connectivity_results, dict)
        assert len(connectivity_results) > 0
        
        # Each provider should have connectivity test results
        for provider_name, test_result in connectivity_results.items():
            assert "status" in test_result
            assert "latency" in test_result
            assert "error_message" in test_result
            
            assert test_result["status"] in ["connected", "disconnected", "timeout"]
            if test_result["status"] == "connected":
                assert test_result["latency"] >= 0
                assert test_result["error_message"] is None
            else:
                assert test_result["error_message"] is not None
        
        # Validate summary
        summary = result["summary"]
        assert "total_providers" in summary
        assert "connected_providers" in summary
        assert "avg_connection_time" in summary
        
        assert summary["total_providers"] == len(connectivity_results)
        assert 0 <= summary["connected_providers"] <= summary["total_providers"]
        if summary["connected_providers"] > 0:
            assert summary["avg_connection_time"] >= 0
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_provider_rate_limits_success(self, provider_service):
        """Test successful provider rate limits retrieval."""
        result = await provider_service.get_provider_rate_limits("anthropic")
        
        assert_success_response(result)
        
        # Validate structure
        assert "provider" in result
        assert "rate_limits" in result
        assert "current_usage" in result
        
        # Validate provider
        assert result["provider"] == "anthropic"
        
        # Validate rate limits
        rate_limits = result["rate_limits"]
        assert isinstance(rate_limits, dict)
        assert "requests_per_minute" in rate_limits
        assert "requests_per_hour" in rate_limits
        assert "tokens_per_minute" in rate_limits
        assert "tokens_per_day" in rate_limits
        
        assert rate_limits["requests_per_minute"] > 0
        assert rate_limits["requests_per_hour"] > 0
        assert rate_limits["tokens_per_minute"] > 0
        assert rate_limits["tokens_per_day"] > 0
        
        # Validate current usage
        current_usage = result["current_usage"]
        assert isinstance(current_usage, dict)
        assert "current_rpm" in current_usage
        assert "current_rph" in current_usage
        assert "current_tpm" in current_usage
        assert "current_tpd" in current_usage
        
        assert current_usage["current_rpm"] >= 0
        assert current_usage["current_rph"] >= 0
        assert current_usage["current_tpm"] >= 0
        assert current_usage["current_tpd"] >= 0
        
        # Validate that current usage doesn't exceed limits
        assert current_usage["current_rpm"] <= rate_limits["requests_per_minute"]
        assert current_usage["current_rph"] <= rate_limits["requests_per_hour"]
        assert current_usage["current_tpm"] <= rate_limits["tokens_per_minute"]
        assert current_usage["current_tpd"] <= rate_limits["tokens_per_day"]


class TestProviderServiceErrorHandling:
    """Test error handling in Provider Service."""
    
    @pytest.fixture
    def error_prone_service(self):
        """Create a service that simulates various errors."""
        service = ProviderService()
        
        # Mock OpenRouter client to raise exceptions
        service.openrouter_client = Mock()
        service.openrouter_client.chat.completions.create.side_effect = Exception("API Error")
        
        return service
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_api_error_handling(self, error_prone_service):
        """Test handling of API errors."""
        task_data = {
            "task_type": "music_theory",
            "prompt": "Test prompt"
        }
        
        result = await error_prone_service.route_to_provider(task_data)
        
        assert_error_response(result)
        assert "API Error" in result["error"]["message"]
        assert result["error"]["status_code"] == 500
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_timeout_error_handling(self, error_prone_service):
        """Test handling of timeout errors."""
        import asyncio
        
        error_prone_service.openrouter_client.chat.completions.create.side_effect = \
            asyncio.TimeoutError("Request timeout")
        
        task_data = {
            "task_type": "music_theory",
            "prompt": "Test prompt"
        }
        
        result = await error_prone_service.route_to_provider(task_data)
        
        assert_error_response(result)
        assert "timeout" in result["error"]["message"].lower()
        assert result["error"]["status_code"] == 408
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_rate_limit_error_handling(self, error_prone_service):
        """Test handling of rate limit errors."""
        class RateLimitError(Exception):
            def __init__(self):
                self.status_code = 429
                self.message = "Rate limit exceeded"
        
        error_prone_service.openrouter_client.chat.completions.create.side_effect = RateLimitError()
        
        task_data = {
            "task_type": "music_theory",
            "prompt": "Test prompt"
        }
        
        result = await error_prone_service.route_to_provider(task_data)
        
        assert_error_response(result)
        assert result["error"]["status_code"] == 429
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_authentication_error_handling(self, error_prone_service):
        """Test handling of authentication errors."""
        class AuthenticationError(Exception):
            def __init__(self):
                self.status_code = 401
                self.message = "Invalid API key"
        
        error_prone_service.openrouter_client.chat.completions.create.side_effect = AuthenticationError()
        
        task_data = {
            "task_type": "music_theory",
            "prompt": "Test prompt"
        }
        
        result = await error_prone_service.route_to_provider(task_data)
        
        assert_error_response(result)
        assert result["error"]["status_code"] == 401
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_all_providers_unavailable_handling(self, error_prone_service):
        """Test handling when all providers are unavailable."""
        # Mock all providers as unavailable
        error_prone_service.provider_status = {
            "anthropic": {"status": "unavailable"},
            "openai": {"status": "unavailable"},
            "google": {"status": "unavailable"}
        }
        
        task_data = {
            "task_type": "music_theory",
            "prompt": "Test prompt"
        }
        
        result = await error_prone_service.route_to_provider(task_data)
        
        assert_error_response(result)
        assert "unavailable" in result["error"]["message"].lower()
        assert result["error"]["status_code"] == 503


class TestProviderServiceIntegration:
    """Integration tests for Provider Service."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_provider_workflow(self, provider_service):
        """Test complete provider workflow from status check to routing."""
        # Step 1: Check provider status
        status_result = await provider_service.get_provider_status()
        assert_success_response(status_result)
        
        # Step 2: Get available models from primary provider
        primary_provider = "anthropic"  # Assume this is our primary
        models_result = await provider_service.get_provider_models(primary_provider)
        assert_success_response(models_result)
        
        # Step 3: Test model routing
        routing_result = await provider_service.test_model_routing()
        assert_success_response(routing_result)
        
        # Step 4: Route a sample request
        task_data = {
            "task_type": "music_theory",
            "prompt": "Explain the concept of chord progressions",
            "complexity": "intermediate"
        }
        
        route_result = await provider_service.route_to_provider(task_data)
        assert_success_response(route_result)
        
        # Step 5: Estimate cost for a similar request
        cost_data = {
            "provider": route_result["provider"],
            "model": route_result["model"],
            "prompt_tokens": 100,
            "max_completion_tokens": 500
        }
        
        cost_result = await provider_service.estimate_request_cost(cost_data)
        assert_success_response(cost_result)
        
        # Step 6: Get performance metrics
        metrics_result = await provider_service.get_provider_performance_metrics()
        assert_success_response(metrics_result)
        
        # Step 7: Test connectivity
        connectivity_result = await provider_service.test_provider_connectivity()
        assert_success_response(connectivity_result)
        
        # Verify consistency across results
        # The routed provider should be in the available providers list
        available_providers = [
            name for name, info in status_result["providers"].items() 
            if info["status"] == "available"
        ]
        assert route_result["provider"] in available_providers
        
        # The routed model should be in the models list for that provider
        routed_model = route_result["model"]
        provider_models = models_result["models"]
        model_names = [model["name"] for model in provider_models]
        assert routed_model in model_names
        
        # The cost should be reasonable for the token counts
        assert cost_result["estimated_cost"] > 0
        assert cost_result["estimated_cost"] < 1.0  # Should be less than $1 for this request
        
        # The performance metrics should include the routed provider
        assert route_result["provider"] in metrics_result["metrics"]
        
        # The connectivity test should include the routed provider
        assert route_result["provider"] in connectivity_result["connectivity_results"]
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_multiple_task_routing_performance(self, provider_service):
        """Test performance of routing multiple tasks."""
        import time
        
        # Define multiple tasks to route
        tasks = [
            {
                "task_type": "music_theory",
                "prompt": "Explain chord progressions",
                "complexity": "simple"
            },
            {
                "task_type": "creative_content",
                "prompt": "Generate a creative song",
                "complexity": "intermediate"
            },
            {
                "task_type": "technical_analysis",
                "prompt": "Analyze audio features",
                "complexity": "advanced"
            },
            {
                "task_type": "music_history",
                "prompt": "Explain baroque music",
                "complexity": "intermediate"
            },
            {
                "task_type": "instrument_technique",
                "prompt": "Guitar fingerpicking techniques",
                "complexity": "advanced"
            }
        ]
        
        # Measure routing performance
        start_time = time.time()
        results = []
        
        for task in tasks:
            result = await provider_service.route_to_provider(task)
            assert_success_response(result)
            results.append(result)
        
        end_time = time.time()
        total_routing_time = end_time - start_time
        
        # Verify all tasks were routed successfully
        assert len(results) == len(tasks)
        
        # Verify performance (should be fast for 5 tasks)
        assert total_routing_time < 5.0, f"Routing took {total_routing_time}s for 5 tasks"
        
        # Verify that different tasks might use different providers/models
        providers = [r["provider"] for r in results]
        models = [r["model"] for r in results]
        
        # Should have some variety (unless all tasks route to same provider)
        # This is a loose check since routing logic might favor certain providers
        unique_providers = len(set(providers))
        unique_models = len(set(models))
        
        # Should have at least some variety unless all tasks are very similar
        assert unique_providers >= 1  # At least one provider
        assert unique_models >= 1  # At least one model
        
        # Verify that all responses are valid
        for result in results:
            assert_valid_routing_response(result)
            assert len(result["response"]) > 0
            assert result["latency"] > 0
            assert result["tokens_used"] > 0
        
        # Calculate average latency and tokens per request
        avg_latency = sum(r["latency"] for r in results) / len(results)
        avg_tokens = sum(r["tokens_used"] for r in results) / len(results)
        
        # Verify reasonable performance metrics
        assert avg_latency < 3.0, f"Average latency {avg_latency}s is too high"
        assert avg_tokens > 50, f"Average tokens {avg_tokens} is too low"
        
        # Verify that total cost would be reasonable
        total_tokens = sum(r["tokens_used"] for r in results)
        estimated_total_cost = total_tokens * 0.00001  # Rough estimate: $0.01 per 1K tokens
        
        assert estimated_total_cost < 0.10, f"Estimated total cost ${estimated_total_cost} is too high for 5 tasks"
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_provider_fallback_resilience(self, provider_service):
        """Test provider fallback resilience when providers fail."""
        import asyncio
        
        # Step 1: Get initial status
        initial_status = await provider_service.get_provider_status()
        assert_success_response(initial_status)
        
        available_providers = [
            name for name, info in initial_status["providers"].items() 
            if info["status"] == "available"
        ]
        
        if len(available_providers) < 2:
            pytest.skip("Need at least 2 available providers for fallback test")
        
        # Step 2: Mock primary provider failure
        primary_provider = available_providers[0]
        
        # Temporarily make primary provider unavailable
        original_status = provider_service.provider_status
        provider_service.provider_status[primary_provider]["status"] = "unavailable"
        
        try:
            # Step 3: Route request - should fallback to another provider
            task_data = {
                "task_type": "music_theory",
                "prompt": "Test fallback routing",
                "provider_preference": primary_provider  # Prefer unavailable provider
            }
            
            result = await provider_service.route_to_provider(task_data)
            assert_success_response(result)
            
            # Should have fallen back to a different provider
            assert result["provider"] != primary_provider
            assert result["provider"] in available_providers
            
        finally:
            # Step 4: Restore original status
            provider_service.provider_status = original_status
        
        # Step 5: Verify restored provider is available again
        final_status = await provider_service.get_provider_status()
        assert_success_response(final_status)
        
        # Primary provider should be available again
        assert final_status["providers"][primary_provider]["status"] == "available"