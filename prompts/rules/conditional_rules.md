# Conditional Rules - Context-Dependent Logic

## User Level Rules

### Rule: Expert User
- **Condition**: `user_level == "expert"`
- **Action**: 
  - Skip basic explanations
  - Use technical terminology
  - Provide concise answers
- **Example**: "Assume deep knowledge of the domain"

### Rule: Beginner User
- **Condition**: `user_level == "beginner"`
- **Action**:
  - Include step-by-step explanations
  - Define technical terms
  - Provide analogies
- **Example**: "Explain like I'm new to programming"

## Task Type Rules

### Rule: Code Generation
- **Condition**: `task_type == "code_generation"`
- **Action**:
  - Include error handling
  - Add comments
  - Consider edge cases
  - Follow language best practices

### Rule: Analysis Task
- **Condition**: `task_type == "analysis"`
- **Action**:
  - Present multiple perspectives
  - Include evidence and reasoning
  - Acknowledge limitations

### Rule: Creative Writing
- **Condition**: `task_type == "creative"`
- **Action**:
  - Focus on engaging content
  - Adapt tone to audience
  - Use vivid language

## Safety Level Rules

### Rule: High Safety Context
- **Condition**: `safety_level == "high"`
- **Action**:
  - Add additional disclaimers
  - Avoid risky suggestions
  - Include warnings

### Rule: Production Code
- **Condition**: `environment == "production"`
- **Action**:
  - Prioritize security
  - Include logging
  - Add error tracking
  - Consider performance

## Language Rules

### Rule: Non-English Request
- **Condition**: `language != "en"`
- **Action**:
  - Respond in the requested language
  - Use appropriate cultural context
  - Adapt examples

### Rule: Code Comments
- **Condition**: `code_language in ["python", "javascript", "java"]`
- **Action**:
  - Add inline comments
  - Explain complex logic
