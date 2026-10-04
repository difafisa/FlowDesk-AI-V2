# FlowDesk Webhooks

## 1. Overview

FlowDesk webhooks allow external applications to receive real-time notifications when specific events occur in FlowDesk.

Instead of repeatedly requesting FlowDesk for changes, an external system can provide a webhook endpoint. FlowDesk sends an HTTP request to that endpoint when a supported event occurs.

FlowDesk currently supports the following webhook events:

- `ticket.created`
- `ticket.updated`
- `ticket.resolved`
- `customer.created`

Webhook functionality is available on **Pro** and **Enterprise** plans.

> **Note:** Webhooks are different from the FlowDesk API. The API allows an external application to request information from FlowDesk, while webhooks allow FlowDesk to notify an external application when supported events occur.

---

## 2. What Are Webhooks?

A webhook is an HTTP callback that FlowDesk sends to an external URL when a configured event occurs.

The general flow is:

1. An event occurs in FlowDesk.
2. FlowDesk identifies webhook subscriptions configured for that event.
3. FlowDesk sends an HTTPS `POST` request to the configured endpoint.
4. The receiving application processes the request.
5. The receiving application returns an HTTP response.
6. FlowDesk considers the delivery successful when the endpoint responds successfully.

For example:

```text
Customer created
       ↓
FlowDesk detects customer.created
       ↓
FlowDesk sends HTTPS POST
       ↓
https://example.com/flowdesk/webhook
       ↓
External application processes payload
       ↓
HTTP success response
```

---

## 3. Webhook Availability by Plan

Webhook functionality depends on the FlowDesk subscription plan.

| Plan       | Webhooks | API Access |
| ---------- | -------- | ---------- |
| Free       | No       | No         |
| Pro        | Yes      | Yes        |
| Enterprise | Yes      | Yes        |

Free customers cannot configure or receive FlowDesk webhooks.

Pro and Enterprise customers can use the supported webhook events.

> **Important:** Upgrading from Free to Pro or Enterprise enables webhook functionality. The Free plan does not provide webhook access.

---

## 4. Supported Webhook Events

FlowDesk supports four webhook events.

| Event              | Description                                       |
| ------------------ | ------------------------------------------------- |
| `ticket.created`   | Triggered when a new ticket is created.           |
| `ticket.updated`   | Triggered when a ticket is updated.               |
| `ticket.resolved`  | Triggered when a ticket is resolved.              |
| `customer.created` | Triggered when a new customer profile is created. |

No other webhook events are included in the standard FlowDesk webhook event set.

---

## 5. `ticket.created`

### Event Name

```text
ticket.created
```

### Description

The `ticket.created` event is triggered when a new ticket is created in FlowDesk.

### Trigger Condition

The event occurs after a new ticket is created.

### HTTP Method

FlowDesk sends the notification using:

```http
POST
```

The request is sent over HTTPS.

### Request Headers

Webhook requests use HTTP headers appropriate for a JSON webhook request.

Example:

```http
Content-Type: application/json
```

### Example Payload

```json
{
    "event": "ticket.created",
    "data": {
        "ticket_id": "tkt_20481",
        "customer_id": "cus_10042",
        "subject": "Unable to access dashboard",
        "description": "The customer cannot access the dashboard.",
        "status": "open",
        "priority": "high",
        "assigned_agent": "agent_17",
        "created_at": "2026-09-09T08:30:00Z",
        "updated_at": "2026-09-09T08:30:00Z"
    }
}
```

The ticket data follows the FlowDesk ticket structure.

### Expected Response

The receiving endpoint should return a successful HTTP response after successfully processing the webhook.

Example:

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
    "status": "received"
}
```

### Delivery Behavior

FlowDesk sends the webhook to the configured endpoint when the ticket is created.

If delivery fails, FlowDesk retries the delivery according to the standard webhook retry policy described in [Failed Delivery and Retry Policy](#15-failed-delivery-and-retry-policy).

---

## 6. `ticket.updated`

### Event Name

```text
ticket.updated
```

### Description

The `ticket.updated` event is triggered when an existing ticket is updated.

### Trigger Condition

The event occurs when information associated with an existing ticket changes.

### HTTP Method

```http
POST
```

Requests are sent using HTTPS.

### Request Headers

```http
Content-Type: application/json
```

### Example Payload

```json
{
    "event": "ticket.updated",
    "data": {
        "ticket_id": "tkt_20481",
        "customer_id": "cus_10042",
        "subject": "Unable to access dashboard",
        "description": "The customer cannot access the dashboard.",
        "status": "pending",
        "priority": "high",
        "assigned_agent": "agent_17",
        "created_at": "2026-09-09T08:30:00Z",
        "updated_at": "2026-09-09T09:15:00Z"
    }
}
```

### Expected Response

A successful webhook receiver can respond with:

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
    "status": "received"
}
```

### Delivery Behavior

FlowDesk sends the notification after the ticket update occurs.

Failed deliveries are retried according to the standard retry policy.

---

## 7. `ticket.resolved`

### Event Name

```text
ticket.resolved
```

### Description

The `ticket.resolved` event is triggered when a ticket reaches the `resolved` status.

### Trigger Condition

The event occurs when the ticket status changes to:

```text
resolved
```

### HTTP Method

```http
POST
```

The request is sent over HTTPS.

### Request Headers

```http
Content-Type: application/json
```

### Example Payload

```json
{
    "event": "ticket.resolved",
    "data": {
        "ticket_id": "tkt_20481",
        "customer_id": "cus_10042",
        "subject": "Unable to access dashboard",
        "description": "The customer cannot access the dashboard.",
        "status": "resolved",
        "priority": "high",
        "assigned_agent": "agent_17",
        "created_at": "2026-09-09T08:30:00Z",
        "updated_at": "2026-09-09T10:00:00Z"
    }
}
```

### Expected Response

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
    "status": "received"
}
```

### Delivery Behavior

FlowDesk sends the webhook after the ticket is resolved.

If the receiving endpoint does not successfully process the request, FlowDesk retries the delivery according to the standard retry policy.

---

## 8. `customer.created`

### Event Name

```text
customer.created
```

### Description

The `customer.created` event is triggered when a new customer profile is created.

### Trigger Condition

The event occurs after a new FlowDesk customer profile is created.

### HTTP Method

```http
POST
```

The request is sent using HTTPS.

### Request Headers

```http
Content-Type: application/json
```

### Example Payload

```json
{
    "event": "customer.created",
    "data": {
        "customer_id": "cus_10042",
        "name": "Sarah Johnson",
        "email": "sarah@example.com",
        "company": "Acme Solutions",
        "tags": ["enterprise", "priority"],
        "custom_fields": {
            "customer_tier": "Gold",
            "onboarding_status": "Complete"
        }
    }
}
```

### Expected Response

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
    "status": "received"
}
```

### Delivery Behavior

FlowDesk sends the webhook after the customer profile is created.

Failed deliveries are retried according to the standard retry policy.

---

## 9. Webhook Configuration

Webhook configuration allows a Pro or Enterprise workspace to specify where FlowDesk should send event notifications.

A typical configuration contains:

- Webhook endpoint URL
- One or more supported events
- Active/inactive configuration state

### Configuration Procedure

1. Open the FlowDesk workspace settings.
2. Navigate to **Developer Settings** or the webhook configuration area.
3. Select **Webhooks**.
4. Select **Create webhook**.
5. Enter the HTTPS endpoint URL.
6. Select the supported events to receive.
7. Save the webhook configuration.
8. Test the endpoint before relying on it for production processing.

Example endpoint:

```text
https://example.com/flowdesk/webhook
```

> **Important:** Webhook endpoints must use HTTPS. Do not configure production webhook delivery using an unencrypted HTTP endpoint.

---

## 10. Webhook Endpoint Requirements

A webhook endpoint is the external URL that receives FlowDesk notifications.

The endpoint should:

- Be accessible from the internet.
- Support HTTPS.
- Accept HTTP `POST` requests.
- Accept JSON request bodies.
- Return an appropriate HTTP response after processing the request.
- Process webhook requests reliably.
- Respond promptly enough to avoid unnecessary delivery failures.

Example:

```text
https://example.com/flowdesk/webhook
```

A webhook endpoint should not require interactive user authentication such as a browser login.

---

## 11. HTTP Method

All FlowDesk webhook notifications are sent using:

```http
POST
```

For example:

```http
POST /flowdesk/webhook HTTP/1.1
Host: example.com
Content-Type: application/json
```

FlowDesk does not use `GET` requests for webhook event delivery.

---

## 12. Request Headers

Webhook requests contain HTTP headers that identify the request format.

The request body is JSON, so webhook receivers should support:

```http
Content-Type: application/json
```

Example:

```http
POST /flowdesk/webhook HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "event": "ticket.created",
  "data": {
    "ticket_id": "tkt_20481"
  }
}
```

> **Note:** The webhook payload should be parsed as JSON rather than treated as plain text.

---

## 13. Webhook Payloads

Webhook payloads contain information about the event that occurred.

A typical payload contains:

- `event`
- `data`

Example:

```json
{
    "event": "customer.created",
    "data": {
        "customer_id": "cus_10042",
        "name": "Sarah Johnson",
        "email": "sarah@example.com",
        "company": "Acme Solutions"
    }
}
```

The structure of `data` depends on the event.

### Ticket Events

Ticket-related events can contain:

- `ticket_id`
- `customer_id`
- `subject`
- `description`
- `status`
- `priority`
- `assigned_agent`
- `created_at`
- `updated_at`

### Customer Events

Customer-related events can contain:

- `customer_id`
- `name`
- `email`
- `company`
- `tags`
- `custom_fields`

> **Note:** The `customer_id` in a ticket payload identifies the customer associated with that ticket.

---

## 14. Delivery Behavior

When a supported event occurs, FlowDesk sends an HTTPS `POST` request to the configured webhook endpoint.

The basic delivery lifecycle is:

```text
Event occurs
    ↓
Webhook event identified
    ↓
HTTPS POST sent
    ↓
Endpoint processes payload
    ↓
Successful HTTP response
    ↓
Delivery completed
```

The receiving application should process the request and return a successful response after accepting the event.

Webhook consumers should also design their processing logic to tolerate duplicate deliveries because a failed response can cause FlowDesk to retry the same event.

> **Best practice:** Make webhook processing idempotent where possible so that processing the same notification more than once does not unintentionally duplicate an operation.

---

## 15. Failed Delivery and Retry Policy

FlowDesk retries failed webhook deliveries **up to 3 times**.

A delivery can be considered unsuccessful when the receiving endpoint fails to properly accept or process the webhook request.

The retry process can be represented as:

```text
Initial delivery
      ↓
   Failed
      ↓
   Retry 1
      ↓
   Failed
      ↓
   Retry 2
      ↓
   Failed
      ↓
   Retry 3
```

After the maximum of three retries, FlowDesk stops retrying that webhook delivery.

> **Important:** The retry policy applies to failed webhook deliveries. Your webhook receiver should therefore be prepared to receive the same event more than once.

---

## 16. Webhook Security

FlowDesk sends webhook requests using HTTPS.

HTTPS protects data during transmission between FlowDesk and the configured webhook endpoint.

When implementing a webhook receiver:

- Use an HTTPS endpoint.
- Protect the webhook endpoint from unauthorized access.
- Validate incoming request data.
- Process only supported FlowDesk events.
- Avoid exposing customer information unnecessarily.
- Store webhook logs securely.
- Do not place sensitive credentials in webhook payloads.

FlowDesk's security capabilities include:

- HTTPS
- Encrypted data transmission
- Role-based access control
- Audit logs

> **Security note:** HTTPS protects data in transit but does not by itself guarantee that an incoming request is from the expected sender. Webhook receivers should implement appropriate request validation controls for their environment.

---

## 17. Webhook Testing

Before using a webhook endpoint in production, verify that it can receive and process FlowDesk webhook requests.

### Recommended Testing Procedure

1. Configure an HTTPS endpoint.
2. Create a webhook configuration in FlowDesk.
3. Select the event you want to test.
4. Trigger the corresponding event in FlowDesk.
5. Inspect the request received by your application.
6. Verify the HTTP method is `POST`.
7. Verify the request contains JSON.
8. Verify the `event` value.
9. Verify the payload data.
10. Return a successful HTTP response.
11. Confirm that the delivery completes successfully.

Example test endpoint:

```text
https://example.com/flowdesk/webhook
```

A test receiver should log the received event without exposing sensitive information in publicly accessible logs.

---

## 18. Webhook Troubleshooting

### Webhook Is Not Available

**Cause:** The workspace is using the Free plan.

**Solution:** Webhooks are available only on Pro and Enterprise plans.

---

### Endpoint Does Not Receive Requests

Check:

1. The webhook is configured for the correct event.
2. The endpoint URL is correct.
3. The endpoint uses HTTPS.
4. The endpoint is publicly reachable.
5. The endpoint accepts `POST` requests.
6. The receiving application is running.
7. The receiving application can parse JSON requests.

---

### Webhook Delivery Keeps Failing

Check the endpoint's HTTP response and application logs.

Common causes include:

- Endpoint unavailable.
- Incorrect URL.
- HTTPS configuration problems.
- Server errors.
- Request body parsing errors.
- Endpoint rejecting `POST` requests.

Because FlowDesk retries failed deliveries up to three times, temporary failures can result in multiple requests for the same event.

---

### Payload Cannot Be Parsed

Ensure the endpoint handles:

```http
Content-Type: application/json
```

and parses the request body as JSON.

For example:

```json
{
    "event": "ticket.created",
    "data": {
        "ticket_id": "tkt_20481"
    }
}
```

---

### Receiving Duplicate Events

**Cause:** FlowDesk may retry a delivery when the previous delivery was unsuccessful.

**Solution:** Design the receiving system to handle duplicate event delivery safely.

Where possible, use the event's relevant resource identifier, such as `ticket_id` or `customer_id`, together with your application's own processing records to prevent unintended duplicate operations.

---

## 19. Example Webhook Requests

### Ticket Created

```http
POST /flowdesk/webhook HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "event": "ticket.created",
  "data": {
    "ticket_id": "tkt_20481",
    "customer_id": "cus_10042",
    "subject": "Unable to access dashboard",
    "description": "The customer cannot access the dashboard.",
    "status": "open",
    "priority": "high",
    "assigned_agent": "agent_17",
    "created_at": "2026-09-09T08:30:00Z",
    "updated_at": "2026-09-09T08:30:00Z"
  }
}
```

### Ticket Resolved

```http
POST /flowdesk/webhook HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "event": "ticket.resolved",
  "data": {
    "ticket_id": "tkt_20481",
    "customer_id": "cus_10042",
    "subject": "Unable to access dashboard",
    "description": "The customer cannot access the dashboard.",
    "status": "resolved",
    "priority": "high",
    "assigned_agent": "agent_17",
    "created_at": "2026-09-09T08:30:00Z",
    "updated_at": "2026-09-09T10:00:00Z"
  }
}
```

### Customer Created

```http
POST /flowdesk/webhook HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "event": "customer.created",
  "data": {
    "customer_id": "cus_10042",
    "name": "Sarah Johnson",
    "email": "sarah@example.com",
    "company": "Acme Solutions",
    "tags": [
      "enterprise",
      "priority"
    ],
    "custom_fields": {
      "customer_tier": "Gold"
    }
  }
}
```

---

## 20. Example Webhook Responses

After successfully receiving and processing a webhook, the receiving application can return a successful HTTP response.

Example:

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
    "status": "received"
}
```

Another valid successful response can contain a simple status message:

```http
HTTP/1.1 200 OK
Content-Type: application/json
```

```json
{
    "status": "success"
}
```

The receiving system should return a successful response only after it has accepted the webhook for processing.

> **Best practice:** If processing is asynchronous, the receiving application can accept the event and queue it for later processing, then return a successful response after the event has been safely accepted.

---

## 21. Common Webhook Errors

| Problem                         | Likely Cause                             | Recommended Action                               |
| ------------------------------- | ---------------------------------------- | ------------------------------------------------ |
| Webhooks unavailable            | Workspace is on Free plan                | Upgrade to Pro or Enterprise                     |
| `POST` rejected                 | Endpoint does not support POST           | Configure the endpoint to accept POST            |
| HTTPS connection failure        | Invalid or unavailable HTTPS endpoint    | Verify the endpoint's HTTPS configuration        |
| Payload parsing failure         | JSON body not handled correctly          | Parse the request as JSON                        |
| Repeated webhook requests       | Previous delivery failed                 | Make webhook processing idempotent               |
| Delivery stops after retries    | Maximum retry count reached              | Fix the endpoint and verify future deliveries    |
| Wrong event received            | Incorrect webhook event configuration    | Review the configured event subscriptions        |
| Endpoint unavailable            | Receiving application or network failure | Verify that the endpoint is reachable            |
| Unauthorized access to endpoint | Insufficient endpoint protection         | Implement appropriate endpoint security controls |

### Webhook Quick Reference

| Property                | FlowDesk Behavior                                                         |
| ----------------------- | ------------------------------------------------------------------------- |
| Available plans         | Pro, Enterprise                                                           |
| Free plan               | Webhooks unavailable                                                      |
| HTTP method             | HTTPS `POST`                                                              |
| Payload format          | JSON                                                                      |
| Supported events        | `ticket.created`, `ticket.updated`, `ticket.resolved`, `customer.created` |
| Failed delivery retries | Up to 3 times                                                             |
| Transport security      | HTTPS / encrypted data transmission                                       |
| API relationship        | Webhooks notify external systems; API provides programmatic access        |
