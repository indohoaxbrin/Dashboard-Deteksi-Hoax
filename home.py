import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

# Caching data loading
@st.cache_data
def load_data():
    df = pd.read_csv("mafindo_mix_llm.csv")
    return df

# Caching WordCloud generation
@st.cache_resource
def generate_wordcloud(text, colormap, stopwords):
    wordcloud = WordCloud(width=500, height=200, background_color='white', colormap=colormap, stopwords=stopwords).generate(text)
    return wordcloud

def show_home():
    # Load the dataset
    df = load_data()

    # Convert 'Tanggal' to datetime
    df['Tanggal'] = pd.to_datetime(df['Tanggal'], format='%d/%m/%Y')
    df['Year'] = df['Tanggal'].dt.year

    # Convert text columns to string to avoid type errors
    df['Content'] = df['Content'].astype(str)

    # Define additional stopwords
    additional_stopwords = {"dan", "di", "yang", "ke", "dari", "untuk", "pada", "adalah", "sebuah", "dengan", "tersebut", "ini", "itu", "atau", "dalam", "juga", "adalah", "yg", "tapi"}

    # Combine default stopwords with additional stopwords
    combined_stopwords = set(STOPWORDS).union(additional_stopwords)


    # Row with 4 visualizations
    col1, col2, col3, col4 = st.columns([1.5, 2.5, 1.5, 2.5])

    # Visualization 1: Bar chart for Hoax vs Non-Hoax using Plotly
    with col1:
        st.markdown("<h6 style='font-size: 14px; margin-bottom: 0;'>Hoax vs Non-Hoax</h6>", unsafe_allow_html=True)
        df_label_counts = df['Label'].value_counts().reset_index()
        df_label_counts.columns = ['Label', 'Jumlah']
        bar_chart_label = px.bar(df_label_counts, x='Label', y='Jumlah', color='Label',
                                color_discrete_map={'HOAX': 'red', 'NON-HOAX': 'green'})
        bar_chart_label.update_layout(
            width=200, height=150, xaxis_title='Label', yaxis_title='Jumlah',
            xaxis_title_font_size=10, yaxis_title_font_size=10,
            xaxis_tickfont_size=8, yaxis_tickfont_size=8, margin=dict(t=10, b=10, l=10, r=10),
            showlegend=False
        )
        st.plotly_chart(bar_chart_label, use_container_width=False)

    # Visualization 2: Bar chart for Hoax vs Non-Hoax per Data Source using Plotly
    with col2:
        st.markdown("<h6 style='font-size: 14px; margin-bottom: 0;'>Hoax vs Non-Hoax per Data Source</h6>", unsafe_allow_html=True)
        datasource_label_counts = df.groupby(['Datasource', 'Label']).size().reset_index(name='counts')
        fig_datasource = px.bar(datasource_label_counts, x='Datasource', y='counts', color='Label', barmode='group',
                               color_discrete_map={'HOAX': 'red', 'NON-HOAX': 'green'})
        fig_datasource.update_layout(
            width=500, height=150, xaxis_title='Datasource', yaxis_title='Jumlah',
            xaxis_title_font_size=10, yaxis_title_font_size=10,
            xaxis_tickfont_size=6, yaxis_tickfont_size=8, xaxis_tickangle=0,
            margin=dict(t=10, b=10, l=10, r=50),
            legend=dict(
                font=dict(size=8),  # Smaller font size for the legend
                traceorder='normal',
                orientation='v',  # Vertical orientation of the legend
                title_text='Label',  # Title for the legend
                yanchor='top', y=1, xanchor='left', x=1.05,  # Adjust position of the legend
                bgcolor='rgba(255, 255, 255, 0)',  # Transparent background for legend
                bordercolor='rgba(0, 0, 0, 0)'  # No border color
            ),
            showlegend=True
        )
        st.plotly_chart(fig_datasource, use_container_width=False)
    
    # Visualization 3: Line chart for Hoax per Year using Plotly
    with col3:
        st.markdown("<h6 style='font-size: 14px; margin-bottom: 0;'>Hoax per Tahun</h6>", unsafe_allow_html=True)
    
    # Filter data to include only years up to 2023
        hoax_per_year = df[(df['Label'] == 'HOAX') & (df['Year'] <= 2023)].groupby('Year').size().reset_index(name='count')
    
        line_chart_hoax = px.line(hoax_per_year, x='Year', y='count', line_shape='linear',
                              color_discrete_sequence=['red'])
        line_chart_hoax.update_layout(
            width=200, height=150, xaxis_title='Tahun', yaxis_title='Jumlah Hoax',
            xaxis_title_font_size=10, yaxis_title_font_size=10,
            xaxis_tickfont_size=8, yaxis_tickfont_size=8, margin=dict(t=10, b=10, l=10, r=10),
            showlegend=False
        )
        st.plotly_chart(line_chart_hoax, use_container_width=False)

    
    # Visualization 4: Bar chart for Topics per Year using Plotly
    with col4:
        st.markdown("<h6 style='font-size: 14px; margin-bottom: 0;'>Topik per Tahun</h6>", unsafe_allow_html=True)
        df['Tanggal'] = pd.to_datetime(df['Tanggal'], format='%d/%m/%Y')
        df['Year'] = df['Tanggal'].dt.year

        # Filter the data to include only years up to 2023
        df_mafindo_filtered = df[df['Year'] <= 2023]

        topics_per_year = df_mafindo_filtered.groupby(['Year', 'Topic']).size().reset_index(name='count')

        # Create the vertical bar chart
        bar_chart_topics = px.bar(topics_per_year, x='Year', y='count', color='Topic',
                                  color_continuous_scale=px.colors.sequential.Viridis)

        # Update layout to adjust the legend
        bar_chart_topics.update_layout(
            width=600, height=150, xaxis_title='Tahun', yaxis_title='Jumlah Topik',
            xaxis_title_font_size=10, yaxis_title_font_size=10,
            xaxis_tickfont_size=8, yaxis_tickfont_size=8, margin=dict(t=10, b=10, l=10, r=10),
            showlegend=True,
            legend=dict(
                yanchor="top", y=1, xanchor="left", x=1.02,  # Adjust position of the legend
                bgcolor='rgba(255, 255, 255, 0)',  # Transparent background for legend
                bordercolor='rgba(0, 0, 0, 0)',  # No border color
                itemclick='toggleothers',  # Allow toggling of legend items
                itemsizing='constant',  # Consistent sizing for legend items
                font=dict(size=8),
                traceorder='normal',
                orientation='v',  # Vertical orientation of legend
                title_text='Topic'
            )
        )

        st.plotly_chart(bar_chart_topics, use_container_width=True)

        
    # Create a new row for WordCloud visualizations
    col5, col6, col7 = st.columns([2, 2.5, 2.5])

    # Wordcloud for Hoax
    with col5:
        st.markdown("<h6 style='font-size: 14px; margin-bottom: 0;'>Wordcloud for Hoax</h6>", unsafe_allow_html=True)
        hoax_text = ' '.join(df[df['Label'] == 'HOAX']['Content'])
        wordcloud_hoax = generate_wordcloud(hoax_text, 'Reds', combined_stopwords)
        fig_hoax = plt.figure(figsize=(5, 2.5))
        plt.imshow(wordcloud_hoax, interpolation='bilinear')
        plt.axis('off')
        st.pyplot(fig_hoax)
    
    with col6:
        st.markdown("<h6 style='font-size: 14px; margin-bottom: 0;'>Klasifikasi</h6>", unsafe_allow_html=True)
        df_classification_counts = df['Classification'].value_counts().reset_index()
        df_classification_counts.columns = ['Classification', 'Count']
    
        # Create the donut chart
        donut_chart_classification = px.pie(df_classification_counts, names='Classification', values='Count', 
                                        hole=0.3, color_discrete_sequence=px.colors.qualitative.Set2)
    
        # Update layout to move the legend and adjust its size
        donut_chart_classification.update_layout(
            width=300, height=170,  # Adjust the size of the chart
            margin=dict(t=20, b=20, l=20, r=120),  # Adjust margins to make room for the legend
            legend=dict(
                yanchor="top", y=1, xanchor="left", x=1.07,  # Adjust position of the legend
                bgcolor='rgba(255, 255, 255, 0)',  # Transparent background for legend
                bordercolor='rgba(0, 0, 0, 0)',  # No border color
                itemclick='toggleothers',  # Allow toggling of legend items
                itemsizing='constant',  # Consistent sizing for legend items
                font=dict(size=8),  # Smaller font size for the legend
                traceorder='normal',
                orientation='v',  # Vertical legend
                title_text='Classification'  # Title for the legend
            )
        )
        st.plotly_chart(donut_chart_classification, use_container_width=True)

    with col7:
        st.markdown("<h6 style='font-size: 14px; margin-bottom: 0;'>Tone</h6>", unsafe_allow_html=True)
        df_tone_counts = df['Tone'].value_counts().reset_index()
        df_tone_counts.columns = ['Tone', 'Count']
    
        # Create the donut chart
        donut_chart_tone = px.pie(df_tone_counts, names='Tone', values='Count', 
                                        hole=0.3, color_discrete_sequence=px.colors.qualitative.Set2)
    
        # Update layout to move the legend and adjust its size
        donut_chart_tone.update_layout(
            width=250, height=170,  # Adjust the size of the chart
            margin=dict(t=20, b=20, l=20, r=100),  # Adjust margins to make room for the legend
            legend=dict(
                yanchor="top", y=1, xanchor="left", x=1.07,  # Adjust position of the legend
                bgcolor='rgba(255, 255, 255, 0)',  # Transparent background for legend
                bordercolor='rgba(0, 0, 0, 0)',  # No border color
                itemclick='toggleothers',  # Allow toggling of legend items
                itemsizing='constant',  # Consistent sizing for legend items
                font=dict(size=8),  # Smaller font size for the legend
                traceorder='normal',
                orientation='v',  # Vertical legend
                title_text='Tone'  # Title for the legend
            )
        )
        st.plotly_chart(donut_chart_tone, use_container_width=True)

    col8, col9 = st.columns([5, 1.5])
        
    # Evaluation Metrics Table
    data = [
        ["indobenchmark/indobert-base-p2", 0.6898, 0.9793, 0.8094, 0.8400, 0.1981, 0.3206, 0.7023],
        ["cahya/bert-base-indonesian-522M", 0.7545, 0.8756, 0.8106, 0.6800, 0.4811, 0.5635, 0.7358],
        ["indolem/indobert-base-uncased", 0.7536, 0.8238, 0.7871, 0.6136, 0.5094, 0.5567, 0.7124],
        ["mdhugol/indonesia-bert-sentiment-classification", 0.7444, 0.8601, 0.7981, 0.6447, 0.4623, 0.5385, 0.7191]
    ]

    highest_accuracy = max(data, key=lambda x: x[-1])

    # Header Table
    html_table = """
    <table style="width:100%; border-collapse: collapse; font-size: 12px; border-top: 1px solid black; border-bottom: 1px solid black;">
    <tr style="border-bottom: 1px solid black; text-align: center; border-top: 1px solid black;">
        <th rowspan="2" style="border: none; padding: 5px; font-size: 14px; text-align: left; border-top: 1px solid black;">Pre-trained Model</th>
        <th colspan="3" style="border: none; padding: 5px; font-size: 14px; text-align: center; border-top: 1px solid black;">NON-HOAX</th>
        <th colspan="3" style="border: none; padding: 5px; font-size: 14px; text-align: center; border-top: 1px solid black;">HOAX</th>
        <th rowspan="2" style="border: none; padding: 5px; font-size: 14px; text-align: center; border-top: 1px solid black;">Accuracy</th>
    </tr>
    <tr style="border-bottom: 1px solid black;">
        <th style="border: none; padding: 5px; font-size: 12px; width:80px; text-align: center;">Precision</th>
        <th style="border: none; padding: 5px; font-size: 12px; width:80px; text-align: center;">Recall</th>
        <th style="border: none; padding: 5px; font-size: 12px; width:80px; text-align: center;">F1-Score</th>
        <th style="border: none; padding: 5px; font-size: 12px; width:80px; text-align: center;">Precision</th>
        <th style="border: none; padding: 5px; font-size: 12px; width:80px; text-align: center;">Recall</th>
        <th style="border: none; padding: 5px; font-size: 12px; width:80px; text-align: center;">F1-Score</th>
    </tr>
    """

    # Isi Data
    for row in data:
        formatted_row = [f"{item:.4f}" if isinstance(item, float) else item for item in row]
        if row == highest_accuracy:
            html_table += "<tr style='background-color: #FC9576; font-size: 12px; text-align: center; border: 1px solid transparent;'>"
        else:
            html_table += "<tr style='font-size: 12px; text-align: center; border: 1px solid transparent;'>"
    
        # Left-align the first column (Pre-trained Model)
        html_table += f"<td style='border: none; padding: 5px; text-align: left; font-size: 12px;'>{row[0]}</td>"
    
        # Center-align the rest of the columns
        for item in formatted_row[1:]:
            html_table += f"<td style='border: none; padding: 5px; text-align: center; font-size: 12px;'>{item}</td>"
    
        html_table += "</tr>"

    # Add a border to the last row
    html_table += "<tr style='border-top: 1px solid black;'></tr>"

    html_table += "</table>"

    # Tampilkan Tabel di Streamlit
    with col8:
        st.markdown("<h6 style='font-size: 14px; margin-bottom: 0;'>Matriks Evaluasi</h6>", unsafe_allow_html=True)
        st.markdown(html_table, unsafe_allow_html=True)
        

        html_table_col9 = """
        <table style="width:100%; border-collapse: collapse; font-size: 12px;">
            <thead>
                <tr style="border-top: 1.5px solid #B2BABB; border-bottom: 1.5px solid #B2BABB;"> 
                    <th style="padding: 8px; border: 1px solid transparent; font-weight: bold; background-color: #f2f2f2; text-align: left;">Label</th>
                    <th style="padding: 8px; border: 1px solid transparent; font-weight: bold; background-color: #f2f2f2; text-align: center;">Train</th>
                    <th style="padding: 8px; border: 1px solid transparent; font-weight: bold; background-color: #f2f2f2; text-align: center;">Test</th>
                    <th style="padding: 8px; border: 1px solid transparent; font-weight: bold; background-color: #f2f2f2; text-align: center;">Dev</th>
                </tr>
            </thead>
            <tbody>
                <tr style="border-bottom: 1px solid transparent;">
                    <td style="padding: 8px; border: 1px solid transparent; background-color: #f2f2f2;">HOAX</td>
                    <td style="padding: 8px; border: 1px solid transparent; background-color: #f2f2f2; text-align: center;">11.563</td>
                    <td style="padding: 8px; border: 1px solid transparent; background-color: #f2f2f2; text-align: center;">193</td>
                    <td style="padding: 8px; border: 1px solid transparent; background-color: #f2f2f2; text-align: center;">193</td>
                </tr>
                <tr style="border-bottom: 1px solid black;">
                    <td style="padding: 8px; border: 1px solid transparent; background-color: #f2f2f2;">NON-HOAX</td>
                    <td style="padding: 8px; border: 1px solid transparent; background-color: #f2f2f2; text-align: center;">789</td>
                    <td style="padding: 8px; border: 1px solid transparent; background-color: #f2f2f2; text-align: center;">106</td>
                    <td style="padding: 8px; border: 1px solid transparent; background-color: #f2f2f2; text-align: center;">106</td>
                </tr>
                <tr style="font-weight: bold; border-top: 1px solid transparent; border-bottom: 1.5px solid #B2BABB;">
                    <td style="padding: 8px; border: 1px solid transparent; background-color: #f2f2f2;">TOTAL</td>
                    <td style="padding: 8px; border: 1px solid transparent; background-color: #f2f2f2; text-align: center;">12,352</td>
                    <td style="padding: 8px; border: 1px solid transparent; background-color: #f2f2f2; text-align: center;">299</td>
                    <td style="padding: 8px; border: 1px solid transparent; background-color: #f2f2f2; text-align: center;">299</td>
                </tr>
            </tbody>
        </table>
        """

# Display the table in col9 using HTML
    with col9:
        st.markdown("<h6 style='font-size: 14px; margin-bottom: 0;'>Statistik Data</h6>", unsafe_allow_html=True)
        st.markdown(html_table_col9, unsafe_allow_html=True)