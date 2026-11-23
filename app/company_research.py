"""Read the public, dated FinAI edition. Provider credentials stay with its author."""
from datetime import date

import requests
import streamlit as st

EDITION_URL = "https://raw.githubusercontent.com/brej-29/finai-realtime-market-analytics/main/apps/web/edition/briefs.json"
DESK_URL = "https://brej-29.github.io/finai-realtime-market-analytics/#research"
ISSUERS = {"AAPL": "Apple", "MSFT": "Microsoft", "NVDA": "NVIDIA"}


@st.cache_data(ttl=3600, show_spinner=False)
def load_edition():
    response = requests.get(EDITION_URL, timeout=8)
    response.raise_for_status()
    return response.json()


def show_research(symbol):
    with st.expander("Company research · Apple, Microsoft and NVIDIA"):
        options = list(ISSUERS)
        selected = st.selectbox("Read a sourced brief", options,
                                index=options.index(symbol) if symbol in options else None,
                                format_func=lambda value: f"{ISSUERS[value]} ({value})",
                                placeholder="Choose a company")
        if selected is None:
            st.caption("Company profile, investor disclosures and recent news from the dated FinAI research edition.")
            st.link_button("Browse the research desk", DESK_URL)
            return
        try:
            edition = load_edition()
            company = next(c for c in edition["companies"] if c["symbol"] == selected)
            retrieved = date.fromisoformat(edition["retrieved"])
        except (requests.RequestException, ValueError, KeyError, StopIteration):
            st.info("The saved edition is temporarily unavailable.")
            st.link_button("Open the published brief", f"{DESK_URL}/{selected}")
            return
        st.caption(f"Evidence retrieved {retrieved:%B %d, %Y} · Tavily via OmniRoute")
        for section in company["groups"]:
            st.subheader(section["label"])
            st.write(section["text"])
            for source in section["sources"]:
                st.markdown(f"[{source['title']}]({source['url']})")
                if source.get("published"):
                    st.caption(f"Published {source['published']}")

