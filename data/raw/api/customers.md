# FlowDesk Customer Management

## 1. Overview

FlowDesk Customer Management provides a centralized way to organize customer information and connect customer profiles with support tickets.

A customer profile stores information that helps support teams identify customers, understand their organization, organize customers into groups, and associate customer activity with support tickets.

A FlowDesk customer profile can contain:

- `customer_id`
- `name`
- `email`
- `company`
- `tags`
- Custom fields

Customer profiles are also connected to tickets through `customer_id`. This relationship allows agents to identify which customer submitted or is associated with a particular support ticket.

> **Note:** Customer information should be kept accurate and up to date so that agents can correctly identify customers and understand their support history.

---

## 2. Customer Profiles

A customer profile represents an individual customer or customer contact managed within FlowDesk.

Profiles provide a central location for customer information used by support agents and other authorized team members.

Customer profiles can be used to:

- Identify a customer.
- Store contact information.
- Associate a customer with a company.
- Organize customers using tags.
- Store additional business-specific information using custom fields.
- Associate customers with support tickets.

A customer profile can be viewed and updated from the customer management area of FlowDesk, subject to the user's permissions.

---

## 3. Customer Profile Anatomy

Each customer profile contains a set of standard fields and organizational attributes.

| Field         | Purpose                                                   | Example                  |
| ------------- | --------------------------------------------------------- | ------------------------ |
| `customer_id` | Unique identifier for the customer                        | `cus_10042`              |
| `name`        | Customer's name                                           | `Sarah Johnson`          |
| `email`       | Customer's email address                                  | `sarah@example.com`      |
| `company`     | Company associated with the customer                      | `Acme Solutions`         |
| `tags`        | Labels used to organize and segment customers             | `enterprise`, `priority` |
| Custom fields | Additional customer information defined for the workspace | `customer_tier: Gold`    |

The standard fields provide the core customer identity, while tags and custom fields provide additional organization and context.

---

## 4. Customer ID

`customer_id` is the unique identifier assigned to a customer profile.

Example:

```text
customer_id: cus_10042
```

The customer ID is primarily used to identify a customer consistently across FlowDesk.

It is particularly important when connecting customers with tickets.

For example:

```text
Customer:
customer_id: cus_10042
name: Sarah Johnson
email: sarah@example.com
```

A ticket associated with this customer can reference:

```text
customer_id: cus_10042
```

### Customer ID Best Practices

- Treat `customer_id` as the primary identifier for the customer.
- Use the customer ID when referring to a customer in integrations or API operations.
- Do not manually change a customer's identifier.
- Avoid using the customer's name as a unique identifier because multiple customers can have the same name.

> **Note:** Customer IDs should be preserved when updating customer information so that existing relationships with tickets remain intact.

---

## 5. Name

The `name` field stores the customer's name.

Example:

```text
name: Sarah Johnson
```

The name helps agents identify customers when working with customer profiles and support tickets.

Use the customer's recognizable name rather than unrelated internal labels.

---

## 6. Email

The `email` field stores the customer's primary email address.

Example:

```text
email: sarah@example.com
```

The email address can help agents identify and communicate with the customer.

### Email Best Practices

- Keep the email address accurate.
- Avoid unnecessary duplicate customer profiles for the same customer.
- Verify the address when updating customer information.
- Use an appropriate customer email rather than an internal agent address.

> **Warning:** Incorrect email information can make it difficult for support teams to identify or contact the correct customer.

---

## 7. Company

The `company` field identifies the organization associated with the customer.

Example:

```text
company: Acme Solutions
```

This is useful when FlowDesk is used by B2B support teams that manage multiple contacts from the same organization.

Multiple customer profiles can represent different contacts associated with the same company.

For example:

```text
Sarah Johnson → Acme Solutions
Michael Lee   → Acme Solutions
```

Each contact can maintain a separate customer profile while sharing the same company information.

---

## 8. Tags

Tags are labels that help teams organize and categorize customer profiles.

Examples include:

```text
enterprise
priority
trial
vip
technical
```

Tags can be used to identify groups of customers based on business or support characteristics.

For example, a customer might have:

```text
tags:
  - enterprise
  - priority
```

### Tag Usage

Tags can help support teams:

- Group related customers.
- Identify important customer segments.
- Filter customer records.
- Add context to customer profiles.
- Support customer segmentation workflows.

Tags should be meaningful and applied consistently across the workspace.

---

## 9. Custom Fields

Custom fields allow teams to store additional customer information that is not covered by the standard profile fields.

For example:

```text
Custom fields:
  customer_tier: Gold
  onboarding_status: Complete
  account_manager: Alex
```

Custom fields are useful when an organization needs to maintain business-specific information.

### Examples of Custom Field Usage

| Custom Field        | Example Value | Purpose                                  |
| ------------------- | ------------- | ---------------------------------------- |
| `customer_tier`     | `Gold`        | Identify the customer's service tier     |
| `onboarding_status` | `Complete`    | Track onboarding progress                |
| `account_manager`   | `Alex`        | Identify the responsible account manager |

Custom fields should be used for information that is relevant to customer management and support operations.

> **Note:** Custom fields are workspace-specific extensions to the standard customer profile. The examples above are illustrative; organizations can define fields appropriate to their workflows.

---

## 10. Creating a Customer

Authorized users can create a customer profile from the customer management area.

### Procedure

1. Open **Customers** in FlowDesk.
2. Select **Create customer**.
3. Enter the customer's name.
4. Enter the customer's email address.
5. Enter the company, if applicable.
6. Add relevant tags.
7. Enter applicable custom field values.
8. Review the information.
9. Select **Create**.

FlowDesk assigns a unique `customer_id` to the new customer profile.

Example resulting profile:

```text
customer_id: cus_10042
name: Sarah Johnson
email: sarah@example.com
company: Acme Solutions
tags:
  - enterprise
  - priority
custom_fields:
  customer_tier: Gold
```

> **Best practice:** Check whether the customer already exists before creating a new profile to reduce duplicate customer records.

---

## 11. Viewing Customer Details

To view a customer:

1. Open **Customers**.
2. Search for the customer.
3. Select the relevant customer profile.
4. Review the customer's profile information.

The profile can contain:

- Customer ID
- Name
- Email
- Company
- Tags
- Custom fields
- Associated ticket information

Viewing the customer profile gives agents additional context when handling support requests.

---

## 12. Updating Customer Information

Customer information should be updated when a customer's details change.

### Procedure

1. Open the customer's profile.
2. Select **Edit**.
3. Update the relevant information.
4. Review the changes.
5. Save the customer profile.

For example, if a customer changes companies:

```text
Before:
company: Acme Solutions

After:
company: Northstar Technologies
```

The customer's `customer_id` remains the identifier for the existing profile.

> **Important:** Updating customer information should not be treated as creating a new customer. Preserve the existing customer profile when the same customer changes information.

---

## 13. Managing Customer Tags

Tags can be added or removed from a customer profile.

### Adding a Tag

1. Open the customer profile.
2. Locate the **Tags** section.
3. Select **Add tag**.
4. Choose or enter the appropriate tag.
5. Save the change.

### Removing a Tag

1. Open the customer profile.
2. Locate the **Tags** section.
3. Find the tag to remove.
4. Remove the tag.
5. Save the change.

For example:

```text
Before:
tags:
  - trial
  - technical

After:
tags:
  - customer
  - technical
```

Use consistent naming conventions for tags so that customer segmentation remains reliable.

---

## 14. Managing Custom Fields

Custom fields provide additional customer attributes beyond the standard profile structure.

### Adding or Updating a Custom Field

1. Open the customer profile.
2. Select **Edit**.
3. Locate the custom fields section.
4. Add or update the required field.
5. Enter the appropriate value.
6. Save the customer profile.

Example:

```text
customer_tier: Gold
```

If the customer's tier changes:

```text
customer_tier: Platinum
```

Custom fields should contain information that is useful to support or customer-management workflows.

> **Best practice:** Avoid creating multiple custom fields that represent the same information. Establish clear naming conventions before adding workspace-specific fields.

---

## 15. Customer Segmentation

Customer segmentation is the process of organizing customers into meaningful groups.

FlowDesk can support segmentation using customer attributes such as:

- Tags
- Company
- Custom fields
- Customer information

For example, a support team could use tags to identify:

```text
enterprise
priority
trial
technical
```

A customer profile could therefore be represented as:

```text
Customer: Sarah Johnson
Company: Acme Solutions

Tags:
- enterprise
- priority
- technical

Custom fields:
- customer_tier: Gold
- onboarding_status: Complete
```

This information can help support teams identify customers that share common characteristics.

### Segmentation Best Practices

Use tags for broad, reusable classifications and custom fields for structured business-specific information.

For example:

| Requirement                     | Recommended Approach |
| ------------------------------- | -------------------- |
| Identify priority customers     | Tag                  |
| Identify customer tier          | Custom field         |
| Identify trial customers        | Tag                  |
| Store onboarding status         | Custom field         |
| Group customers by organization | Company              |

---

## 16. Customer and Ticket Relationships

Customers and tickets are connected through `customer_id`.

A ticket contains a `customer_id` that identifies the customer associated with the ticket.

For example:

```text
Customer
customer_id: cus_10042
name: Sarah Johnson
email: sarah@example.com
```

A related ticket can contain:

```text
ticket_id: tkt_20481
customer_id: cus_10042
subject: Unable to access dashboard
status: open
priority: high
```

The shared `customer_id` establishes the relationship between the ticket and customer.

### Why the Relationship Matters

This relationship allows support agents to:

- Identify who is associated with a ticket.
- View customer information while handling a ticket.
- Understand a customer's support activity.
- Maintain consistent customer identity across multiple tickets.

> **Important:** Customer information and ticket information are separate resources. A change to a customer's profile does not change the ticket's own fields such as `ticket_id`, `subject`, `status`, or `priority`.

---

## 17. Customer Management Best Practices

### Maintain Accurate Profiles

Keep customer information current, particularly:

- Name
- Email
- Company

### Avoid Duplicate Profiles

Before creating a new customer, search existing profiles using available customer information.

Duplicate profiles can make customer history harder to understand and may result in customer activity being distributed across multiple records.

### Use Consistent Tags

Establish a consistent tagging convention.

For example, avoid having several tags that represent the same concept:

```text
priority
high-priority
high_priority
```

Choose one convention and apply it consistently.

### Use Custom Fields Carefully

Custom fields should represent meaningful, structured information.

Avoid using custom fields as a replacement for information already represented by standard fields.

### Preserve Customer IDs

Use the existing `customer_id` when maintaining an existing customer profile.

Do not create a new customer profile simply because the customer's name, email, or company information has changed.

### Protect Customer Information

Only authorized team members should access or modify customer information.

FlowDesk provides role-based access control and audit logs as part of its security capabilities.

---

## 18. Common Customer Management Issues

### Duplicate Customer Profiles

**Problem:** The same customer appears in multiple profiles.

**Possible causes:**

- A new profile was created without checking existing customers.
- Customer information was entered inconsistently.
- Different contacts were incorrectly treated as separate instances of the same customer.

**Recommended action:**

1. Search for existing profiles before creating a new customer.
2. Compare the customer's available information.
3. Determine which profile should be maintained.
4. Avoid creating additional duplicate profiles.

---

### Incorrect Customer Email

**Problem:** The email address in the profile is incorrect.

**Recommended action:**

1. Open the customer profile.
2. Select **Edit**.
3. Verify the correct email address.
4. Update the profile.
5. Save the changes.

---

### Missing Company Information

**Problem:** A customer's company is not displayed.

**Recommended action:**

Update the customer's `company` field if the organization is known.

For example:

```text
company: Acme Solutions
```

---

### Inconsistent Tags

**Problem:** Similar customers use different tags for the same classification.

**Example:**

```text
priority
high-priority
high_priority
```

**Recommended action:** Establish a workspace-wide tagging convention and standardize existing tags where appropriate.

---

### Missing Custom Field Information

**Problem:** A customer profile does not contain information expected by a support workflow.

**Recommended action:**

1. Verify whether the information belongs in a custom field.
2. Check whether the relevant custom field has been defined.
3. Update the customer's profile if appropriate.
4. Ensure agents use the same field consistently.

---

### Ticket Associated With the Wrong Customer

**Problem:** A ticket displays an unexpected customer.

**Cause:** The ticket's `customer_id` points to a different customer profile.

**Recommended action:**

1. Verify the ticket's `customer_id`.
2. Open the referenced customer profile.
3. Confirm that the customer information is correct.
4. If the association is incorrect, follow the workspace's authorized ticket-management process to correct it.

---

## 19. API Considerations

Customer management can be integrated with systems using the FlowDesk API when API access is available.

API access is available on:

- **Pro**
- **Enterprise**

The **Free** plan does not include API access.

The FlowDesk API uses Bearer Token authentication.

### Authentication

API requests must include:

```http
Authorization: Bearer <API_TOKEN>
```

The API base URL is:

```text
https://api.flowdesk.example/v1
```

For example, an authenticated customer-related request can be structured as:

```bash
curl https://api.flowdesk.example/v1/customers/cus_10042 \
  -H "Authorization: Bearer <API_TOKEN>"
```

The exact customer endpoint and supported operations should be used according to the API capabilities available to the FlowDesk account.

### API Rate Limits

| Plan       | API Access |          Rate Limit |
| ---------- | ---------- | ------------------: |
| Free       | No         |                 N/A |
| Pro        | Yes        |  60 requests/minute |
| Enterprise | Yes        | 300 requests/minute |

> **Note:** API authentication and authorization are separate. A valid Bearer Token authenticates the request, but the authenticated client must still have permission to access or modify the requested customer resource.

### Customer ID in API Integrations

When integrating customer information with external systems, use `customer_id` as the FlowDesk customer identifier.

Example:

```json
{
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
```

When customer information is referenced together with tickets, the same `customer_id` establishes the relationship between the customer and associated ticket records.

> **Security warning:** Never expose API tokens in customer-facing applications, public repositories, documentation, or logs. Store API credentials securely and send API requests over HTTPS.
