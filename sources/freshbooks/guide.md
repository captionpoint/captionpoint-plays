# FreshBooks

REST API access to Matt's FreshBooks account, focused on **invoicing** workflows across multiple businesses.

## Scope

- **Primary use:** invoicing — create, view, send, and track invoices
- **Multiple businesses:** Matt has more than one business on the account. Every invoice/client call requires an `account_id` (the business identifier). Confirm which business before mutating data.
- Secondary: clients (list, create, update) — needed to attach invoices

## Authentication

OAuth 2.0. Tokens are auto-refreshed by Craft Agent. If auth breaks, re-run `source_oauth_trigger({ sourceSlug: "freshbooks" })`.

## Businesses (account_id reference)

Matt owns two businesses on this FreshBooks account. Use the right `account_id` for the right business — **wrong account = wrong books**.

| Business | `account_id` | `business_id` | Timezone | Industry |
|---|---|---|---|---|
| Bivins Brothers Creative | `B15w` | 675904 | America/Chicago | Creative Professionals |
| CaptionPoint | `zgwdBW` | 2361042 | America/New_York | Arts and Entertainment |

**Default:** If Matt doesn't specify, ask which business. Don't assume.

To re-verify or check for new businesses: `GET auth/api/v1/users/me` → `response.business_memberships[].business`.

## API Reference

Base URL: `https://api.freshbooks.com/`

### Identity
- `GET auth/api/v1/users/me` — current user + business memberships (use to discover `account_id`)

### Invoices
- `GET accounting/account/{account_id}/invoices/invoices` — list invoices
  - Query params: `search[customerid]`, `search[status]`, `page`, `per_page`, `include[]=lines`
- `GET accounting/account/{account_id}/invoices/invoices/{invoice_id}` — single invoice
- `POST accounting/account/{account_id}/invoices/invoices` — create invoice
  - Body shape: `{ "invoice": { "customerid": <id>, "create_date": "YYYY-MM-DD", "lines": [{"name": "...", "qty": 1, "unit_cost": {"amount": "100.00", "code": "USD"}}] } }`
- `PUT accounting/account/{account_id}/invoices/invoices/{invoice_id}` — update invoice
- `PUT accounting/account/{account_id}/invoices/invoices/{invoice_id}` with `{"invoice": {"action_email": true}}` — send invoice
- `PUT accounting/account/{account_id}/invoices/invoices/{invoice_id}` with `{"invoice": {"vis_state": 1}}` — archive (0=active, 1=deleted, 2=archived)

### Clients
- `GET accounting/account/{account_id}/users/clients` — list clients
- `GET accounting/account/{account_id}/users/clients/{client_id}` — single client
- `POST accounting/account/{account_id}/users/clients` — create client
  - Body: `{ "client": { "email": "...", "fname": "...", "lname": "...", "organization": "..." } }`

## Guidelines

- **Always confirm `account_id`** before any write — wrong business = wrong books.
- Amounts use the `{"amount": "100.00", "code": "USD"}` shape, not bare numbers.
- Dates are `YYYY-MM-DD`.
- Rate limits: ~30 requests per 30 seconds per token. Batch reads where possible.
- Invoice status values: `draft`, `sent`, `viewed`, `paid`, `partial`, `disputed`, `overdue`, etc.
- The API nests responses under `response.result` for most endpoints — drill in when parsing.

## Examples

**List unpaid invoices for a business:**
```
GET accounting/account/{account_id}/invoices/invoices?search[status]=sent&search[status]=overdue&search[status]=viewed
```

**Create a draft invoice:**
```
POST accounting/account/{account_id}/invoices/invoices
{
  "invoice": {
    "customerid": 12345,
    "create_date": "2026-06-03",
    "lines": [
      {"name": "Web development", "qty": 10, "unit_cost": {"amount": "125.00", "code": "USD"}}
    ]
  }
}
```
