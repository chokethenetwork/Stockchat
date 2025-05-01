try:
    from langchain_community.embeddings import OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
    print("✅ langchain-community is properly installed")
except ImportError as e:
    print("❌ Error importing langchain-community:", str(e))

try:
    import streamlit as st
    print("✅ streamlit is properly installed")
except ImportError:
    print("❌ streamlit is not installed")

try:
    import fitz
    print("✅ PyMuPDF is properly installed")
except ImportError:
    print("❌ PyMuPDF is not installed")