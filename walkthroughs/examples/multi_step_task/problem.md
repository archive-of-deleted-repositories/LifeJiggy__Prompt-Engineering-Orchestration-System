# Multi-Step Task Example

## Problem Statement
Build a complete feature: User notification system with email and SMS support.

## Solution Walkthrough

### Step 1: Requirements Analysis
1. Identify notification types (email, SMS)
2. Define user preferences
3. Set up delivery tracking
4. Plan error handling

### Step 2: Database Design
- Users table: id, email, phone, preferences
- Notifications table: id, user_id, type, content, status
- Logs table: id, notification_id, timestamp, status

### Step 3: Backend Implementation
1. Create notification service
2. Implement email provider integration
3. Implement SMS provider integration
4. Add retry logic
5. Set up webhooks for delivery status

### Step 4: API Development
- POST /notifications - Send notification
- GET /notifications/:id - Get status
- PUT /preferences - Update preferences
- GET /preferences - Get preferences

### Step 5: Testing
1. Unit tests for service layer
2. Integration tests for API
3. Mock provider tests
4. Load testing

## Expected Deliverables
- [x] Database schema
- [x] Notification service
- [x] Email integration
- [x] SMS integration
- [x] REST API
- [x] Unit tests (90% coverage)
- [x] Integration tests
- [x] Documentation
