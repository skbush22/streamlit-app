import streamlit as st
import requests


def test():

  sched_next = requests.get("https://api.performfeeds.com/soccerdata/match/qxcx5jmswgto1qeqcjzghtddt/?_rt=c&tmcl=929cd2ue4bpcebvx91rx9e3h0&live=yes&_pgSz=400&_pgNm=2&_lcl=en&_fmt=jsonp&_clbk=W32b7874e6f7b21140cce4e44b90e48dcf2e8bf48b", 
    headers={'referer': "https://optaplayerstats.statsperform.com/en_GB/soccer", 'origin':"https://optaplayerstats.statsperform.com/en_GB/soccer",
    'user-agent': 'Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US);'})
  sched = sched_next.headers

  return sched