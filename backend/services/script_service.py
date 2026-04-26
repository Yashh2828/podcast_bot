import random
from langchain_huggingface import HuggingFaceEndpoint
from backend.config import LLM_MODEL, HUGGINGFACE_API_TOKEN
from backend.services.rag_pipeline import retrieve_context


def generate_fallback_script(
    host_name: str,
    guest_name: str,
    topics: list,
    duration: int,
) -> str:
    """Generate a basic fallback script when LLM fails."""
    print("⚠️ Using fallback script generation")
    
    # Create a simple conversational script with actual names
    lines = [
        f"[{host_name}]: Hey everyone, welcome back to the podcast! I'm {host_name}, and today I'm joined by {guest_name}.",
        f"[{guest_name}]: Hey {host_name}, thanks for having me on! Excited to be here.",
        f"[{host_name}]: Absolutely! So today we're going to talk about some really interesting topics. Let me just check my notes here... um, so we're looking at {', '.join(topics[:3]) if topics else 'some fascinating subjects'}.",
    ]
    
    # Add topic discussions
    for topic in topics[:5]:
        lines.extend([
            f"[{host_name}]: So let's dive into {topic}. What are your thoughts on that?",
            f"[{guest_name}]: Yeah, you know, {topic} is really interesting. I think there's a lot to unpack there. Basically, it's one of those areas where... um, you really need to look at the details.",
            f"[{host_name}]: Right? I mean, that's exactly what I was thinking. It's like... there's so much depth to it.",
            f"[{guest_name}]: Absolutely. And you know, people often overlook the nuances, but that's where the real insights come from.",
        ])
    
    # Add closing
    lines.extend([
        f"[{host_name}]: Well {guest_name}, this has been such a great conversation. I feel like we could keep going for hours!",
        f"[{guest_name}]: Ha! I know, right? Time flies when you're discussing interesting stuff.",
        f"[{host_name}]: For sure. Well, thanks so much for joining us today. This was really insightful.",
        f"[{guest_name}]: Thanks for having me, {host_name}. Always a pleasure!",
        f"[{host_name}]: And thanks to all our listeners. Catch you next time!",
    ])
    
    return "\n\n".join(lines)


def generate_script(
    host_name: str,
    guest_name: str,
    host_gender: str,
    guest_gender: str,
    host_speed: str,
    guest_speed: str,
    topics: list,
    duration: int,
) -> str:
    """Generate a realistic podcast script based on parameters and RAG context."""
    try:
        print(f"🔄 Initializing LLM for script generation ({LLM_MODEL})...")
        
        llm = HuggingFaceEndpoint(
            repo_id=LLM_MODEL,
            huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
            temperature=0.8,
            max_new_tokens=2048,
            timeout=120
        )

        word_count = duration * 150

        context_queries = " ".join(topics)
        retrieved_context = retrieve_context(context_queries, k=5)
        context_text = (
            "\n".join(retrieved_context) if retrieved_context else "No additional context"
        )

        gender_pronouns = {"male": "he/him", "female": "she/her", "other": "they/them"}
        host_pronoun = gender_pronouns.get(host_gender.lower(), "they/them")
        guest_pronoun = gender_pronouns.get(guest_gender.lower(), "they/them")

        def speed_to_text(speed) -> str:
            """Convert numeric speed (50-150) to descriptive text."""
            try:
                speed_val = int(speed)
                if speed_val <= 70:
                    return "speaking clearly and deliberately, with natural pauses"
                elif speed_val <= 120:
                    return "speaking at a conversational pace"
                else:
                    return "speaking energetically and quickly"
            except (ValueError, TypeError):
                return "speaking at a conversational pace"
        
        host_speed_text = speed_to_text(host_speed)
        guest_speed_text = speed_to_text(guest_speed)

        prompt = f"""<task>Create a realistic podcast script for two hosts having a natural conversation</task>

<participants>
Host: {host_name} ({host_gender}, {host_speed_text})
Guest: {guest_name} ({guest_gender}, {guest_speed_text})
</participants>

<topics>{", ".join(topics)}</topics>

<duration>{duration} minutes (~{word_count} words)</duration>

<background_context>
{context_text}
</background_context>

<format>
Use ONLY this format for output (use the actual names, not HOST/GUEST):
[{host_name}]: dialogue
[{guest_name}]: dialogue

Do not use any other format or labels. Always use the actual participant names in brackets.
</format>

<requirements>
- Create natural conversation with smooth topic transitions
- Include FREQUENT natural filler words throughout: "um", "uh", "hmm", "you know", "like", "right?", "so", "I mean", "basically"
- Use realistic back-and-forth with overlapping thoughts and interruptions
- Warm opening greeting with genuine enthusiasm and personal remarks
- Natural closing with thanks, goodbyes, and friendly remarks
- Conversational tone, NOT scripted or formal - sound like real people talking
- Natural pauses indicated by "..." where speakers think or react
- Include actual reactions: "Ha!", "Interesting!", "Exactly!", "Right!", "Yeah!"
- Integrate background context naturally into conversation - weave it in, don't list it
- Maintain speaking pace: {host_speed_text.split(",")[0]} for host, {guest_speed_text.split(",")[0]} for guest
- Create balance: about 50-50 speaking time between host and guest
- Target approximately {word_count} words of dialogue (not counting labels)
- Make it sound like two friends having a genuine discussion, not an interview
</requirements>

<instruction>Generate the podcast script now:</instruction>"""

        print("🔄 Calling LLM for script generation...")
        response = llm.invoke(prompt)
        print(f"✓ Script generated successfully ({len(response)} chars)")
        
        # Post-process to ensure names are used instead of generic labels
        script = response.strip()
        script = script.replace("[HOST]:", f"[{host_name}]:").replace("[GUEST]:", f"[{guest_name}]:")
        return script
        
    except Exception as e:
        print(f"❌ LLM script generation failed: {str(e)}")
        print("⚠️ Falling back to template-based script generation")
        return generate_fallback_script(host_name, guest_name, topics, duration)


def regenerate_script(
    host_name: str,
    guest_name: str,
    host_gender: str,
    guest_gender: str,
    host_speed: int,
    guest_speed: int,
    topics: list,
    duration: int,
    modification_request: str,
) -> str:
    """Regenerate a podcast script with specific modifications or improvements."""
    try:
        print(f"🔄 Initializing LLM for script regeneration ({LLM_MODEL})...")
        
        llm = HuggingFaceEndpoint(
            repo_id=LLM_MODEL,
            huggingfacehub_api_token=HUGGINGFACE_API_TOKEN,
            temperature=0.8,
            max_new_tokens=2048,
            timeout=120
        )

        word_count = duration * 150

        context_queries = " ".join(topics)
        retrieved_context = retrieve_context(context_queries, k=5)
        context_text = (
            "\n".join(retrieved_context) if retrieved_context else "No additional context"
        )

        gender_pronouns = {"male": "he/him", "female": "she/her", "other": "they/them"}
        host_pronoun = gender_pronouns.get(host_gender.lower(), "they/them")
        guest_pronoun = gender_pronouns.get(guest_gender.lower(), "they/them")

        def speed_to_text(speed: int) -> str:
            """Convert numeric speed (50-150) to descriptive text."""
            if speed <= 70:
                return "speaking clearly and deliberately, with natural pauses"
            elif speed <= 120:
                return "speaking at a conversational pace"
            else:
                return "speaking energetically and quickly"
        
        host_speed_text = speed_to_text(host_speed)
        guest_speed_text = speed_to_text(guest_speed)

        prompt = f"""<task>Regenerate a podcast script with specific improvements</task>

<modification_request>
{modification_request}
</modification_request>

<participants>
Host: {host_name} ({host_gender}, {host_speed_text})
Guest: {guest_name} ({guest_gender}, {guest_speed_text})
</participants>

<topics>{", ".join(topics)}</topics>

<duration>{duration} minutes (~{word_count} words)</duration>

<background_context>
{context_text}
</background_context>

<format>
Use ONLY this format for output (use the actual names, not HOST/GUEST):
[{host_name}]: dialogue
[{guest_name}]: dialogue

Do not use any other format or labels. Always use the actual participant names in brackets.
</format>

<requirements>
- Apply the modification request to improve the script
- Create natural conversation with smooth topic transitions
- Include FREQUENT natural filler words throughout: "um", "uh", "hmm", "you know", "like", "right?", "so", "I mean", "basically"
- Use realistic back-and-forth with overlapping thoughts and interruptions
- Warm opening greeting with genuine enthusiasm and personal remarks
- Natural closing with thanks, goodbyes, and friendly remarks
- Conversational tone, NOT scripted or formal - sound like real people talking
- Natural pauses indicated by "..." where speakers think or react
- Include actual reactions: "Ha!", "Interesting!", "Exactly!", "Right!", "Yeah!"
- Integrate background context naturally into conversation - weave it in, don't list it
- Maintain speaking pace: {host_speed_text.split(",")[0]} for host, {guest_speed_text.split(",")[0]} for guest
- Create balance: about 50-50 speaking time between host and guest
- Target approximately {word_count} words of dialogue (not counting labels)
- Make it sound like two friends having a genuine discussion, not an interview
</requirements>

<instruction>Generate the improved podcast script now:</instruction>"""

        print("🔄 Calling LLM for script regeneration...")
        response = llm.invoke(prompt)
        print(f"✓ Script regenerated successfully ({len(response)} chars)")
        
        # Post-process to ensure names are used instead of generic labels
        script = response.strip()
        script = script.replace("[HOST]:", f"[{host_name}]:").replace("[GUEST]:", f"[{guest_name}]:")
        return script
        
    except Exception as e:
        print(f"❌ LLM script regeneration failed: {str(e)}")
        print("⚠️ Falling back to template-based script generation")
        # For regeneration, we just generate a new script and add a note about the modification
        base_script = generate_fallback_script(host_name, guest_name, topics, duration)
        modification_note = f"\n\n[Modification requested: {modification_request}]\n"
        return modification_note + base_script
