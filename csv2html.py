import pandas as pd
import argparse
import sys

def create_google_charts_html(df, key_column, data_columns, output_file='output.html'):
    """
    Generates an HTML file with Google Charts based on pass/fail data in a DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame.
        key_column (str): The name of the column to group by.
        data_columns (list): A list of column names with 'pass'/'fail' data.
        output_file (str): The name of the HTML file to generate.
    """
    # --- 1. Data Processing ---
    # Calculate pass percentages for each data column, grouped by the key column.
    chart_data = {}
    for col in data_columns:
        # Calculate total entries per key
        total = df.groupby(key_column)[col].count()
        # Calculate 'pass' entries per key
        passes = df[df[col].str.lower() == 'pass'].groupby(key_column)[col].count()
        
        # Combine into a single DataFrame
        summary_df = pd.DataFrame({'total': total, 'passes': passes}).fillna(0)
        
        # Calculate percentage. Avoid division by zero.
        summary_df['percentage'] = (summary_df['passes'] / summary_df['total'] * 100).fillna(0)
        
        # Convert the processed data to a list format for Google Charts
        # Format: [['Key', 'Pass Percentage'], ['Value1', 75.0], ['Value2', 88.0]]
        data_list = [[key_column, 'Pass Percentage']]
        data_list.extend(summary_df[['percentage']].reset_index().values.tolist())
        chart_data[col] = data_list

    # --- 2. HTML Generation ---
    # Start building the HTML string
    html_content = """
<html>
<head>
    <title>CSV Data Charts</title>
    <!-- Load Google Charts library -->
    <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
    <script type="text/javascript">
      google.charts.load('current', {'packages':['corechart', 'bar']});
"""

    # --- 3. JavaScript for Charts ---
    # Generate a drawChart function for each data column
    for i, col in enumerate(data_columns):
        chart_id = f"chart_div_{i}"
        data_array_string = str(chart_data[col])

        html_content += f"""
      google.charts.setOnLoadCallback(draw_{col.replace(' ', '_')}_Chart);

      function draw_{col.replace(' ', '_')}_Chart() {{
        var data = google.visualization.arrayToDataTable({data_array_string});

        var options = {{
          title: 'Pass Percentage for {col}',
          chartArea: {{width: '60%'}},
          hAxis: {{
            title: 'Pass Percentage',
            minValue: 0,
            maxValue: 100
          }},
          vAxis: {{
            title: '{key_column}'
          }},
          bars: 'horizontal',
          legend: {{ position: "none" }}
        }};

        var chart = new google.visualization.BarChart(document.getElementById('{chart_id}'));
        chart.draw(data, options);
      }}
"""
    
    html_content += """
    </script>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; padding: 20px; }
        .chart-container { 
            width: 90%; 
            max-width: 800px;
            height: 400px; 
            margin: 40px auto;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 { text-align: center; color: #333; }
    </style>
</head>
<body>
    <h1>Data Analysis Report</h1>
"""

    # --- 4. HTML Divs for Charts ---
    # Create a div element for each chart to be rendered in
    for i, col in enumerate(data_columns):
        chart_id = f"chart_div_{i}"
        html_content += f'<div id="{chart_id}" class="chart-container"></div>\n'

    html_content += """
</body>
</html>
"""

    # --- 5. Write to File ---
    try:
        with open(output_file, 'w') as f:
            f.write(html_content)
        print(f"✅ Successfully generated chart file: {output_file}")
    except IOError as e:
        print(f"❌ Error writing to file {output_file}: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main function to parse arguments and run the script."""
    parser = argparse.ArgumentParser(
        description="Create an HTML file with Google Charts from a CSV file.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("csv_file", help="The path to the input CSV file.")
    parser.add_argument("key_column", help="The column to use as the key for summarizing data.")
    parser.add_argument("data_columns", nargs='+', help="One or more data columns containing 'pass'/'fail' values.")
    parser.add_argument("-o", "--output", default="charts.html", help="The name of the output HTML file (default: charts.html).")

    args = parser.parse_args()

    # --- File and Column Validation ---
    try:
        df = pd.read_csv(args.csv_file)
    except FileNotFoundError:
        print(f"❌ Error: The file '{args.csv_file}' was not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading or parsing CSV file: {e}", file=sys.stderr)
        sys.exit(1)

    required_columns = [args.key_column] + args.data_columns
    for col in required_columns:
        if col not in df.columns:
            print(f"❌ Error: Column '{col}' not found in the CSV file.", file=sys.stderr)
            print(f"Available columns are: {list(df.columns)}", file=sys.stderr)
            sys.exit(1)

    create_google_charts_html(df, args.key_column, args.data_columns, args.output)


if __name__ == "__main__":
    main()
