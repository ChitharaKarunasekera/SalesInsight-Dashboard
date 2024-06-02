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
    # Group by Country and sum the TotalPrice
    sales_by_country = df.groupby('Country')['TotalPrice'].sum().sort_values(ascending=False)

    # Check if 'United Kingdom' is in the data
    if 'United Kingdom' in sales_by_country.index:
        uk_sales = sales_by_country.loc['United Kingdom']
        sales_by_country = sales_by_country.drop('United Kingdom')
    else:
        uk_sales = None

    # Take the top 10 countries excluding UK
    top_countries = sales_by_country.head(10)

    # Create the bar chart
    fig = px.bar(
        top_countries,
        x=top_countries.index,
        y='TotalPrice',
        title='Sales by Country (excluding UK)' if uk_sales else 'Sales by Country',
        color=top_countries.index,
        color_discrete_sequence=px.colors.qualitative.Bold
    )

    fig.update_layout(
        xaxis_title='Country',
        yaxis_title='Total Sales',
        xaxis_tickangle=-45,
        template='plotly_white',
        hovermode='x unified'
    )

    # Add dropdown menu for dynamic country selection
    fig.update_layout(
        updatemenus=[
            {
                'buttons': [
                    {
                        'label': 'Top 5 Countries',
                        'method': 'update',
                        'args': [{'y': [sales_by_country.head(5).values], 'x': [sales_by_country.head(5).index]},
                                 {'title': 'Top 5 Countries', 'coloraxis': {'colorscale': 'Viridis'}}]
                    },
                    {
                        'label': 'Top 10 Countries',
                        'method': 'update',
                        'args': [{'y': [sales_by_country.head(10).values], 'x': [sales_by_country.head(10).index]},
                                 {'title': 'Top 10 Countries', 'coloraxis': {'colorscale': 'Viridis'}}]
                    },
                    {
                        'label': 'Top 15 Countries',
                        'method': 'update',
                        'args': [{'y': [sales_by_country.head(15).values], 'x': [sales_by_country.head(15).index]},
                                 {'title': 'Top 15 Countries', 'coloraxis': {'colorscale': 'Viridis'}}]
                    }
                ],
                'direction': 'down',
                'showactive': True,
            }
        ]
    )

    return fig.to_html(full_html=False), uk_sales


def generate_top_products_chart(df):
    top_products = df.groupby('Description')['TotalPrice'].sum().sort_values(ascending=False).head(10)

    fig = px.bar(
        top_products,
        x=top_products.values,
        y=top_products.index,
        orientation='h',
        title='Top 10 Products by Sales',
        labels={'x': 'Total Sales', 'y': 'Product'},
        color=top_products.values,
        color_continuous_scale='Viridis'
    )

    fig.update_layout(
        xaxis_title='Total Sales',
        yaxis_title='Product',
        template='plotly_white',
        hovermode='y unified',
        coloraxis_showscale=False
    )

    fig.update_traces(
        marker_line_color='black',
        marker_line_width=1.5,
        opacity=0.8
    )


    return fig.to_html(full_html=False)

def generate_customer_retention_chart(df):
    # Filter repeat customers
    repeat_customers = df.groupby('CustomerID').filter(lambda x: len(x) > 1)
    # Calculate retention rate
    retention_rate = len(repeat_customers['CustomerID'].unique()) / len(df['CustomerID'].unique()) * 100

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=retention_rate,
        title={'text': "Customer Retention Rate (%)"},
        delta={'reference': 50, 'increasing': {'color': '#FFC96F'}, 'decreasing': {'color': '#FF8080'}},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#7286D3"},
            'steps': [
                {'range': [0, 25], 'color': "#FF8080"},
                {'range': [25, 50], 'color': "#FFCF81"},
                {'range': [50, 75], 'color': "#FFC96F"},
                {'range': [75, 100], 'color': "#BFF6C3"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': 50
            }
        }
    ))

    return fig.to_html(full_html=False)



def generate_aov_chart(df):
    aov = df.groupby(df['InvoiceDate'].dt.to_period('M'))['TotalPrice'].mean()
    aov.index = aov.index.to_timestamp()  # Convert PeriodIndex to Timestamp for Plotly compatibility

    fig = px.line(
        aov,
        x=aov.index,
        y='TotalPrice',
        title='Average Order Value (AOV) Over Time',
        labels={'TotalPrice': 'Average Order Value', 'index': 'Date'},
        markers=True
    )

    # Add trendline using rolling mean
    rolling_mean = aov.rolling(window=3).mean()
    fig.add_trace(go.Scatter(
        x=rolling_mean.index,
        y=rolling_mean,
        mode='lines',
        name='3-Month Rolling Average',
        line=dict(dash='dash', color='firebrick')
    ))

    # Customize layout
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Average Order Value',
        hovermode='x unified',
        template='plotly_white',
        legend=dict(
            x=0.01,
            y=0.99,
            bgcolor='rgba(255, 255, 255, 0)',
            bordercolor='rgba(255, 255, 255, 0)'
        ),
        annotations=[
            dict(
                x=aov.index[0],
                y=aov.max(),
                xref="x",
                yref="y",
                text="Highest AOV",
                showarrow=True,
                arrowhead=7,
                ax=0,
                ay=-40
            )
        ]
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
        labels={'TotalPrice': 'Total Sales', 'Hour': 'Hour of Day'},
        color=sales_by_hour.index,
        color_continuous_scale=px.colors.sequential.Cividis  # Changed color palette to Cividis
    )

    fig.update_layout(
        xaxis_title='Hour of Day',
        yaxis_title='Total Sales',
        template='plotly_white',
        coloraxis_showscale=False
    )

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
def generate_rfm_analysis_chart(df):
    df['Recency'] = (df['InvoiceDate'].max() - df['InvoiceDate']).dt.days
    rfm = df.groupby('CustomerID').agg({
        'Recency': 'min',
        'InvoiceNo': 'count',
        'TotalPrice': 'sum'
    }).reset_index()
    rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']

    fig = px.scatter(rfm, x='Recency', y='Monetary', size='Frequency', color='Monetary', title='RFM Analysis')
    fig.update_layout(template='plotly_white')

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


def generate_cohort_analysis_chart(df):
    df['OrderPeriod'] = df['InvoiceDate'].dt.to_period('M')
    df['CohortGroup'] = df.groupby('CustomerID')['InvoiceDate'].transform('min').dt.to_period('M')

    cohort_data = df.groupby(['CohortGroup', 'OrderPeriod']).agg({
        'CustomerID': 'nunique'
    }).reset_index()
    cohort_data['CohortPeriod'] = (cohort_data['OrderPeriod'] - cohort_data['CohortGroup']).apply(attrgetter('n'))

    cohort_pivot = cohort_data.pivot_table(index='CohortGroup', columns='CohortPeriod', values='CustomerID')

    fig = px.imshow(cohort_pivot, aspect='auto', color_continuous_scale='Viridis', title='Cohort Analysis')
    fig.update_layout(xaxis_title='Cohort Period', yaxis_title='Cohort Group', template='plotly_white')

    return fig.to_html(full_html=False)