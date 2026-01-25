# Skill: Code Generation

## Description
Generates high-quality, production-ready code across multiple programming languages with proper structure, error handling, and documentation.

## Capabilities
- Algorithm implementation
- Data structure design
- API development
- Framework-specific code
- Code refactoring and optimization
- Unit test generation
- Code documentation

## Supported Languages
- Python, JavaScript, TypeScript
- Java, C++, Go
- Rust, Swift, Kotlin
- SQL, HTML/CSS, Shell scripts

## Prompt Template

```
You are an expert {{ language }} developer.

Task: {{ task_description }}

Context:
- Language: {{ language }}
- Framework: {{ framework | default: "none" }}
- Complexity: {{ complexity | default: "intermediate" }}
- Requirements: {{ requirements | default: "none" }}

{% if existing_code %}
Existing code context:
{{ existing_code }}
{% endif %}

{% if examples %}
Reference examples:
{{ examples }}
{% endif %}

Provide:
1. Complete, working code solution
2. Explanation of the approach
3. Time and space complexity analysis
4. Test cases (if applicable)

Code should:
- Follow {{ language }} best practices
- Include proper error handling
- Be well-commented and documented
- Be ready for production use
```

## Few-Shot Examples

### Example 1: Binary Search
**Input**: "Implement binary search in Python"
**Output**: Complete implementation with comments, complexity analysis, and test cases

### Example 2: REST API
**Input**: "Create a REST API endpoint for user authentication in Node.js"
**Output**: Express.js route with JWT authentication, validation, and error handling

## Evaluation Metrics
- Code correctness (unit test pass rate): target > 95%
- Code quality (linting scores): target > 8/10
- Performance efficiency (time/space): optimal complexity
- Security (vulnerability scanning): no critical issues

## Error Handling
- Validate all inputs
- Handle edge cases
- Provide meaningful error messages
- Log errors appropriately
