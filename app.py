import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from ddgs import DDGS
import chromadb

# ── LLM setup ────────────────────
gemini_api_key = os.getenv("GEMINI_API_KEY") or os.getenv('GOOGLE_API_KEY') or os.getenv('GOOGLE_API_KEY_JSON')
if not gemini_api_key:
    print("Warning: GEMINI_API_KEY (or GOOGLE_API_KEY) not found in environment; LLM and agent will be disabled.")
    llm = None
else:
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except Exception as e:
        print(f"Failed to import Gemini client library: {e}")
        llm = None
    else:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            api_key=gemini_api_key,
            temperature=0
        )

# ── RAG setup (resilient) ─────────────────
RAG_AVAILABLE = True
try:
    loader = TextLoader("ZingTel_guide.txt")
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=100)
    chunks = splitter.split_documents(documents)

    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    try:
        chroma_client = chromadb.Client()
        collection = chroma_client.get_or_create_collection('zingtel_agent')

        texts = [chunk.page_content for chunk in chunks]
        embeddings = embedding_model.encode(texts).tolist()
        collection.add(
            documents=texts,
            embeddings=embeddings,
            ids=[f"chunk_{i}" for i in range(len(texts))]
        )
        print(f"RAG ready — {len(texts)} chunks loaded")
    except Exception as e:
        print(f"Chromadb or embeddings initialization failed: {e}")
        collection = None
        chroma_client = None
        RAG_AVAILABLE = False
except Exception as e:
    print(f"RAG disabled: {e}")
    RAG_AVAILABLE = False
    collection = None
    chroma_client = None
    embedding_model = None
    chunks = []

# ── tools ─────────────────
@tool
def search_zingtel_docs(question: str) -> str:
    """Search ZingTel's official documents for policies, procedures, 
    and service information. Use this for any ZingTel-specific questions."""
    if not RAG_AVAILABLE or collection is None or embedding_model is None:
        return "Document search is currently unavailable."
    question_embedding = embedding_model.encode([question]).tolist()
    results = collection.query(
        query_embeddings=question_embedding,
        n_results=4
    )
    chunks_found = results['documents'][0]
    if not chunks_found:
        return "No relevant information found in documents"
    return "\n".join(chunks_found)

@tool
def search_web(query: str) -> str:
    """Search the web for current information, news, or anything 
    not in ZingTel's documents."""
    with DDGS() as ddgs:
        results = list(ddgs.text(query, max_results=3))
    if not results:
        return "No results found"
    output = ""
    for r in results:
        output += f"Title: {r['title']}\nSummary: {r['body']}\n\n"
    return output

@tool
def get_package_details(package_name: str) -> str:
    """Get ZingTel package pricing and details.
    Input: basic, standard, or premium"""
    packages = {
        "basic": "Rs. 300/month — 5GB data, 100 minutes, free SMS",
        "standard": "Rs. 600/month — 15GB data, 300 minutes, free SMS",
        "premium": "Rs. 1200/month — Unlimited data, unlimited minutes, free SMS"
    }
    return packages.get(package_name.lower(), "Package not found")

@tool
def calculate_total_cost(input_str: str) -> str:
    """Calculate total cost for a package over multiple months.
    Input format: 'package_name,months' — example: 'premium,12'"""
    try:
        parts = input_str.split(",")
        package = parts[0].strip().lower()
        months = int(parts[1].strip())
        prices = {"basic": 300, "standard": 600, "premium": 1200}
        if package not in prices:
            return "Package not found"
        total = prices[package] * months
        return f"{package.capitalize()} package for {months} months = Rs. {total}"
    except:
        return "Invalid format. Use: package_name,months"

@tool
def convert_to_usd(pkr_amount: str) -> str:
    """Convert Pakistani Rupees to USD.
    Input: amount in PKR as a number"""
    try:
        pkr = float(pkr_amount)
        usd = pkr / 278
        return f"Rs. {pkr:.0f} = ${usd:.2f} USD"
    except:
        return "Invalid amount"
    
tools = [search_zingtel_docs, search_web, get_package_details,
         calculate_total_cost, convert_to_usd]


memory = MemorySaver()

if llm is not None:
    try:
        agent = create_react_agent(
            llm,
            tools,
            checkpointer=memory,
            prompt="""You are Zara, ZingTel's intelligent customer support agent.

You have access to:
- ZingTel's official documents (use search_zingtel_docs)
- Web search for current information
- Package details and cost calculators
- Currency converter

Rules:
- Always search ZingTel docs first for company-specific questions
- Be professional, helpful, and concise
- Remember the conversation history
- If something isn't in your tools or documents, say so honestly"""
        )
    except Exception as e:
        print(f"Failed to create agent: {e}")
        agent = None
else:
    agent = None

# ──Chat with memory ────────────────────
# thread_id links messages together — same ID = same conversation memory
config = {"configurable": {"thread_id": "customer_001"}}

def chat(user_input):
    if agent is None:
        return "Zara is not available right now because the API limit has been reached. Please try again later."
    try:
        result = agent.invoke(
            {"messages": [HumanMessage(content=user_input)]},
            config=config
        )
        response = result["messages"][-1].content
        if isinstance(response, list):
            response = response[0].get('text', str(response))
        return response
    except Exception as e:
        print(f"Agent invocation failed: {e}")
        return "Zara is not available right now because the API limit has been reached. Please try again later."


if __name__ == '__main__':
    print("=== ZingTel Intelligent Support Agent ===")
    print("Powered by RAG + Memory + Web Search\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            print("Thank you for contacting ZingTel. Goodbye!")
            break
        answer = chat(user_input)
        print(f"\nZara: {answer}\n")
