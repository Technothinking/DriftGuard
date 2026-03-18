from jinja2 import Template

def generate_html_report(results, drift_score, top_features, output_path="reports/drift_report.html"):
    
    template_str = """
    <html>
    <head>
        <title>Drift Report</title>
        <style>
            body { font-family: Arial; padding: 20px; }
            h1 { color: #333; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ccc; padding: 10px; text-align: center; }
            th { background-color: #f4f4f4; }
            .drift { background-color: #ffcccc; }
            .no-drift { background-color: #ccffcc; }
        </style>
    </head>
    <body>
        <h1>📊 Drift Analysis Report</h1>
        <table>
            <tr>
                <th>Feature</th>
                <th>Type</th>
                <th>PSI</th>
                <th>P-Value</th>
                <th>Drift</th>
            </tr>

            {% for feature, res in results.items() %}
            <tr class="{{ 'drift' if res.drift else 'no-drift' }}">
                <td>{{ feature }}</td>
                <td>{{ res.type }}</td>
                <td>{{ res.psi if res.psi is defined else '-' }}</td>
                <td>{{ res.p_value }}</td>
                <td>{{ res.drift }}</td>
            </tr>
            {% endfor %}
        </table>

        <h2>📊 Overall Drift Score</h2>
        <p><b>Score:</b> {{ drift_score.score }} ({{ drift_score.level }})</p>

        <h2>🚨 Alerts</h2>
        <ul>
        {% for alert in alerts %}
        <li>{{ alert }}</li>
        {% endfor %}
        </ul>

        <h2>🔥 Top Drift Drivers</h2>
        <ul>
        {% for f, s in top_features %}
        <li>{{ f }} (impact: {{ s }})</li>
        {% endfor %}
        </ul>
    </body>
    </html>
    """

    template = Template(template_str)
    html = template.render(results=results)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)