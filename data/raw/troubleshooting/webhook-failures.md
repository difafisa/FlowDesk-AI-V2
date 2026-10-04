# Webhook Failure Troubleshooting

## 1. Overview

FlowDesk webhooks allow Pro and Enterprise customers to receive event notifications from FlowDesk at an external HTTPS endpoint.

When a supported event occurs, FlowDesk sends an HTTPS `POST` request to the configured webhook endpoint. Supported webhook events are:

- `ticket.created`
- `ticket.updated`
- `ticket.resolved`
- `customer.created`

If a webhook delivery fails, FlowDesk retries the delivery up to 3 times. A failed delivery may result from an incorrect endpoint configuration, an unavailable server, an HTTP error response, an HTTPS problem, or an issue with how the receiving application handles the request.

This guide helps developers and administrators identify the cause of failed webhook deliveries and determine the appropriate corrective action.

> **Note:** Webhooks are available only on Pro and Enterprise plans. Free customers do not have webhook access.

---

## 2. Webhook Requirements

A FlowDesk webhook endpoint must satisfy the following requirements.

| Requirement         | Description                                                                                                    |
| ------------------- | -------------------------------------------------------------------------------------------------------------- |
| HTTPS               | The webhook endpoint must use HTTPS.                                                                           |
| POST handling       | The endpoint must accept incoming HTTP `POST` requests.                                                        |
| Correct URL         | The configured webhook URL must point to the intended endpoint.                                                |
| Server availability | The endpoint's server must be reachable when FlowDesk sends the request.                                       |
| HTTP response       | The endpoint should return an appropriate successful HTTP response when the webhook is processed successfully. |

A typical webhook URL might look like:

```text
https://example.yourcompany.com/webhooks/flowdesk
```

The receiving application should be configured to process the incoming request and return a successful `2xx` response when processing completes successfully.

---

## 3. Common Webhook Failure Scenarios

### 3.1 Endpoint Returns a 4xx Status

**Symptom:** FlowDesk webhook deliveries fail and the endpoint responds with a client-error status such as `400`, `401`, `403`, or `404`.

**Possible causes:**

- The request payload is rejected by the application.
- Authentication or authorization requirements are not satisfied.
- The configured endpoint path is incorrect.
- The receiving application does not permit the request.

**Troubleshooting steps:**

1. Check the endpoint's application logs.
2. Identify the HTTP status returned to FlowDesk.
3. Verify that the webhook URL is correct.
4. Verify that the endpoint accepts `POST` requests.
5. Check any authentication or authorization requirements configured on the receiving application.
6. Correct the endpoint configuration or application behavior.
7. Test the endpoint again.

**Expected result:** The endpoint accepts the webhook request and returns an appropriate `2xx` response.

---

### 3.2 Endpoint Returns a 5xx Status

**Symptom:** FlowDesk sends a webhook request, but the receiving server returns a `5xx` response.

**Possible causes:**

- An application error occurred while processing the request.
- The server is overloaded.
- A dependency used by the application is unavailable.
- A proxy or gateway cannot reach the application.

**Troubleshooting steps:**

1. Check the application logs for errors at the time of the webhook request.
2. Verify that the server is running normally.
3. Check the health of application dependencies.
4. Review recent application or infrastructure changes.
5. Resolve the server-side error.
6. Send a test request to confirm that the endpoint now responds successfully.

**Expected result:** The endpoint processes the request without a server-side error and returns a `2xx` response.

---

### 3.3 Endpoint Timeout

**Symptom:** The webhook delivery does not complete successfully because the receiving endpoint does not respond in an acceptable time.

**Possible causes:**

- The application is processing the request too slowly.
- The server is overloaded.
- A downstream service is unavailable or responding slowly.
- Network connectivity problems exist between the endpoint and its dependencies.

**Troubleshooting steps:**

1. Check server and application logs.
2. Identify whether the request reached the application.
3. Review application processing time.
4. Check dependent services used during webhook processing.
5. Reduce unnecessary processing during the initial webhook request where appropriate.
6. Test the endpoint again.

**Expected result:** The endpoint becomes available and responds successfully within an appropriate period.

---

### 3.4 Invalid Endpoint URL

**Symptom:** FlowDesk cannot successfully deliver webhooks to the configured URL.

**Possible causes:**

- The URL contains a typo.
- The endpoint path has changed.
- The configured URL points to an incorrect environment.
- The endpoint has been removed.

**Troubleshooting steps:**

1. Review the configured webhook URL.
2. Check the hostname and path for errors.
3. Confirm that the endpoint exists.
4. Verify that the endpoint is publicly reachable as required by the receiving environment.
5. Confirm that the endpoint uses HTTPS.
6. Update the webhook configuration if the URL has changed.

**Expected result:** FlowDesk can reach the intended HTTPS endpoint.

---

### 3.5 Endpoint Unavailable

**Symptom:** Webhook deliveries fail because the destination server cannot be reached or is not accepting requests.

**Possible causes:**

- The server is offline.
- The application has stopped.
- Infrastructure maintenance is in progress.
- A network or gateway problem is preventing access.

**Troubleshooting steps:**

1. Check whether the server is running.
2. Check application and infrastructure logs.
3. Verify that the endpoint is reachable.
4. Check any reverse proxy or gateway in front of the application.
5. Restore the endpoint if it is unavailable.
6. Test the webhook endpoint with an HTTPS `POST`.

**Expected result:** The server accepts requests and returns an appropriate successful response.

---

### 3.6 HTTPS Certificate Problems

**Symptom:** FlowDesk cannot successfully establish an HTTPS connection with the configured endpoint.

**Possible causes:**

- The endpoint's TLS certificate is invalid.
- The certificate has expired.
- The certificate does not correctly match the endpoint hostname.
- The HTTPS configuration is incomplete.

**Troubleshooting steps:**

1. Verify that the endpoint uses `https://`.
2. Check the certificate associated with the endpoint.
3. Confirm that the certificate is valid and has not expired.
4. Verify that the certificate corresponds to the endpoint hostname.
5. Correct the HTTPS configuration.
6. Test the endpoint again.

**Expected result:** The endpoint can establish a valid HTTPS connection.

> **Warning:** FlowDesk webhook endpoints must use HTTPS. An HTTP-only endpoint does not satisfy the webhook requirements.

---

### 3.7 Server Rejects POST Requests

**Symptom:** The endpoint is reachable, but webhook requests are rejected because the application does not accept `POST` requests.

**Possible causes:**

- The route is configured for another HTTP method.
- A web server rule rejects `POST`.
- An application framework route is incorrectly configured.

**Troubleshooting steps:**

1. Verify that the configured route accepts `POST`.
2. Check web server or reverse proxy rules.
3. Check application routing configuration.
4. Send a test HTTPS `POST` request.
5. Confirm that the endpoint returns a successful response.

**Expected result:** The endpoint accepts HTTPS `POST` requests from FlowDesk.

---

### 3.8 Endpoint Authentication or Authorization Problems

**Symptom:** The receiving application returns `401` or `403`, or otherwise rejects incoming webhook requests.

**Possible causes:**

- The endpoint requires authentication that the incoming request does not satisfy.
- Authorization rules reject the request.
- Access controls have changed.
- The webhook endpoint was configured incorrectly.

**Troubleshooting steps:**

1. Check the endpoint's authentication configuration.
2. Review application and gateway logs.
3. Identify why the request is being rejected.
4. Verify that the webhook endpoint is configured to accept the intended FlowDesk webhook requests.
5. Correct the endpoint configuration.
6. Test the endpoint again.

**Expected result:** The receiving application accepts the webhook request and returns a successful response.

> **Note:** Do not disable security controls unnecessarily. Adjust the receiving application's configuration according to your organization's security requirements.

---

### 3.9 Incorrect Webhook Configuration

**Symptom:** A supported FlowDesk event is not being delivered to the expected endpoint.

**Possible causes:**

- The webhook endpoint URL is incorrect.
- The wrong event is being investigated.
- The webhook configuration does not correspond to the expected workflow.
- The customer is using a Free plan without webhook access.

**Troubleshooting steps:**

1. Confirm that the FlowDesk account is on a Pro or Enterprise plan.
2. Confirm that the event is one of the supported webhook events.
3. Verify the configured endpoint URL.
4. Verify that the receiving server accepts HTTPS `POST` requests.
5. Check endpoint logs for incoming requests.
6. Correct any configuration errors.
7. Test the endpoint again.

**Expected result:** The supported event is delivered to the intended HTTPS endpoint.

---

## 4. HTTP Status Code Troubleshooting

The HTTP response from the receiving endpoint provides an important indication of whether the webhook was processed successfully.

| HTTP Status                 | Meaning                                                                 | Troubleshooting Guidance                                                                                                          |
| --------------------------- | ----------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `200–299`                   | Successful response                                                     | The endpoint accepted the request successfully. Investigate application-level processing if the expected result is still missing. |
| `400 Bad Request`           | The server considers the request invalid                                | Check the endpoint's request parsing, expected payload structure, and application logs.                                           |
| `401 Unauthorized`          | Authentication is required or not accepted                              | Review the endpoint's authentication requirements and configuration.                                                              |
| `403 Forbidden`             | The server understood the request but refuses access                    | Check authorization rules, access controls, and gateway configuration.                                                            |
| `404 Not Found`             | The requested endpoint cannot be found                                  | Verify the webhook URL, hostname, route, and endpoint path.                                                                       |
| `408 Request Timeout`       | The server timed out waiting for the request                            | Check network connectivity and server availability.                                                                               |
| `429 Too Many Requests`     | The receiving service is rate limiting requests                         | Review the receiving application's rate limits and capacity.                                                                      |
| `500 Internal Server Error` | The receiving application encountered an error                          | Check application logs and resolve the server-side error.                                                                         |
| `502 Bad Gateway`           | A gateway or proxy received an invalid response from an upstream server | Check reverse proxies, gateways, and upstream application availability.                                                           |
| `503 Service Unavailable`   | The server is temporarily unable to handle the request                  | Check server health, application availability, and infrastructure capacity.                                                       |
| `504 Gateway Timeout`       | A gateway did not receive a timely response from an upstream server     | Check gateway configuration and upstream application response times.                                                              |

> **Important:** A `2xx` response indicates a successful HTTP response, but it does not necessarily confirm that your application completed every downstream business operation successfully. Check application logs when webhook processing appears incomplete.

---

## 5. Webhook Retry Behavior

When a FlowDesk webhook delivery fails, FlowDesk retries the delivery **up to 3 times**.

A failed delivery can occur because the endpoint is temporarily unavailable, returns an unsuccessful HTTP response, or encounters another delivery problem.

A retry does not necessarily mean that the webhook endpoint is permanently failing. For example, a temporary server outage may be resolved before a subsequent delivery attempt.

### Troubleshooting Failed Retries

When investigating repeated webhook failures:

1. Check the receiving server's logs.
2. Determine whether FlowDesk requests reached the endpoint.
3. Record the HTTP status returned by the endpoint.
4. Check application and infrastructure errors.
5. Verify the endpoint's availability.
6. Check HTTPS configuration.
7. Verify that the endpoint accepts `POST` requests.
8. Correct the underlying problem.
9. Test the endpoint independently.

Do not assume that repeated delivery attempts indicate a FlowDesk configuration problem. The receiving endpoint's logs are often the best source of information about why a delivery failed.

> **Note:** FlowDesk specifies up to 3 retries for failed webhook deliveries. An exact retry interval is not defined in this documentation and should not be assumed.

---

## 6. Event-Specific Troubleshooting

FlowDesk supports four webhook events. If one specific event is not being received, first verify that the expected event actually occurred and that the event is supported.

### 6.1 `ticket.created`

This event relates to ticket creation.

If the expected webhook is not received:

1. Confirm that a ticket was successfully created.
2. Confirm that `ticket.created` is the event being investigated.
3. Verify the configured webhook endpoint.
4. Check the receiving server logs for the incoming request.
5. Check the HTTP response returned by the endpoint.
6. Review any errors in the receiving application.

**Expected result:** The configured HTTPS endpoint receives the `ticket.created` webhook request.

---

### 6.2 `ticket.updated`

This event relates to ticket updates.

If the event is not received:

1. Confirm that the ticket was actually updated.
2. Verify that the event being investigated is `ticket.updated`.
3. Check the endpoint configuration.
4. Review server logs for incoming requests.
5. Check the HTTP response generated by the endpoint.
6. Investigate any application errors.

**Expected result:** The endpoint receives the webhook associated with the supported ticket update event.

---

### 6.3 `ticket.resolved`

This event relates to ticket resolution.

If the expected webhook is missing:

1. Confirm that the ticket was resolved.
2. Verify that `ticket.resolved` is the event being investigated.
3. Check the configured webhook endpoint.
4. Review endpoint logs.
5. Check the HTTP response.
6. Investigate application or infrastructure errors.

**Expected result:** The configured HTTPS endpoint receives the `ticket.resolved` webhook request.

---

### 6.4 `customer.created`

This event relates to customer creation.

If the expected webhook is missing:

1. Confirm that the customer was created successfully.
2. Verify that `customer.created` is the expected event.
3. Check the webhook endpoint configuration.
4. Review receiving server logs.
5. Check the HTTP response returned by the endpoint.
6. Investigate any server-side errors.

**Expected result:** The endpoint receives the `customer.created` webhook request.

> **Note:** Do not troubleshoot an unsupported event as though it were a delivery failure. The FlowDesk webhook event list currently supports only `ticket.created`, `ticket.updated`, `ticket.resolved`, and `customer.created`.

---

## 7. Endpoint Testing

Testing the endpoint independently can help determine whether the problem is related to the receiving application or its infrastructure.

### Check Server Logs

Start by checking the logs of the application that receives FlowDesk webhooks.

Look for:

- Incoming `POST` requests
- Request timestamps
- HTTP response codes
- Application errors
- Authentication or authorization failures
- Reverse proxy or gateway errors

If no request appears in the logs, investigate endpoint availability, URL configuration, HTTPS configuration, and network access.

### Send a Test HTTPS POST Request

Developers can send a simple test request to verify that their endpoint accepts HTTPS `POST` requests.

For example:

```bash
curl -X POST "https://example.yourcompany.com/webhooks/flowdesk" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "ticket.created",
    "ticket_id": "TCK-1001",
    "customer_id": "CUS-2001"
  }'
```

The payload above is a fictional troubleshooting example and is intended to test basic request handling.

### Verify POST Handling

Confirm that the endpoint:

1. Accepts the `POST` method.
2. Accepts JSON requests when the application expects JSON.
3. Can process the incoming request.
4. Returns an appropriate successful HTTP response.

For example, a successful endpoint may return:

```http
HTTP/1.1 200 OK
```

### Verify HTTPS

The test URL should use HTTPS:

```text
https://example.yourcompany.com/webhooks/flowdesk
```

An HTTP-only URL does not satisfy FlowDesk webhook requirements.

---

## 8. Plan Availability

Webhook access depends on the customer's FlowDesk subscription plan.

| Plan       | Webhook Access |
| ---------- | -------------- |
| Free       | No             |
| Pro        | Yes            |
| Enterprise | Yes            |

### Free Customers

Free customers do not have webhook access.

If a Free customer expects FlowDesk to deliver webhooks, this is a **plan availability issue**, not a webhook delivery failure.

### Pro Customers

Pro customers have access to FlowDesk webhooks and can troubleshoot delivery problems using the procedures in this guide.

### Enterprise Customers

Enterprise customers have access to FlowDesk webhooks and can troubleshoot delivery problems using the same endpoint, HTTPS, HTTP response, and server-log checks described above.

> **Important:** Do not interpret the absence of webhook functionality on the Free plan as a failed webhook delivery.

---

## 9. Troubleshooting Decision Table

| Error / Symptom                                        | Likely Cause                                               | Recommended Action                                                      |
| ------------------------------------------------------ | ---------------------------------------------------------- | ----------------------------------------------------------------------- |
| Endpoint returns `400`                                 | Request rejected as invalid                                | Check application logs and request handling                             |
| Endpoint returns `401`                                 | Authentication requirement is not satisfied                | Review endpoint authentication configuration                            |
| Endpoint returns `403`                                 | Request is forbidden                                       | Check authorization and access-control rules                            |
| Endpoint returns `404`                                 | Incorrect URL or route                                     | Verify the configured webhook URL and endpoint path                     |
| Endpoint returns `500`                                 | Application-side error                                     | Check application logs and resolve the server error                     |
| Endpoint returns `503`                                 | Server temporarily unavailable                             | Check server health and application availability                        |
| Endpoint returns `504`                                 | Upstream service or gateway timeout                        | Check gateway and upstream application response times                   |
| Webhook request never appears in server logs           | Endpoint unavailable, incorrect URL, or connection problem | Verify URL, server availability, HTTPS, and endpoint accessibility      |
| HTTPS connection fails                                 | Certificate or TLS configuration problem                   | Check certificate validity, hostname, and HTTPS configuration           |
| Endpoint rejects `POST`                                | Route or server does not allow POST                        | Configure the webhook route to accept HTTPS POST requests               |
| Webhook keeps failing after retries                    | Underlying endpoint problem remains unresolved             | Inspect endpoint logs and correct the underlying error                  |
| `ticket.created` webhook is missing                    | Event or endpoint configuration problem                    | Confirm ticket creation, event configuration, URL, and server logs      |
| Automation or application expects an unsupported event | Event is not part of the supported webhook set             | Verify that the event is one of FlowDesk's four supported events        |
| Free customer expects webhook delivery                 | Webhooks are unavailable on the Free plan                  | Upgrade to a plan with webhook access or use another supported workflow |

---

## 10. Frequently Asked Questions

### Which FlowDesk plans support webhooks?

Webhooks are available on **Pro** and **Enterprise** plans. Free customers do not have webhook access.

### Which webhook events does FlowDesk support?

FlowDesk supports:

- `ticket.created`
- `ticket.updated`
- `ticket.resolved`
- `customer.created`

No other webhook events should be assumed to be supported.

### What HTTP method does FlowDesk use for webhooks?

FlowDesk sends webhook requests using **HTTPS POST**.

### Does my webhook endpoint have to use HTTPS?

Yes. FlowDesk webhook endpoints must use HTTPS. An HTTP-only endpoint does not meet the webhook requirements.

### How many times does FlowDesk retry a failed webhook?

FlowDesk retries failed webhook deliveries **up to 3 times**.

### Does a retry mean my webhook endpoint is permanently broken?

No. A retry may occur because of a temporary endpoint outage, server error, timeout, or another delivery problem. Check your endpoint logs to identify the underlying cause.

### What does a `500` response mean for a webhook?

A `500` response indicates that the receiving application encountered an internal server error. Check the application logs and resolve the server-side problem.

### What should I check if FlowDesk sends a webhook but my application does not receive it?

First verify the configured endpoint URL, HTTPS configuration, server availability, and POST handling. Then check server, reverse proxy, or gateway logs to determine whether the request reached your infrastructure.

### What should I do if my endpoint returns `429 Too Many Requests`?

A `429` response indicates that the receiving service is applying rate limiting. Review the receiving application's rate limits and capacity, then adjust the endpoint's handling as appropriate.

### How can I test whether my webhook endpoint works?

Send a test HTTPS `POST` request to the endpoint and verify that the application receives it and returns an appropriate successful `2xx` response. Server logs are also useful for confirming that the request reached the application.
