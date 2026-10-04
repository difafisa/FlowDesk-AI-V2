# FlowDesk Authentication

## 1. Overview

FlowDesk uses separate authentication mechanisms for accessing the **FlowDesk application** and the **FlowDesk API**.

Authentication verifies who is accessing FlowDesk, while authorization determines what that authenticated user or API client is permitted to access.

| Access Type                   | Authentication Method | Availability       |
| ----------------------------- | --------------------- | ------------------ |
| FlowDesk application          | User account login    | All plans          |
| FlowDesk application with SSO | Single Sign-On (SSO)  | Enterprise only    |
| FlowDesk API                  | Bearer Token          | Pro and Enterprise |
| API access on Free plan       | Not available         | Free plan          |

FlowDesk also uses role-based access control (RBAC) to restrict actions according to a user's assigned role and permissions.

> **Note:** Authentication and authorization are separate concepts. Successfully authenticating with FlowDesk does not automatically grant permission to perform every action.

---

## 2. User Authentication

FlowDesk application users authenticate using their FlowDesk user account credentials.

Application authentication is used when accessing the FlowDesk web application, including areas such as:

- Tickets
- Customer profiles
- Automation
- Analytics
- Team management
- Billing and subscription management

After successful authentication, FlowDesk determines which resources and actions the user can access based on their assigned permissions.

Enterprise customers can additionally use SSO for application authentication.

---

## 3. Login

To access the FlowDesk application:

1. Open the FlowDesk application.
2. Enter your FlowDesk account credentials.
3. Submit the login form.
4. FlowDesk verifies the provided credentials.
5. After successful authentication, FlowDesk establishes an authenticated application session.
6. FlowDesk applies the user's authorization and role permissions.

If authentication fails, verify that the credentials are correct and try again.

> **Security note:** Never share your FlowDesk account credentials with another user. Each team member should use their own FlowDesk account.

---

## 4. Logout

Users should log out when they finish using FlowDesk, particularly when accessing FlowDesk from a shared or public computer.

To log out:

1. Open the user account menu.
2. Select **Log out**.
3. FlowDesk ends the current authenticated application session.
4. To access the application again, the user must authenticate again.

Logging out of the FlowDesk application does not change API tokens that have previously been issued.

---

## 5. API Authentication

FlowDesk API requests use **Bearer Token authentication**.

The FlowDesk API is available only on:

- Pro
- Enterprise

The Free plan does not include API access.

The API base URL is:

```text
https://api.flowdesk.example/v1
```

Every authenticated API request must provide a valid API token in the HTTP `Authorization` header.

---

## 6. Bearer Token Authentication

FlowDesk uses the standard Bearer Token format.

The token is provided after the `Bearer` scheme in the `Authorization` header:

```http
Authorization: Bearer <API_TOKEN>
```

For example:

```http
GET /tickets HTTP/1.1
Host: api.flowdesk.example
Authorization: Bearer <API_TOKEN>
```

The API token identifies and authenticates the API client making the request.

> **Warning:** Treat API tokens as confidential credentials. Do not publish tokens in source code, documentation, screenshots, public repositories, or client-side applications.

---

## 7. API Token Usage

API tokens are used to authenticate requests to the FlowDesk API.

A typical API request includes:

1. The FlowDesk API base URL.
2. The requested API endpoint.
3. The `Authorization` header.
4. A valid Bearer Token.

For example:

```bash
curl https://api.flowdesk.example/v1/tickets \
  -H "Authorization: Bearer <API_TOKEN>"
```

API access is subject to the rate limit associated with the customer's subscription plan.

| Plan       | API Access |          Rate Limit |
| ---------- | ---------- | ------------------: |
| Free       | No         |                 N/A |
| Pro        | Yes        |  60 requests/minute |
| Enterprise | Yes        | 300 requests/minute |

> **Note:** Having an API token does not override authorization restrictions. API requests remain subject to the permissions associated with the authenticated API access.

---

## 8. Authentication Headers

FlowDesk API requests should include the `Authorization` HTTP header.

### Authorization Header

```http
Authorization: Bearer <API_TOKEN>
```

A complete request can look like:

```http
GET https://api.flowdesk.example/v1/tickets
Authorization: Bearer <API_TOKEN>
```

### cURL Example

```bash
curl https://api.flowdesk.example/v1/tickets \
  -H "Authorization: Bearer <API_TOKEN>"
```

Replace `<API_TOKEN>` with the valid API token associated with your FlowDesk account.

---

## 9. Authentication Errors

An API request can fail when authentication credentials are missing, invalid, or otherwise cannot be accepted.

Common authentication-related responses include:

| HTTP Status        | Error                      | Description                                                                                                          |
| ------------------ | -------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `401 Unauthorized` | `authentication_required`  | The request does not contain valid authentication credentials.                                                       |
| `401 Unauthorized` | `invalid_token`            | The supplied Bearer Token is invalid or cannot be authenticated.                                                     |
| `403 Forbidden`    | `insufficient_permissions` | The request is authenticated, but the authenticated client does not have permission to perform the requested action. |

Example error response:

```json
{
    "error": {
        "code": "invalid_token",
        "message": "The provided API token is invalid."
    }
}
```

A `401 Unauthorized` response generally indicates an authentication problem, while a `403 Forbidden` response indicates that authentication succeeded but access to the requested resource or action is not permitted.

---

## 10. Authorization and Access Control

Authentication and authorization serve different purposes.

### Authentication

Authentication answers:

> **"Who are you?"**

Examples include:

- Signing in to the FlowDesk application.
- Providing a valid API Bearer Token.

### Authorization

Authorization answers:

> **"What are you allowed to do?"**

FlowDesk applies authorization after authentication to determine whether a user or API client can access a resource or perform an action.

Authorization can depend on:

- The user's assigned role.
- The permissions associated with that role.
- The customer's FlowDesk subscription plan.
- Whether the requested feature is available on that plan.

For example, a user on a Free subscription cannot use the FlowDesk API because API access is not included in the Free plan, even if the user is otherwise authorized to manage tickets within the application.

---

## 11. Role-Based Access Control

FlowDesk uses **role-based access control (RBAC)** to manage user permissions.

RBAC associates users with roles, and roles determine which actions those users are permitted to perform.

Typical administrative access may include managing:

- Team members
- Customer information
- Tickets
- Automation
- Analytics
- Subscription settings

Access should be assigned according to the user's responsibilities.

> **Best practice:** Grant users only the permissions they need to perform their work.

API authentication and application RBAC should also be treated as separate access layers. An API token authenticates an API request, while authorization determines whether the requested operation is permitted.

---

## 12. SSO Availability

Single Sign-On (SSO) is available **only to Enterprise customers**.

| Plan       | SSO |
| ---------- | --- |
| Free       | No  |
| Pro        | No  |
| Enterprise | Yes |

Free and Pro customers must use the standard FlowDesk application authentication process.

Enterprise customers can use SSO as an additional application authentication option.

> **Important:** SSO availability does not change the API authentication method. FlowDesk API requests continue to use Bearer Token authentication.

---

## 13. Security Best Practices

Follow these practices when managing FlowDesk authentication credentials.

### Protect Account Credentials

- Do not share user account credentials.
- Use a unique password for your FlowDesk account.
- Log out when using shared computers.
- Review team access regularly.

### Protect API Tokens

- Store API tokens securely.
- Do not commit API tokens to source-control repositories.
- Do not place API tokens directly in publicly accessible frontend code.
- Do not include tokens in screenshots or support requests.
- Use environment variables or an appropriate secrets-management mechanism for applications.

For example:

```bash
export FLOWDESK_API_TOKEN="<API_TOKEN>"
```

An application can then use the token when constructing authenticated API requests.

### Use HTTPS

FlowDesk API requests should use the HTTPS API endpoint:

```text
https://api.flowdesk.example/v1
```

HTTPS helps protect authentication credentials and API traffic during transmission.

---

## 14. Authentication Examples

### Basic API Request

```bash
curl https://api.flowdesk.example/v1/tickets \
  -H "Authorization: Bearer <API_TOKEN>"
```

### Request with an HTTP Header

```http
GET /v1/tickets HTTP/1.1
Host: api.flowdesk.example
Authorization: Bearer <API_TOKEN>
```

### Python Example

```python
import requests

API_TOKEN = "<API_TOKEN>"

headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

response = requests.get(
    "https://api.flowdesk.example/v1/tickets",
    headers=headers
)

print(response.status_code)
print(response.json())
```

### Successful Authentication

If the API token is valid and the authenticated client has permission to access the requested resource, FlowDesk processes the request.

For example:

```text
GET https://api.flowdesk.example/v1/tickets
Authorization: Bearer <API_TOKEN>
```

The request is authenticated using the supplied Bearer Token before authorization is evaluated.

---

## 15. Common Authentication Issues

### Missing Authorization Header

**Symptom:** The API returns `401 Unauthorized`.

**Cause:** The request does not contain the required `Authorization` header.

**Solution:**

Add the Bearer Token:

```http
Authorization: Bearer <API_TOKEN>
```

---

### Invalid API Token

**Symptom:** The API returns an `invalid_token` authentication error.

**Cause:** The supplied token is not valid.

**Solution:**

1. Verify that the correct token is being used.
2. Check that the complete token is being passed.
3. Ensure the `Bearer` authentication scheme is included.
4. Retry the request with a valid token.

---

### Using API Access on the Free Plan

**Symptom:** You cannot authenticate API requests while using a Free subscription.

**Cause:** API access is not included in the Free plan.

**Solution:** API access requires a Pro or Enterprise subscription.

---

### Authentication vs. Authorization Error

**Symptom:** The API returns `403 Forbidden`.

**Cause:** Authentication succeeded, but the authenticated client does not have sufficient permission to perform the requested operation.

**Solution:**

Review the permissions and authorization associated with the authenticated user or API client.

A valid API token alone does not guarantee access to every FlowDesk resource.

---

### SSO Expectations on Non-Enterprise Plans

**Symptom:** SSO configuration is not available.

**Cause:** SSO is an Enterprise-only feature.

**Solution:** SSO is available only on the Enterprise plan. Free and Pro customers use standard FlowDesk application authentication.

---

### Quick Reference

| Question                                               | Answer                                                |
| ------------------------------------------------------ | ----------------------------------------------------- |
| How do users authenticate to the FlowDesk application? | Through their FlowDesk user account                   |
| Is SSO available?                                      | Yes, but only for Enterprise                          |
| How is the API authenticated?                          | Bearer Token                                          |
| What header is required?                               | `Authorization: Bearer <API_TOKEN>`                   |
| What is the API base URL?                              | `https://api.flowdesk.example/v1`                     |
| Does Free include API access?                          | No                                                    |
| What is the Pro API rate limit?                        | 60 requests/minute                                    |
| What is the Enterprise API rate limit?                 | 300 requests/minute                                   |
| Does authentication grant all permissions?             | No                                                    |
| What does `401 Unauthorized` indicate?                 | An authentication problem                             |
| What does `403 Forbidden` indicate?                    | Authentication succeeded, but access is not permitted |
