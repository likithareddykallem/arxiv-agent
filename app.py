import pandas as pd
import streamlit as st

from main import run_pipeline

st.title("PROTAC Knowledge Extraction Agent")

query = st.text_input("Enter Query", "PROTAC linker")

if st.button("Run Agent"):
    with st.spinner("Retrieving PROTAC linker papers and extracting linker types..."):
        state = run_pipeline(query)

        if state.extracted_data:
            df = pd.DataFrame(state.extracted_data)
            st.success(f"Extracted {len(df)} structured insights")
            st.dataframe(df)
        else:
            st.warning("No linker information extracted.")
