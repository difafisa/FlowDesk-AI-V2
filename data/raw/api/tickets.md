# FlowDesk Ticket API

## 1. Overview

The FlowDesk Ticket API provides programmatic access to ticket
management. It can be used to create, retrieve, update, list, and delete
tickets.

Tickets contain the following fields:

-   `ticket_id`
-   `customer_id`
-   `subject`
-   `description`
-   `status`
-   `priority`
-   `assigned_agent`
-   `created_at`
-   `updated_at`

### Supported ticket statuses

-   `open`
-   `pending`
-   `resolved`
-   `closed`

### Supported ticket priorities

-   `low`
-   `medium`
-   `high`
-   `urgent`

> **Note:** API access is available on Pro and Enterprise plans. Free
> customers do not have API access.

------------------------------------------------------------------------

## 2. Authentication

FlowDesk API requests use Bearer Token authentication.

Include the API token in the `Authorization` request header:

``` text
Authorization: Bearer <API_TOKEN>
```

All API requests should be sent over HTTPS.

### Authentication header

  -----------------------------------------------------------------------
  Header                  Required                Description
  ----------------------- ----------------------- -----------------------
  `Authorization`         Yes                     Bearer token used to
                                                  authenticate the
                                                  request.

  `Content-Type`          Yes for JSON request    Must be
                          bodies                  `application/json` when
                                                  sending JSON.

  `Accept`                Recommended             Set to
                                                  `application/json` when
                                                  a JSON response is
                                                  expected.
  -----------------------------------------------------------------------

> **Warning:** Keep API tokens confidential. Do not expose tokens in
> client-side applications, source control, or public logs.

------------------------------------------------------------------------

## 3. Base URL

The FlowDesk API base URL is:

``` text
https://api.flowdesk.example/v1
```

Ticket endpoints use the `/tickets` resource beneath this base URL.

------------------------------------------------------------------------

## 4. Create Ticket

Creates a new ticket.

### HTTP method

`POST`

### Endpoint

``` text
/tickets
```

### Description

Creates a ticket using the supplied customer, subject, description,
status, priority, and assignment information.

### Authentication requirement

Bearer Token authentication is required.

### Required parameters

  ------------------------------------------------------------------------
  Parameter        Type                          Required Description
  ---------------- ---------------- --------------------- ----------------
  `customer_id`    string                             Yes Identifier of
                                                          the customer
                                                          associated with
                                                          the ticket.

  `subject`        string                             Yes Ticket subject.

  `description`    string                             Yes Ticket
                                                          description.
  ------------------------------------------------------------------------

### Optional parameters

  --------------------------------------------------------------------------
  Parameter          Type                          Required Description
  ------------------ ---------------- --------------------- ----------------
  `status`           string                              No Ticket status.
                                                            Supported
                                                            values: `open`,
                                                            `pending`,
                                                            `resolved`,
                                                            `closed`.

  `priority`         string                              No Ticket priority.
                                                            Supported
                                                            values: `low`,
                                                            `medium`,
                                                            `high`,
                                                            `urgent`.

  `assigned_agent`   string                              No Agent assigned
                                                            to the ticket.
  --------------------------------------------------------------------------

### Request headers

``` text
Authorization: Bearer <API_TOKEN>
Content-Type: application/json
Accept: application/json
```

### Request body

``` json
{
  "customer_id": "cust_1001",
  "subject": "Unable to access account",
  "description": "The customer cannot sign in to their account.",
  "priority": "high",
  "assigned_agent": "agent_42"
}
```

### cURL example

``` bash
curl -X POST "https://api.flowdesk.example/v1/tickets" \
  -H "Authorization: Bearer <API_TOKEN>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "customer_id": "cust_1001",
    "subject": "Unable to access account",
    "description": "The customer cannot sign in to their account.",
    "priority": "high",
    "assigned_agent": "agent_42"
  }'
```

### Response body

``` json
{
  "ticket_id": "ticket_2001",
  "customer_id": "cust_1001",
  "subject": "Unable to access account",
  "description": "The customer cannot sign in to their account.",
  "status": "open",
  "priority": "high",
  "assigned_agent": "agent_42",
  "created_at": "2026-09-08T07:00:00Z",
  "updated_at": "2026-09-08T07:00:00Z"
}
```

### HTTP status codes

    Status Meaning
  -------- ----------------------------------------------
     `201` Ticket created successfully.
     `400` Request is invalid.
     `401` Authentication failed or token is missing.
     `403` API access is not permitted for the account.
     `429` API rate limit exceeded.

### Error example

``` json
{
  "error": {
    "code": "invalid_request",
    "message": "The customer_id field is required."
  }
}
```

------------------------------------------------------------------------

## 5. Get Ticket

Retrieves a ticket by its identifier.

### HTTP method

`GET`

### Endpoint

``` text
/tickets/{ticket_id}
```

### Description

Returns the ticket identified by `ticket_id`.

### Authentication requirement

Bearer Token authentication is required.

### Required parameters

  ------------------------------------------------------------------------
  Parameter        Type                          Required Description
  ---------------- ---------------- --------------------- ----------------
  `ticket_id`      string                             Yes Ticket
                                                          identifier
                                                          supplied in the
                                                          URL path.

  ------------------------------------------------------------------------

### Optional parameters

None.

### Request headers

``` text
Authorization: Bearer <API_TOKEN>
Accept: application/json
```

### Request body

No request body is required.

### cURL example

``` bash
curl -X GET "https://api.flowdesk.example/v1/tickets/ticket_2001" \
  -H "Authorization: Bearer <API_TOKEN>" \
  -H "Accept: application/json"
```

### Response body

``` json
{
  "ticket_id": "ticket_2001",
  "customer_id": "cust_1001",
  "subject": "Unable to access account",
  "description": "The customer cannot sign in to their account.",
  "status": "open",
  "priority": "high",
  "assigned_agent": "agent_42",
  "created_at": "2026-09-08T07:00:00Z",
  "updated_at": "2026-09-08T07:00:00Z"
}
```

### HTTP status codes

    Status Meaning
  -------- ----------------------------------------------
     `200` Ticket retrieved successfully.
     `401` Authentication failed or token is missing.
     `403` API access is not permitted for the account.
     `404` Ticket was not found.
     `429` API rate limit exceeded.

### Error example

``` json
{
  "error": {
    "code": "ticket_not_found",
    "message": "The requested ticket was not found."
  }
}
```

------------------------------------------------------------------------

## 6. Update Ticket

Updates an existing ticket.

### HTTP method

`PATCH`

### Endpoint

``` text
/tickets/{ticket_id}
```

### Description

Updates one or more supported ticket fields.

### Authentication requirement

Bearer Token authentication is required.

### Required parameters

  ------------------------------------------------------------------------
  Parameter        Type                          Required Description
  ---------------- ---------------- --------------------- ----------------
  `ticket_id`      string                             Yes Ticket
                                                          identifier
                                                          supplied in the
                                                          URL path.

  ------------------------------------------------------------------------

### Optional parameters

  --------------------------------------------------------------------------
  Parameter          Type                          Required Description
  ------------------ ---------------- --------------------- ----------------
  `customer_id`      string                              No Customer
                                                            associated with
                                                            the ticket.

  `subject`          string                              No Updated ticket
                                                            subject.

  `description`      string                              No Updated ticket
                                                            description.

  `status`           string                              No Updated status:
                                                            `open`,
                                                            `pending`,
                                                            `resolved`, or
                                                            `closed`.

  `priority`         string                              No Updated
                                                            priority: `low`,
                                                            `medium`,
                                                            `high`, or
                                                            `urgent`.

  `assigned_agent`   string                              No Agent assigned
                                                            to the ticket.
  --------------------------------------------------------------------------

### Request headers

``` text
Authorization: Bearer <API_TOKEN>
Content-Type: application/json
Accept: application/json
```

### Request body

``` json
{
  "status": "pending",
  "priority": "medium",
  "assigned_agent": "agent_18"
}
```

### cURL example

``` bash
curl -X PATCH "https://api.flowdesk.example/v1/tickets/ticket_2001" \
  -H "Authorization: Bearer <API_TOKEN>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "status": "pending",
    "priority": "medium",
    "assigned_agent": "agent_18"
  }'
```

### Response body

``` json
{
  "ticket_id": "ticket_2001",
  "customer_id": "cust_1001",
  "subject": "Unable to access account",
  "description": "The customer cannot sign in to their account.",
  "status": "pending",
  "priority": "medium",
  "assigned_agent": "agent_18",
  "created_at": "2026-09-08T07:00:00Z",
  "updated_at": "2026-09-08T07:30:00Z"
}
```

### HTTP status codes

    Status Meaning
  -------- ----------------------------------------------
     `200` Ticket updated successfully.
     `400` Request is invalid.
     `401` Authentication failed or token is missing.
     `403` API access is not permitted for the account.
     `404` Ticket was not found.
     `429` API rate limit exceeded.

### Error example

``` json
{
  "error": {
    "code": "invalid_priority",
    "message": "Priority must be low, medium, high, or urgent."
  }
}
```

------------------------------------------------------------------------

## 7. List Tickets

Returns a collection of tickets available to the authenticated account.

### HTTP method

`GET`

### Endpoint

``` text
/tickets
```

### Description

Retrieves a list of tickets.

### Authentication requirement

Bearer Token authentication is required.

### Required parameters

None.

### Optional parameters

The endpoint supports the following optional resource-selection
parameters:

  --------------------------------------------------------------------------
  Parameter          Type                          Required Description
  ------------------ ---------------- --------------------- ----------------
  `status`           string                              No Filter tickets
                                                            by status:
                                                            `open`,
                                                            `pending`,
                                                            `resolved`, or
                                                            `closed`.

  `priority`         string                              No Filter tickets
                                                            by priority:
                                                            `low`, `medium`,
                                                            `high`, or
                                                            `urgent`.

  `customer_id`      string                              No Filter tickets
                                                            associated with
                                                            a customer.

  `assigned_agent`   string                              No Filter tickets
                                                            assigned to an
                                                            agent.
  --------------------------------------------------------------------------

### Request headers

``` text
Authorization: Bearer <API_TOKEN>
Accept: application/json
```

### Request body

No request body is required.

### cURL example

``` bash
curl -X GET "https://api.flowdesk.example/v1/tickets?status=open&priority=high" \
  -H "Authorization: Bearer <API_TOKEN>" \
  -H "Accept: application/json"
```

### Response body

``` json
{
  "tickets": [
    {
      "ticket_id": "ticket_2001",
      "customer_id": "cust_1001",
      "subject": "Unable to access account",
      "description": "The customer cannot sign in to their account.",
      "status": "open",
      "priority": "high",
      "assigned_agent": "agent_42",
      "created_at": "2026-09-08T07:00:00Z",
      "updated_at": "2026-09-08T07:00:00Z"
    },
    {
      "ticket_id": "ticket_2002",
      "customer_id": "cust_1004",
      "subject": "Billing question",
      "description": "The customer has a question about their subscription.",
      "status": "open",
      "priority": "high",
      "assigned_agent": "agent_18",
      "created_at": "2026-09-08T07:15:00Z",
      "updated_at": "2026-09-08T07:20:00Z"
    }
  ]
}
```

### HTTP status codes

    Status Meaning
  -------- ----------------------------------------------
     `200` Tickets retrieved successfully.
     `400` One or more query parameters are invalid.
     `401` Authentication failed or token is missing.
     `403` API access is not permitted for the account.
     `429` API rate limit exceeded.

### Error example

``` json
{
  "error": {
    "code": "invalid_status",
    "message": "Status must be open, pending, resolved, or closed."
  }
}
```

------------------------------------------------------------------------

## 8. Delete Ticket

Deletes an existing ticket.

### HTTP method

`DELETE`

### Endpoint

``` text
/tickets/{ticket_id}
```

### Description

Deletes the specified ticket.

### Authentication requirement

Bearer Token authentication is required.

### Required parameters

  ------------------------------------------------------------------------
  Parameter        Type                          Required Description
  ---------------- ---------------- --------------------- ----------------
  `ticket_id`      string                             Yes Ticket
                                                          identifier
                                                          supplied in the
                                                          URL path.

  ------------------------------------------------------------------------

### Optional parameters

None.

### Request headers

``` text
Authorization: Bearer <API_TOKEN>
Accept: application/json
```

### Request body

No request body is required.

### cURL example

``` bash
curl -X DELETE "https://api.flowdesk.example/v1/tickets/ticket_2001" \
  -H "Authorization: Bearer <API_TOKEN>" \
  -H "Accept: application/json"
```

### Response body

A successful deletion does not require a response body.

### HTTP status codes

    Status Meaning
  -------- ----------------------------------------------
     `204` Ticket deleted successfully.
     `401` Authentication failed or token is missing.
     `403` API access is not permitted for the account.
     `404` Ticket was not found.
     `429` API rate limit exceeded.

### Error example

``` json
{
  "error": {
    "code": "ticket_not_found",
    "message": "The requested ticket was not found."
  }
}
```

------------------------------------------------------------------------

## 9. Ticket Status

The `status` field describes the current state of a ticket.

  Status       Description
  ------------ ----------------------------------------------------
  `open`       Ticket is open and requires support work.
  `pending`    Ticket is pending further activity or information.
  `resolved`   Ticket has been resolved.
  `closed`     Ticket is closed.

Use only the supported status values when creating or updating tickets.

### Example

``` json
{
  "status": "resolved"
}
```

------------------------------------------------------------------------

## 10. Ticket Priority

The `priority` field indicates the priority assigned to a ticket.

  -----------------------------------------------------------------------
  Priority                            Description
  ----------------------------------- -----------------------------------
  `low`                               Low-priority support request.

  `medium`                            Standard-priority support request.

  `high`                              High-priority support request.

  `urgent`                            Urgent support request requiring
                                      the highest available priority.
  -----------------------------------------------------------------------

Use only the supported priority values when creating or updating
tickets.

### Example

``` json
{
  "priority": "urgent"
}
```

------------------------------------------------------------------------

## 11. Request Examples

### Create a high-priority ticket

``` bash
curl -X POST "https://api.flowdesk.example/v1/tickets" \
  -H "Authorization: Bearer <API_TOKEN>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "customer_id": "cust_1001",
    "subject": "Production access issue",
    "description": "The customer cannot access the production workspace.",
    "priority": "high"
  }'
```

### Update a ticket status

``` bash
curl -X PATCH "https://api.flowdesk.example/v1/tickets/ticket_2001" \
  -H "Authorization: Bearer <API_TOKEN>" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{
    "status": "resolved"
  }'
```

### List high-priority tickets

``` bash
curl -X GET "https://api.flowdesk.example/v1/tickets?priority=high" \
  -H "Authorization: Bearer <API_TOKEN>" \
  -H "Accept: application/json"
```

------------------------------------------------------------------------

## 12. Response Examples

### Successful ticket response

``` json
{
  "ticket_id": "ticket_2001",
  "customer_id": "cust_1001",
  "subject": "Production access issue",
  "description": "The customer cannot access the production workspace.",
  "status": "open",
  "priority": "high",
  "assigned_agent": "agent_42",
  "created_at": "2026-09-08T07:00:00Z",
  "updated_at": "2026-09-08T07:00:00Z"
}
```

### Ticket list response

``` json
{
  "tickets": [
    {
      "ticket_id": "ticket_2001",
      "customer_id": "cust_1001",
      "subject": "Production access issue",
      "description": "The customer cannot access the production workspace.",
      "status": "open",
      "priority": "high",
      "assigned_agent": "agent_42",
      "created_at": "2026-09-08T07:00:00Z",
      "updated_at": "2026-09-08T07:00:00Z"
    }
  ]
}
```

------------------------------------------------------------------------

## 13. Error Responses

FlowDesk API errors use a JSON error object containing an error code and
human-readable message.

### General error format

``` json
{
  "error": {
    "code": "invalid_request",
    "message": "The request could not be processed."
  }
}
```

### HTTP status code reference

  -----------------------------------------------------------------------
                               HTTP status Meaning
  ---------------------------------------- ------------------------------
                                     `400` The request contains invalid
                                           data or parameters.

                                     `401` Authentication is missing or
                                           invalid.

                                     `403` The authenticated account is
                                           not permitted to perform the
                                           operation.

                                     `404` The requested ticket does not
                                           exist.

                                     `429` The account has exceeded its
                                           API rate limit.
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 14. Rate Limits

FlowDesk API access is subject to plan-based rate limits.

  Plan         API access                  Rate limit
  ------------ ------------ -------------------------
  Free         No                      Not applicable
  Pro          Yes             60 requests per minute
  Enterprise   Yes            300 requests per minute

A `429 Too Many Requests` response indicates that the applicable API
rate limit has been exceeded.

### Rate-limit error example

``` json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "API rate limit exceeded."
  }
}
```

> **Note:** Free customers cannot use the Ticket API because API access
> is unavailable on the Free plan.

------------------------------------------------------------------------

## 15. Common API Errors

### `invalid_request`

The request is missing a required field or contains invalid request
data.

``` json
{
  "error": {
    "code": "invalid_request",
    "message": "The customer_id field is required."
  }
}
```

Check the request body and required parameters before retrying.

### `authentication_failed`

The API token is missing or invalid.

``` json
{
  "error": {
    "code": "authentication_failed",
    "message": "Authentication failed."
  }
}
```

Check that the request includes:

``` text
Authorization: Bearer <API_TOKEN>
```

### `api_access_unavailable`

The account does not have API access.

``` json
{
  "error": {
    "code": "api_access_unavailable",
    "message": "API access is not available for this plan."
  }
}
```

API access is available on Pro and Enterprise plans.

### `ticket_not_found`

The requested ticket does not exist.

``` json
{
  "error": {
    "code": "ticket_not_found",
    "message": "The requested ticket was not found."
  }
}
```

Verify the `ticket_id` and retry the request.

### `invalid_status`

The supplied ticket status is not supported.

``` json
{
  "error": {
    "code": "invalid_status",
    "message": "Status must be open, pending, resolved, or closed."
  }
}
```

Use one of the supported values: `open`, `pending`, `resolved`, or
`closed`.

### `invalid_priority`

The supplied ticket priority is not supported.

``` json
{
  "error": {
    "code": "invalid_priority",
    "message": "Priority must be low, medium, high, or urgent."
  }
}
```

Use one of the supported values: `low`, `medium`, `high`, or `urgent`.

### `rate_limit_exceeded`

The account has exceeded its plan-based API request limit.

``` json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "API rate limit exceeded."
  }
}
```

Reduce request frequency and retry after the rate-limit window has
cleared.

------------------------------------------------------------------------

## API Endpoint Summary

  Method     Endpoint                 Description
  ---------- ------------------------ ------------------
  `POST`     `/tickets`               Create a ticket.
  `GET`      `/tickets/{ticket_id}`   Get a ticket.
  `PATCH`    `/tickets/{ticket_id}`   Update a ticket.
  `GET`      `/tickets`               List tickets.
  `DELETE`   `/tickets/{ticket_id}`   Delete a ticket.
