import streamlit as st
import requests


def test():

    sched_next = requests.get(st.secrets.mls.next_url, 
                              headers={'referer': st.secrets.mls.referer, 'origin':st.secrets.mls.origin,
                              'user-agent': 'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US);'})
    sched = sched_next.text

    return sched