import streamlit as st
import os
from dotenv import load_dotenv
import re
import logging
import requests
import json

# Import agent apps

from agents.air_quality import air_quality_app
from agents.gold_rate import gold_rate_app
from agents.nutrition import nutrition_app

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AI Router Agent Implementation

class RouterAgent:
    def __init__(self):
        self.models_loaded = False
        self.classifier = None
        self.fallback_api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.last_routing_method = None  # Track which method was used
        
        self._load_models()
    
    def _load_models(self):
        """Load the appropriate AI models for classification"""
        try:
            # Use a lightweight model for classification
            from transformers import pipeline
            try:
                # Use a smaller, more reliable model
                self.classifier = pipeline(
                    "zero-shot-classification",
                    model="facebook/bart-large-mnli",
                    device=-1  # Use CPU
                )
                self.models_loaded = True
                logger.info("BART zero-shot model loaded successfully")
            except Exception as e:
                logger.warning(f"Could not load BART model: {e}")
                # Fallback to an even simpler model
                try:
                    self.classifier = pipeline(
                        "text-classification",
                        model="distilbert-base-uncased",
                        device=-1
                    )
                    self.models_loaded = True
                    logger.info("DistilBERT text classification model loaded successfully")
                except Exception as e2:
                    logger.error(f"Could not load any local models: {e2}")
                    self.models_loaded = False
            
        except ImportError:
            logger.warning("Transformers library not available")
            self.models_loaded = False
    
    def route_with_api(self, query: str) -> str:
        """Use HuggingFace API for classification if local models fail"""
        self.last_routing_method = "API"
        if not self.fallback_api_key:
            logger.warning("No HuggingFace API key available for fallback")
            return "error"
            
        try:
            API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-mnli"
            headers = {"Authorization": f"Bearer {self.fallback_api_key}"}
            
            payload = {
                "inputs": query,
                "parameters": {
                    "candidate_labels": ["air quality", "gold rate", "nutrition"],
                    "multi_label": False
                }
            }
            
            logger.info(f"Making API request for query: {query}")
            response = requests.post(API_URL, headers=headers, json=payload)
            result = response.json()
            
            if "error" in result:
                logger.error(f"API error: {result['error']}")
                return "error"
                
            best_label = result['labels'][0]
            best_score = result['scores'][0]
            
            logger.info(f"API response - Label: {best_label}, Score: {best_score}")
            
            if best_score > 0.5:
                label_map = {
                    "air quality": "air_quality",
                    "gold rate": "gold_rate", 
                    "nutrition": "nutrition"
                }
                return label_map.get(best_label, "error")
                
        except Exception as e:
            logger.error(f"API routing failed: {e}")
            
        return "error"
    
    def route_query(self, query: str) -> str:
        """Route user query to the appropriate agent using AI"""
        # First try local models
        if self.models_loaded and self.classifier:
            try:
                # For zero-shot models
                if hasattr(self.classifier, 'task') and self.classifier.task == 'zero-shot-classification':
                    self.last_routing_method = "Local Zero-Shot Model"
                    result = self.classifier(query, candidate_labels=["air quality", "gold rate", "nutrition"])
                    best_label = result['labels'][0]
                    best_score = result['scores'][0]
                    
                    logger.info(f"Zero-shot model - Query: '{query}', Label: {best_label}, Score: {best_score}")
                    
                    if best_score > 0.5:
                        label_map = {
                            "air quality": "air_quality",
                            "gold rate": "gold_rate", 
                            "nutrition": "nutrition"
                        }
                        return label_map.get(best_label, "error")
                
                # For text classification models (fallback)
                else:
                    self.last_routing_method = "Local Text Classification Model"
                    # Simple keyword-based fallback if classification model fails
                    query_lower = query.lower()
                    
                    # Check for air quality keywords
                    air_keywords = ["air quality", "pollution", "aqi", "pm2.5", "pm10", "smog", "dust", "mask", "breathe"]
                    if any(keyword in query_lower for keyword in air_keywords):
                        logger.info(f"Keyword match - Air quality: {query}")
                        return "air_quality"
                    
                    # Check for gold rate keywords
                    gold_keywords = ["gold rate", "gold price", "22k", "24k", "carat", "gram", "buy gold", "sell gold"]
                    if any(keyword in query_lower for keyword in gold_keywords):
                        logger.info(f"Keyword match - Gold rate: {query}")
                        return "gold_rate"
                    
                    # Check for nutrition keywords
                    nutrition_keywords = ["nutrition", "calorie", "protein", "fat", "carb", "food", "diet", "healthy"]
                    if any(keyword in query_lower for keyword in nutrition_keywords):
                        logger.info(f"Keyword match - Nutrition: {query}")
                        return "nutrition"
                    
            except Exception as e:
                logger.error(f"Local model routing failed: {e}")
        
        # Fallback to API if local models fail
        return self.route_with_api(query)

# Initialize the router agent
router_agent = RouterAgent()

# Enhanced Agentic System

class AgenticSystem:
    def __init__(self):
        self.conversation_history = []
    
    def process_query(self, user_query: str) -> dict:
        """Process user query using AI agentic approach"""
        # Use AI router to determine the right agent
        agent_type = router_agent.route_query(user_query)
        
        # Prepare response
        response = {
            "agent_type": agent_type,
            "response": None,
            "suggestions": [],
            "routing_method": router_agent.last_routing_method
        }
        
        # Generate appropriate response based on agent type
        if agent_type != "error":
            response["response"] = f"I'll help you with that using our {agent_type.replace('_', ' ')} agent."
            
            # Add context-aware suggestions
            if agent_type == "air_quality":
                response["suggestions"] = [
                    "Check air quality in your city",
                    "Get pollution alerts",
                    "Health recommendations based on AQI"
                ]
            elif agent_type == "gold_rate":
                response["suggestions"] = [
                    "Current gold prices",
                    "Price trends analysis",
                    "Get Email reports"
                ]
            elif agent_type == "nutrition":
                response["suggestions"] = [
                    "Food nutrition facts",
                    "Calorie information",
                    "Get Email reports"
                ]
        else:
            response["response"] = "I'm not sure how to help with that. I specialize in air quality, gold rates, and nutrition information."
            response["suggestions"] = [
                "Ask about air quality in your city",
                "Inquire about current gold rates", 
                "Get nutrition information for foods"
            ]
        
        return response

# Initialize the agentic system
agentic_system = AgenticSystem()

# -------------------------
# Main Hub App
# -------------------------
st.set_page_config(page_title="AI Agentic System", page_icon="🤖", layout="wide")
st.title("🤖 AI Agentic System")

# Initialize session state
if 'current_agent' not in st.session_state:
    st.session_state.current_agent = None
if 'show_agent_ui' not in st.session_state:
    st.session_state.show_agent_ui = False
if 'last_query' not in st.session_state:
    st.session_state.last_query = ""
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'agent_to_use' not in st.session_state:
    st.session_state.agent_to_use = None

# Sidebar for navigation
with st.sidebar:
    st.title("Navigation")
    
    if st.button("🏠 Home", use_container_width=True, key="home_button"):
        st.session_state.current_agent = None
        st.session_state.show_agent_ui = False
        st.session_state.last_query = ""
        st.session_state.agent_to_use = None
        st.rerun()
    
    st.divider()
    
    st.subheader("Manual Agent Selection")
    agent_option = st.radio(
        "Select agent directly:",
        ["Air Quality", "Gold Rate", "Nutrition"],
        index=0 if st.session_state.current_agent == "air_quality" else 
              1 if st.session_state.current_agent == "gold_rate" else 
              2 if st.session_state.current_agent == "nutrition" else 0,
        key="agent_radio"
    )
    
    if st.button("Use Selected Agent", use_container_width=True, key="use_selected_agent"):
        agent_map = {
            "Air Quality": "air_quality",
            "Gold Rate": "gold_rate",
            "Nutrition": "nutrition"
        }
        st.session_state.current_agent = agent_map[agent_option]
        st.session_state.show_agent_ui = True
        st.session_state.last_query = ""
        st.session_state.agent_to_use = None
        st.rerun()

# Check if we need to switch to an agent
if st.session_state.agent_to_use:
    st.session_state.current_agent = st.session_state.agent_to_use
    st.session_state.show_agent_ui = True
    st.session_state.agent_to_use = None
    st.rerun()

# Show agent UI if selected
if st.session_state.show_agent_ui:
    if st.session_state.current_agent == "air_quality":
        st.subheader("🌫️ Air Quality Agent")
        air_quality_app()
    elif st.session_state.current_agent == "gold_rate":
        st.subheader("💰 Gold Rate Agent")
        gold_rate_app()
    elif st.session_state.current_agent == "nutrition":
        st.subheader("🍎 Nutrition Agent")
        nutrition_app()
    
    if st.button("← Back to AI Assistant", use_container_width=True, key="back_to_assistant"):
        st.session_state.show_agent_ui = False
        st.session_state.current_agent = None
        st.session_state.agent_to_use = None
        st.rerun()

# Main chat interface (only show if not in agent UI)
else:
    st.header("Chat with AI Agentic System")
    st.write("I can help you with air quality information, gold rates, and nutrition facts!")
    
    # Display only the last response, not the entire history
    if st.session_state.chat_history:
        last_msg = st.session_state.chat_history[-1]
        with st.chat_message("assistant"):
            st.write(last_msg["content"])
            
            # Display suggestions if available
            if "suggestions" in last_msg and last_msg["suggestions"]:
                st.write("**I can help you with:**")
                for suggestion in last_msg["suggestions"]:
                    st.write(f"- {suggestion}")
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about air quality, gold rates, or nutrition..."):
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Process with AI agentic system
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = agentic_system.process_query(prompt)
                
                # Store response in session state
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response["response"],
                    "agent_type": response["agent_type"],
                    "suggestions": response["suggestions"],
                    "routing_method": response.get("routing_method", "Unknown")
                })
                
                # Display AI response
                st.write(response["response"])
                
                # Display suggestions if available
                if response["suggestions"]:
                    st.write("**I can help you with:**")
                    for suggestion in response["suggestions"]:
                        st.write(f"- {suggestion}")
                
                # If an agent was identified, redirect automatically
                if response["agent_type"] != "error":
                    st.session_state.agent_to_use = response["agent_type"]
                    st.rerun()