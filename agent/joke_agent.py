
import os
from dotenv import load_dotenv
from openai import OpenAI

# Initialize OpenAI
load_dotenv()
client = OpenAI(api_key=os.getenv("env_key"))


# Agent 1: Generate a joke
def joke_generator(topic):
    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.8,
        messages=[
            {
                "role": "system",
                "content": "You are a funny comedian. Create one short, funny joke."
            },
            {
                "role": "user",
                "content": f"Create a joke about: {topic}"
            }
        ]
    )

    return res.choices[0].message.content.strip()


# Agent 2: Rate the joke
def joke_rater(joke):
    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a joke evaluator. Rate the joke from 1 to 10 "
                    "based on humor, creativity, and relevance. "
                    "Return a score out of 10 and one short explanation."
                )
            },
            {
                "role": "user",
                "content": f"Rate this joke:\n{joke}"
            }
        ]
    )

    return res.choices[0].message.content.strip()


# Main workflow
def run_joke_agent(topic):
    if not isinstance(topic, str) or not topic.strip():
        return "Please provide a valid topic."

    # Agent-to-agent call 1: Generate the joke
    joke = joke_generator(topic.strip())

    # Agent-to-agent call 2: Rate the generated joke
    rating = joke_rater(joke)

    return {
        "topic": topic,
        "joke": joke,
        "rating": rating
    }


# Test the project
if __name__ == "__main__":
    topic = input("Enter a topic for your joke: ")

    result = run_joke_agent(topic)

    if isinstance(result, dict):
        print("\nTopic:", result["topic"])
        print("\nGenerated joke:", result["joke"])
        print("\nJoke rating:", result["rating"])
    else:
        print(result)
