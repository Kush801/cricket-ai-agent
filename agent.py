import os
from groq import Groq
from sentence_transformers import SentenceTransformer
import chromadb
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

client_groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Load match data ──
df = pd.read_csv("match_data.csv")
df = df[df["Winner"] != "No Result"]

# Convert to sentences
sentences = []
for _, row in df.iterrows():
    sentence = f"{row['Team1']} vs {row['Team2']} at {row['Venue']} on {row['Date']}. {row['Winner']} won."
    sentences.append(sentence)

print(f"Total matches: {len(sentences)}")

#text convesion to numbers
embed_model = SentenceTransformer("all-MiniLM-L6-v2")
embed = embed_model.encode(sentences)

#storing in vector database
client= chromadb.Client()
collection = client.create_collection("cricket_matches")
collection.add(
    documents=sentences,
    embeddings=embed.tolist(),
    ids=[str(i) for i in range(len(sentences))]
)
print(f"Loaded {len(sentences)} matches into vector database!")

# search function
def search_matches(query):
    query_vector = embed_model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_vector,
        n_results=3
    )
    matches = results["documents"][0]
    return "\n".join([f"{i+1}. {m}" for i, m in enumerate(matches)])


# agent
def ask_agent(user_input):
    # Step 1 — search cricket data using RAG
    print("Searching match data...")
    search_results = search_matches(user_input)
    print(f"Found:\n{search_results}\n")

    # Step 2 — send to Groq LLM with search results as context
    print("Thinking...")
    response = client_groq.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a cricket expert assistant. Answer questions based only on the match data provided to you. Be concise and clear."
            },
            {
                "role": "user",
                "content": f"Here is the match data:\n{search_results}\n\nNow answer this question: {user_input}"
            }
        ]
    )
    return response.choices[0].message.content

# ── Chat loop ──
print("\nCricket AI Agent ready!")
print("Type 'exit' to quit\n")

while True:
    user_input = input("You: ")
    
    if user_input.lower() == "exit":
        print("Goodbye!")
        break
    
    answer = ask_agent(user_input)
    print("\nAgent:", answer)
    print()