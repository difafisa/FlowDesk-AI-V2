# FlowDesk API Error Troubleshooting

## 1. Overview

This guide helps developers, technical administrators, and FlowDesk support agents diagnose and resolve common errors encountered when using the FlowDesk API.

The FlowDesk API provides programmatic access to FlowDesk resources and requires:

- A **Pro** or **Enterprise** subscription.
- A valid FlowDesk API token.
- Bearer Token authentication.
- Requests sent to the correct API base URL.
- Valid HTTP methods, parameters, request bodies, and JSON syntax.

### Base URL

```text
https://api.flowdesk.example/v1
```

All API endpoints should use the `/v1` API version.

### Authentication

FlowDesk API requests use Bearer Token authentication.

```http
Authorization: Bearer <API_TOKEN>
```

Example:

```http
GET /v1/tickets/FD-10025 HTTP/1.1
Host: api.flowdesk.example
Authorization: Bearer <API_TOKEN>
Accept: application/json
```

> **Note:** API access is not available on the Free plan. Free customers must upgrade to Pro or Enterprise before making API requests.

---

## 2. API Access by Subscription Plan

API availability and rate limits depend on the customer's subscription plan.

| Plan       | API Access | Rate Limit          |
| ---------- | ---------- | ------------------- |
| Free       | No         | Not available       |
| Pro        | Yes        | 60 requests/minute  |
| Enterprise | Yes        | 300 requests/minute |

### Free Plan

The Free plan does not include API access. API requests made by Free customers may fail because API functionality is unavailable for the subscription.

Upgrading to Pro or Enterprise enables API access.

### Pro Plan

Pro customers have API access with a limit of **60 requests per minute**.

### Enterprise Plan

Enterprise customers have API access with a limit of **300 requests per minute**.

> **Important:** Do not attempt to resolve a Free-plan API access problem by changing the API token or increasing retry frequency. API access is not included with the Free plan.

---

# 3. Authentication Errors

Authentication errors occur when FlowDesk cannot establish a valid authenticated API session from the supplied credentials.

The most common authentication problems are:

1. Missing `Authorization` header.
2. Invalid API token.
3. Expired or revoked token.
4. Incorrect Bearer Token format.

## 3.1 Missing Authorization Header

### Example Request

```http
GET /v1/tickets/FD-10025 HTTP/1.1
Host: api.flowdesk.example
Accept: application/json
```

### Example Error

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json
```

```json
{
    "error": {
        "code": "authentication_required",
        "message": "Authorization header is required."
    }
}
```

### Likely Cause

The request does not contain an `Authorization` header.

### Troubleshooting Steps

1. Confirm that the request includes an `Authorization` header.
2. Confirm that the authentication scheme is `Bearer`.
3. Confirm that the token is present after `Bearer`.
4. Retry the request.

Correct example:

```http
Authorization: Bearer <API_TOKEN>
```

---

## 3.2 Invalid API Token

### Example Request

```http
GET /v1/tickets/FD-10025 HTTP/1.1
Host: api.flowdesk.example
Authorization: Bearer invalid-token
Accept: application/json
```

### Example Error

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json
```

```json
{
    "error": {
        "code": "invalid_token",
        "message": "The supplied API token is invalid."
    }
}
```

### Likely Cause

The token may have been copied incorrectly or may not be a valid FlowDesk API token.

### Troubleshooting Steps

1. Check the configured API token.
2. Look for accidental whitespace or missing characters.
3. Verify that the application is loading the intended token.
4. Replace the token if necessary.
5. Retry the request.

Avoid logging API tokens in application logs.

---

## 3.3 Expired or Revoked Token

### Example Error

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json
```

```json
{
    "error": {
        "code": "token_invalid",
        "message": "The API token is expired or has been revoked."
    }
}
```

### Likely Cause

The token is no longer valid.

### Troubleshooting Steps

1. Confirm the token's current status in the FlowDesk account.
2. Determine whether the token was revoked.
3. Generate or obtain a valid replacement token if appropriate.
4. Update the application configuration.
5. Retry the request.

---

## 3.4 Incorrect Bearer Token Format

### Incorrect

```http
Authorization: <API_TOKEN>
```

or:

```http
Authorization: Token <API_TOKEN>
```

### Correct

```http
Authorization: Bearer <API_TOKEN>
```

### Example Error

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json
```

```json
{
    "error": {
        "code": "invalid_authorization",
        "message": "Authorization must use the Bearer authentication scheme."
    }
}
```

### Troubleshooting Steps

1. Check the `Authorization` header.
2. Ensure it starts with `Bearer`.
3. Separate `Bearer` and the token with a single space.
4. Retry the request.

---

# 4. HTTP Error Codes

FlowDesk API responses use standard HTTP status codes to communicate the general result of a request.

The exact response behavior can vary by endpoint. The following codes represent common troubleshooting cases and should not be interpreted as a guarantee that every FlowDesk endpoint returns every listed status code.

## 4.1 400 Bad Request

### Meaning

The server cannot process the request because the request is malformed or contains invalid input.

### Common FlowDesk-Related Causes

- Malformed query parameters.
- Invalid request syntax.
- Missing information required to process the request.
- Invalid parameter formatting.

### Example

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json
```

```json
{
    "error": {
        "code": "bad_request",
        "message": "The request could not be processed."
    }
}
```

### Recommended Action

1. Review the complete request.
2. Check query parameters.
3. Check the request body.
4. Verify the HTTP method.
5. Retry after correcting the malformed input.

---

## 4.2 401 Unauthorized

### Meaning

The request does not contain valid authentication credentials.

### Common Causes

- Missing `Authorization` header.
- Invalid token.
- Expired or revoked token.
- Incorrect Bearer Token syntax.

### Recommended Action

Verify:

```http
Authorization: Bearer <API_TOKEN>
```

Then confirm that the token is valid and retry the request.

---

## 4.3 403 Forbidden

### Meaning

The request was authenticated, but access to the requested operation or resource is not permitted.

### Common FlowDesk-Related Causes

- The authenticated account does not have permission for the requested operation.
- The requested API functionality is not available to the subscription.
- An account or user role does not have sufficient access.

### Example

```http
HTTP/1.1 403 Forbidden
Content-Type: application/json
```

```json
{
    "error": {
        "code": "forbidden",
        "message": "You do not have permission to perform this operation."
    }
}
```

### Recommended Action

1. Confirm the account's subscription plan.
2. Confirm API access is enabled for the plan.
3. Check the user's or integration's permissions.
4. Verify that the operation is appropriate for the account.
5. Contact FlowDesk support if the permissions appear correct.

---

## 4.4 404 Not Found

### Meaning

The requested endpoint or resource could not be found.

### Common Causes

- Incorrect endpoint path.
- Incorrect resource ID.
- Resource is no longer available.
- Incorrect API version.
- Missing `/v1` path.

### Example

```http
GET /v1/tickets/FD-99999 HTTP/1.1
Host: api.flowdesk.example
Authorization: Bearer <API_TOKEN>
```

```http
HTTP/1.1 404 Not Found
Content-Type: application/json
```

```json
{
    "error": {
        "code": "resource_not_found",
        "message": "The requested ticket was not found."
    }
}
```

### Recommended Action

1. Confirm the URL.
2. Confirm `/v1` is included.
3. Check the resource ID.
4. Verify that the resource exists.
5. Retry using the correct resource identifier.

---

## 4.5 405 Method Not Allowed

### Meaning

The HTTP method is not supported for the requested resource.

### Common Causes

- Using `GET` where the operation requires another method.
- Using `POST` against a read-only operation.
- Client code configured with the wrong HTTP method.

### Example

```http
DELETE /v1/tickets/FD-10025 HTTP/1.1
Host: api.flowdesk.example
Authorization: Bearer <API_TOKEN>
```

If the specific resource does not support that operation, the server may respond:

```http
HTTP/1.1 405 Method Not Allowed
Content-Type: application/json
```

```json
{
    "error": {
        "code": "method_not_allowed",
        "message": "The HTTP method is not supported for this resource."
    }
}
```

### Recommended Action

1. Review the endpoint documentation.
2. Confirm the supported HTTP method.
3. Check the client implementation.
4. Retry using the correct method.

---

## 4.6 409 Conflict

### Meaning

The request conflicts with the current state of the resource.

### Common Causes

- Attempting an operation that conflicts with the resource's current state.
- Concurrent updates to the same resource.
- Attempting to create a resource that conflicts with an existing resource.

### Example

```http
HTTP/1.1 409 Conflict
Content-Type: application/json
```

```json
{
    "error": {
        "code": "resource_conflict",
        "message": "The requested operation conflicts with the current resource state."
    }
}
```

### Recommended Action

1. Retrieve the current resource state.
2. Check whether another operation changed the resource.
3. Adjust the request based on the current state.
4. Retry when appropriate.

---

## 4.7 422 Unprocessable Entity

### Meaning

The request is syntactically valid, but the submitted data cannot be accepted.

### Common Causes

- Invalid field values.
- Incorrect business data.
- Invalid ticket status.
- Invalid ticket priority.
- Incorrect field types.

### Example

```json
{
    "subject": "Unable to log in",
    "description": "Customer cannot access their account.",
    "priority": "critical"
}
```

If `critical` is not a valid FlowDesk ticket priority, the API may return:

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
```

```json
{
    "error": {
        "code": "validation_failed",
        "message": "One or more fields contain invalid values.",
        "fields": {
            "priority": "Priority must be low, medium, high, or urgent."
        }
    }
}
```

### Recommended Action

Use one of the supported ticket priorities:

```text
low
medium
high
urgent
```

Review all validation messages before resubmitting the request.

---

## 4.8 429 Too Many Requests

### Meaning

The client has exceeded the API request rate allowed by its subscription.

### FlowDesk Rate Limits

| Plan       |      API Rate Limit |
| ---------- | ------------------: |
| Pro        |  60 requests/minute |
| Enterprise | 300 requests/minute |

### Example

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
```

```json
{
    "error": {
        "code": "rate_limit_exceeded",
        "message": "API request rate limit exceeded."
    }
}
```

### Recommended Action

1. Reduce request frequency.
2. Avoid unnecessary repeated requests.
3. Implement retry logic.
4. Use exponential backoff.
5. Check whether multiple application processes are sharing the same API access.
6. Retry after an appropriate delay.

> **Important:** The Free plan does not have API access and therefore does not have an API rate limit to troubleshoot.

---

## 4.9 500 Internal Server Error

### Meaning

The server encountered an unexpected condition while processing the request.

### Common Causes

A 500 response generally indicates a server-side problem rather than a malformed client request.

### Example

```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json
```

```json
{
    "error": {
        "code": "internal_server_error",
        "message": "An unexpected server error occurred."
    }
}
```

### Recommended Action

1. Check your application logs.
2. Confirm the request is valid.
3. Retry after a short period.
4. Determine whether the error is temporary.
5. Contact FlowDesk support if the problem persists.

Do not repeatedly send requests at high frequency when a server error occurs.

---

## 4.10 502 Bad Gateway

### Meaning

A gateway or intermediary received an invalid response while attempting to process the request.

### Common Causes

A 502 response generally indicates a temporary server-side or intermediary communication problem.

### Recommended Action

1. Retry after a short period.
2. Confirm that the request itself is valid.
3. Check application logs.
4. Determine whether subsequent requests succeed.
5. Contact FlowDesk support if the issue continues.

Do not assume that a 502 indicates an invalid API token.

---

## 4.11 503 Service Unavailable

### Meaning

The service is temporarily unavailable or unable to process the request.

### Common Causes

- Temporary service unavailability.
- Temporary server-side conditions.
- A service interruption.

### Example

```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json
```

```json
{
    "error": {
        "code": "service_unavailable",
        "message": "The API is temporarily unavailable."
    }
}
```

### Recommended Action

1. Wait briefly.
2. Retry the request.
3. Use retry logic with exponential backoff.
4. Check application logs.
5. Contact FlowDesk support if the problem persists.

---

# 5. Rate Limit Errors

FlowDesk limits API request frequency according to the subscription plan.

| Plan       | API Access |          Rate Limit |
| ---------- | ---------- | ------------------: |
| Free       | No         |       Not available |
| Pro        | Yes        |  60 requests/minute |
| Enterprise | Yes        | 300 requests/minute |

## Recognizing Rate Limiting

A rate-limit problem commonly appears as:

```http
HTTP/1.1 429 Too Many Requests
```

Example:

```json
{
    "error": {
        "code": "rate_limit_exceeded",
        "message": "API request rate limit exceeded."
    }
}
```

## Recommended Retry Strategy

Applications should avoid immediately repeating a request after receiving a `429`.

A simple exponential backoff strategy can increase the delay between attempts:

```text
Attempt 1: wait 1 second
Attempt 2: wait 2 seconds
Attempt 3: wait 4 seconds
Attempt 4: wait 8 seconds
```

The exact retry strategy should be appropriate for the application's workload.

## Reduce Unnecessary Requests

Consider:

- Removing duplicate requests.
- Avoiding aggressive polling.
- Caching data that does not need to be retrieved repeatedly.
- Combining application operations where the API supports the required operation.
- Preventing multiple application workers from unnecessarily requesting the same data.

> **Note:** Do not treat rate limiting as an authentication problem. A valid API token can still receive a `429` response when the applicable request rate is exceeded.

---

# 6. Request Validation Errors

Request validation problems occur when the request reaches the API but the supplied data cannot be processed.

## 6.1 Missing Required Fields

Example ticket request:

```http
POST /v1/tickets HTTP/1.1
Host: api.flowdesk.example
Authorization: Bearer <API_TOKEN>
Content-Type: application/json
```

```json
{
    "description": "Customer cannot access their account."
}
```

The API may return:

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json
```

```json
{
    "error": {
        "code": "missing_field",
        "message": "Required field 'subject' is missing."
    }
}
```

### Troubleshooting

1. Review the endpoint's required fields.
2. Confirm that every required field is included.
3. Check for misspelled property names.
4. Retry with a complete request.

---

## 6.2 Invalid Field Values

FlowDesk tickets use the following statuses:

```text
open
pending
resolved
closed
```

They use the following priorities:

```text
low
medium
high
urgent
```

An invalid request might contain:

```json
{
    "subject": "Login problem",
    "description": "Customer cannot log in.",
    "status": "in-progress",
    "priority": "high"
}
```

A possible response is:

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
```

```json
{
    "error": {
        "code": "validation_failed",
        "message": "Invalid ticket status.",
        "fields": {
            "status": "Status must be open, pending, resolved, or closed."
        }
    }
}
```

### Troubleshooting

Replace the unsupported value with a valid FlowDesk value.

---

## 6.3 Incorrect Data Types

For example, an application might send a numeric value where a text field is expected:

```json
{
    "subject": 12345,
    "description": "Customer cannot log in.",
    "priority": "high"
}
```

The API may respond with:

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
```

```json
{
    "error": {
        "code": "validation_failed",
        "message": "Invalid field type.",
        "fields": {
            "subject": "Subject must be a string."
        }
    }
}
```

### Troubleshooting

Check the expected data type for every request property before sending the request.

---

## 6.4 Invalid JSON

Malformed JSON can prevent the API from parsing the request.

Incorrect:

```json
{
    "subject": "Login problem",
    "description": "Customer cannot log in.",
    "priority": "high"
}
```

The trailing comma makes this invalid JSON.

A possible response is:

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json
```

```json
{
    "error": {
        "code": "invalid_json",
        "message": "The request body contains invalid JSON."
    }
}
```

### Troubleshooting

1. Validate the JSON before sending it.
2. Remove trailing commas.
3. Ensure strings use valid JSON quotation marks.
4. Confirm that the `Content-Type` is appropriate for the request.

---

## 6.5 Incorrect Request Method

Using an unsupported HTTP method can result in:

```http
HTTP/1.1 405 Method Not Allowed
```

Before changing the request, verify the operation's documented HTTP method.

Do not switch methods arbitrarily because a request returned another error.

---

# 7. Resource Not Found

A `404 Not Found` response indicates that the requested endpoint or resource could not be found.

## Common Causes

### Incorrect Endpoint Path

For example:

```text
/v1/ticket/FD-10025
```

may be incorrect if the resource path is:

```text
/v1/tickets/FD-10025
```

### Incorrect Resource ID

Example:

```text
/v1/tickets/FD-99999
```

If the ticket does not exist, the API may return:

```http
HTTP/1.1 404 Not Found
```

### Resource No Longer Available

A resource may no longer be available under the requested identifier.

### Incorrect API Version

FlowDesk API requests should use:

```text
https://api.flowdesk.example/v1
```

For example, an application incorrectly configured to call:

```text
https://api.flowdesk.example/v2
```

may encounter a resource or endpoint error.

### Troubleshooting Procedure

1. Check the complete request URL.
2. Confirm the base URL.
3. Confirm `/v1` is present.
4. Check the endpoint path.
5. Check the resource identifier.
6. Confirm that the resource exists.
7. Retry the request.

---

# 8. Server-Side Errors

Server-side errors generally indicate that the request reached the API but the server could not successfully complete it.

The most relevant responses are:

- `500 Internal Server Error`
- `502 Bad Gateway`
- `503 Service Unavailable`

## Recommended Procedure

### Step 1: Verify the Request

Confirm:

- Base URL.
- `/v1` API version.
- HTTP method.
- Authorization header.
- Request parameters.
- Request body.
- JSON syntax.

### Step 2: Check Application Logs

Review your application's logs for:

- Request timestamps.
- HTTP method.
- Endpoint.
- Response status.
- Request correlation information, if available.

Do not store API tokens or other sensitive credentials in logs.

### Step 3: Retry Carefully

For temporary server errors:

```text
1. Wait briefly.
2. Retry once.
3. If the error continues, increase the delay.
4. Continue using controlled retry logic.
```

Exponential backoff can help avoid creating additional load during temporary failures.

### Step 4: Contact FlowDesk Support

If the problem continues after verifying the request and retrying, contact FlowDesk support with:

- HTTP status code.
- Approximate request time.
- Endpoint used.
- HTTP method.
- Sanitized request details.
- Response body.
- Relevant application logs.

Never include the API token in a support request.

---

# 9. Example Troubleshooting Scenarios

## Scenario 1: Free Plan Cannot Access the API

### Problem

A customer on the Free plan attempts to retrieve a ticket through the API.

### Example Request

```http
GET /v1/tickets/FD-10025 HTTP/1.1
Host: api.flowdesk.example
Authorization: Bearer <API_TOKEN>
Accept: application/json
```

### Example Response

```http
HTTP/1.1 403 Forbidden
Content-Type: application/json
```

```json
{
    "error": {
        "code": "api_access_unavailable",
        "message": "API access is not available for the current subscription plan."
    }
}
```

### Likely Cause

The Free plan does not include API access.

### Recommended Fix

Upgrade the FlowDesk subscription to Pro or Enterprise before using the API.

---

## Scenario 2: Missing Authorization Header

### Problem

An application sends a request without credentials.

### Example Request

```http
GET /v1/tickets/FD-10025 HTTP/1.1
Host: api.flowdesk.example
Accept: application/json
```

### Example Response

```http
HTTP/1.1 401 Unauthorized
Content-Type: application/json
```

```json
{
    "error": {
        "code": "authentication_required",
        "message": "Authorization header is required."
    }
}
```

### Likely Cause

The request does not include the required Bearer Token.

### Recommended Fix

Add:

```http
Authorization: Bearer <API_TOKEN>
```

and retry the request.

---

## Scenario 3: Invalid Ticket Priority

### Problem

An application attempts to create a ticket with an unsupported priority.

### Example Request

```http
POST /v1/tickets HTTP/1.1
Host: api.flowdesk.example
Authorization: Bearer <API_TOKEN>
Content-Type: application/json
```

```json
{
    "customer_id": "CUS-20015",
    "subject": "Unable to access account",
    "description": "Customer cannot log in.",
    "priority": "critical"
}
```

### Example Response

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
```

```json
{
    "error": {
        "code": "validation_failed",
        "message": "Invalid ticket priority.",
        "fields": {
            "priority": "Priority must be low, medium, high, or urgent."
        }
    }
}
```

### Likely Cause

`critical` is not a supported FlowDesk ticket priority.

### Recommended Fix

Use one of:

```text
low
medium
high
urgent
```

---

## Scenario 4: Incorrect Ticket ID

### Problem

An application requests a ticket that does not exist.

### Example Request

```http
GET /v1/tickets/FD-99999 HTTP/1.1
Host: api.flowdesk.example
Authorization: Bearer <API_TOKEN>
Accept: application/json
```

### Example Response

```http
HTTP/1.1 404 Not Found
Content-Type: application/json
```

```json
{
    "error": {
        "code": "resource_not_found",
        "message": "The requested ticket was not found."
    }
}
```

### Likely Cause

The ticket ID is incorrect or the requested ticket is no longer available.

### Recommended Fix

Verify the ticket ID and confirm that the ticket exists before retrying.

---

## Scenario 5: Pro Account Exceeds Rate Limit

### Problem

A Pro application sends more than 60 API requests within one minute.

### Example Request

```http
GET /v1/tickets/FD-10025 HTTP/1.1
Host: api.flowdesk.example
Authorization: Bearer <API_TOKEN>
Accept: application/json
```

### Example Response

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
```

```json
{
    "error": {
        "code": "rate_limit_exceeded",
        "message": "API request rate limit exceeded."
    }
}
```

### Likely Cause

The application exceeded the Pro plan's limit of 60 requests per minute.

### Recommended Fix

Reduce request frequency and implement controlled retries with exponential backoff.

---

## Scenario 6: Invalid JSON Request

### Problem

A ticket creation request contains malformed JSON.

### Example Request

```http
POST /v1/tickets HTTP/1.1
Host: api.flowdesk.example
Authorization: Bearer <API_TOKEN>
Content-Type: application/json
```

```json
{
    "customer_id": "CUS-20015",
    "subject": "Login problem",
    "description": "Customer cannot log in.",
    "priority": "high"
}
```

### Example Response

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json
```

```json
{
    "error": {
        "code": "invalid_json",
        "message": "The request body contains invalid JSON."
    }
}
```

### Likely Cause

The request contains a trailing comma after the `priority` property.

### Recommended Fix

Remove the trailing comma and validate the JSON before sending it.

---

## Scenario 7: Incorrect API Version

### Problem

An application is configured to use an unsupported API version path.

### Example Request

```http
GET /v2/tickets/FD-10025 HTTP/1.1
Host: api.flowdesk.example
Authorization: Bearer <API_TOKEN>
Accept: application/json
```

### Example Response

```http
HTTP/1.1 404 Not Found
Content-Type: application/json
```

```json
{
    "error": {
        "code": "resource_not_found",
        "message": "The requested API resource was not found."
    }
}
```

### Likely Cause

The application is using `/v2` instead of the documented `/v1` API path.

### Recommended Fix

Configure the application to use:

```text
https://api.flowdesk.example/v1
```

---

## Scenario 8: Temporary Server Error

### Problem

A valid API request returns an internal server error.

### Example Request

```http
GET /v1/tickets/FD-10025 HTTP/1.1
Host: api.flowdesk.example
Authorization: Bearer <API_TOKEN>
Accept: application/json
```

### Example Response

```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json
```

```json
{
    "error": {
        "code": "internal_server_error",
        "message": "An unexpected server error occurred."
    }
}
```

### Likely Cause

A temporary server-side problem prevented the request from completing.

### Recommended Fix

1. Verify the request is correctly formed.
2. Check application logs.
3. Wait briefly.
4. Retry using controlled retry logic.
5. Contact FlowDesk support if the error persists.

---

# 10. API Troubleshooting Checklist

Use the following checklist before escalating an API error.

- [ ] **Subscription plan:** Is the account Free, Pro, or Enterprise?
- [ ] **API access:** Does the subscription include API access?
- [ ] **API base URL:** Is the request using `https://api.flowdesk.example/v1`?
- [ ] **API version:** Is `/v1` included in the request path?
- [ ] **Authorization header:** Is the header present?
- [ ] **API token:** Is the token valid and current?
- [ ] **HTTP method:** Is the correct method being used?
- [ ] **Request body:** Does the body contain the required fields?
- [ ] **Request parameters:** Are parameters correctly formatted and valid?
- [ ] **JSON:** Is the request body valid JSON?
- [ ] **Rate limits:** Is the application within the applicable request limit?
- [ ] **HTTP response code:** What status code did FlowDesk return?
- [ ] **Response body:** Does the error response identify a specific field or cause?
- [ ] **Application logs:** Do local logs provide additional context?
- [ ] **Retry behavior:** If the error is temporary, is retry logic controlled?

---

# 11. Troubleshooting Decision Table

| Error                       | Likely Cause                           | Recommended Action                                               |
| --------------------------- | -------------------------------------- | ---------------------------------------------------------------- |
| `401 Unauthorized`          | Missing Authorization header           | Add `Authorization: Bearer <API_TOKEN>`.                         |
| `401 Unauthorized`          | Invalid API token                      | Verify the token and replace it if necessary.                    |
| `401 Unauthorized`          | Expired or revoked token               | Obtain a valid token and update the application configuration.   |
| `403 Forbidden`             | API access unavailable on Free plan    | Upgrade to Pro or Enterprise.                                    |
| `403 Forbidden`             | Insufficient permissions               | Verify account and user permissions.                             |
| `400 Bad Request`           | Malformed request                      | Review request syntax, parameters, and body.                     |
| `400 Bad Request`           | Invalid JSON                           | Validate and correct the JSON request body.                      |
| `422 Unprocessable Entity`  | Invalid field value                    | Check allowed values for the affected field.                     |
| `422 Unprocessable Entity`  | Incorrect data type                    | Send the field using the expected data type.                     |
| `404 Not Found`             | Incorrect resource ID                  | Verify that the resource ID is correct.                          |
| `404 Not Found`             | Incorrect endpoint or API version      | Verify the `/v1` base path and endpoint.                         |
| `405 Method Not Allowed`    | Incorrect HTTP method                  | Use the method supported by the requested operation.             |
| `409 Conflict`              | Resource state conflict                | Retrieve the current resource state and adjust the request.      |
| `429 Too Many Requests`     | Pro or Enterprise rate limit exceeded  | Reduce request frequency and use exponential backoff.            |
| `500 Internal Server Error` | Temporary server-side error            | Retry after a short delay and contact support if persistent.     |
| `502 Bad Gateway`           | Temporary gateway/intermediary problem | Retry after a short delay and investigate if persistent.         |
| `503 Service Unavailable`   | Temporary service unavailability       | Retry with controlled backoff and contact support if persistent. |

---

# 12. Frequently Asked Questions

## 12.1 Why am I receiving `401 Unauthorized`?

A `401 Unauthorized` response usually indicates an authentication problem. Check that the request contains:

```http
Authorization: Bearer <API_TOKEN>
```

Also verify that the token is valid and has not expired or been revoked.

---

## 12.2 Does the Free plan support the FlowDesk API?

No. API access is available only on Pro and Enterprise plans.

The Free plan does not have an API rate limit because API access itself is unavailable.

---

## 12.3 What is the FlowDesk API base URL?

The FlowDesk API base URL is:

```text
https://api.flowdesk.example/v1
```

Requests should use the `/v1` API version.

---

## 12.4 What causes a `403 Forbidden` response?

A `403` indicates that authentication succeeded but the requested operation is not permitted.

Check the subscription plan, API availability, and relevant permissions.

For Free customers, API access is unavailable.

---

## 12.5 What should I do when I receive `429 Too Many Requests`?

A `429` generally means the application exceeded its applicable API request limit.

Pro customers are limited to **60 requests per minute**, while Enterprise customers are limited to **300 requests per minute**.

Reduce request frequency and implement exponential backoff before retrying.

---

## 12.6 Does a `404` always mean that the ticket was deleted?

No. A `404 Not Found` can have several causes.

Check:

- The endpoint path.
- The `/v1` API version.
- The resource ID.
- Whether the requested resource exists.

---

## 12.7 Why am I receiving `422 Unprocessable Entity`?

A `422` generally means the request is structurally valid but contains data that cannot be accepted.

Check field values and data types. For example, FlowDesk ticket priorities must be:

```text
low
medium
high
urgent
```

Ticket statuses must be:

```text
open
pending
resolved
closed
```

---

## 12.8 Should I retry every API error?

No.

Authentication, authorization, validation, and resource errors generally require correcting the request rather than repeatedly retrying it.

Controlled retries are more appropriate for temporary conditions such as `500`, `502`, `503`, and, with appropriate backoff, `429`.

---

## 12.9 How should I troubleshoot repeated `500`, `502`, or `503` responses?

First verify that the request is correctly constructed. Then:

1. Check application logs.
2. Retry after a short period.
3. Use controlled retry logic with exponential backoff.
4. Determine whether the problem is temporary.
5. Contact FlowDesk support if the error persists.

Do not include API tokens when sharing logs or request details with support.

---

## 12.10 What information should I provide when contacting FlowDesk support?

Provide enough information to reproduce and diagnose the problem without exposing credentials.

Recommended information includes:

- HTTP status code.
- Approximate request time.
- API endpoint.
- HTTP method.
- Sanitized request parameters.
- Sanitized request body.
- Response body.
- Relevant application logs.

Never provide the API token itself.
