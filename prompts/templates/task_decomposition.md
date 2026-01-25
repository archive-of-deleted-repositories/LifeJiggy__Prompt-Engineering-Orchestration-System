# Task Decomposition Template

Use this template for breaking down complex tasks:

```
## Task: {{ task_name }}

### Step 1: Understanding
- **Objective**: {{ what needs to be accomplished }}
- **Constraints**: {{ limitations and requirements }}
- **Success Criteria**: {{ how to measure completion }}

### Step 2: Decomposition
**Subtasks**:
1. {{ first subtask }}
   - Input: {{ what it needs }}
   - Output: {{ what it produces }}
   - Dependencies: {{ what it depends on }}

2. {{ second subtask }}
   - Input: {{ what it needs }}
   - Output: {{ what it produces }}
   - Dependencies: {{ what it depends on }}

3. {{ third subtask }}
   - Input: {{ what it needs }}
   - Output: {{ what it produces }}
   - Dependencies: {{ what it depends on }}

### Step 3: Execution Order
1. {{ independent task or first dependency }}
2. {{ task with resolved dependencies }}
3. {{ task with all dependencies met }}
4. {{ final integration }}

### Step 4: Validation
- [ ] Subtask 1 complete
- [ ] Subtask 2 complete
- [ ] Subtask 3 complete
- [ ] Integration tested
- [ ] Quality checks passed
```

## Example

```
Task: Build a REST API for user management

Step 1: Understanding
- Objective: Create CRUD API for users
- Constraints: Python/FastAPI, PostgreSQL
- Success Criteria: All endpoints working, tests passing

Step 2: Decomposition
1. Database setup
   - Input: Schema design
   - Output: User table
   - Dependencies: None

2. API endpoints
   - Input: Database model
   - Output: CRUD endpoints
   - Dependencies: Database ready

3. Authentication
   - Input: User model, endpoints
   - Output: Protected routes
   - Dependencies: Endpoints ready

Step 3: Execution Order
1. Database setup
2. API endpoints
3. Authentication
4. Testing

Step 4: Validation
- [x] Database setup complete
- [x] Endpoints implemented
- [ ] Auth integrated
- [ ] Tests passing
```
