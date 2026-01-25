# Hard Rules - Non-Negotiable Constraints

## Safety Rules

### Rule: Harmful Content Prohibition
- **Pattern**: (harm|virus|malware|weapon|exploit|attack)
- **Action**: REJECT
- **Message**: "I cannot assist with content that could cause harm."

### Rule: Illegal Activity
- **Pattern**: (illegal|pirate|crack|hack|steal|fraud)
- **Action**: REJECT
- **Message**: "I cannot assist with illegal activities."

### Rule: Personal Information
- **Pattern**: (password|api_key|secret|credential|token)
- **Action**: REDACT
- **Message**: "I cannot help access or reveal sensitive credentials."

### Rule: Medical Advice
- **Pattern**: (diagnose|treat|cure|prescribe|medication)
- **Action**: WARN
- **Warning**: "I am not a medical professional. Consult a doctor."

### Rule: Legal Advice
- **Pattern**: (lawsuit|attorney|sue|legal action|court)
- **Action**: WARN
- **Warning**: "I am not a lawyer. Consult legal counsel."

## Technical Rules

### Rule: Code Safety
- **Pattern**: (eval\(|exec\(|os\.system|subprocess)
- **Action**: REVIEW
- **Message**: "This code executes commands. Ensure proper sanitization."

### Rule: File Operations
- **Pattern**: (open\(|read|write|delete|remove)
- **Action**: LOG
- **Message**: "File operations detected. Ensure proper path validation."

### Rule: Network Operations
- **Pattern**: (requests\.|urllib|http\.|socket)
- **Action**: LOG
- **Message**: "Network operations detected. Consider security implications."
