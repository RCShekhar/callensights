import jwt
import logging
from typing import Optional, TypedDict
from botocore.exceptions import ClientError
import boto3


class DecodedPayload(TypedDict, total=False):
    """
    TypedDict representing the decoded payload of a JWT token.

    Attributes:
        aud (str): Audience claim.
        azp (str): Authorized party claim.
        created_dt (int): Creation timestamp of the token.
        email (str): Email claim.
        exp (int): Expiration timestamp of the token.
        first_name (Optional[str]): First name claim (optional).
        iat (int): Issued At timestamp of the token.
        iss (str): Issuer claim.
        jti (str): JWT ID claim.
        last_name (Optional[str]): Last name claim (optional).
        nbf (int): Not Before timestamp of the token.
        ph_number (Optional[str]): Phone number claim (optional).
        sub (str): Subject claim.
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
        self.decoding_algorithm = "RS256"
        self.audience = "callensights-api-prod"
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
        jw_token = self.extract_bearer_token(token)
        try:
            payload = jwt.decode(
                jw_token,
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
        SECRET_NAME = "callensights/clerk"

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


if __name__ == "__main__":
    main()
