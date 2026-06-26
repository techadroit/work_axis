from backend.app.llm.model_provider.model_provider_name import OPENAI_NAME, GOOGLE_NAME, AZURE_NAME, AWS_NAME, OLLAMA_NAME, \
    ANTHROPIC_NAME


class SettingsRepository:

    def __init__(self):
        # Initialize database connection or any required resources here
        pass

    def get_all_model_providers(self):
        """
        Get all supported model providers with their configuration schema for UI generation.

        Returns:
            List of dictionaries containing provider name and required fields for API calls
        """
        return [
            {
                "name": OPENAI_NAME,
                "model_list": "https://platform.openai.com/docs/models",
                "fields": [
                    {
                        "name": "api_key",
                        "label": "API Key",
                        "description":"The OpenAI API uses API keys for authentication. "
                                      "Visit <a href='https://platform.openai.com/account/api-keys' target='_blank'>"
                                      "API Keys</a> page to retrieve the API key you'll use in your requests.",
                        "type": "text",
                        "required": True,
                        "placeholder": "Insert API Key",
                    },
                    {
                        "name": "base_url",
                        "label": "Base URL",
                        "description": "The Base endpoint to use. "
                                       "Visit <a href='https://platform.openai.com/docs/api-reference/chat/create' target='_blank'>"
                                       "API Keys</a> for more information.",
                        "type": "text",
                        "required": True,
                        "default": "https://api.openai.com/v1",
                        "placeholder": "https://api.openai.com/v1"
                    }
                ]
            },
            {
                "name": ANTHROPIC_NAME,
                "model_list": "https://platform.claude.com/docs/en/about-claude/models",
                "fields": [
                    {
                        "name": "api_key",
                        "label": "API Key",
                        "description": "The Anthropic API uses API keys for authentication. "
                                       "Visit <a href='https://console.anthropic.com/settings/keys' target='_blank'>"
                                       "API Keys</a> page to retrieve the API key you'll use in your requests.",
                        "type": "text",
                        "required": True,
                        "placeholder": "Insert API Key"
                    },
                    {
                        "name": "base_url",
                        "label": "Base URL",
                        "description": "The Base endpoint to use. "
                                       "Visit <a href='https://docs.anthropic.com/en/api/messages' target='_blank'>"
                                       "Anthropic Api Documentation</a> for more information.",
                        "type": "text",
                        "required": True,
                        "default": "https://api.anthropic.com",
                        "placeholder": "https://api.anthropic.com"
                    }
                ]
            },
            {
                "name": GOOGLE_NAME,
                "model_list": "https://ai.google.dev/gemini-api/docs/models/gemini",
                "fields": [
                    {
                        "name": "api_key",
                        "label": "API Key",
                        "description": "The Gemini API uses API keys for authentication. "
                                       "Visit <a href='https://aistudio.google.com/apikey' target='_blank'>"
                                       "API Keys</a> page to retrieve the API key you'll use in your requests.",
                        "type": "text",
                        "required": True,
                        "placeholder": "Insert API Key"
                    },
                    {
                        "name": "base_url",
                        "label": "Base URL",
                        "description": "The Base endpoint to use. "
                                       "Visit <a href='https://ai.google.dev/gemini-api/docs/openai' target='_blank'>"
                                       "Gemini Documentation</a> for more information.",
                        "type": "text",
                        "required": False,
                        "default": "https://generativelanguage.googleapis.com/v1beta",
                        "placeholder": "https://generativelanguage.googleapis.com/v1beta"
                    }
                ]
            },
            {
                "name": AZURE_NAME,
                "model_list": "https://oai.azure.com/deployments",
                "fields": [
                    {
                        "name": "api_key",
                        "label": "API Key",
                        "description": "The Azure API uses API keys for authentication. "
                                       "Visit <a href='https://oai.azure.com/' target='_blank'>"
                                       "API Keys</a> page to retrieve the API key you'll use in your requests.",
                        "type": "text",
                        "required": True,
                        "placeholder": "Insert API Key"
                    },
                    {
                        "name": "base_url",
                        "label": "Base URL",
                        "description": "The Base endpoint to use. "
                                       "Visit <a href='https://learn.microsoft.com/en-us/azure/ai-foundry/openai/latest' target='_blank'>"
                                       "Azure documentation</a> for more information.",
                        "type": "text",
                        "required": True,
                        "placeholder": "https://your-resource.openai.azure.com"
                    },
                    {
                        "name": "api_version",
                        "label": "API Version",
                        "type": "text",
                        "required": False,
                        "default": "api_version",
                        "placeholder": "2024-02-15-preview"
                    }
                ]
            },
            {
                "name": AWS_NAME,
                "model_list": "https://aws.amazon.com/bedrock/model-choice/",
                "fields": [
                    {
                        "name": "aws_access_key_id",
                        "label": "AWS Access Key ID",
                        "type": "text",
                        "required": True,
                        "placeholder": "Insert AWS Access Key ID"
                    },
                    {
                        "name": "aws_secret_access_key",
                        "label": "AWS Secret Access Key",
                        "type": "password",
                        "required": True,
                        "placeholder": "Insert AWS Secret Access Key"
                    },
                    {
                        "name": "region",
                        "label": "Region",
                        "type": "text",
                        "required": True,
                        "placeholder": "us-east-1"
                    },
                    {
                        "name": "model_provider",
                        "label": "Model Provider",
                        "description": "The Model Provider. "
                                       "Visit <a href='https://docs.aws.amazon.com/bedrock/' target='_blank'>"
                                       "Aws Documentation</a> for more information.",
                        "type": "text",
                        "required": False,
                        "placeholder": "meta"
                    }
                ]
            },
            {
                "name": OLLAMA_NAME,
                "fields": [
                    {
                        "name": "base_url",
                        "label": "Base URL",
                        "type": "text",
                        "required": True,
                        "default": "http://localhost:11434",
                        "placeholder": "http://localhost:11434",
                        "description": "The URL where Ollama is running. Default is localhost on port 11434. Change if running remotely.",
                        "doc_link": "https://github.com/ollama/ollama/blob/main/docs/api.md"
                    }
                ]
            }
        ]
