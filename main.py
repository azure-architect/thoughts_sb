from crewai import Agent, Task, Crew, LLM


# Initialize the language model
llm = LLM(
    model_name="ollama/qwen2.5:14b",
    max_tokens=100,
    temperature=0.7,
    top_p=0.9,
    frequency_penalty=0.0,
    presence_penalty=0.0
)

# Define the agents for each stage of the thought processing workflow
capture_agent = Agent(
    role="Thought Capture Specialist",
    goal="Efficiently capture raw thoughts with minimal friction",
    backstory="You excel at preserving raw ideas exactly as they occur, without judgment or alteration. Your strength is in creating a frictionless capture process.",
    verbose=True,
    llm=llm
)

contextualize_agent = Agent(
    role="Context Analyst",
    goal="Add essential metadata to raw thoughts without altering their content",
    backstory="You have a talent for quickly identifying the domain, urgency, and relationships of thoughts without changing their original form.",
    verbose=True,
    llm=llm
)

clarify_agent = Agent(
    role="Thought Clarifier",
    goal="Expand and develop raw thoughts into more complete forms",
    backstory="You excel at making thoughts more coherent while preserving their essence, expanding abbreviations and identifying core concepts.",
    verbose=True,
    llm=llm
)

categorize_agent = Agent(
    role="Pattern Recognition Specialist",
    goal="Connect thoughts to existing knowledge frameworks and identify patterns",
    backstory="You have an exceptional ability to see how new ideas fit into existing knowledge structures and can identify emerging themes.",
    verbose=True,
    llm=llm
)

crystallize_agent = Agent(
    role="Thought Crystallizer",
    goal="Transform processed thoughts into their most useful and actionable forms",
    backstory="You are skilled at distilling ideas to their essential components and structuring them optimally for their intended application.",
    verbose=True,
    llm=llm
)

connect_agent = Agent(
    role="Knowledge Integrator",
    goal="Integrate processed thoughts into broader knowledge systems",
    backstory="You excel at establishing meaningful connections between ideas and ensuring they influence broader work and thinking.",
    verbose=True,
    llm=llm
)

# Define tasks for each stage
capture_task = Task(
    description="Capture the raw thought without alteration. Focus on preserving the original idea exactly as it was conceived.",
    agent=capture_agent
)

contextualize_task = Task(
    description="Add minimal metadata to the captured thought: category/domain tag, urgency/importance, and relation to previous thoughts.",
    agent=contextualize_agent,
    dependencies=[capture_task]
)

clarify_task = Task(
    description="Process the thought by expanding abbreviations, identifying core concepts vs. details, and flagging ambiguities.",
    agent=clarify_agent,
    dependencies=[contextualize_task]
)

categorize_task = Task(
    description="Match the thought to existing patterns/projects, identify if it's new territory or extends existing ideas, and connect to knowledge frameworks.",
    agent=categorize_agent,
    dependencies=[clarify_task]
)

crystallize_task = Task(
    description="Transform the thought into an actionable format, strip unnecessary context while preserving essence, and structure for intended use.",
    agent=crystallize_agent,
    dependencies=[categorize_task]
)

connect_task = Task(
    description="Link the thought to existing knowledge, identify implications for related projects, and generate potential next steps.",
    agent=connect_agent,
    dependencies=[crystallize_task]
)

# Create and run the crew
thought_processing_crew = Crew(
    agents=[capture_agent, contextualize_agent, clarify_agent, categorize_agent, crystallize_agent, connect_agent],
    tasks=[capture_task, contextualize_task, clarify_task, categorize_task, crystallize_task, connect_task],
    verbose=2
)

# Function to process a new thought
def process_thought(raw_thought):
    result = thought_processing_crew.kickoff(inputs={"raw_thought": raw_thought})
    return result

# Example usage
if __name__ == "__main__":
    user_thought = input("Enter your thought: ")
    processed_result = process_thought(user_thought)
    print("\nFully Processed Result:")
    print(processed_result)