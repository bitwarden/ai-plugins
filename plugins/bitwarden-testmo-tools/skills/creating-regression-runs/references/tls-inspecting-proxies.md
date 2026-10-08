# TLS-inspecting proxies

Nothing here needs configuring — it explains a fallback the scripts take on their own.

On a network behind a TLS-inspecting proxy (Zscaler and similar), Python may refuse the connection with
`CERTIFICATE_VERIFY_FAILED`. Two things cause it, and both have to be true to break: the proxy's root CA
is absent from `certifi`, and Python 3.13+ enables `VERIFY_X509_STRICT`, which rejects that root outright
when its Basic Constraints are not marked critical. `curl` uses the OS trust store and is not strict, so
it connects where Python cannot.

The scripts handle this themselves: `call()` tries `urllib` first and, only on a verification failure,
prints a one-line note and switches to `curl` for the rest of the session. The key stays out of `ps` on
both paths — the `curl` path passes the Authorization header through `curl --config -` on stdin, never in
argv. That header is the **only** thing on stdin: the URL, method, and body all travel as argv elements,
so nothing spec-derived can inject a directive into the config that carries the key. Nothing to
configure; if `curl` is missing too, the error says so.
