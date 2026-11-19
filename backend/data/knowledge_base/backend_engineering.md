# Backend Engineering — starter study notes

## HTTP and REST API design
An API exposes resources through predictable routes and HTTP methods. GET retrieves data, POST creates or triggers processing, PUT or PATCH updates data, and DELETE removes a resource. Use appropriate status codes, validate request bodies, return consistent error structures, and avoid exposing internal exception details. Pagination and filtering help keep responses manageable.

## Service separation
A maintainable backend separates routing, validation, business logic, persistence, and integrations. Route handlers should coordinate work rather than contain all business rules. Service functions make workflows testable, while repository or ORM code manages persistence. Configuration and secrets belong in environment variables rather than source code.

## Relational databases and transactions
Relational databases represent data in tables connected by keys. Primary keys identify rows and foreign keys enforce relationships. Transactions group operations so they succeed or fail as a unit. ACID describes atomicity, consistency, isolation, and durability. Indexes can speed up reads but add storage and write overhead, so they should support actual query patterns.

## Authentication and authorization
Authentication establishes who a user is; authorization determines what that user may do. Passwords should be stored using a dedicated password hashing algorithm, never as plain text. Protected endpoints should validate credentials and enforce role or ownership checks on every relevant request. Sensitive tokens should not be logged.

## Caching and reliability
Caching stores frequently used results to reduce latency and load. Cache invalidation is difficult because data may change while a cached copy remains. Reliability also depends on timeouts, bounded retries, idempotency for retried operations, structured logging, and health checks. Retries should use backoff and should not blindly repeat non-idempotent actions.

## Testing and deployment
Unit tests validate small functions, integration tests verify interactions between components, and end-to-end tests exercise user workflows. Containers package an application and its runtime dependencies. Environment-specific configuration should be externalized, and deployments should include health checks and observable logs.
