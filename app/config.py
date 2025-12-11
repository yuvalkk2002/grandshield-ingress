import json
from typing import Optional

import boto3
from botocore.exceptions import ClientError
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.exceptions import ConfigurationError
from app.core.logger import logger


class Settings(BaseSettings):
    AWS_REGION: str = "eu-north-1"
    SECRET_NAME: str = "qa/grandshield-api-keys"
    ENV: str = "dev"
    
    # These will be populated from Secrets Manager or Env
    DEEPGRAM_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    def load_aws_secrets(self):
        """
        Load secrets from AWS Secrets Manager if not in local environment.
        """
        if self.ENV == "local":
            logger.info("loading_secrets_from_env")
            # In local, pydantic reads from .env or os.environ automatically
            # explicitly checking if they are missing might be good
            if not self.DEEPGRAM_API_KEY:
                logger.warning("deepgram_api_key_missing_in_local_env")
            return

        session = boto3.session.Session()
        client = session.client(service_name='secretsmanager', region_name=self.AWS_REGION)
        
        try:
            logger.info("fetching_secrets_from_aws", secret_name=self.SECRET_NAME)
            resp = client.get_secret_value(SecretId=self.SECRET_NAME)
            
            if 'SecretString' in resp:
                secrets = json.loads(resp['SecretString'])
                self.DEEPGRAM_API_KEY = secrets.get("DEEPGRAM_API_KEY")
                self.GOOGLE_API_KEY = secrets.get("GOOGLE_API_KEY")
                logger.info("secrets_loaded_successfully")
            else:
                raise ConfigurationError("SecretString not found in the response")
                
        except ClientError as e:
            logger.error("aws_secrets_manager_error", error=str(e))
            raise ConfigurationError("Failed to load secrets from AWS", original_error=e) from e
        except Exception as e:
            logger.error("unexpected_error_loading_secrets", error=str(e))
            raise ConfigurationError("Unexpected error loading secrets", original_error=e) from e

settings = Settings()
