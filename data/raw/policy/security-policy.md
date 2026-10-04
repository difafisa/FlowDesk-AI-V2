# FlowDesk Security Policy

## 1. Security Policy Overview

FlowDesk is designed to help organizations manage customer support operations while providing security capabilities for protecting access to accounts and support information.

FlowDesk security capabilities include:

- HTTPS for network communication.
- Encrypted data transmission.
- Role-based access control.
- Audit logs.
- Single Sign-On (SSO) for Enterprise customers.

Security is a shared responsibility. FlowDesk provides security controls within the platform, while customers are responsible for appropriately managing their accounts, users, credentials, and access permissions.

> **Note:** This policy describes FlowDesk's documented security capabilities. It does not make claims about certifications, compliance frameworks, or security standards that are not specifically documented.

## 2. Security Principles

FlowDesk's security approach is based on several principles:

1. **Protect data in transit** — HTTPS and encrypted data transmission help protect information while it is transmitted.
2. **Control access** — Role-based access control helps organizations limit access to FlowDesk resources.
3. **Maintain visibility** — Audit logs provide visibility into relevant administrative and security-related activity.
4. **Secure authentication** — FlowDesk provides authentication and access-management capabilities appropriate to the available subscription features.
5. **Provide enterprise controls** — Enterprise customers have access to SSO as part of the Enterprise plan.

## 3. HTTPS and Data Transmission

FlowDesk uses **HTTPS** for supported network communication.

HTTPS helps protect information exchanged between customers and FlowDesk while it is transmitted.

Customers should also ensure that systems integrating with FlowDesk use secure HTTPS connections when communicating with FlowDesk services.

## 4. Encryption in Transit

FlowDesk uses **encrypted data transmission** to protect information while it is being transmitted.

This protection applies to data moving between systems over supported network connections.

FlowDesk does not specify particular encryption algorithms, key lengths, or other cryptographic implementation details in this policy.

> **Important:** This policy does not make claims about specific encryption standards, certifications, or compliance frameworks.

## 5. Role-Based Access Control

FlowDesk supports **role-based access control (RBAC)**.

RBAC allows organizations to manage access based on user roles rather than giving every team member the same level of access.

For example, an organization might use different roles for:

- Support agents who manage customer conversations and tickets.
- Team members who require administrative access.
- Users who need limited access to specific FlowDesk resources.

These are examples of how roles may be organized. They do not represent a fixed FlowDesk permission matrix.

### Recommended Access-Control Approach

1. Give team members only the access they need for their responsibilities.
2. Review user access when responsibilities change.
3. Remove access for users who no longer require it.
4. Periodically review account permissions.
5. Use administrative controls carefully for sensitive operations.

## 6. Audit Logs

FlowDesk provides **audit logs** to help organizations maintain visibility into administrative and security-related activity.

Audit logs can help customers:

- Review relevant account activity.
- Investigate unexpected administrative actions.
- Monitor changes to access or configuration.
- Support internal security reviews.
- Identify activity that may require investigation.

The exact activities recorded may depend on the applicable FlowDesk functionality.

> **Note:** This policy does not specify an audit-log retention period.

## 7. Authentication and Access Management

Customers are responsible for maintaining secure access to their FlowDesk accounts.

Recommended access-management practices include:

- Protecting account credentials.
- Limiting account access to authorized team members.
- Assigning appropriate user permissions.
- Reviewing access regularly.
- Removing access when it is no longer required.

### API Authentication

For plans that include API access, FlowDesk API requests use **Bearer Token authentication**.

API tokens should be treated as sensitive credentials. Customers should:

- Store API tokens securely.
- Avoid exposing tokens in public repositories or client-side code.
- Limit access to tokens to authorized personnel.
- Rotate or replace compromised tokens as appropriate.

> **Important:** API access is unavailable on the Free plan. API access is available on Pro and Enterprise.

## 8. Single Sign-On (SSO)

FlowDesk supports **Single Sign-On (SSO) only for Enterprise customers**.

SSO is included as part of the Enterprise plan and provides an additional way for Enterprise organizations to manage user authentication through their supported identity-management processes.

SSO availability by plan:

| Plan       | SSO |
| ---------- | --- |
| Free       | No  |
| Pro        | No  |
| Enterprise | Yes |

> **Important:** SSO is not available on Pro or Free.

## 9. Plan Availability

FlowDesk security capabilities vary by subscription plan.

| Security capability         | Free | Pro | Enterprise |
| --------------------------- | ---: | --: | ---------: |
| HTTPS                       |  Yes | Yes |        Yes |
| Encrypted data transmission |  Yes | Yes |        Yes |
| Role-based access control   |  Yes | Yes |        Yes |
| Audit logs                  |  Yes | Yes |        Yes |
| SSO                         |   No |  No |        Yes |
| API access                  |   No | Yes |        Yes |

SSO is the only capability in this table that is restricted to Enterprise.

## 10. Customer Security Responsibilities

Customers are responsible for securely managing their FlowDesk accounts and access.

Customers should:

### Protect Credentials

- Keep account credentials confidential.
- Avoid sharing credentials between users.
- Use appropriate organizational controls for account access.

### Manage User Access

- Grant access only to authorized team members.
- Assign appropriate roles and permissions.
- Review access periodically.
- Remove access when team members no longer need it.

### Monitor Activity

- Review available audit logs.
- Investigate unexpected administrative or security-related activity.
- Establish internal procedures for responding to suspicious activity.

### Protect API Tokens

For Pro and Enterprise customers using API access:

- Treat API tokens as confidential credentials.
- Store tokens securely.
- Do not expose tokens in public source code.
- Restrict token access to authorized personnel.

## 11. Security Incident Reporting

Customers who suspect a security incident involving their FlowDesk account should report the issue to **FlowDesk Support** as soon as possible.

When reporting a suspected incident, provide relevant information such as:

- A description of the suspected security issue.
- The affected FlowDesk account or functionality.
- Approximate date and time of the activity, if known.
- Relevant error messages or activity details.
- Steps already taken to protect the account.

Customers should avoid sharing passwords or API tokens in support requests.

FlowDesk Support can use the information provided to investigate the reported issue and advise on appropriate next steps.

## 12. Security Best Practices

Customers can improve account security by following these practices:

- Restrict FlowDesk access to authorized team members.
- Review user permissions regularly.
- Protect account credentials.
- Monitor audit logs for unexpected activity.
- Protect API tokens when using API-enabled plans.
- Use HTTPS for systems that communicate with FlowDesk.
- Report suspected security incidents promptly.
- Review access after organizational or role changes.

> **Warning:** Never include passwords, API tokens, or other sensitive authentication credentials in a support request.

## 13. Frequently Asked Questions

### Does FlowDesk encrypt data?

Yes. FlowDesk uses encrypted data transmission to protect data while it is being transmitted.

### Does FlowDesk use HTTPS?

Yes. HTTPS is a supported FlowDesk security capability and helps protect information during network transmission.

### What is role-based access control?

Role-based access control allows organizations to manage access to FlowDesk resources based on assigned user roles. This helps limit access to appropriate team members.

### Does FlowDesk provide audit logs?

Yes. FlowDesk provides audit logs that can help customers review administrative and security-related activity.

### Is SSO available on Pro?

No. SSO is not available on Pro.

### Which plan includes SSO?

SSO is available only on the **Enterprise** plan.

### Do Free customers have API access?

No. API access is unavailable on the Free plan. Pro and Enterprise include API access.

### What can customers do to improve account security?

Customers should protect account credentials, limit access to authorized users, manage permissions carefully, monitor audit logs, and protect API tokens when using API-enabled plans.

### Does FlowDesk provide a security certification?

This policy does not specify any security certifications or compliance frameworks. Customers should not infer certification or compliance status from the security capabilities described here.

### Does FlowDesk specify how long audit logs are retained?

No. This policy does not specify an audit-log retention period.
