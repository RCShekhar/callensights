import jwt
import logging
from typing import Optional, TypedDict
from botocore.exceptions import ClientError
import boto3

from app.src.common.config.app_settings import get_app_settings
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


class DecodedPayload(TypedDict, total=False):
    """
    TypedDict representing the decoded payload of a JWT token.

    Attributes:
        aud (str): Audience claim.
        email (str): Email claim.
        user_id (str): User ID claim.
        user_name (str): User name claim.
    """

    aud: str
    email: str
    user_id: str
    role: Optional[str]
    user_name: str


class JWTDecoder:
    """
    JWTDecoder class for decoding JWT tokens using RSA256 algorithm.

    Attributes:
        decoding_algorithm (str): Algorithm used for decoding.
        audience (str): Expected audience claim value.
        boto_session (boto3.session.Session): Boto3 session for AWS services.
        boto_client (boto3.client): Boto3 client for AWS Secrets Manager.
    """

    def __init__(self):
        self.settings = get_app_settings()
        self.decoding_algorithm = "RS256"
        self.audience = self.settings.CLERK_AUDIENCE
        self.boto_session = boto3.session.Session()
        self.boto_client = self.boto_session.client(
            service_name="secretsmanager",
            region_name="us-east-1",
        )

    def extract_bearer_token(self, authorization_header: str) -> Optional[str]:
        """
        Extracts the JWT token from the Authorization header.

        Args:
            authorization_header (str): Authorization header containing the JWT token.

        Returns:
            Optional[str]: Extracted JWT token or None if extraction fails.
        """
        try:
            _, token = authorization_header.split()
            return token
        except ValueError:
            logging.error("Failed to extract JWT token from Authorization header.")
            return None

    def decode_jwt(self, token: str) -> DecodedPayload:
        """
        Decodes the JWT token using the specified algorithm and validates its claims.

        Args:
            token (str): JWT token to be decoded.

        Returns:
            DecodedPayload: Decoded payload of the JWT token.

        Raises:
            jwt.ExpiredSignatureError: If the token has expired.
            jwt.InvalidTokenError: If the token is invalid.
        """
        secret = self.get_secret()
        try:
            payload = jwt.decode(
                token,
                secret,
                algorithms=[self.decoding_algorithm],
                audience=self.audience,
                verify_signature=True,
            )
            return payload
        except jwt.ExpiredSignatureError:
            logging.error("Token has expired.")
            raise
        except jwt.InvalidTokenError:
            logging.error("Invalid token.")
            raise

    def get_secret(self) -> str:
        """
        Retrieves the secret from AWS Secrets Manager.

        Returns:
            str: Secret value.

        Raises:
            Exception: If failed to retrieve the secret.
        """

        SECRET_NAME = self.settings.CLERK_SECRET

        try:
            get_secret_value_response = self.boto_client.get_secret_value(
                SecretId=SECRET_NAME
            )
        except ClientError as e:
            logging.error(f"Failed to retrieve secret '{SECRET_NAME}': {e}")
            raise Exception(f"Failed to retrieve secret '{SECRET_NAME}': {e}") from e

        return get_secret_value_response["SecretString"]


def main():
    """
    This is the main function that demonstrates the usage of JWTDecoder to decode a JWT token.

    It initializes the logging configuration and sets the logger to the current module.
    Then, it sets a dummy authorization header for demonstration purposes.

    Note: Replace the "<redacted>" in the "authorization_header" with a real JWT token for actual usage.

    Parameters: None

    Returns: None
    """
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    authorization_header = "Bearer <redacted>"

    jwt_decoder = JWTDecoder()

    try:
        decoded_payload = jwt_decoder.decode_jwt(authorization_header)
        logger.info("Decoded payload: %s", decoded_payload)
    except jwt.ExpiredSignatureError:
        logger.error("Error decoding the JWT: Token has expired.")
    except jwt.InvalidTokenError:
        logger.error("Error decoding the JWT: Invalid token.")
    except Exception as e:
        logger.error("Error decoding the JWT: %s", e)


jwt_decoder = JWTDecoder()


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            else:
                try:
                    decoded_payload = jwt_decoder.decode_jwt(credentials.credentials)
                except jwt.InvalidSignatureError:
                    raise HTTPException(
                        status_code=403,
                        detail="Unauthorized: The provided token is invalid. Please ensure you are using the correct token.",
                    )
                except jwt.ExpiredSignatureError:
                    raise HTTPException(
                        status_code=403,
                        detail="Unauthorized: The provided token has expired. Please refresh your token.",
                    )
                except jwt.InvalidTokenError:
                    raise HTTPException(
                        status_code=403,
                        detail="Unauthorized: You must be authenticated to perform this request. The provided token is invalid or malformed.f",
                    )
                except Exception:
                    raise HTTPException(
                        status_code=403,
                        detail="An unexpected error occurred. Please try again later, and if the problem persists, contact support.",
                    )

            return decoded_payload
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")


if __name__ == "__main__":
    main()
