from crewai import Agent, Crew, Task
from remenis.adapters import RemenisCrewAIMemory

# Drop-in persistent memory with local zlib level-9 compression & SQLite-Vec
memory = RemenisCrewAIMemory(storage_path="crew_session.rmns")

researcher = Agent(
    role='Senior Research Analyst',
    goal='Uncover cutting-edge AI infrastructure trends',
    backstory='Obsessed with local-first execution and edge computing.',
    memory=memory  # Powered by Remenis LSER binary backend
)

print("[SUCCESS] CrewAI agent loop secured with Remenis .rmns memory backend.")
