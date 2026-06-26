# """
# SSL Configuration Module for Secure API Calls
# Handles SSL certificate generation and configuration for HTTPS
# """
# import os
# import ssl
# from pathlib import Path
# from typing import Tuple, Optional
#
# from utils.logger_util import log_info, log_error
#
#
# def get_ssl_cert_dir() -> Path:
#     """Get or create SSL certificates directory"""
#     cert_dir = Path(__file__).parent / "data" / "ssl_certs"
#     cert_dir.mkdir(parents=True, exist_ok=True)
#     return cert_dir
#
#
# def generate_self_signed_cert() -> Tuple[str, str]:
#     """
#     Generate self-signed SSL certificate for development/testing
#     Returns: tuple of (cert_path, key_path)
#     """
#     try:
#         from cryptography import x509
#         from cryptography.x509.oid import NameOID
#         from cryptography.hazmat.primitives import hashes
#         from cryptography.hazmat.backends import default_backend
#         from cryptography.hazmat.primitives.asymmetric import rsa
#         from cryptography.hazmat.primitives import serialization
#         import datetime
#
#         cert_dir = get_ssl_cert_dir()
#         cert_path = cert_dir / "cert.pem"
#         key_path = cert_dir / "key.pem"
#
#         # Check if certificates already exist
#         if cert_path.exists() and key_path.exists():
#             log_info(f"SSL certificates already exist at {cert_dir}")
#             return str(cert_path), str(key_path)
#
#         log_info("Generating self-signed SSL certificate...")
#
#         # Generate private key
#         private_key = rsa.generate_private_key(
#             public_exponent=65537,
#             key_size=2048,
#             backend=default_backend()
#         )
#
#         # Generate certificate
#         subject = issuer = x509.Name([
#             x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
#             x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"State"),
#             x509.NameAttribute(NameOID.LOCALITY_NAME, u"City"),
#             x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"PersonalAI"),
#             x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
#         ])
#
#         cert = x509.CertificateBuilder().subject_name(
#             subject
#         ).issuer_name(
#             issuer
#         ).public_key(
#             private_key.public_key()
#         ).serial_number(
#             x509.random_serial_number()
#         ).not_valid_before(
#             datetime.datetime.now(datetime.timezone.utc)
#         ).not_valid_after(
#             datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365)
#         ).add_extension(
#             x509.SubjectAlternativeName([
#                 x509.DNSName(u"localhost"),
#                 x509.DNSName(u"127.0.0.1"),
#             ]),
#             critical=False,
#         ).sign(private_key, hashes.SHA256(), default_backend())
#
#         # Write private key
#         with open(key_path, "wb") as f:
#             f.write(private_key.private_bytes(
#                 encoding=serialization.Encoding.PEM,
#                 format=serialization.PrivateFormat.TraditionalOpenSSL,
#                 encryption_algorithm=serialization.NoEncryption()
#             ))
#
#         # Write certificate
#         with open(cert_path, "wb") as f:
#             f.write(cert.public_bytes(serialization.Encoding.PEM))
#
#         log_info(f"SSL certificates generated successfully at {cert_dir}")
#         return str(cert_path), str(key_path)
#
#     except ImportError:
#         log_error("cryptography package not installed. Install with: pip install cryptography")
#         raise
#     except Exception as e:
#         log_error(f"Failed to generate SSL certificates: {e}")
#         raise
#
#
# def get_ssl_context(cert_path: Optional[str] = None, key_path: Optional[str] = None) -> ssl.SSLContext:
#     """
#     Create SSL context for secure connections
#
#     Args:
#         cert_path: Path to SSL certificate (optional)
#         key_path: Path to SSL private key (optional)
#
#     Returns:
#         SSL context configured for secure connections
#     """
#     ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
#
#     if cert_path and key_path:
#         ssl_context.load_cert_chain(cert_path, key_path)
#
#     # Configure for security
#     ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
#     ssl_context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
#
#     return ssl_context
#
#
# def get_client_ssl_context(verify: bool = True) -> ssl.SSLContext:
#     """
#     Create SSL context for client HTTP requests using cryptography-backed certificates
#
#     Args:
#         verify: Whether to verify SSL certificates
#
#     Returns:
#         SSL context for client connections
#     """
#     if verify:
#         ssl_context = ssl.create_default_context()
#
#         # Try to use certifi's CA bundle for better certificate verification
#         try:
#             import certifi
#             ca_bundle_path = certifi.where()
#             ssl_context.load_verify_locations(cafile=ca_bundle_path)
#             log_info(f"SSL context configured with certifi CA bundle: {ca_bundle_path}")
#         except ImportError:
#             log_info("certifi not available, using system default CA certificates")
#         except Exception as e:
#             log_error(f"Failed to load certifi CA bundle: {e}, using system default")
#     else:
#         ssl_context = ssl.create_default_context()
#         ssl_context.check_hostname = False
#         ssl_context.verify_mode = ssl.CERT_NONE
#         log_info("SSL context configured with certificate verification disabled")
#
#     return ssl_context
#
#
# def configure_httpx_ssl():
#     """
#     Configure httpx library to use proper SSL settings
#     Returns SSL verify parameter for httpx clients
#     """
#     # For production: return True or path to CA bundle
#     # For development with self-signed certs: return False or custom context
#     return True  # Enable SSL verification by default
#
#
# def configure_requests_ssl():
#     """
#     Configure requests library to use proper SSL settings
#     Returns verify parameter for requests
#     """
#     # For production: return True or path to CA bundle
#     # For development with self-signed certs: return False
#     return True  # Enable SSL verification by default
#
#
# if __name__ == "__main__":
#     # Test SSL certificate generation
#     cert, key = generate_self_signed_cert()
#     print(f"Certificate: {cert}")
#     print(f"Key: {key}")
#
