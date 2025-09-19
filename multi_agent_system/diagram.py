from graphviz import Digraph
from logger_setup import logger

def write_mermaid(path="diagram.md"):
    mermaid = """flowchart TD
    U[UserInputNode: Enter topic]
    U --> R1[Round 1: Scientist]
    R1 --> R2[Round 2: Philosopher]
    R2 --> R3[Round 3: Scientist]
    R3 --> R4[Round 4: Philosopher]
    R4 --> R5[Round 5: Scientist]
    R5 --> R6[Round 6: Philosopher]
    R6 --> R7[Round 7: Scientist]
    R7 --> R8[Round 8: Philosopher]
    R8 --> J[JudgeNode: Summarize & Decide]
    J --> L[Logs & Final Verdict]
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(mermaid)
    logger.info("Wrote Mermaid diagram to %s", path)

def write_graphviz_png(output="dag_diagram"):
    """
    Attempt to render a PNG via Graphviz. If Graphviz system binary isn't installed,
    this function may raise; the caller can handle exceptions.
    """
    dot = Digraph(comment="Multi-Agent Debate DAG", format="png")
    dot.attr(rankdir="TB")

    dot.node("U", "UserInputNode\n(Enter topic)")
    for i in range(1, 9):
        role = "Scientist" if i % 2 != 0 else "Philosopher"
        dot.node(f"R{i}", f"Round {i}\n{role}")
    dot.node("J", "JudgeNode\n(Summary & Winner)")
    dot.node("L", "Logs & Final Verdict")

    dot.edge("U", "R1")
    for i in range(1, 8):
        dot.edge(f"R{i}", f"R{i+1}")
    dot.edge("R8", "J")
    dot.edge("J", "L")

    filename = dot.render(output, cleanup=True)
    logger.info("Graphviz PNG written: %s", filename)

if __name__ == "__main__":
    write_mermaid()
    try:
        write_graphviz_png()
    except Exception as e:
        logger.warning("Could not render Graphviz PNG (system Graphviz may be missing): %s", e)
        logger.info("Mermaid file is still available as diagram.md")
