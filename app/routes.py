import os
from flask import current_app as app
from flask import render_template
from analytics import (
    load_data,
    generate_monthly_sales_chart,
    generate_sales_by_country_chart,
    generate_top_products_chart,
    generate_customer_retention_chart,
    generate_aov_chart,
    generate_top_customers_chart,
    generate_sales_growth_chart,
    generate_customer_acquisition_retention_chart,
    generate_sales_by_hour_chart,
    generate_sales_heatmap,
    generate_sales_by_category_chart,
    generate_customer_segmentation_chart
)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    print("Current Working Directory:", os.getcwd())

    base_dir = os.path.abspath(os.path.dirname(__file__))
    data_file = os.path.join(base_dir, 'data/online_retail.csv')
    print("Data file path:", data_file)

    df, error = load_data(data_file)
    if error:
        return error, 404

    graph1_html = generate_monthly_sales_chart(df)
    graph2_html, uk_sales = generate_sales_by_country_chart(df)
    graph3_html = generate_top_products_chart(df)
    graph5_html = generate_customer_retention_chart(df)
    graph6_html = generate_aov_chart(df)
    graph7_html = generate_top_customers_chart(df)
    graph8_html = generate_customer_acquisition_retention_chart(df)
    graph9_html = generate_sales_by_hour_chart(df)
    graph10_html = generate_sales_by_category_chart(df)

    return render_template(
        'dashboard.html',
        graph1_html=graph1_html,
        graph2_html=graph2_html,
        graph3_html=graph3_html,
        graph5_html=graph5_html,
        graph6_html=graph6_html,
        graph7_html=graph7_html,
        graph8_html=graph8_html,
        graph9_html=graph9_html,
        graph10_html=graph10_html,
    )

@app.route('/heatmap')
def heatmap_page():
    print("Current Working Directory:", os.getcwd())

    base_dir = os.path.abspath(os.path.dirname(__file__))
    data_file = os.path.join(base_dir, 'data/online_retail.csv')
    print("Data file path:", data_file)

    df, error = load_data(data_file)
    if error:
        return error, 404

    graph_html = generate_sales_heatmap(df)

    return render_template(
        'heatmap_page.html',
        graph_html=graph_html
    )

@app.route('/customer_segmentation')
def customer_segmentation():
    print("Current Working Directory:", os.getcwd())

    base_dir = os.path.abspath(os.path.dirname(__file__))
    data_file = os.path.join(base_dir, 'data/online_retail.csv')
    print("Data file path:", data_file)

    df, error = load_data(data_file)
    if error:
        return error, 404

    graph_html = generate_customer_segmentation_chart(df)

    return render_template(
        'customer_segmentation.html',
        graph_html=graph_html
    )