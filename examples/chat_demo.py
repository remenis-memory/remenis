from remenis import MemoryEngine

# Initialize your memory engine
memory = MemoryEngine()

def ai_chat_loop():
    print("--- Remenis Memory Chat Demo ---")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        
        # Skip search if user presses Enter on an empty line
        if not user_input:
            continue

        if user_input.lower() == 'exit':
            break

        # 1. Recall relevant past memories based on user input
        recalled = memory.recall(user_input, limit=2)
        
        if recalled:
            print("\n[AI Memory Context Found]:")
            for item in recalled:
                print(f"  - ({item['score']}) {item['content']}")
            print()

        # 2. Store the user's input as a new memory
        memory.store(user_input)
        print("AI: Got it, I've saved that into memory.\n")

if __name__ == "__main__":
    ai_chat_loop()
