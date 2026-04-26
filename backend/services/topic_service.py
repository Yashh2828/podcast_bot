import re
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.documents import Document
from backend.config import LLM_MODEL, HUGGINGFACE_API_TOKEN


def extract_topics_fallback(documents) -> list:
    """Fallback: Extract topics using keyword extraction when LLM fails."""
    print("⚠️ Using fallback topic extraction")
    
    # Combine all text
    all_text = " ".join([doc.page_content for doc in documents[:5]])
    all_text = all_text.lower()
    
    # Common topic keywords to look for
    common_topics = [
        "artificial intelligence", "machine learning", "deep learning", "neural networks",
        "technology", "innovation", "business", "startup", "entrepreneurship",
        "science", "research", "health", "medicine", "education", "environment",
        "climate", "sustainability", "economics", "finance", "investment",
        "marketing", "social media", "culture", "politics", "society"
    ]
    
    found_topics = []
    for topic in common_topics:
        if topic in all_text:
            found_topics.append(topic.title())
    
    # If still no topics, use generic ones based on document structure
    if not found_topics:
        # Extract first sentence of each paragraph as potential topics
        sentences = re.split(r'[.!?]+', all_text)
        for sent in sentences[:10]:
            sent = sent.strip()
            if len(sent) > 20 and len(sent) < 100:
                # Capitalize and clean
                topic = sent[:50].strip().title()
                if topic:
                    found_topics.append(topic)
    
    # Return unique topics, max 10
    unique_topics = list(dict.fromkeys(found_topics))[:10]
    
    # Ensure at least some generic topics
    if len(unique_topics) < 3:
        unique_topics = ["Key Insights", "Main Discussion Points", "Document Analysis"]
    
    return unique_topics


def extract_topics(documents) -> list:
    """Extract 5-10 topics from documents using LLM."""
    try:
        print(f"🔄 Initializing LLM for topic extraction ({LLM_MODEL})...")
        
        llm = HuggingFaceEndpoint(
            repo_id=LLM_MODEL,
            huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
            temperature=0.7,
            max_new_tokens=512,
            timeout=60
        )

        combined_content = "\n\n".join(
            [doc.page_content for doc in documents[:10]]
        )
        combined_content = combined_content[:3000]

        prompt = f"""<task>Extract podcast discussion topics from document content</task>

<document_content>
{combined_content}
</document_content>

<requirements>
- Extract exactly 5-10 distinct topics or themes
- Topics must be suitable for podcast discussion
- Each topic should be concise (1-5 words)
- Return ONLY the numbered list, nothing else
- Format: "1. Topic Name" on each line
</requirements>

<output_format>
1. Topic Name
2. Another Topic
3. Third Topic
(continue for 5-10 topics total)
</output_format>

Generate the topic list:"""

        print("🔄 Calling LLM for topic extraction...")
        response = llm.invoke(prompt)
        topics_text = response.strip()
        print(f"✓ LLM response received: {topics_text[:200]}...")

        topics = []
        for line in topics_text.strip().split("\n"):
            line = line.strip()
            if line and len(line) > 0 and line[0].isdigit():
                topic = line.lstrip("0123456789").lstrip(". ").strip()
                if topic:
                    topics.append(topic)

        result = topics[:10] if len(topics) > 10 else topics
        
        if len(result) >= 3:
            print(f"✓ Extracted {len(result)} topics from LLM")
            return result
        else:
            print(f"⚠️ Only {len(result)} topics from LLM, using fallback")
            return extract_topics_fallback(documents)
            
    except Exception as e:
        print(f"❌ LLM topic extraction failed: {str(e)}")
        print("⚠️ Falling back to keyword-based topic extraction")
        return extract_topics_fallback(documents)
