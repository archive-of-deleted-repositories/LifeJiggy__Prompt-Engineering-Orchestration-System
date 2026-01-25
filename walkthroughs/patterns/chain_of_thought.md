"""Chain-of-thought prompting guide."""

chain_of_thought = """
# Chain of Thought Prompting

Chain-of-thought (CoT) prompting is a technique that encourages the model to show its reasoning process step by step.

## When to Use

- Complex multi-step problems
- Mathematical calculations
- Logical reasoning tasks
- Decision making with multiple factors
- Debugging and analysis

## Structure

```
Question: [complex question]

Let's think step by step:
1. First, identify what is being asked
2. Break down the problem into smaller parts
3. Analyze each part systematically
4. Combine insights to form a solution
5. Verify the answer makes sense

Answer: [reasoned answer]
```

## Example

**Question:** If a train leaves New York at 8 AM traveling 60 mph, and another train leaves Boston at 10 AM traveling 80 mph, and the distance is 200 miles, when will they meet?

**Chain-of-Thought:**
1. Train A (NY) starts at 8 AM at 60 mph
2. Train B (Boston) starts at 10 AM at 80 mph
3. By 10 AM, Train A has traveled 2 hours * 60 mph = 120 miles
4. Remaining distance: 200 - 120 = 80 miles
5. Combined speed: 60 + 80 = 140 mph
6. Time to meet: 80 miles / 140 mph = 0.57 hours ≈ 34 minutes
7. 10 AM + 34 minutes = 10:34 AM

**Answer:** 10:34 AM

## Best Practices

1. **Explicit Instructions**: Always say "Let's think step by step"
2. **Number Steps**: Use numbered steps for clarity
3. **Intermediate Checks**: Verify each step before proceeding
4. **Complete All Steps**: Don't skip logical connections
5. **Final Verification**: Check if answer makes sense
"""

tree_of_thoughts = """
# Tree of Thoughts Prompting

Tree-of-thoughts (ToT) prompting extends CoT by exploring multiple reasoning paths simultaneously.

## When to Use

- Problems with multiple valid approaches
- Creative problem solving
- Strategic planning
- Code generation with multiple solutions
- Negotiation and game theory scenarios

## Structure

```
Question: [complex question]

Let's explore multiple approaches:

Branch 1: [Approach 1]
- Step 1.1: [reasoning]
- Step 1.2: [reasoning]
- Result: [outcome]

Branch 2: [Approach 2]
- Step 2.1: [reasoning]
- Step 2.2: [reasoning]
- Result: [outcome]

Branch 3: [Approach 3]
- Step 3.1: [reasoning]
- Step 3.2: [reasoning]
- Result: [outcome]

Comparison and Evaluation:
- Strengths of each approach
- Weaknesses of each approach
- Best choice and reasoning

Final Answer: [selected solution]
```

## Example

**Question:** How should a company decide between building, buying, or partnering for a new technology?

**Branch 1 - Build:**
- Control over technology ✓
- Higher initial cost ✗
- Takes time to develop ✗
- Team learning ✓

**Branch 2 - Buy:**
- Faster time to market ✓
- Immediate functionality ✓
- Vendor dependency ✗
- Integration challenges ✗

**Branch 3 - Partner:**
- Shared risk ✓
- Combined expertise ✓
- Complex negotiations ✗
- Shared control ✗

**Evaluation:** For critical core technology, build makes sense. For non-core capabilities, partner or buy depending on timeline.

**Final Answer:** [recommended approach with justification]
"""

reflexion = """
# Reflexion Prompting

Reflexion adds self-critique and revision to the reasoning process.

## When to Use

- Tasks requiring high accuracy
- Creative writing with specific requirements
- Code generation with multiple iterations
- Complex analysis requiring validation
- Learning from mistakes

## Structure

```
Task: [description]

Initial Attempt:
[initial solution]

Self-Critique:
- What works well?
- What could be improved?
- What is missing or incorrect?

Revision based on critique:
[improved solution]

Final Check:
[verification of improvements]

Final Answer: [revised solution]
```

## Example

**Task:** Write a function to validate email addresses.

**Initial Attempt:**
```python
def validate_email(email):
    return '@' in email
```

**Self-Critique:**
- ✗ Too simple - allows 'a@b'
- ✗ Doesn't check for valid domain format
- ✗ No length validation
- ✗ Doesn't handle whitespace
- ✗ No TLD requirement

**Revision:**
```python
import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))
```

**Final Check:**
- ✓ Checks username format
- ✓ Validates domain
- ✓ Requires TLD
- ✓ Handles whitespace
- ✓ Pattern is comprehensive

**Final Answer:** [revised implementation with tests]
"""
