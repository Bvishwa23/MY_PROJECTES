import streamlit as st
import random
import string
import cv2
from PIL import Image

class Player:
    def __init__(self, name, age, sport, medical_clearance, similar_events=None, event_name=None, phone_image=None):
        self.registration_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        self.name = name
        self.age = age
        self.sport = sport
        self.medical_clearance = medical_clearance
        self.similar_events = similar_events
        self.event_name = event_name
        self.phone_image = phone_image

class Team:
    def __init__(self, name, members):
        self.registration_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        self.name = name
        self.members = members

class RegistrationPortal:
    def __init__(self):
        self.players = []
        self.teams = []

    def register_individual_player(self, name, age, sport, medical_clearance, similar_events=False, event_name=None, image=None):
        if 15 <= int(age) <= 24:
            if similar_events:
                if event_name:
                    player = Player(name, age, sport, medical_clearance, similar_events, event_name, image)
                    self.players.append(player)
                    st.success("Player registered successfully!")
                    self.make_payment(250, "Individual")
                else:
                    st.warning("Registration cancelled. Please provide the event name for similar events.")
            else:
                if medical_clearance:  # Check if medical clearance is provided
                    player = Player(name, age, sport, medical_clearance, similar_events, event_name, image)
                    self.players.append(player)
                    st.success("Player registered successfully!")
                    self.make_payment(250, "Individual")
                else:
                    st.warning("Registration cancelled. Medical clearance is required.")
        else:
            st.warning("Registration cancelled due to age restrictions.")

    def register_team(self, team_name, num_players):
        st.header(f"Enter details for team '{team_name}':")
        team_members = []
        for i in range(num_players):
            st.subheader(f"Enter details for team member {i+1}:")
            name = st.text_input("Enter player's name:", key=f"player_name_{team_name}_{i}")
            age = st.number_input("Enter player's age:", min_value=0, step=1, key=f"player_age_{team_name}_{i}")
            sport = st.text_input("Enter player's sport:", key=f"player_sport_{team_name}_{i}")
            medical_clearance = st.radio("Cleared Medical Test:", options=["Yes", "No"], key=f"player_medical_{team_name}_{i}") == "Yes"
            similar_events = st.radio("Participated in Similar Events:", options=["Yes", "No"], key=f"player_events_{team_name}_{i}") == "Yes"
            event_name = st.text_input("Enter event name:", key=f"player_event_name_{team_name}_{i}") if similar_events else None
            if similar_events:
                similar_events = True
            else:
                similar_events = False
                event_name = None
            image = None  # Removed image capturing part for team registration
            team_member = Player(name, age, sport, medical_clearance, similar_events, event_name, image)
            team_members.append(team_member)
        self.teams.append(Team(team_name, team_members))
        st.success("Team registered successfully!")
        self.make_payment(1000 * num_players, "Team")

    def generate_random_competitors(self):
        return random.randint(5, 20)

    def make_payment(self, amount, registration_type):
        st.title("Payment Information")
        st.write(f"Amount to be paid: {amount} INR")
        upi_id = st.text_input("Enter UPI ID for payment:", key=f"upi_id_{registration_type}")
        if upi_id:
            st.write(f"Processing payment of {amount} INR to UPI ID: {upi_id}")
            st.success("Payment successful.")
            st.write("---")
            st.write("Registration Details:")
            self.display_registration_info(amount)
            if st.button("Next"):
                st.write("Players registration completed successfully!")
        else:
            st.error("Payment failed: UPI ID not provided.")

    def display_registration_info(self, amount):
        st.title("Registration Information")

        # Display unique registration ID
        st.write("Registration ID:", self.generate_unique_registration_id())

        # Display player or team information
        if self.players:
            st.write("Player Information:")
            for player in self.players:
                self.display_player_info(player)
        elif self.teams:
            st.write("Team Information:")
            for team in self.teams:
                st.write(f"Team Name: {team.name}")
                if team.members:
                    st.write("Team Members:")
                    for member in team.members:
                        self.display_player_info(member)
        else:
            st.write("No registration information available.")

        # Display number of competitors
        st.write("Number of Competitors:", self.generate_random_competitors())

        # Display payment amount
        st.write("Amount Paid:", f"{amount} INR")

    def display_player_info(self, player):
        st.write(f"Name: {player.name}, Age: {player.age}, Sport: {player.sport}")
        if player.similar_events:
            st.write(f"Event Name: {player.event_name}")
        if player.phone_image:
            st.image(player.phone_image, caption='Player Image', use_column_width=True, width=200)

    def capture_image(self, key):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Error: Could not open camera.")
            return None
        ret, frame = cap.read()
        cap.release()

        if not ret:
            st.error("Error: Failed to capture image.")
            return None

        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb_image)

        st.image(pil_image, caption='Captured Image', use_column_width=True)
        if st.button('Use this image', key=f"use_image_{key}"):
            return pil_image
        elif st.button('Retake Image', key=f"retake_image_{key}"):
            return self.capture_image(key)
        else:
            return None

    def generate_unique_registration_id(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def prompt_registration_options(self):
        st.title("Registration Portal")
        option = st.selectbox("Select Option", ["Register Individual Player", "Register Team"])
        if option == "Register Individual Player":
            name = st.text_input("Enter player's name:", key="individual_name")
            age = st.number_input("Enter player's age:", min_value=0, step=1, key="individual_age")
            sport = st.text_input("Enter player's sport:", key="individual_sport")
            medical_clearance = st.radio("Cleared Medical Test:", options=["Yes", "No"], key="individual_medical") == "Yes"
            if not medical_clearance:
                st.warning("Registration cancelled. Medical clearance is required.")
                return
            similar_events = st.radio("Participated in Similar Events:", options=["Yes", "No"], key="individual_events") == "Yes"
            event_name = st.text_input("Enter event name:", key="individual_event_name") if similar_events else None
            image = self.capture_image("individual_image")
            self.register_individual_player(name, age, sport, medical_clearance, similar_events, event_name, image)
        elif option == "Register Team":
            team_name = st.text_input("Enter team name:", key="team_name")
            num_players = st.number_input("Enter number of team members:", min_value=1, step=1, key="team_num_players")
            if num_players > 0:
                self.register_team(team_name, num_players)


def main():
    st.set_page_config(page_title="Registration Portal")
    portal = RegistrationPortal()
    portal.prompt_registration_options()


if __name__ == "__main__":
    main()