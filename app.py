import streamlit as st
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns; sns.set(rc={'axes.facecolor':(0,0,0,0), 'figure.facecolor':(0,0,0,0)})


import random
class HareQuotaVoting:
    def __init__(self, candidates, seats, ballots):
        self.candidates = candidates
        self.seats = seats
        self.ballots = ballots
        self.quota = 0
        self.elected = []
        self.eliminated = []
    def calculate_quota(self):
        total_votes = len(self.ballots)
        self.quota = total_votes // (self.seats + 1) + 1
    def count_first_preferences(self):
        first_preferences = {candidate: 0 for candidate in self.candidates}
        for ballot in self.ballots:
            if ballot:
                first_preferences[ballot[0]] += 1
        return first_preferences
    def transfer_surplus(self, candidate, votes):
        surplus = votes - self.quota
        transfer_value = surplus / votes
        for ballot in self.ballots:
            if ballot and ballot[0] == candidate:
                next_preference = next((c for c in ballot[1:] if c not in self.elected and c not in self.eliminated), None)
                if next_preference:
                    self.ballots[self.ballots.index(ballot)] = [next_preference] + [c for c in ballot if c != next_preference]
    def eliminate_candidate(self, candidate):
        self.eliminated.append(candidate)
        for ballot in self.ballots:
            if ballot and ballot[0] == candidate:
                next_preference = next((c for c in ballot[1:] if c not in self.elected and c not in self.eliminated), None)
                if next_preference:
                    self.ballots[self.ballots.index(ballot)] = [next_preference] + [c for c in ballot if c != next_preference]
                else:
                    self.ballots[self.ballots.index(ballot)] = []
    def run_election(self):
        self.calculate_quota()
        while len(self.elected) < self.seats:
            first_preferences = self.count_first_preferences()
            # Check for candidates reaching quota
            for candidate, votes in first_preferences.items():
                if votes >= self.quota and candidate not in self.elected:
                    self.elected.append(candidate)
                    self.transfer_surplus(candidate, votes)
                    if len(self.elected) == self.seats:
                        return self.elected
            # If no candidate reaches quota, eliminate the one with fewest votes
            if not any(votes >= self.quota for votes in first_preferences.values()):
                min_votes = min(votes for candidate, votes in first_preferences.items() if candidate not in self.elected and candidate not in self.eliminated)
                to_eliminate = [candidate for candidate, votes in first_preferences.items() if votes == min_votes and candidate not in self.elected and candidate not in self.eliminated]
                self.eliminate_candidate(random.choice(to_eliminate))
        return self.elected
      

# st.set_page_config(page_title="Borda Count Selection", layout="wide")
st.set_page_config(page_title="Hare Quota Voting")
st.header("Hare Quota Voting System")
st.write("""This app leverages the Hare Quota voting system to elect candidates in an election""")
st.markdown("Here is a **[link](https://en.wikipedia.org/wiki/Hare_quota)** to learn more about the Hare Quota voting system.")

with st.expander("Open to see instructions on the data format that works well with this website"):
    st.write("""The format of the data that works well with the algorithm needs the choices listed as columns with each observations representing the voters' decisions""")
    st.write("""This is useful for selecting the right columns for running the algorithm.""")
    
    test_data = pd.read_excel("data.xlsx")
    st.write("Below is a sample of the data")
    st.dataframe(test_data.head(3), use_container_width=True)
    
uploaded_data = st.file_uploader("Upload the file containing the rank", type=["csv", "xlsx"])

if uploaded_data is not None:
  if "xlsx" in str(uploaded_data.name):
    df = pd.read_excel(uploaded_data)
    # st.dataframe(df, use_container_width=True)
  elif "csv" in str(uploaded_data.name):
    df = pd.read_csv(uploaded_data)
    # st.dataframe(df, use_container_width=True)
  else:
    df = pd.DataFrame()
    st.error("Please upload a file in the csv or xlsx format")


  if len(df) > 0:
    num_candidates = st.number_input("How many candidates would you like to select?", value = 0)
    st.write("Use the widget below to select the columns for voting. Select them in order of their rank")
    with st.form(key="Selecting columns"):
      choices = st.multiselect("Make your selections", list(df.columns))
      submit_button = st.form_submit_button(label="Submit")
      
    if submit_button:
      n = len(choices)
      new_df = df[choices]
      # st.dataframe(new_df, use_container_width=True)
      
      array_data = np.array(new_df)
      new_array = list(np.unique(array_data))
      # df["id"] = df.index
      # new_df = df.melt(id_vars="id", value_vars=df.columns, var_name="choice_rank", value_name="selection")
      # final = new_df.pivot_table(index="id", columns=["selection"], values="choice_rank", aggfunc=lambda x: ' '.join(x))
      # final = final.reset_index(drop=True)
      # # choice_order = choices
      # order_dict = {}
      # for i in range(n):
      #     order_dict[choice_order[i]] = n - i - 1
      # final_df = final.replace(list(order_dict.keys()), list(order_dict.values()))
      ballots = new_df.values.tolist()
      candidates = list(new_array)
      seats = num_candidates
      # rank_df = pd.DataFrame(final_df.sum(axis=0))
      # rank_df = rank_df.rename(columns={0: "total_counts"})
      # rank_df = rank_df.sort_values("total_counts", ascending=False).reset_index(drop=False)
      # rank_df["level"] = rank_df.index
      # rank_df["grp"] = rank_df["level"].apply(lambda x: 1 if x < num_candidates else 0)
      # #st.dataframe(rank_df)

      # fig, ax = plt.subplots(figsize=(8,6))
      # sns.barplot(x="total_counts", y="selection", data=rank_df, hue = "grp")
      # ax.set_title("Results",fontdict= {'fontsize': 10, 'fontweight':'bold'})
      # ax.set_xlabel("Counts")
      # ax.set_ylabel("Selection")
      # ax.xaxis.label.set_color('white')       
      # ax.yaxis.label.set_color('white')
      # ax.title.set_color('white')
      # ax.tick_params(axis='x', colors='white')   
      # ax.tick_params(axis='y', colors='white')
      # st.pyplot(fig)
      
      # selected_list=list(rank_df.head(num_candidates)["selection"])

      election = HareQuotaVoting(candidates, seats, ballots)
      result = election.run_election()

      st.markdown("**Elected candidates:**")
      for val in result:
        st.write(val)
