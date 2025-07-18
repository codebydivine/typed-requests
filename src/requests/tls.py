import random
import ssl


def _create_ssl_context(use_http2: bool, disable_tls_1_3: bool) -> ssl.SSLContext:
    ssl_context = ssl.create_default_context()

    if use_http2:
        ssl_context.set_alpn_protocols(["h2", "http/1.1"])

    if disable_tls_1_3:
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        ssl_context.maximum_version = ssl.TLSVersion.TLSv1_2
    else:
        ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
        ssl_context.maximum_version = ssl.TLSVersion.TLSv1_3
    
    # Shuffle the ciphersuites
    ciphersuites = ssl_context.get_ciphers()
    random.shuffle(ciphersuites)
    ssl_context.set_ciphers(':'.join(cipher['name'] for cipher in ciphersuites))
    
    return ssl_context

# Create pre-defined SSL contexts
TLS_CONTEXT_HTTP2 = _create_ssl_context(use_http2=True, disable_tls_1_3=False)
TLS_CONTEXT_HTTP1 = _create_ssl_context(use_http2=False, disable_tls_1_3=False)
TLS_CONTEXT_HTTP2_NO_TLS13 = _create_ssl_context(use_http2=True, disable_tls_1_3=True)
TLS_CONTEXT_HTTP1_NO_TLS13 = _create_ssl_context(use_http2=False, disable_tls_1_3=True)
