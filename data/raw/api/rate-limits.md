# FlowDesk API Rate Limits

## 1. Overview

FlowDesk API rate limits control the number of API requests a customer can make within a one-minute period.

Rate limits help maintain API availability and provide consistent performance for FlowDesk customers.

API access and rate limits depend on the customer's subscription plan:

| Plan       | API Access |              Rate Limit |
| ---------- | ---------- | ----------------------: |
| Free       | No         |         API unavailable |
| Pro        | Yes        |  60 requests per minute |
| Enterprise | Yes        | 300 requests per minute |

> **Important:** These limits are fixed according to the FlowDesk subscription plan. The Free plan does not provide API access.

---

## 2. What Are API Rate Limits?

An API rate limit defines how many requests an application can send to FlowDesk during a specified period.

FlowDesk measures API usage in **requests per minute**.

For example, a Pro customer can make up to:

```text
60 requests per minute
```

An application that sends requests faster than the applicable limit may receive a rate-limit error.

Rate limiting applies to requests made through the FlowDesk API. It does not change the functionality of the FlowDesk web application.

---

## 3. Rate Limits by Subscription Plan

The FlowDesk API rate limits are:

| Subscription Plan | API Access | Requests Per Minute |
| ----------------- | ---------- | ------------------: |
| Free              | No         |     API unavailable |
| Pro               | Yes        |                  60 |
| Enterprise        | Yes        |                 300 |

These values are defined by the FlowDesk product specification and should be used when designing API integrations.

---

## 4. Free Plan

The Free plan does **not** include API access.

| Property                        | Free                         |
| ------------------------------- | ---------------------------- |
| API access                      | No                           |
| Requests per minute             | API unavailable              |
| Bearer Token API authentication | Not available for API access |

Applications should not attempt to use the FlowDesk API with a Free subscription.

> **Note:** The absence of an API rate limit for Free does not mean that Free customers have unlimited API requests. API access itself is unavailable.

---

## 5. Pro Plan

The Pro plan includes API access with a limit of:

```text
60 requests per minute
```

A Pro integration can therefore make up to 60 API requests within the applicable one-minute rate-limit period.

Example usage:

```text
Request 1
Request 2
...
Request 60
```

If the client continues making requests after reaching the applicable limit, FlowDesk can reject additional requests until the rate-limit window permits more requests.

---

## 6. Enterprise Plan

The Enterprise plan includes API access with a limit of:

```text
300 requests per minute
```

Enterprise integrations therefore have a significantly higher request allowance than Pro integrations.

Example:

```text
Requests 1–300 → within the Enterprise limit
Request 301+   → may be rate limited
```

Enterprise customers should still implement rate-limit handling rather than assuming that requests can always be sent without restriction.

---

## 7. Requests Per Minute

FlowDesk expresses API limits as **requests per minute**.

The applicable limits are:

```text
Pro        → 60 requests/minute
Enterprise → 300 requests/minute
```

For example, a Pro application that sends 60 requests during a minute has reached its configured request allowance for that period.

A client should avoid deliberately sending requests at the maximum rate continuously when it can reduce unnecessary API calls.

> **Best practice:** Treat the published limit as a ceiling rather than a target. Cache data, batch application work where supported, and avoid unnecessary polling.

---

## 8. Rate Limit Enforcement

FlowDesk enforces rate limits based on the customer's subscription plan.

When a client remains within the applicable limit, API requests are processed normally.

When the client exceeds the applicable rate limit, FlowDesk rejects additional requests with a rate-limit response.

A typical flow is:

```text
API request
    ↓
Check subscription and authentication
    ↓
Check current API usage
    ↓
Within limit?
   /       \
 Yes       No
  ↓         ↓
Process    429
request    response
```

### Example

A Pro customer has a limit of 60 requests per minute.

If an application sends more requests than permitted during the applicable rate-limit window, FlowDesk may return:

```http
HTTP/1.1 429 Too Many Requests
```

The client should temporarily stop sending requests and retry according to its backoff strategy.

---

## 9. Rate Limit Headers

FlowDesk provides rate-limit information through HTTP response headers.

A typical successful response can include:

```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 42
X-RateLimit-Reset: 1725872460
```

The headers indicate:

| Header                  | Meaning                                                             |
| ----------------------- | ------------------------------------------------------------------- |
| `X-RateLimit-Limit`     | Maximum requests allowed during the applicable rate-limit window    |
| `X-RateLimit-Remaining` | Approximate number of requests remaining in the current window      |
| `X-RateLimit-Reset`     | Unix timestamp indicating when the current rate-limit window resets |

For an Enterprise account, the limit header would reflect the Enterprise limit:

```http
X-RateLimit-Limit: 300
```

> **Note:** Clients should use the response headers when available rather than assuming that every request consumes the same amount of time.

---

## 10. Rate Limit Errors

When an API client exceeds its applicable request limit, FlowDesk returns the HTTP status:

```http
429 Too Many Requests
```

A rate-limit error indicates that the client should reduce its request frequency and retry later.

Example:

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 15
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
```

The `Retry-After` header indicates how long the client should wait before attempting the request again.

### Common HTTP Status Codes

| HTTP Status                 | Meaning                               | Rate-Limit Relevance                     |
| --------------------------- | ------------------------------------- | ---------------------------------------- |
| `200 OK`                    | Request succeeded                     | Request was accepted                     |
| `401 Unauthorized`          | Authentication failed                 | Not a rate-limit error                   |
| `403 Forbidden`             | Authenticated client lacks permission | Not a rate-limit error                   |
| `429 Too Many Requests`     | Rate limit exceeded                   | Client should slow down and retry        |
| `500 Internal Server Error` | Server-side failure                   | Not necessarily related to rate limiting |

> **Important:** A `429` response should not be treated as an authentication or authorization failure. It indicates that the client has exceeded its API request allowance.

---

## 11. Handling Rate Limit Errors

Applications should explicitly detect HTTP `429` responses.

### Recommended Procedure

1. Send the API request.
2. Check the HTTP status code.
3. If the response is successful, continue processing.
4. If the response is `429`, stop sending requests temporarily.
5. Read the `Retry-After` header when available.
6. Wait for the specified period.
7. Retry the request.
8. If rate limiting continues, increase the backoff interval.

Example:

```python
import time
import requests

url = "https://api.flowdesk.example/v1/tickets"

headers = {
    "Authorization": "Bearer <API_TOKEN>"
}

response = requests.get(url, headers=headers)

if response.status_code == 429:
    retry_after = int(response.headers.get("Retry-After", "15"))
    time.sleep(retry_after)
    response = requests.get(url, headers=headers)

response.raise_for_status()
```

> **Best practice:** Do not immediately retry a `429` response in a tight loop. Doing so can generate additional unnecessary requests and prolong rate limiting.

---

## 12. Retry and Backoff Strategies

A good API client should use a backoff strategy when it receives a rate-limit response.

### Fixed Backoff

A simple strategy is to wait for a fixed period before retrying.

```text
Request → 429
Wait 15 seconds
Retry
```

### Exponential Backoff

For repeated rate-limit responses, exponential backoff can progressively increase the waiting period.

Example:

```text
First failure  → wait 2 seconds
Second failure → wait 4 seconds
Third failure  → wait 8 seconds
Fourth failure → wait 16 seconds
```

A client can also add a small random delay, commonly called jitter, to prevent many clients from retrying simultaneously.

### Recommended Strategy

When a `429` response includes `Retry-After`:

1. Read the `Retry-After` value.
2. Wait for the specified duration.
3. Retry the request.
4. If another `429` occurs, use an increasing backoff interval.

When `Retry-After` is unavailable, use an exponential backoff strategy with a reasonable maximum retry interval.

---

## 13. Best Practices

### Monitor API Usage

Track request volume within your application so that the integration does not unexpectedly exceed its plan limit.

For example:

```text
Pro limit:
60 requests/minute
```

An application should monitor its request rate instead of waiting until it receives `429` responses.

### Avoid Unnecessary Requests

Do not repeatedly request the same data when the application already has the required information.

Consider:

- Caching frequently accessed data.
- Avoiding unnecessary polling.
- Reusing previously retrieved information.
- Scheduling synchronization jobs efficiently.

### Implement Backoff

Always handle `429 Too Many Requests` responses gracefully.

### Respect `Retry-After`

When FlowDesk provides a `Retry-After` header, use it to determine when to retry.

### Spread Requests

Avoid sending a large number of requests in a short burst when the same work can be distributed over time.

For example, instead of:

```text
60 requests immediately
```

a client can distribute requests throughout the minute when its workflow permits.

### Monitor Subscription Changes

The applicable rate limit depends on the customer's plan.

| Plan       |          Rate Limit |
| ---------- | ------------------: |
| Free       |     API unavailable |
| Pro        |  60 requests/minute |
| Enterprise | 300 requests/minute |

Applications should be designed to operate within the limit associated with the customer's current plan.

---

## 14. Example API Requests

FlowDesk API requests use Bearer Token authentication.

### cURL Request

```bash
curl https://api.flowdesk.example/v1/tickets \
  -H "Authorization: Bearer <API_TOKEN>"
```

The request consumes API capacity when made by a Pro or Enterprise customer.

### Request With Rate-Limit Information

```bash
curl -i https://api.flowdesk.example/v1/tickets \
  -H "Authorization: Bearer <API_TOKEN>"
```

A successful response may contain:

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1725872460
```

For Enterprise, the corresponding limit would be:

```http
X-RateLimit-Limit: 300
```

> **Note:** Free customers cannot use these API requests because API access is unavailable on the Free plan.

---

## 15. Example Rate Limit Error Responses

### Pro Plan

When a Pro integration exceeds the 60 requests-per-minute limit:

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 20
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
```

Example JSON body:

```json
{
    "error": {
        "code": "rate_limit_exceeded",
        "message": "API rate limit exceeded. Please retry after the specified interval."
    }
}
```

### Enterprise Plan

An Enterprise customer can receive a similar response after exceeding the Enterprise limit:

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 10
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 0
```

Example response:

```json
{
    "error": {
        "code": "rate_limit_exceeded",
        "message": "API rate limit exceeded. Please retry after the specified interval."
    }
}
```

The client should wait before retrying.

---

## 16. Common Rate Limit Issues

### Too Many Requests in a Short Period

**Problem:** The application sends requests in large bursts.

**Solution:**

- Spread requests over time.
- Monitor request volume.
- Implement backoff.
- Avoid unnecessary API calls.

---

### Repeated `429` Responses

**Problem:** The application continues receiving `429 Too Many Requests`.

**Possible causes:**

- Requests are being retried too quickly.
- The application generates more requests than the subscription allows.
- Multiple application processes share the same API capacity.

**Solution:**

1. Stop immediate retries.
2. Respect `Retry-After`.
3. Implement exponential backoff.
4. Reduce unnecessary requests.
5. Monitor overall API usage.

---

### Incorrectly Treating `429` as an Authentication Error

**Problem:** The application reports an invalid API token when it receives `429`.

**Solution:** Handle rate limiting separately from authentication errors.

```text
401 → Authentication problem
403 → Authorization problem
429 → Rate limit exceeded
```

---

### Assuming Free Has an Unlimited Rate Limit

**Problem:** An application attempts to use the API because the Free plan has no numeric rate-limit value.

**Solution:** The Free plan has **no API access**. It should not be treated as an unlimited API plan.

---

### Hard-Coding the Pro Limit

**Problem:** An integration always assumes a limit of 60 requests per minute.

**Cause:** The integration was designed only for Pro customers.

**Solution:** Account for the customer's subscription plan:

```text
Free        → API unavailable
Pro         → 60 requests/minute
Enterprise  → 300 requests/minute
```

---

## 17. FAQ

### What is the FlowDesk API rate limit for Pro?

The Pro plan allows **60 requests per minute**.

### What is the FlowDesk API rate limit for Enterprise?

The Enterprise plan allows **300 requests per minute**.

### Does the Free plan have an API rate limit?

No numeric API rate limit applies because the **Free plan does not include API access**.

### What happens when I exceed the API rate limit?

FlowDesk can return:

```http
429 Too Many Requests
```

The client should stop sending requests temporarily and retry after the appropriate waiting period.

### Should I retry a `429` response immediately?

No. Immediate retries can cause additional rate-limit failures. Use `Retry-After` when provided and implement backoff.

### Does a `401` response mean I exceeded my rate limit?

No. `401 Unauthorized` indicates an authentication problem. Rate-limit errors use `429 Too Many Requests`.

### Does a `403` response mean I exceeded my rate limit?

No. `403 Forbidden` indicates that the authenticated client does not have permission to perform the requested operation.

### Can I make more than 60 requests per minute on Pro?

The Pro plan's published limit is **60 requests per minute**. Applications should remain within this limit.

### Can Enterprise customers make unlimited API requests?

No. Enterprise has a higher limit of **300 requests per minute**, but API requests remain subject to rate limiting.

### How should I design my integration to avoid rate limits?

Use efficient request patterns, avoid unnecessary polling, monitor API usage, distribute requests where possible, and implement `429` handling with backoff.

### What is the FlowDesk API base URL?

The FlowDesk API base URL is:

```text
https://api.flowdesk.example/v1
```

API requests use Bearer Token authentication:

```http
Authorization: Bearer <API_TOKEN>
```

### Rate Limit Quick Reference

| Plan           | API Access |              Rate Limit |
| -------------- | ---------- | ----------------------: |
| **Free**       | No         |         API unavailable |
| **Pro**        | Yes        |  **60 requests/minute** |
| **Enterprise** | Yes        | **300 requests/minute** |

| Item                       | FlowDesk Behavior                 |
| -------------------------- | --------------------------------- |
| Rate-limit unit            | Requests per minute               |
| Rate-limit error           | `429 Too Many Requests`           |
| Retry guidance             | Use `Retry-After` when available  |
| Recommended retry strategy | Backoff with increasing delays    |
| API authentication         | Bearer Token                      |
| API base URL               | `https://api.flowdesk.example/v1` |
