import streamlit as st
import requests


def test():

  sched_next = requests.get(st.secrets.mls.next_url, 
    headers={'referer': "https://optaplayerstats.statsperform.com/en_GB/soccer", 'origin':"https://optaplayerstats.statsperform.com/en_GB/soccer",
    'user-agent': 'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US);'})
  sched = sched_next.text

  return sched