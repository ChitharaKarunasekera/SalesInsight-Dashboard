import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def load_data(file_path):
    try:
        df = pd.read_csv(file_path, encoding='ISO-8859-1')
    except FileNotFoundError as e:
        return None, f"File not found: {e}"

    df.dropna(subset=['CustomerID'], inplace=True)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['CustomerID'] = df['CustomerID'].astype(str)
    df.drop_duplicates(inplace=True)
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']

    return df, None


def generate_monthly_sales_chart(df):
    monthly_sales = df.set_index('InvoiceDate').resample('M')['TotalPrice'].sum()

    fig = px.line(
        monthly_sales,
        x=monthly_sales.index,
        y='TotalPrice',
        title='Monthly Sales',
        labels={'TotalPrice': 'Total Sales', 'InvoiceDate': 'Date'},
        markers=True
    )

    fig.add_trace(
        go.Scatter(
            x=monthly_sales.index,
            y=monthly_sales.rolling(window=3).mean(),
            mode='lines',
            line=dict(dash='dash', color='firebrick'),
            name='3-Month Rolling Average'
        )
    )

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Total Sales',
        hovermode='x unified',
        template='plotly_white'
    )

    return fig.to_html(full_html=False)


def generate_sales_by_country_chart(df):
    sales_by_country = df.groupby('Country')['TotalPrice'].sum().sort_values(ascending=False)
    uk_sales = sales_by_country.loc['United Kingdom']
    sales_by_country = sales_by_country.drop('United Kingdom').head(10)

    fig = px.bar(
        sales_by_country,
        x=sales_by_country.index,
        y='TotalPrice',
        title='Sales by Country (excluding UK)',
        color=sales_by_country.index
    )

    fig.update_layout(
        xaxis_title='Country',
        yaxis_title='Total Sales',
        xaxis_tickangle=-45
    )

    return fig.to_html(full_html=False), uk_sales


def generate_top_products_chart(df):
    top_products = df.groupby('Description')['TotalPrice'].sum().sort_values(ascending=False).head(10)

    fig = px.bar(
        top_products,
        x=top_products.values,
        y=top_products.index,
        orientation='h',
        title='Top 10 Products by Sales'
    )

    return fig.to_html(full_html=False)


def generate_customer_retention_chart(df):
    repeat_customers = df.groupby('CustomerID').filter(lambda x: len(x) > 1)
    retention_rate = len(repeat_customers['CustomerID'].unique()) / len(df['CustomerID'].unique()) * 100

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=retention_rate,
        title={'text': "Customer Retention Rate (%)"},
        gauge={'axis': {'range': [None, 100]}}
    ))

    return fig.to_html(full_html=False)


def generate_aov_chart(df):
    aov = df.groupby(df['InvoiceDate'].dt.to_period('M'))['TotalPrice'].mean()

    fig = px.line(
        aov,
        x=aov.index.astype(str),
        y='TotalPrice',
        title='Average Order Value (AOV) Over Time'
    )

    return fig.to_html(full_html=False)


def generate_top_customers_chart(df):
    top_customers = df.groupby('CustomerID')['TotalPrice'].sum().sort_values(ascending=False).head(10)

    fig = px.bar(
        top_customers,
        x=top_customers.values,
        y=top_customers.index,
        orientation='h',
        title='Top 10 Customers by Sales'
    )

    return fig.to_html(full_html=False)

# #####################################################################################################
def generate_sales_growth_chart(df):
    monthly_sales = df.set_index('InvoiceDate').resample('M')['TotalPrice'].sum()
    monthly_growth = monthly_sales.pct_change().dropna() * 100

    fig = px.line(
        monthly_growth,
        x=monthly_growth.index,
        y='TotalPrice',
        title='Monthly Sales Growth Rate',
        labels={'TotalPrice': 'Growth Rate (%)', 'InvoiceDate': 'Date'},
        markers=True
    )

    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Growth Rate (%)',
        hovermode='x unified',
        template='plotly_white'
    )

    return fig.to_html(full_html=False)


def generate_customer_acquisition_retention_chart(df):
    df['InvoiceDateMonth'] = df['InvoiceDate'].dt.to_period('M')

    customer_acquisition = df.groupby('InvoiceDateMonth')['CustomerID'].nunique()
    repeat_customers = df.groupby('CustomerID').filter(lambda x: len(x) > 1)
    customer_retention = repeat_customers.groupby(repeat_customers['InvoiceDate'].dt.to_period('M'))[
        'CustomerID'].nunique()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=customer_acquisition.index.astype(str),
            y=customer_acquisition,
            mode='lines+markers',
            name='Customer Acquisition'
        )
    )
    fig.add_trace(
        go.Scatter(
            x=customer_retention.index.astype(str),
            y=customer_retention,
            mode='lines+markers',
            name='Customer Retention'
        )
    )

    fig.update_layout(
        title='Customer Acquisition and Retention Over Time',
        xaxis_title='Date',
        yaxis_title='Number of Customers',
        hovermode='x unified',
        template='plotly_white'
    )

    return fig.to_html(full_html=False)


def generate_sales_by_hour_chart(df):
    df['Hour'] = df['InvoiceDate'].dt.hour
    sales_by_hour = df.groupby('Hour')['TotalPrice'].sum()

    fig = px.bar(
        sales_by_hour,
        x=sales_by_hour.index,
        y='TotalPrice',
        title='Sales Distribution by Hour',
        labels={'TotalPrice': 'Total Sales', 'Hour': 'Hour of Day'}
    )

    fig.update_layout(
        xaxis_title='Hour of Day',
        yaxis_title='Total Sales',
        template='plotly_white'
    )

    return fig.to_html(full_html=False)


def generate_sales_heatmap(df):
    df['Month'] = df['InvoiceDate'].dt.month
    sales_heatmap = df.pivot_table(index='Country', columns='Month', values='TotalPrice', aggfunc='sum').fillna(0)

    # Normalize the data
    sales_heatmap_normalized = sales_heatmap.apply(lambda x: x / x.max(), axis=1)

    # Apply a log scale to the color axis to better visualize differences
    fig = px.imshow(
        sales_heatmap_normalized,
        labels=dict(x="Month", y="Country", color="Total Sales (normalized)"),
        x=sales_heatmap_normalized.columns,
        y=sales_heatmap_normalized.index,
        title='Sales Heatmap by Country and Month'
    )

    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Country',
        template='plotly_white',
        coloraxis_colorbar=dict(
            title="Total Sales (normalized)",
            tickvals=[0, 0.2, 0.4, 0.6, 0.8, 1],
            ticktext=['0', '0.2', '0.4', '0.6', '0.8', '1']
        )
    )

    # Apply color transformation to the color scale
    fig.update_coloraxes(colorscale='Viridis')

    return fig.to_html(full_html=False)


def generate_sales_by_category_chart(df):
    # Example categorization by first word in description; you might have better category data
    df['ProductCategory'] = df['Description'].apply(lambda x: x.split()[0] if pd.notnull(x) else 'Unknown')
    sales_by_category = df.groupby('ProductCategory')['TotalPrice'].sum().sort_values(ascending=False).head(10)

    fig = px.bar(
        sales_by_category,
        x=sales_by_category.index,
        y='TotalPrice',
        title='Sales by Product Category',
        labels={'TotalPrice': 'Total Sales', 'ProductCategory': 'Category'}
    )

    fig.update_layout(
        xaxis_title='Product Category',
        yaxis_title='Total Sales',
        template='plotly_white'
    )

    return fig.to_html(full_html=False)


# $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
def generate_customer_segmentation_chart(df):
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    # Prepare data for clustering
    customer_data = df.groupby('CustomerID').agg({
        'TotalPrice': 'sum',
        'InvoiceNo': 'count',
        'InvoiceDate': lambda x: (df['InvoiceDate'].max() - x.max()).days
    }).reset_index()
    customer_data.columns = ['CustomerID', 'TotalSpent', 'Frequency', 'Recency']

    # Standardize data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(customer_data[['TotalSpent', 'Frequency', 'Recency']])

    # K-means clustering
    kmeans = KMeans(n_clusters=4, random_state=42)
    customer_data['Cluster'] = kmeans.fit_predict(scaled_data)

    fig = px.scatter_3d(customer_data, x='Recency', y='Frequency', z='TotalSpent', color='Cluster', title='Customer Segmentation')
    fig.update_layout(template='plotly_white')

    return fig.to_html(full_html=False)