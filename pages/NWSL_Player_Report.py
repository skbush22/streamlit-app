import streamlit as st
from utils import app
import pandas as pd

st.title('NWSL Player Report Maker 1.0')

st.text('''Welcome to the 1.0 version of my player report maker! There's some  
information you should know about this app. It is still a work in progress (i.e.  
I will be doing my best to add customizability and new features), so please judge it  
as such! Additionally, there are some rules to follow: 

- Currently, when a player has played for more than two teams, their full-    
  season stats will be returned, not just the stats for the team that you     
  entered. This will hopefully be fixed in a future version.
- Finally, goalkeepers are currently not supported. Sorry.

If you run into a player name that returns an error, or if you can't find a certain 
player, please let me know and I will do my best to fix it. 

Credit: Data from Opta, American Soccer Analysis''')
tab1 = st.tabs(['Base'])

player_list_df = pd.read_csv('ASA_Player_List_NWSL.csv')
player_options = list(player_list_df.Name.unique())

text_input_player = st.selectbox('Select a player:', player_options, index=None, placeholder='Select...')

if text_input_player:
	text_input_team = st.selectbox('Select a team:',
		('Bay FC',
		 'North Carolina Courage',
		 'Kansas City Current',
		 'Orlando Pride',
		 'Washington Spirit',
		 'Houston Dash',
		 'Utah Royals',
		 'Portland Thorns FC',
		 'Racing Louisville FC',
		 'Seattle Reign FC',
		 'San Diego Wave FC',
		 'Chicago Red Stars',
		 'Angel City FC',
		 'NJ/NY Gotham FC'),
		index=None,
		placeholder='Select...'
		)

	if text_input_team:
		try:
			with st.spinner('Processing...'):
				result = app.run_player_graphic(text_input_player, text_input_team, 'NWSL')
				st.pyplot(fig=result)
		except ValueError:
			st.write('Sorry. Your request could not be processed.\nPlease check that all player and team selections are correct.\nIf so, and request is still not processing, contact me on X.')
