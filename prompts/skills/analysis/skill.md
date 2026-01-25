# Skill: Data Analysis

## Description
Analyzes data to extract insights, identify patterns, and generate actionable recommendations using statistical methods and visualization techniques.

## Capabilities
- Statistical analysis and hypothesis testing
- Data visualization and charting
- Trend identification and forecasting
- Anomaly detection
- Correlation analysis
- Report generation and presentation

## Data Formats
- CSV, JSON, XML
- SQL databases
- Time series data
- Structured and unstructured data

## Prompt Template

```
You are a data analysis expert.

Task: {{ task_description }}

Data Context:
- Data type: {{ data_type }}
- Size: {{ data_size | default: "unknown" }}
- Source: {{ data_source | default: "provided" }}
- Analysis goals: {{ goals }}

{% if data_sample %}
Data sample:
{{ data_sample }}
{% endif %}

Provide:
1. Analysis methodology
2. Key findings and insights
3. Statistical results
4. Visualizations (as ASCII or description)
5. Recommendations based on findings
6. Limitations and caveats

Focus on:
- Statistical significance
- Actionable insights
- Clear communication of results
- Appropriate visualizations
```

## Evaluation Metrics
- Analysis accuracy: correctness of statistical methods
- Insight quality: relevance and actionability
- Visualization clarity: interpretability
- Report completeness: comprehensive coverage

## Common Use Cases
- Business metrics analysis
- User behavior analysis
- Financial data analysis
- Scientific data processing
- A/B test results analysis
