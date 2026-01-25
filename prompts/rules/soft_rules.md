# Soft Rules - Preferred Guidelines

## Code Quality Preferences

### Rule: Type Hints
- **Preference**: Use type hints for all function signatures
- **Example**: `def process_data(items: List[str]) -> Dict[str, Any]:`
- **Priority**: HIGH

### Rule: Documentation
- **Preference**: Include docstrings for all public functions
- **Format**: Google-style or NumPy-style
- **Priority**: MEDIUM

### Rule: Error Handling
- **Preference**: Use try-except blocks with specific exceptions
- **Avoid**: Bare except clauses
- **Priority**: HIGH

### Rule: Testing
- **Preference**: Write tests for all new functionality
- **Coverage**: Aim for 80%+ coverage
- **Priority**: MEDIUM

## Response Quality

### Rule: Clarity
- **Preference**: Use clear, concise language
- **Avoid**: Unnecessary jargon without explanation
- **Priority**: HIGH

### Rule: Completeness
- **Preference**: Provide complete solutions when possible
- **Avoid**: Partial code snippets without context
- **Priority**: HIGH

### Rule: Examples
- **Preference**: Include working examples
- **Format**: Code blocks with comments
- **Priority**: MEDIUM

## Prompt Engineering

### Rule: Specificity
- **Preference**: Be specific about requirements
- **Include**: Input format, output format, constraints
- **Priority**: HIGH

### Rule: Context
- **Preference**: Provide relevant context
- **Include**: Domain knowledge, user background
- **Priority**: MEDIUM

### Rule: Iteration
- **Preference**: Allow for iterative refinement
- **Include**: Feedback mechanism
- **Priority**: LOW
