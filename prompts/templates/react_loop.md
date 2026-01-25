# ReAct (Reasoning + Acting) Template

Use this template for interactive problem solving:

```
## Task: {{ task_description }}

### Thought-Action-Observation Loop

**Iteration 1**
- **Thought**: {{ what you're thinking about the current state }}
- **Action**: {{ tool you're going to use }}
- **Action Input**: {{ parameters for the tool }}
- **Observation**: {{ result of the action }}

**Iteration 2**
- **Thought**: {{ what you learned from the observation }}
- **Action**: {{ next tool to use }}
- **Action Input**: {{ parameters for the tool }}
- **Observation**: {{ result of the action }}

...

**Final Answer**
{{ synthesized answer based on all observations }}
```

## Example

```
Task: Find the file mentioned in the README

Iteration 1
- Thought: I need to first find and read the README file
- Action: read_file
- Action Input: {"filepath": "README.md"}
- Observation: README mentions "See config/settings.py for details"

Iteration 2
- Thought: The README references config/settings.py, let me read it
- Action: read_file
- Action Input: {"filepath": "config/settings.py"}
- Observation: File contains database configuration with DB_NAME="production.db"

Iteration 3
- Thought: I found the database name is "production.db", let me verify this file exists
- Action: search_files
- Action Input: {"pattern": "**/production.db"}
- Observation: No matches found

Iteration 4
- Thought: The database file doesn't exist yet, it's just a configuration
- Action: None (task complete)
- Observation: Task complete

Final Answer: The README references config/settings.py which defines DB_NAME="production.db". This is a configuration file that specifies the database name, but the actual database file may not exist yet.
```

## Template for Tool Selection

```
## Tool Selection Criteria

1. **What information do I need?**
   - File content → read_file
   - Directory listing → list_directory
   - Find files → search_files
   - Create content → write_file

2. **What format is best?**
   - Text data → Return as string
   - Structured data → Return as JSON
   - Binary data → Return as base64

3. **What constraints apply?**
   - Read-only → Use read/search tools
   - Path validation → Automatic
   - Permissions → Handled by server
```
