import streamlit as st
import pandas as pd
from io import StringIO
import asyncio
from pipline import run_news_workflow  # Import the backend function to process requests


# Asynchronous function to process a query with filters using the backend
async def process_query_with_backend(query, theme, location):
    filters = {}
    # Apply a category filter if it is not "All"
    if theme != "All":
        filters["category"] = theme
    # Apply a location filter if it is not "All"
    if location != "All":
        filters["country"] = location
    # Call the backend function with the query and filters
    return await run_news_workflow(query, filters)


# Helper function to execute an asynchronous call in a synchronous Streamlit environment
def process_query(query, theme, location):
    # Create an asynchronous event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    # Run the asynchronous function synchronously
    results = loop.run_until_complete(process_query_with_backend(query, theme, location))
    return results


# Set the title of the Streamlit application
st.title("Article Summarizer and Categorizer")

# Sidebar for navigation
st.sidebar.title("Navigation")
# Navigation options: "Home" page or "Results" page
page = st.sidebar.radio("Go to", ["Home", "Results"])

# Initialize session state to store user data
if "query" not in st.session_state:
    st.session_state.query = ""  # User query
    st.session_state.theme = "All"  # Selected theme
    st.session_state.location = ""  # Selected location

# Home Page
if page == "Home":
    st.header("Enter Your Query")  # Page header

    # Section for user input
    query = st.text_input("Enter your query", placeholder="Type your query here...")
    # Dropdown menu to filter by category (optional)
    theme = st.selectbox(
        "Filter by theme (optional)",
        ["All", "business", "entertainment", "general", "health", "science", "sports", "technology"]
    )
    # Dropdown menu to filter by location (optional)
    location = st.selectbox("Filter by location (optional)", ["All", "us", "uk", "fr"])

    # Button to process the query
    if st.button("Process"):
        # Store user inputs in session state
        st.session_state.query = query
        st.session_state.theme = theme
        st.session_state.location = location

        # Display result
        st.header("Results")

        # Check if a valid query is provided
        if st.session_state.query:
            # Retrieve stored user inputs from session state
            query = st.session_state.query
            theme = st.session_state.theme
            location = st.session_state.location

            # Fetch results from the backend
            try:
                results = process_query(query, theme, location)  # Call the async processing function

                # Display the results, if available
                if results:
                    for result in results:
                        # Display the article title
                        st.subheader(result["title"])
                        # Display a summary of the article
                        st.write(f"**Summary**: {result['summary']}")
                        # Display the sentiment detected for the article
                        st.write(f"**Sentiment**: {result['sentiment']}")
                        # Provide a link to the source of the article
                        st.write(f"**Source**: {st.page_link(result['url'], label=result['source'], icon='🌎')}")
                        st.write("---")  # Separator between results

                    # Options to export the results in different formats
                    export_format = st.radio("Export format", ["JSON", "CSV"])
                    if st.button("Download"):
                        # Convert results into a Pandas DataFrame
                        df = pd.DataFrame(results)
                        # Export results as JSON
                        if export_format == "JSON":
                            st.download_button(
                                label="Download JSON",
                                data=df.to_json(orient="records", indent=4),
                                file_name="results.json",
                                mime="application/json"
                            )
                        # Export results as CSV
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
                    # Inform the user if no results match the given filters
                    st.write("No results found for the given filters.")
            except Exception as e:
                # Display an error message if something goes wrong
                st.error(f"An error occurred while processing the query: {e}")
        else:
            # Prompt the user to process a query from the Home page first
            st.write("Please process a query from the Home page first.")