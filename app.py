import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain_community.embeddings import HuggingFaceEmbeddings  # Change this line
from langchain_community.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from document_processor import process_documents
from sensor_simulator import AnimalSensor
from abnormality_detector import AbnormalityDetector
from animal_registry import AnimalRecord
import json
import threading
import time
import os
from dotenv import load_dotenv
from datetime import datetime
from custom_llm import DistilBertLLM  # Change from DeepseekLLM
import torch

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="StockChat - Livestock Assistant",
    page_icon="🐮",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    .stTextInput, .stTextArea {
        background-color: #f0f0f0;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-message {
        background-color: #f0f0f0;
    }
    .bot-message {
        background-color: #000000;
        color: #ffffff;
    }
    .upload-section {
        padding: 2rem;
        border-radius: 0.5rem;
        background-color: #f8f8f8;
        margin-bottom: 1rem;
    }
    .css-1d391kg {
        padding: 2rem;
    }
    @media (max-width: 768px) {
        .stApp {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    if "memory" not in st.session_state:
        st.session_state.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None
    if "sensor_config" not in st.session_state:
        st.session_state.sensor_config = {
            "simulation_enabled": False,
            "monitoring_interval": 30,
            "animals": ["Cow001", "Cow002", "Cow003"]
        }
    if "latest_readings" not in st.session_state:
        st.session_state.latest_readings = {}
    if "alerts" not in st.session_state:
        st.session_state.alerts = []
    if "animal_registry" not in st.session_state:
        st.session_state.animal_registry = {}

def create_conversational_chain(vector_store):
    llm = DistilBertLLM()
    
    def qa_chain(inputs: dict) -> dict:
        question = inputs["question"]
        
        # Get relevant documents
        docs = vector_store.similarity_search(question, k=3)
        context = "\n\n".join(doc.page_content for doc in docs)
        
        # Add sensor data to context if available
        if st.session_state.latest_readings:
            sensor_context = "\nCurrent sensor readings:\n"
            for animal_id, reading in st.session_state.latest_readings.items():
                sensor_context += f"{animal_id}: Temp {reading['temperature']}°C, HR {reading['heart_rate']} bpm\n"
            context += "\n" + sensor_context
        
        try:
            # Get answer from DistilBERT
            answer = llm(question, context=context)
            
            # If no answer is found, provide a default response
            if not answer or answer == "No answer found":
                answer = "I couldn't find a specific answer in the documents. Please try rephrasing your question or provide more context."
            
            return {"answer": answer}
        except Exception as e:
            return {"answer": f"Error processing question: {str(e)}"}
    
    return qa_chain

def register_animal(record: AnimalRecord):
    """Register animal and update vector store"""
    # Add to registry
    st.session_state.animal_registry[record.animal_id] = record
    
    # Update sensor config if needed
    if record.animal_id not in st.session_state.sensor_config["animals"]:
        st.session_state.sensor_config["animals"].append(record.animal_id)
    
    # Update vector store with animal information
    if st.session_state.vector_store is not None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': device},
            encode_kwargs={'device': device, 'batch_size': 32}
        )
        texts = [record.to_text()]
        new_vectorstore = FAISS.from_texts(texts, embeddings)
        st.session_state.vector_store.merge_from(new_vectorstore)

def add_animal_note(animal_id: str, note: str):
    """Add a note to an animal's history and update vector store"""
    if animal_id in st.session_state.animal_registry:
        animal = st.session_state.animal_registry[animal_id]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        # Initialize notes_history if it doesn't exist
        if not hasattr(animal, 'notes_history'):
            animal.notes_history = []
            
        # Add note to animal's history
        animal.notes_history.append({
            "timestamp": timestamp,
            "note": note
        })
        
        # Update vector store with new note
        if st.session_state.vector_store is not None:
            try:
                device = "cuda" if torch.cuda.is_available() else "cpu"
                embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    model_kwargs={'device': device},
                    encode_kwargs={'device': device, 'batch_size': 32}
                )
                note_text = f"""
                Animal Note:
                ID: {animal_id}
                Date: {timestamp}
                Note: {note}
                """
                new_vectorstore = FAISS.from_texts([note_text], embeddings)
                st.session_state.vector_store.merge_from(new_vectorstore)
            except Exception as e:
                st.error(f"Error updating vector store: {str(e)}")
                return False
        
        return True
    return False

def monitor_sensors():
    detector = AbnormalityDetector(st.session_state.animal_registry)
    while st.session_state.sensor_config["simulation_enabled"]:
        for animal_id in st.session_state.sensor_config["animals"]:
            # Get animal record
            animal_record = st.session_state.animal_registry.get(animal_id)
            if not animal_record:
                continue
                
            # Create and link sensor
            sensor = AnimalSensor(animal_id)
            if not sensor.link_to_animal(animal_record):
                continue
                
            # Generate and process reading
            reading = sensor.generate_reading()
            if reading:
                st.session_state.latest_readings[animal_id] = reading
                
                abnormalities = detector.check_reading(reading)
                if abnormalities:
                    alert = {
                        "timestamp": reading["timestamp"],
                        "animal_id": animal_id,
                        "sensor_id": animal_record.sensor_id,
                        "abnormalities": abnormalities
                    }
                    st.session_state.alerts.insert(0, alert)
                    
                    animal_context = f"""
                    Animal Details:
                    - Name: {animal_record.name}
                    - Breed: {animal_record.breed}
                    - Sensor ID: {animal_record.sensor_id}
                    - Notes: {animal_record.notes}
                    """
                    
                    prompt = f"Animal {animal_id}{animal_context} shows the following abnormal readings: {', '.join(abnormalities)}. What could be causing this?"
                    st.session_state.chat_history.append({"role": "assistant", "content": "🚨 ALERT: " + prompt})
        
        time.sleep(st.session_state.sensor_config["monitoring_interval"])

def main():
    initialize_session_state()
    
    st.title("StockChat 🐮")
    st.subheader("")

    # Document Management in Sidebar
    with st.sidebar:
        st.header("📚 Knowledge Base")
        uploaded_files = st.file_uploader(
            "Upload Farm Records & Medical Documents",
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=True,
            help="Upload documents to provide context for the AI assistant"
        )
        
        # Update the document processing section in main()
        if uploaded_files:
            with st.spinner("Processing documents..."):
                try:
                    texts = process_documents(uploaded_files)
                    # Initialize HuggingFace embeddings with specific device
                    embeddings = HuggingFaceEmbeddings(
                        model_name="sentence-transformers/all-MiniLM-L6-v2",
                        model_kwargs={'device': 'cpu'}  # Force CPU usage
                    )
                    st.session_state.vector_store = FAISS.from_texts(texts, embeddings)
                    st.success(f"✅ Successfully processed {len(uploaded_files)} documents")
                    
                    # Display processed documents
                    with st.expander("Processed Documents"):
                        for file in uploaded_files:
                            st.text(f"📄 {file.name}")
                except Exception as e:
                    st.error(f"Error processing documents: {str(e)}")

        # Sensor Configuration Section
        st.header("📡 Sensor Settings")
        monitoring_interval = st.slider(
            "Monitoring Interval (seconds)", 
            min_value=5, 
            max_value=60, 
            value=st.session_state.sensor_config["monitoring_interval"]
        )
        st.session_state.sensor_config["monitoring_interval"] = monitoring_interval

        # Animal Registration Form
        st.header("🐮 Animal Registration")
        with st.expander("Add New Animal", expanded=False):
            with st.form("animal_registration"):
                col1, col2 = st.columns(2)
                
                with col1:
                    animal_id = st.text_input("Animal ID*")
                    name = st.text_input("Name")
                    breed = st.text_input("Breed")
                    birth_date = st.date_input("Birth Date")
                    sensor_id = st.selectbox(
                        "Select Sensor",
                        options=[""] + list(AnimalSensor.AVAILABLE_SENSORS.keys()),
                        format_func=lambda x: f"{x} - {AnimalSensor.AVAILABLE_SENSORS.get(x, '')}" if x else "Select Sensor"
                    )
                    notes = st.text_area("Notes")
                
                with col2:
                    st.subheader("Vital Sign Thresholds")
                    temp_min = st.number_input("Min Temperature (°C)", value=38.0, step=0.1)
                    temp_max = st.number_input("Max Temperature (°C)", value=39.5, step=0.1)
                    
                    activity_min = st.number_input("Min Activity (steps/hr)", value=20, step=5)
                    activity_max = st.number_input("Max Activity (steps/hr)", value=100, step=5)
                    
                    hr_min = st.number_input("Min Heart Rate (bpm)", value=60, step=5)
                    hr_max = st.number_input("Max Heart Rate (bpm)", value=90, step=5)
                    
                    rr_min = st.number_input("Min Resp Rate (br/min)", value=20, step=2)
                    rr_max = st.number_input("Max Resp Rate (br/min)", value=40, step=2)
                    
                    ph_min = st.number_input("Min Rumen pH", value=5.8, step=0.1)
                    ph_max = st.number_input("Max Rumen pH", value=6.8, step=0.1)
                
                submit = st.form_submit_button("Register Animal")
                
                if submit and animal_id:
                    new_animal = AnimalRecord(
                        animal_id=animal_id,
                        name=name,
                        breed=breed,
                        birth_date=birth_date.strftime("%Y-%m-%d"),
                        sensor_id=sensor_id,
                        notes=notes,
                        registration_date=datetime.now().strftime("%Y-%m-%d"),
                        temp_min=temp_min,
                        temp_max=temp_max,
                        activity_min=activity_min,
                        activity_max=activity_max,
                        heart_rate_min=hr_min,
                        heart_rate_max=hr_max,
                        resp_rate_min=rr_min,
                        resp_rate_max=rr_max,
                        rumen_ph_min=ph_min,
                        rumen_ph_max=ph_max
                    )
                    register_animal(new_animal)
                    st.success(f"✅ Animal {animal_id} registered successfully!")

        # Display Registered Animals
        if st.session_state.animal_registry:
            st.header("📋 Registered Animals")
            for animal_id, record in st.session_state.animal_registry.items():
                with st.expander(f"{animal_id} - {record.name}", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    # Left column: Animal Info
                    with col1:
                        st.markdown("### Basic Information")
                        st.write(f"**Breed:** {record.breed}")
                        st.write(f"**Birth Date:** {record.birth_date}")
                        st.write(f"**📡 Sensor:** {record.sensor_id}")
                        
                        st.markdown("### Vital Sign Thresholds")
                        st.write(f"**Temperature:** {record.temp_min}-{record.temp_max}°C")
                        st.write(f"**Activity:** {record.activity_min}-{record.activity_max} steps/hr")
                        st.write(f"**Heart Rate:** {record.heart_rate_min}-{record.heart_rate_max} bpm")
                        st.write(f"**Resp Rate:** {record.resp_rate_min}-{record.resp_rate_max} br/min")
                        st.write(f"**Rumen pH:** {record.rumen_ph_min}-{record.rumen_ph_max}")
                    
                    # Right column: Notes
                    with col2:
                        st.markdown("### Notes")
                        with st.form(key=f"note_form_{animal_id}"):
                            new_note = st.text_area(
                                "Add new note",
                                key=f"note_{animal_id}",
                                placeholder="Enter observations, treatments, or other notes..."
                            )
                            submit_note = st.form_submit_button("Add Note")
                            if submit_note:
                                if new_note.strip():
                                    if add_animal_note(animal_id, new_note):
                                        st.success("Note added successfully!")
                                else:
                                    st.warning("Please enter a note")
                        
                        # Notes History
                        if hasattr(record, 'notes_history') and record.notes_history:
                            st.markdown("#### History")
                            for note in reversed(record.notes_history):
                                with st.container():
                                    st.markdown(f"""
                                    ---
                                    **{note['timestamp']}**  
                                    {note['note']}
                                    """)

    # Main Content Area
    # Simulation Control
    col1, col2 = st.columns([2, 1])
    with col1:
        simulation_status = "Running ✅" if st.session_state.sensor_config["simulation_enabled"] else "Stopped ⏹️"
        st.header(f"Sensors: {simulation_status}")
    with col2:
        if st.button("Toggle Simulation", type="primary", key="main_simulation_toggle"):
            st.session_state.sensor_config["simulation_enabled"] = not st.session_state.sensor_config["simulation_enabled"]
            if st.session_state.sensor_config["simulation_enabled"]:
                threading.Thread(target=monitor_sensors, daemon=True).start()
                st.success("Simulation started! You will receive alerts for abnormal readings.")
            else:
                st.warning("Simulation stopped.")

    # Alert History (modified to include context from documents)
    if st.session_state.alerts:
        with st.expander("🚨 Recent Alerts", expanded=True):
            for alert in st.session_state.alerts[:5]:
                alert_time = alert["timestamp"].split("T")[1][:8]
                st.warning(
                    f"⏰ {alert_time} - {alert['animal_id']}: "
                    f"{', '.join(alert['abnormalities'])}"
                )
                if st.session_state.vector_store is not None:
                    # Search relevant information in documents
                    chain = create_conversational_chain(st.session_state.vector_store)
                    context_query = f"What are the treatment protocols for {', '.join(alert['abnormalities'])}?"
                    relevant_info = chain({"question": context_query})
                    with st.info("📚 Relevant Information from Documents"):
                        st.markdown(relevant_info['answer'])

    # Sensor Readings Display (existing code)
    if st.session_state.sensor_config["simulation_enabled"]:
        st.markdown("---")
        st.header("📊 Live Sensor Readings")
        cols = st.columns(len(st.session_state.sensor_config["animals"]))
        for i, animal_id in enumerate(st.session_state.sensor_config["animals"]):
            with cols[i]:
                if animal_id in st.session_state.latest_readings:
                    reading = st.session_state.latest_readings[animal_id]
                    st.metric(f"{animal_id} Temperature", f"{reading['temperature']}°C")
                    st.metric("Activity", f"{reading['activity']} steps/hr")
                    st.metric("Heart Rate", f"{reading['heart_rate']} bpm")
                    st.metric("Resp. Rate", f"{reading['respiration_rate']} br/min")
                    st.metric("Rumen pH", f"{reading['rumen_ph']}")

    if st.checkbox("Debug Info"):
        st.write("Registered Animals:", st.session_state.animal_registry)
        st.write("Active Sensors:", st.session_state.sensor_config["animals"])
        st.write("Latest Readings:", st.session_state.latest_readings)

    # Enhanced Chat Interface
    st.markdown("---")
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Enhanced Chat Input with Context
    if prompt := st.chat_input("How can I help you with your livestock today?"):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if st.session_state.vector_store is None:
                response = "⚠️ Please upload some farm records and medical documents so I can provide better assistance!"
            else:
                try:
                    chain = create_conversational_chain(st.session_state.vector_store)
                    
                    with st.spinner("Processing response..."):
                        result = chain({"question": prompt})
                        response = result['answer']
                        
                except Exception as e:
                    response = f"⚠️ Error processing request: {str(e)}"
        
            st.markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})

if __name__ == "__main__":
    main()