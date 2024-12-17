import streamlit as st
import pandas as pd
from io import StringIO

# Mock function to simulate LLM processing
def mock_process(query: str):
    return [
        {
            "title": "Article 1",
            "category": "Politics",
            "sentiment": "Positive",
            "summary": "This is a brief summary of Article 1. It discusses political events in the USA.",
            "location": "USA",
            "source": "Source A"
        },
        {
            "title": "Article 2",
            "category": "Health",
            "sentiment": "Negative",
            "summary": "Summary of Article 2, focusing on health concerns related to the UK.",
            "location": "UK",
            "source": "Source B"
        }
    ]

# Streamlit app
st.title("Article Summarizer and Categorizer")

# Sidebar for navigation
page = st.sidebar.radio("Select a page", ["Home", "Results"])

# Home Page: User Input
if page == "Home":
    st.header("Enter Your Query")

    # User input section
    query = st.text_input("Enter your query", placeholder="Type your query here...")
    theme = st.selectbox("Filter by theme (optional)", ["All", "Politics", "Health"])
    location = st.text_input("Filter by location (optional)", placeholder="Enter a location...")

    if st.button("Process"):
        # Store the inputs to be used on the Results page
        st.session_state.query = query
        st.session_state.theme = theme
        st.session_state.location = location
        
        # Redirect to the Results page
        #st.sidebar.radio("Select a page", ["Home", "Results"], index=1)

# Results Page: Displaying Results
elif page == "Results":
    st.header("Results")

    # Check if session state has data from the Home page
    if "query" in st.session_state:
        query = st.session_state.query
        theme = st.session_state.theme
        location = st.session_state.location
        
        results = mock_process(query)
        
        # Apply filters
        if theme != "All":
            results = [r for r in results if r["category"].lower() == theme.lower()]
        if location:
            results = [r for r in results if r["location"].lower() == location.lower()]
        
        if results:
            # Display results: Titles and Summaries
            for result in results:
                st.subheader(result["title"])  # Display the title
                st.write(result["summary"])    # Display the summary
            
            # Option to download results
            export_format = st.radio("Export format", ["JSON", "CSV"])
            if st.button("Download"):
                df = pd.DataFrame(results)
                if export_format == "JSON":
                    st.download_button(
                        label="Download JSON",
                        data=df.to_json(orient="records", indent=4),
                        file_name="results.json",
                        mime="application/json"
                    )
                elif export_format == "CSV":
                    csv = StringIO()
                    df.to_csv(csv, index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv.getvalue(),
                        file_name="results.csv",
                        mime="text/csv"
                    )
        else:
            st.write("No results found for the given filters.")
    else:
        st.write("Please process a query from the Home page first.")
