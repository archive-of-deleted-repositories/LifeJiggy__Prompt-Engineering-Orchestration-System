# Complex Reasoning Example

## Problem Statement
Design and implement a rate limiting system for a web API that handles different types of requests differently.

## Solution Walkthrough

### Step 1: Understand Requirements
- Identify types of requests (read, write, admin)
- Determine limits per type
- Consider user tiers (free, premium, enterprise)
- Plan for burst handling

### Step 2: Design the Architecture
```
Components:
1. Token Bucket per user/request-type
2. Sliding window counter
3. Redis for distributed state
4. Middleware for integration
```

### Step 3: Implementation Plan
1. Create token bucket class
2. Implement sliding window logic
3. Add Redis integration
4. Build API middleware
5. Write unit tests

### Step 4: Edge Cases
- What happens at midnight (daily reset)?
- How to handle distributed systems?
- What if Redis is unavailable?
- How to handle burst traffic?

### Step 5: Testing Strategy
- Unit tests for each component
- Integration tests for Redis
- Load tests for performance
- Chaos tests for failures

## Expected Output
Complete rate limiting system with:
- [x] Token bucket implementation
- [x] Sliding window counter
- [x] Redis-based distributed state
- [x] API middleware
- [x] Comprehensive tests
- [x] Documentation
