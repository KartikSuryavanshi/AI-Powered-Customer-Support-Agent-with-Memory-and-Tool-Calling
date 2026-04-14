# SSO Troubleshooting Guide

When users are signed out frequently after SSO enablement:

1. Validate identity provider session timeout and token refresh settings.
2. Confirm clock synchronization between IdP and app servers.
3. Ensure callback URLs exactly match production domains.
4. Ask customer to capture timestamped HAR logs for failed sessions.

Enterprise customers should receive updates every 4 business hours for P1/P2 incidents.
