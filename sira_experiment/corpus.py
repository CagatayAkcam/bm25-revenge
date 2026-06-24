"""36-doc SaaS knowledge base with built-in retrieval failure modes."""

DOCS = {
    # Billing / payments
    "pay-err-4032": (
        "Error ERR-4032: card declined due to AVS mismatch. ERR-4032 is raised "
        "by the billing gateway when the address verification system rejects the "
        "cardholder address. Ask the customer to confirm their billing address "
        "and postal code, then retry the charge. ERR-4032 is permanent for the "
        "attempt; retrying without changes will fail again."
    ),
    "pay-err-4031": (
        "Error ERR-4031: card declined due to insufficient funds. The billing "
        "gateway returns ERR-4031 when the issuing bank rejects the charge. The "
        "customer should use a different card or retry after funds are available."
    ),
    "pay-general": (
        "Troubleshooting failed payments. When a payment fails, check the gateway "
        "dashboard for the decline code, verify the customer's card is not "
        "expired, and confirm the account is in good standing. Most payment "
        "errors resolve after the customer updates their card details."
    ),
    "pay-retry-policy": (
        "Dunning and retry policy. Failed subscription charges are retried on a "
        "3-5-7 day schedule. After the final retry the account is downgraded to "
        "the free plan and the user receives a payment failure email."
    ),
    "vat-germany": (
        "Invoice tax bug VAT-1203: wrong VAT rate applied to German customers. "
        "Invoices generated between May 2 and May 9 applied the Austrian 20% "
        "rate instead of the German 19% rate for customers with a DE country "
        "code. Affected invoices must be regenerated with a corrected tax line."
    ),
    "billing-cycle": (
        "How billing cycles work. Subscriptions renew on the anniversary of the "
        "signup date. Mid-cycle plan changes are prorated. Invoices are emailed "
        "to the account owner and available under Settings, then Billing."
    ),

    # Auth / accounts
    "twofa-reset": (
        "Resetting two-factor authentication for a locked-out user. If a user "
        "lost their TOTP device, verify identity with two recovery signals "
        "(billing email plus last-4 of card on file), then clear the TOTP seed "
        "from the admin console. The user re-enrolls at next sign-in. Never "
        "disable enforcement tenant-wide to unblock a single user."
    ),
    "account-security": (
        "Account security best practices. Encourage users to enable two-factor "
        "authentication, use a password manager, and review active sessions. "
        "Suspicious login attempts trigger an email alert and may temporarily "
        "lock the account until the user verifies access."
    ),
    "account-deactivate": (
        "Deactivating and reactivating accounts. Admins can deactivate a user "
        "account from the admin console. Deactivation removes access but keeps "
        "user data intact. Reactivating restores the account exactly as it was. "
        "Deactivation is not deletion; no information is removed."
    ),
    "gdpr-erasure": (
        "Handling GDPR right-to-erasure requests. Under GDPR Article 17 a "
        "customer may request erasure of their personal data. File a privacy "
        "ticket; the privacy job purges profile records, support transcripts and "
        "analytics identifiers within 30 days, then emails a completion receipt."
    ),
    "password-policy": (
        "Password policy. Passwords require 12 characters minimum. Users can "
        "reset a forgotten password from the sign-in page; reset links expire "
        "after 30 minutes. Repeated failed attempts lock the account for 15 "
        "minutes."
    ),
    "session-mgmt": (
        "Session management. Sessions expire after 14 days of inactivity. Users "
        "can review and revoke active sessions under Settings. Revoking a "
        "session signs that device out immediately."
    ),

    # Pricing / plans
    "pricing-tiers": (
        "Plan comparison. Starter includes core features for small teams. "
        "Business adds audit logs, priority support and usage analytics. "
        "Enterprise adds SAML single sign-on, SCIM provisioning, a dedicated "
        "success manager and a 99.95% uptime SLA. Single sign-on is available "
        "on the Enterprise tier only."
    ),
    "plan-limits": (
        "Plan limits and quotas. Starter allows 5 seats and 10,000 API calls "
        "per day. Business allows 50 seats and 100,000 API calls. Enterprise "
        "limits are negotiated per contract. Exceeding a quota returns HTTP 429."
    ),
    "discounts": (
        "Discounts and nonprofit pricing. Annual billing saves 20% on any plan. "
        "Registered nonprofits and educational institutions qualify for an "
        "additional 30% discount on Business and Enterprise plans."
    ),

    # Releases / changelogs
    "changelog-2-13": (
        "Release notes v2.13.0. Added bulk export to CSV, redesigned the "
        "notification center, and fixed a race condition in the import worker. "
        "Deprecated the legacy webhooks API."
    ),
    "changelog-2-14": (
        "Release notes v2.14.0. Introduced the new permissions model with "
        "custom roles, added dark mode, and upgraded the dashboard charting "
        "library. Known issue: report pages may load slowly for large "
        "workspaces; fixed in v2.14.1."
    ),
    "changelog-2-15": (
        "Release notes v2.15.0. Shipped the audit log search API, improved "
        "mobile responsiveness, and reduced cold-start time for serverless "
        "functions. Removed the deprecated legacy webhooks API."
    ),
    "perf-regression": (
        "Incident retro: latency degradation after the v2.14.0 rollout. The new "
        "permissions model introduced an N+1 query pattern on the dashboard "
        "endpoint, raising p95 response times from 180ms to 2.4s for large "
        "workspaces. Mitigated by eager-loading role assignments and adding a "
        "covering index. Permanent fix shipped in v2.14.1."
    ),

    # Infra / ops
    "crashloop": (
        "Debugging CrashLoopBackOff in the production cluster. A container that "
        "exits shortly after start enters CrashLoopBackOff with exponential "
        "backoff. Check kubectl logs --previous for the crash output, verify "
        "liveness probe timeouts, and confirm required environment variables "
        "and secrets are mounted. Most cases trace to a failed migration on "
        "boot or an OOMKilled container with too low a memory limit."
    ),
    "k8s-deploy": (
        "Deploying services to Kubernetes. Services deploy via the CI pipeline "
        "which builds the image, pushes to the registry and applies the "
        "manifests. Rollouts use a 25% surge strategy. Use kubectl rollout "
        "status to watch a deployment complete."
    ),
    "terraform-lock": (
        "Terraform state lock errors. If terraform apply hangs or fails with a "
        "state lock error, a previous run likely crashed while holding the "
        "lock. Inspect the lock with the DynamoDB console, confirm no apply is "
        "actually running, then release it with terraform force-unlock LOCK_ID. "
        "Never force-unlock while a teammate's apply is in progress."
    ),
    "ci-pipeline": (
        "CI pipeline overview. Every merge to main triggers build, test and "
        "deploy stages. Flaky tests can be retried from the pipeline view. A "
        "red deploy stage pages the on-call engineer."
    ),
    "redis-pool": (
        "Worker timeouts caused by Redis connection pool exhaustion. Background "
        "workers opening one Redis connection per job exhaust the pool under "
        "load, and new jobs block until they time out. Configure a shared "
        "connection pool with max_connections sized to worker concurrency, and "
        "set socket_timeout so stuck connections fail fast."
    ),
    "redis-cache": (
        "Caching strategy. We cache rendered dashboard fragments in Redis with "
        "a 5 minute TTL. Cache keys include the workspace id and role hash. "
        "Invalidation happens on permission changes via a pub/sub channel."
    ),
    "pg-upgrade": (
        "Zero-downtime PostgreSQL major version upgrade. Use logical "
        "replication: provision a replica on the new version, replicate until "
        "lag is zero, pause writes briefly, switch the application connection "
        "string, then decommission the old primary. Rehearse the cutover in "
        "staging and keep the old primary for fast rollback."
    ),
    "pg-tuning": (
        "PostgreSQL tuning basics. Watch for sequential scans on large tables, "
        "set shared_buffers to roughly 25% of memory, and enable "
        "log_min_duration_statement to find slow queries."
    ),
    "incident-process": (
        "Incident response process. Declare an incident in the alerts channel, "
        "assign an incident commander, post status updates every 30 minutes, "
        "and write a retro within 5 working days. Sev1 means customer-facing "
        "outage; Sev2 means degraded service."
    ),

    # Integrations / API
    "webhook-rotate": (
        "Rotating a webhook signing secret. Each webhook endpoint has a signing "
        "secret used to compute the X-Signature header. To rotate without "
        "dropping events, add a second secret in the dashboard, deploy receiver "
        "code that accepts both, then revoke the old secret after 24 hours."
    ),
    "webhook-debug": (
        "Debugging webhook deliveries. The dashboard shows delivery attempts, "
        "response codes and payloads for each endpoint. Failed deliveries are "
        "retried with exponential backoff for up to 72 hours."
    ),
    "api-keys": (
        "API key management. Create scoped API keys from the developer "
        "settings. Keys are shown once at creation. Revoking a key invalidates "
        "it within 60 seconds. Rotate keys quarterly as a baseline practice."
    ),
    "rate-limits": (
        "API rate limiting. The public API allows 120 requests per minute per "
        "key. Exceeding the limit returns HTTP 429 with a Retry-After header. "
        "Batch endpoints have a separate 20 requests per minute limit."
    ),
    "sdk-android": (
        "Android SDK integration. Add the dependency, initialize the client in "
        "Application.onCreate with your publishable key, and call identify "
        "after sign-in. ProGuard rules ship inside the artifact."
    ),
    "sdk-ios": (
        "iOS SDK integration. Install via Swift Package Manager, initialize in "
        "the AppDelegate with your publishable key, and call identify after "
        "sign-in. The SDK requires iOS 15 or later."
    ),
    "sso-setup": (
        "Configuring SAML single sign-on. In the admin console upload your "
        "identity provider metadata, map email and group attributes, and test "
        "with a pilot group before enforcing. SCIM provisioning can be enabled "
        "after single sign-on is verified."
    ),
    "data-export": (
        "Exporting workspace data. Owners can export all workspace data as CSV "
        "or JSON from Settings. Exports are prepared asynchronously and a "
        "download link is emailed within a few hours."
    ),
}

# naive: corpus-blind synonyms. candidates: hand-authored, frozen before scoring.
QUERIES = [
    {
        "id": "q1-error-code",
        "query": "payment failed with error ERR-4032",
        "gold": "pay-err-4032",
        "kind": "exact identifier",
        "naive": ["charge", "declined", "transaction", "billing", "card", "issue"],
        "candidates": ["card", "declined", "avs", "mismatch", "billing",
                        "address", "gateway", "charge", "transaction"],
    },
    {
        "id": "q2-webhook-key",
        "query": "how do I rotate the signing key for webhooks",
        "gold": "webhook-rotate",
        "kind": "lexical-friendly",
        "naive": ["update", "change", "credentials", "security", "api"],
        "candidates": ["secret", "signing", "endpoint", "signature",
                        "revoke", "credentials", "rotate"],
    },
    {
        "id": "q3-slow-app",
        "query": "app is really slow after the last update",
        "gold": "perf-regression",
        "kind": "vocabulary mismatch",
        "naive": ["performance", "speed", "fix", "issue", "problem", "lag"],
        "candidates": ["latency", "degradation", "regression", "p95",
                        "response", "slow", "performance", "rollout", "queries"],
    },
    {
        "id": "q4-pod-restart",
        "query": "pod keeps restarting in production",
        "gold": "crashloop",
        "kind": "vocabulary mismatch",
        "naive": ["kubernetes", "failure", "deployment", "service", "container"],
        "candidates": ["crashloopbackoff", "container", "kubectl", "liveness",
                        "oomkilled", "backoff", "crash", "kubernetes"],
    },
    {
        "id": "q5-data-deletion",
        "query": "customer wants their data deleted",
        "gold": "gdpr-erasure",
        "kind": "vocabulary mismatch",
        "naive": ["remove", "account", "information", "user", "delete"],
        "candidates": ["gdpr", "erasure", "privacy", "purge", "personal",
                        "right", "remove", "account"],
    },
    {
        "id": "q6-pg-upgrade",
        "query": "upgrade postgres major version without downtime",
        "gold": "pg-upgrade",
        "kind": "lexical-friendly",
        "naive": ["database", "migration", "update", "maintenance"],
        "candidates": ["postgresql", "logical", "replication", "replica",
                        "cutover", "primary", "migration", "database"],
    },
    {
        "id": "q7-sso-plan",
        "query": "which plan includes SSO",
        "gold": "pricing-tiers",
        "kind": "vocabulary mismatch",
        "naive": ["pricing", "subscription", "features", "tier", "cost"],
        "candidates": ["saml", "single", "sign-on", "enterprise", "tier",
                        "scim", "pricing", "plan"],
    },
    {
        "id": "q8-version",
        "query": "what changed in v2.14.0",
        "gold": "changelog-2-14",
        "kind": "exact identifier",
        "naive": ["release", "notes", "version", "update", "new", "features"],
        "candidates": ["release", "notes", "permissions", "roles",
                        "dark", "mode", "version"],
    },
    {
        "id": "q9-2fa-reset",
        "query": "reset 2FA for a locked out user",
        "gold": "twofa-reset",
        "kind": "expansion trap",
        "naive": ["account", "login", "security", "access", "password",
                   "authentication", "locked"],
        "candidates": ["two-factor", "totp", "recovery", "re-enroll",
                        "authentication", "account", "login", "security",
                        "password", "device"],
    },
    {
        "id": "q10-redis-timeout",
        "query": "timeout connecting to redis from the worker",
        "gold": "redis-pool",
        "kind": "lexical-friendly",
        "naive": ["connection", "error", "cache", "network", "service"],
        "candidates": ["pool", "connection", "exhaustion", "max_connections",
                        "socket_timeout", "concurrency", "cache"],
    },
    {
        "id": "q11-vat",
        "query": "invoice shows wrong VAT for German customers",
        "gold": "vat-germany",
        "kind": "exact identifier",
        "naive": ["tax", "billing", "invoice", "error", "europe"],
        "candidates": ["vat-1203", "tax", "rate", "19%", "de", "regenerated",
                        "invoices", "germany"],
    },
    {
        "id": "q12-terraform",
        "query": "deploy is stuck at terraform apply",
        "gold": "terraform-lock",
        "kind": "vocabulary mismatch",
        "naive": ["deployment", "infrastructure", "pipeline", "failed", "ci"],
        "candidates": ["state", "lock", "force-unlock", "dynamodb",
                        "hangs", "infrastructure", "pipeline"],
    },
]
