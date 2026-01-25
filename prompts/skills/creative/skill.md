# Skill: Creative Writing

## Description
Generates engaging, original creative content across various formats including stories, marketing copy, and narrative content.

## Capabilities
- Blog posts and articles
- Marketing copy and ad content
- Technical documentation
- Creative fiction and storytelling
- Email campaigns
- Social media content

## Writing Styles
- Professional/technical
- Creative/fiction
- Marketing/persuasive
- Educational/instructional
- Conversational/casual

## Prompt Template

```
You are a creative writing expert.

Task: {{ task_description }}

Style Guidelines:
- Tone: {{ tone | default: "professional" }}
- Voice: {{ voice | default: "engaging" }}
- Length: {{ length | default: "medium" }}
- Audience: {{ audience | default: "general" }}

{% if examples %}
Reference style examples:
{{ examples }}
{% endif %}

{% if constraints %}
Constraints:
{{ constraints }}
{% endif %}

Provide:
1. Main content following the style guidelines
2. Alternative opening/closing options
3. Key points covered
4. Call to action (if applicable)

Focus on:
- Engaging narrative flow
- Appropriate voice and tone
- Clear messaging
- Audience relevance
```

## Evaluation Metrics
- Content engagement: reader interest and retention
- Style consistency: adherence to guidelines
- Creativity: originality and uniqueness
- Clarity: ease of understanding
- Conversion: goal achievement (for marketing)

## Common Use Cases
- Blog content creation
- Marketing campaigns
- Product descriptions
- Email newsletters
- Social media posts
- Video scripts
