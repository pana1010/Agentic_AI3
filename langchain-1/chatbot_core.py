import os
from dotenv import load_dotenv
import streamlit as st
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

# ─── Load API Key ───────────────────────────────────────────────────────────────

os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
# load_dotenv()
# os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# ─── Initialize Models ─────────────────────────────────────────────────────────
model = init_chat_model("groq:llama-3.1-8b-instant")
llm   = ChatGroq(model="llama-3.1-8b-instant")

# ─── Prompt Templates ──────────────────────────────────────────────────────────
recommendation_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert energy conservation advisor. Provide practical, "
     "personalized, and actionable advice to reduce energy consumption. "
     "Also suggest energy-efficient appliances and relevant renewable energy options."),
    ("user",
     "User Type: {user_type}\n"
     "Appliances Used: {appliances}\n"
     "Energy Concerns: {concerns}\n"
     "Location (optional): {location}")
])

analysis_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an environmental analyst. Analyze the energy recommendations given "
     "below and estimate their environmental and cost-saving impact."),
    ("user", "{recommendations}")
])

appliance_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are an expert in energy-efficient appliances. Suggest replacements or "
     "improvements for the following:"),
    ("user", "{appliances}")
])

renewable_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a renewable energy consultant. Based on the user's location and use case, "
     "recommend solar/wind/other options."),
    ("user", "Location: {location}\nUser Type: {user_type}")
])

co2_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "You are a sustainability expert. Estimate how many kWh of electricity the user "
     "can save per month from the following energy-saving recommendations. "
     "Only output a number in kWh."),
    ("user", "{recommendations}")
])

# ─── Build Recommendation Chain ─────────────────────────────────────────────────
def create_recommend_chain():
    return recommendation_prompt | model | StrOutputParser()

recommend_chain = create_recommend_chain()

# ─── Standalone Analysis Function ───────────────────────────────────────────────
def analyze_recommendations(recommendations: str) -> str:
    prompt = analysis_prompt.invoke({"recommendations": recommendations})
    return model.invoke(prompt).content

# ─── Other Helpers ──────────────────────────────────────────────────────────────
def get_appliance_suggestions(appliances: str) -> str:
    prompt = appliance_prompt.invoke({"appliances": appliances})
    return model.invoke(prompt).content

def get_renewable_options(location: str, user_type: str) -> str:
    prompt = renewable_prompt.invoke({"location": location, "user_type": user_type})
    return model.invoke(prompt).content

def estimate_kwh_savings(recommendations: str) -> float:
    prompt = co2_prompt.invoke({"recommendations": recommendations})
    resp = model.invoke(prompt).content
    try:
        return float("".join(c for c in resp if c.isdigit() or c == "."))
    except ValueError:
        return 0.0

def calculate_co2_savings(kwh_saved: float) -> dict:
    kg_co2     = kwh_saved * 0.385
    tonnes_co2 = kg_co2 / 1000
    return {
        "kWh Saved": round(kwh_saved, 2),
        "CO₂ Saved (kg)": round(kg_co2, 2),
        "CO₂ Saved (t)": round(tonnes_co2, 3),
    }
