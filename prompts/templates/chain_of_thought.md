# Chain of Thought Template

Use this template for step-by-step reasoning:

```
## Question: {{ question }}

### Reasoning Process

**Step 1: Understand the Question**
- What is being asked?
- What are the key components?
- What is the expected output format?

**Step 2: Identify Relevant Knowledge**
- What do I already know about this topic?
- What information do I need to look up?
- What assumptions am I making?

**Step 3: Break Down the Problem**
- List the sub-problems
- Identify dependencies between sub-problems
- Determine the order of solving

**Step 4: Solve Each Sub-problem**
1. {{ first sub-problem }}
   - Analysis: {{ your reasoning }}
   - Solution: {{ your answer }}
   - Confidence: {{ high/medium/low }}

2. {{ second sub-problem }}
   - Analysis: {{ your reasoning }}
   - Solution: {{ your answer }}
   - Confidence: {{ high/medium/low }}

**Step 5: Combine Solutions**
- How do the sub-solutions fit together?
- Are there any conflicts?
- What is the overall solution?

**Step 6: Verify the Answer**
- Does it answer the original question?
- Are there edge cases?
- Is the answer consistent with known facts?

## Final Answer
{{ your synthesized answer }}

## Confidence Level
{{ high/medium/low }} - {{ justification }}
```

## Example

```
Question: What is the capital of Australia?

Step 1: Understand
- Asking for capital city
- Australia is a country
- Need specific city name

Step 2: Relevant Knowledge
- I know Australia is in Oceania
- Capital is not Sydney (largest city)
- Canberra is the capital

Step 3: Break Down
- Only one answer needed
- No sub-problems

Step 4: Solve
- Canberra is Australia's capital since 1927

Step 5: Combine
- Single fact: Canberra

Step 6: Verify
- Matches known facts
- Canberra is correct

Final Answer: Canberra

Confidence: High - Well-established fact
```
