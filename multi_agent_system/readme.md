🧠 Multi-Agent Debate System (LangGraph-Style DAG)
📌 Overview

This project implements a multi-agent debate system where two AI agents — a Scientist and a Philosopher — debate on any given topic for 8 rounds (4 arguments each).

The debate flow is modeled as a Directed Acyclic Graph (DAG) where:

UserInputNode → takes the debate topic.

Agent Nodes (Scientist & Philosopher) → alternate turns.

MemoryNode → each agent only sees their own relevant memory.

ValidationNode → ensures turn order, no repetition, logical coherence.

JudgeNode → summarizes debate and declares a winner with reasoning.

Logger → stores all transitions, states, and results.


📂project structure

multi_agent_system/
│── main.py                       # CLI runner
│── nodes.py                      # Node implementations
│── utils.py                      # Helper functions
│── logger_setup.py                # Centralized logger
│── diagram.py                    # Generates DAG diagram (Mermaid + PNG)
│── debate_log.txt                 # Debate log (auto-generated)
│── debate_state_snapshots.jsonl   # State snapshots (auto-generated)
│── final_debate_result.json       # Final winner & summary (auto-generated)
│── requirements.txt               # Dependencies
│── README.md                      # Documentation


⚙️ Setup Instructions
1. Install dependencies
pip install -r requirements.txt
2.pip install graphviz

How to run?//
▶️ Running the Debate

Run:

python main.py 

📊 DAG Diagram
Generate diagrams
python diagram.py
This creates:

diagram.md → Mermaid source (renders on GitHub / VS Code).

dag_diagram.png → Graphviz PNG image.
Logs & results are saved automatically:

debate_log.txt

debate_state_snapshots.jsonl

final_debate_result.json