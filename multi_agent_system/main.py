from logger_setup import logger
from utils import write_final_result, save_state_snapshot
from nodes import (
    UserInputNode, ValidationNode, AgentNode, MemoryNode,
    PostAgentValidation, JudgeNode
)

DEFAULT_ROUNDS = 8  # exactly 8 rounds (4 per agent)

def build_initial_state(topic):
    return {
        "topic": topic,
        "round_index": 0,
        "max_rounds": DEFAULT_ROUNDS,
        "transcript": [],
        "agent_memory": {
            "Scientist": {"summary": "", "last_args": []},
            "Philosopher": {"summary": "", "last_args": []}
        },
        "last_speaker": "",
        "validation_errors": [],
        "judge_summary": "",
        "judge_winner": "",
        "judge_reason": ""
    }

def run_debate(topic):
    state = build_initial_state(topic)

    # UserInput node (logs and snapshot)
    UserInputNode(state)

    agents = ["Scientist", "Philosopher"]
    current = 0  # Scientist starts

    # run exactly 8 rounds
    for r in range(1, state["max_rounds"] + 1):
        state["round_index"] = r - 1  # zero-based used by AgentNode
        expected = agents[current]

        # Pre-turn validation (turn ordering)
        ValidationNode(state, expected)

        # Agent speaks (always executed to ensure 8 rounds)
        AgentNode(state, expected)

        # Post-generation validation (repetition/coherence)
        PostAgentValidation(state, expected)

        # Update memory for speaker (only their memory)
        MemoryNode(state, expected)

        # Update last speaker
        state["last_speaker"] = expected

        # Human-readable round line already logged by AgentNode, also snapshot state
        save_state_snapshot(state)

        # alternate
        current = 1 - current

    # After rounds, run JudgeNode
    JudgeNode(state)

    # Write final JSON result (full state)
    write_final_result(state)
    logger.info("Debate complete — outputs written to files.")
    return state

def main():
    # CLI: present prompt similar to assignment
    topic = input("Enter topic for debate: ").strip()
    if not topic:
        print("No topic provided. Exiting.")
        return
    run_debate(topic)

if __name__ == "__main__":
    main()
