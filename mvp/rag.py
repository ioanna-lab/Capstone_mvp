"""
RAG pipeline for the Lease Review Assistant.
Ingests uploaded lease documents into a local Chroma vector store
and answers questions across the full set.

Why Chroma local (not Pinecone):
- No API key needed
- Runs entirely in memory for the session
- Fast enough for 5 documents
- Easy to reset between demo runs
"""

from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langsmith import traceable

from prompts import RAG_SYSTEM, RAG_USER


# shared instances
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# text splitter: 1000 char chunks, 150 char overlap
# why these values: commercial lease clauses are typically 200-600 chars;
# 1000 char chunks keep clauses intact while 150 char overlap prevents
# a clause being split across two chunks with no context on either side
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def build_vectorstore(documents: dict) -> Chroma:
    """
    Build an in-memory Chroma vector store from a dict of {filename: text}.
    Each chunk is tagged with its source filename as metadata
    so the LLM can cite which document an answer came from.

    documents: dict mapping filename -> full extracted text
    returns: a Chroma vectorstore ready for similarity search
    """
    docs = []
    for filename, text in documents.items():
        chunks = splitter.split_text(text)
        for i, chunk in enumerate(chunks):
            docs.append(Document(
                page_content=chunk,
                metadata={
                    "source": filename,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                }
            ))

    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name="lease_portfolio",
    )
    return vectorstore


@traceable(name="query_lease_portfolio")
def query_portfolio(vectorstore: Chroma, question: str, k: int = 6) -> dict:
    """
    Answer a question across all ingested leases using RAG.

    Steps:
    1. Embed the question
    2. Retrieve k most similar chunks from Chroma
    3. Build context string with source citations
    4. Send to GPT-4o with RAG prompt
    5. Return answer + source chunks used

    k=6: retrieve 6 chunks which typically spans 2-3 different leases,
    giving the LLM enough context for cross-document comparison questions.

    Decorated with @traceable so LangSmith logs the retrieval + generation.
    """
    # step 1+2: retrieve relevant chunks
    retrieved = vectorstore.similarity_search(question, k=k)

    if not retrieved:
        return {
            "answer": "No relevant content found in the uploaded leases for this question.",
            "sources": [],
            "chunks_retrieved": 0,
        }

    # step 3: build context string
    context_parts = []
    sources_used = []
    for doc in retrieved:
        source = doc.metadata.get("source", "unknown")
        context_parts.append(f"[From: {source}]\n{doc.page_content}")
        if source not in sources_used:
            sources_used.append(source)

    context = "\n\n---\n\n".join(context_parts)

    # step 4: generate answer
    messages = [
        SystemMessage(content=RAG_SYSTEM),
        HumanMessage(content=RAG_USER.format(
            question=question,
            context=context,
        )),
    ]
    response = llm.invoke(messages)

    return {
        "answer": response.content,
        "sources": sources_used,
        "chunks_retrieved": len(retrieved),
    }
