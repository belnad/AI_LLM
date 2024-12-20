import streamlit as st
import pandas as pd
from io import StringIO
import asyncio
from pipline import run_news_workflow  # Import the backend function

# Function to process the query using the backend
async def process_query_with_backend(query, theme, location):
    filters = {}
    if theme != "All":
        filters["category"] = theme
    if location:
        filters["location"] = location
    return await run_news_workflow(query, filters)

# Helper function to run the async function in a synchronous Streamlit environment
def process_query(query, theme, location):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    results = loop.run_until_complete(process_query_with_backend(query, theme, location))
    return results

# Streamlit app
st.title("Article Summarizer and Categorizer")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Results"])

# Session state initialization
if "query" not in st.session_state:
    st.session_state.query = ""
    st.session_state.theme = "All"
    st.session_state.location = ""

# Home Page
if page == "Home":
    st.header("Enter Your Query")

    # User input section
    query = st.text_input("Enter your query", placeholder="Type your query here...")
    theme = st.selectbox("Filter by theme (optional)", ["All", "Politics", "Health"])
    location = st.text_input("Filter by location (optional)", placeholder="Enter a location...")

    if st.button("Process"):
        # Store the inputs to session state
        st.session_state.query = query
        st.session_state.theme = theme
        st.session_state.location = location

        # Navigate to Results page
        st.header("Results")

        if st.session_state.query:
            query = st.session_state.query
            theme = st.session_state.theme
            location = st.session_state.location

            # Fetch results using the backend
            try:
                results = process_query(query, theme, location)

                # Display results
                if results:
                    for result in results:
                        st.subheader(result["title"])
                        st.write(f"**Summary**: {result['summary']}")
                        st.write(f"**Sentiment**: {result['sentiment']}")
                        st.write(f"**Source**: {st.page_link(result['url'], label=result['source'], icon='🌎')}")
                        st.write("---")

                    # Export results
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
            except Exception as e:
                st.error(f"An error occurred while processing the query: {e}")
        else:
            st.write("Please process a query from the Home page first.")
