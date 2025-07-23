import random
import ssl


def _create_ssl_context(use_http2: bool, disable_tls_1_3: bool) -> ssl.SSLContext:
    """Create SSL context with specified configuration."""
    context = ssl.create_default_context()

    # Configure ALPN protocols
    if use_http2:
        context.set_alpn_protocols(["h2", "http/1.1"])

    # Configure TLS versions
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.maximum_version = ssl.TLSVersion.TLSv1_2 if disable_tls_1_3 else ssl.TLSVersion.TLSv1_3

    # Randomize cipher suites for security
    ciphers = context.get_ciphers()
    random.shuffle(ciphers)
    context.set_ciphers(":".join(cipher["name"] for cipher in ciphers))

    return context


# Pre-defined SSL contexts for common configurations
TLS_CONTEXT_HTTP2 = _create_ssl_context(use_http2=True, disable_tls_1_3=False)
TLS_CONTEXT_HTTP1 = _create_ssl_context(use_http2=False, disable_tls_1_3=False)
TLS_CONTEXT_HTTP2_NO_TLS13 = _create_ssl_context(use_http2=True, disable_tls_1_3=True)
TLS_CONTEXT_HTTP1_NO_TLS13 = _create_ssl_context(use_http2=False, disable_tls_1_3=True)
