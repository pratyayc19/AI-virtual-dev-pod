# memory/chroma_store.py
# Artifact Memory using ChromaDB RAG — Fixed by P1

import chromadb
import os

# Initialize ChromaDB
chroma_client = chromadb.Client()
artifact_collection = chroma_client.get_or_create_collection(name="dev_artifacts")

def save_artifact(artifact_id: str, content: str, metadata: dict = {}):
    """Save any agent output as an artifact."""
    try:
        artifact_collection.add(
            documents=[content],
            ids=[artifact_id],
            metadatas=[metadata]
        )
        print(f"✅ Artifact saved: {artifact_id}")
    except Exception as e:
        # Update if already exists
        artifact_collection.update(
            documents=[content],
            ids=[artifact_id],
            metadatas=[metadata]
        )
        print(f"✅ Artifact updated: {artifact_id}")

def get_artifact(query: str, n_results: int = 1):
    """Retrieve the most relevant artifact for a query."""
    try:
        results = artifact_collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results["documents"][0][0] if results["documents"] else None
    except Exception as e:
        print(f"⚠️ Retrieval warning: {e}")
        return None

def get_artifact_by_id(artifact_id: str):
    """Get a specific artifact by its ID."""
    try:
        results = artifact_collection.get(ids=[artifact_id])
        return results["documents"][0] if results["documents"] else None
    except Exception as e:
        print(f"⚠️ Get by ID warning: {e}")
        return None

if __name__ == "__main__":
    save_artifact("test_artifact", "This is a test user story", {"type": "user_story"})
    result = get_artifact("user story")
    print(f"✅ Retrieved: {result}")


