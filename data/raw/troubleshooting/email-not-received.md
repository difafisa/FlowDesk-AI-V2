# Email Not Received Troubleshooting

## 1. Overview

FlowDesk may send emails for account-related activities, ticket notifications, automation workflows, and subscription-related activities. If an expected email does not appear in your inbox, the message may have been filtered, delayed, or sent to an address different from the one you are checking.

This guide explains common causes of missing FlowDesk emails and provides troubleshooting procedures for different types of messages.

Before contacting FlowDesk support, verify the email address associated with the relevant account or customer record and check your mailbox's spam, junk, filtering, and security settings.

---

## 2. Types of FlowDesk Emails

Depending on the activity performed in FlowDesk, users may receive different types of emails.

### Password Reset Emails

Password-reset emails are sent when a user requests to reset their FlowDesk password.

These messages contain the information needed to continue the password-reset process.

### Account-Related Emails

FlowDesk may send emails related to account activities and access, such as information associated with managing a FlowDesk account.

### Ticket Notification Emails

Ticket-related activities may result in email notifications depending on the applicable notification configuration.

Examples of ticket events that may be associated with notifications include:

- Ticket creation
- Ticket updates
- Ticket assignment
- Ticket resolution

> **Note:** Not every ticket event necessarily generates an email. The presence of a ticket event alone does not guarantee that an email notification will be sent.

### Automation-Generated Emails

FlowDesk automation supports the `send_email` action. When an automation workflow is configured to use this action, FlowDesk can send an email as part of the workflow.

### Billing or Subscription-Related Emails

Customers may receive emails associated with subscription and billing activities, particularly when managing Pro or Enterprise subscriptions.

---

## 3. Common Causes

An expected FlowDesk email may be missing for several reasons.

### Email Delivered to Spam or Junk

Your email provider may classify the message as spam or junk instead of placing it in the primary inbox.

### Incorrect Email Address

The email address stored in the relevant FlowDesk account or customer profile may contain an error.

Check the address carefully, including:

- Spelling
- Domain name
- Missing characters
- Accidental spaces

### Email Delivery Delay

An email may take some time to appear after the action that triggered it. Temporary delivery delays can occur even when the original FlowDesk action was successful.

### Mailbox Storage Limit

A mailbox that has reached its storage limit may be unable to accept new messages.

### Email Filtering Rules

Personal or organizational mailbox rules may automatically move, archive, or delete FlowDesk emails.

### Corporate Email Security Filters

Corporate email systems may quarantine or block messages that they consider suspicious or outside the organization's approved email sources.

### Blocked FlowDesk Sender

A user or administrator may have blocked the sender associated with FlowDesk emails.

### Temporary Email Delivery Problems

A temporary issue affecting email delivery may prevent a message from arriving when expected. If multiple unrelated FlowDesk emails are affected, the problem may require investigation by FlowDesk support.

---

## 4. General Troubleshooting Procedure

Use the following procedure when an expected FlowDesk email does not arrive.

### Step 1: Verify the Email Address

Confirm that the email address associated with the FlowDesk account, customer profile, or relevant action is correct.

Check for:

- Typographical errors
- Incorrect domains
- Unexpected spaces
- An old email address

### Step 2: Check Spam and Junk Folders

Open your email provider's:

- Spam folder
- Junk folder
- Quarantine area, if available

If you find the FlowDesk email there, mark it as legitimate according to your email provider's available options.

### Step 3: Search the Mailbox

Use your email provider's search function to search for FlowDesk-related messages.

Search terms can include:

- `FlowDesk`
- The subject of the expected message
- A relevant ticket identifier
- Terms associated with password reset or subscription activity

### Step 4: Check Email Filtering Rules

Review personal mailbox rules and filters that could:

- Move FlowDesk messages to another folder
- Archive messages automatically
- Delete messages
- Mark messages as spam

### Step 5: Check Corporate Email Security Settings

If you use a corporate email account, ask your organization's email administrator to check whether the message has been quarantined or blocked.

### Step 6: Wait for a Reasonable Delivery Period

If the action was just performed, allow some time for the email to arrive before requesting the action again.

Avoid repeatedly triggering the same email action unless necessary.

### Step 7: Retry the Action When Appropriate

If the original action supports another attempt, repeat it after completing the checks above.

For example, you can request another password-reset email if the previous reset email was not received.

### Step 8: Contact FlowDesk Support

If the email still does not arrive after completing the troubleshooting steps, contact FlowDesk support.

Include:

- The type of email you expected
- The approximate time the action was performed
- The email address involved
- Relevant ticket or account information that is safe to share
- The troubleshooting steps already completed

> **Security warning:** Never include your password, API token, or other authentication secrets in a support request.

---

## 5. Password Reset Email Not Received

Password-reset emails require special handling because the message is needed to regain access to an account.

### Verify the Email Address

Confirm that the email address entered on the password-reset form is the address associated with your FlowDesk account.

Check the spelling and domain carefully.

### Check Spam and Junk Folders

Search your spam and junk folders for the password-reset message.

Also check any quarantine area managed by your email provider or organization.

### Request Another Reset Email

If the original message does not arrive:

1. Verify the account email address.
2. Check spam and junk folders.
3. Search your mailbox for FlowDesk messages.
4. Wait a reasonable amount of time for delivery.
5. Return to the FlowDesk login page.
6. Select **Forgot password?**
7. Submit another password-reset request.

Use the newest reset email when multiple reset messages are received.

> **Note:** Older password-reset links may no longer be valid after a newer reset request has been made.

### If Multiple Reset Emails Are Received

If several password-reset emails arrive:

1. Identify the most recently requested reset email.
2. Open the newest message.
3. Use the reset link from the newest message.
4. Do not rely on older reset links if they no longer work.

### If the Reset Link Has Expired

Password-reset links are temporary.

If the link has expired:

1. Return to the FlowDesk login page.
2. Select **Forgot password?**
3. Enter the account email address.
4. Request a new password-reset email.
5. Open the newest reset email.
6. Follow the new reset link.

If newly generated reset links repeatedly fail, contact FlowDesk support.

---

## 6. Ticket Notification Email Not Received

FlowDesk tickets contain information such as the ticket ID, customer, status, priority, assigned agent, and timestamps.

Ticket activities may be associated with email notifications depending on the applicable notification configuration.

Examples include:

- Ticket creation
- Ticket updates
- Ticket assignment
- Ticket resolution

### Troubleshooting Steps

1. Confirm that the ticket event actually occurred in FlowDesk.
2. Verify the email address associated with the intended recipient.
3. Check the recipient's inbox, spam, and junk folders.
4. Search the mailbox for FlowDesk or the relevant ticket information.
5. Check mailbox filtering rules.
6. If the recipient uses a corporate mailbox, check the organization's email security or quarantine system.
7. If multiple expected ticket notifications are missing, contact FlowDesk support.

> **Important:** Do not assume that every ticket event generates an email. First verify that an email notification is expected for the particular workflow or configuration.

---

## 7. Automation Email Not Received

FlowDesk automation can trigger actions when supported events occur.

The `send_email` action allows an automation workflow to send an email.

If an automation is expected to send an email but the recipient does not receive it, verify the workflow before troubleshooting the mailbox.

### Troubleshooting Steps

1. Confirm that the expected trigger event occurred.
2. Verify that the automation is configured with the correct trigger.
3. Confirm that the workflow includes the `send_email` action.
4. Verify the email recipient configured for the action.
5. Check the recipient's inbox and spam or junk folders.
6. Search the mailbox for FlowDesk messages.
7. Check personal email filtering rules.
8. For corporate email accounts, check whether the message was quarantined or blocked.
9. If the automation appears to execute correctly but emails consistently do not arrive, contact FlowDesk support.

### Example

An automation may be configured to react to `ticket.created` and use `send_email` as its action.

If the ticket is created but the expected email does not appear:

1. Confirm that the ticket was created.
2. Verify that the automation uses `ticket.created` as its trigger.
3. Confirm that `send_email` is included as the action.
4. Verify the configured recipient address.
5. Check the recipient mailbox and corporate email filtering.
6. Contact support if the problem persists.

---

## 8. Corporate Email Environment

Corporate email environments commonly use additional security controls that can delay, quarantine, or block messages.

These controls may include:

- Spam filtering
- Message quarantine
- Sender blocking
- Organization-wide email rules
- Security policies for external email

### For Users

If you use a corporate email account:

1. Check your spam and junk folders.
2. Check whether your organization provides access to a quarantine area.
3. Ask your email administrator whether a FlowDesk message was blocked or quarantined.
4. Provide the administrator with the approximate time the email was expected.
5. Verify that your FlowDesk account or customer email address is correct.

### For Administrators

Administrators should check the organization's email filtering and quarantine systems for the missing message.

If the message is found in quarantine, follow the organization's established process for releasing or allowing legitimate messages.

> **Note:** FlowDesk cannot control filtering decisions made by a customer's corporate email environment.

If the corporate email system has ruled out filtering or blocking, contact FlowDesk support if the problem continues.

---

## 9. When to Contact FlowDesk Support

Contact FlowDesk support when standard mailbox and account troubleshooting does not resolve the problem.

Support should be contacted when:

- Multiple types of FlowDesk emails are consistently missing.
- Expected emails continue to fail after checking spam, filtering, and corporate security settings.
- The email address has been verified as correct.
- Corporate email filtering has been ruled out.
- Password-reset emails cannot be received after repeated troubleshooting.
- Automation appears to trigger correctly but expected emails consistently do not arrive.
- Ticket-related notifications that should be generated by the applicable configuration are consistently missing.
- Subscription-related emails are not received after verifying the account email and mailbox settings.

When contacting support, provide enough information to help investigate the issue without sharing sensitive authentication information.

> **Security warning:** Never provide your FlowDesk password, API token, or other authentication secrets to FlowDesk support.

---

## 10. Troubleshooting Decision Table

| Symptom                                                    | Possible Cause                                          | Recommended Action                                                                             |
| ---------------------------------------------------------- | ------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| Password-reset email is missing                            | Message was filtered or email address is incorrect      | Verify the account email, check spam/junk, search the mailbox, and request another reset email |
| FlowDesk email is in spam                                  | Email provider classified the message as unwanted       | Move or mark the message as legitimate according to your email provider                        |
| Email is not found anywhere in the mailbox                 | Delivery delay or temporary delivery problem            | Wait a reasonable amount of time, then retry the applicable action                             |
| Ticket notification is missing                             | Notification may not be configured for the event        | Verify that the notification is expected, then check the recipient email and mailbox filters   |
| Automation `send_email` action does not result in an email | Incorrect trigger, recipient, or workflow configuration | Verify the trigger, `send_email` action, and recipient address                                 |
| Corporate users do not receive FlowDesk emails             | Corporate filtering or quarantine                       | Ask the email administrator to check filtering and quarantine systems                          |
| Several unrelated FlowDesk emails are missing              | Broader email delivery problem                          | Verify mailbox and corporate filtering, then contact FlowDesk support if the problem persists  |
| Reset link from an older email no longer works             | Reset link has expired or a newer request was made      | Request a new password-reset email and use the newest link                                     |

---

## 11. Frequently Asked Questions

### Why didn't I receive my FlowDesk email?

The email may have been delayed, filtered into spam or junk, sent to an incorrect address, blocked by a corporate email system, or affected by a temporary delivery problem. Start by verifying the email address and checking your mailbox filters.

### Where should I look if a FlowDesk email is missing?

Check your inbox, spam or junk folder, quarantine area if available, archived folders, and mailbox search results. Also review any personal filtering rules.

### How long should I wait before requesting another email?

Allow a reasonable amount of time for the message to arrive before retrying the action. If the message still does not arrive, repeat the applicable action, such as requesting another password-reset email.

### What should I do if I receive multiple password-reset emails?

Use the newest password-reset email. Older reset links may no longer be valid.

### Why did my ticket notification not arrive?

First verify that the particular ticket event is expected to generate a notification under your configuration. Then verify the recipient email address and check spam, mailbox filters, and corporate email security systems.

### My FlowDesk automation uses `send_email`, but the email was not received. What should I check?

Verify that the expected trigger occurred, the automation includes the `send_email` action, and the configured recipient address is correct. Then check the recipient mailbox and any corporate filtering or quarantine systems.

### Can my company's email security system block FlowDesk emails?

Yes. Corporate email systems may filter, quarantine, delay, or block messages. Ask your organization's email administrator to check its email security and quarantine systems.

### When should I contact FlowDesk support?

Contact support when multiple FlowDesk emails are consistently missing, the email address is confirmed to be correct, mailbox and corporate filtering have been ruled out, or a specific email problem persists after completing the relevant troubleshooting steps.
