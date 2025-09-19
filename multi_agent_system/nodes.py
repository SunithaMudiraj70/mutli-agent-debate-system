import random
from logger_setup import logger
from utils import save_state_snapshot, similarity, tokenize, topic_keywords, now

# USER INPUT NODE
def UserInputNode(state):
    # log topic and starting notice
    logger.info("Starting debate between Scientist and Philosopher...")
    logger.info(f"[UserInputNode] Topic set: {state.get('topic')}")
    save_state_snapshot(state)

# AGENT NODE (Scientist / Philosopher)
def AgentNode(state, agent_name, tries=2):
    """
    Generate an argument for agent_name based on the topic and persona.
    Ensures at least one topic keyword appears; will retry up to `tries` times.
    """
    topic = state.get("topic", "")
    round_index = state.get("round_index", 0)
    mem = state["agent_memory"].get(agent_name, {"summary": "", "last_args": []})

    kws = topic_keywords(topic)
    # pick a focus keyword rotating through available keywords
    focus = kws[round_index % len(kws)]

    # persona templates per round-type (claim, evidence, implication, conclusion)
    scientist_templates = [
        f"AI evidence suggests {focus} poses measurable risks and needs oversight.",
        f"Data indicates that {focus} can cause harms without safeguards.",
        f"From a public-safety view, {focus} requires structured regulation.",
        f"In conclusion, regulation mitigates risks associated with {focus}."
    ]
    philosopher_templates = [
        f"Restricting {focus} risks undermining autonomy and philosophical inquiry.",
        f"Philosophically, the value of freedom around {focus} must be preserved.",
        f"Excess control of {focus} can stifle creativity and moral progress.",
        f"In conclusion, preserving freedom around {focus} supports human dignity."
    ]

    # choose template based on how many times agent has spoken
    template_index = len(mem.get("last_args", [])) % 4
    base_text = (scientist_templates if agent_name == "Scientist" else philosopher_templates)[template_index]

    # strengthen variation: add a small evidence or example fragment based on keyword
    example_fragments = [
        f" For example, recent studies about {focus} show measurable effects.",
        f" Consider historical cases involving {focus} that produced harm.",
        f" Surveys and reports on {focus} highlight community concerns."
    ]
    fragment = random.choice(example_fragments) if random.random() < 0.6 else ""

    text = base_text + fragment

    # Validate coherence: require at least one keyword (we used focus, so normally ok).
    # But still check: if not present, attempt a regeneration (tries times).
    attempt = 1
    while attempt <= tries:
        if any(k in tokenize(text) for k in kws):
            break
        # regenerate by appending the focus word clearly
        text = text + f" (topic: {focus})"
        attempt += 1

    # Save transcript entry
    entry = {"agent": agent_name, "text": text, "round": round_index + 1, "ts": now()}
    state.setdefault("transcript", []).append(entry)

    # Update per-agent memory (last_args)
    mem_last = mem.get("last_args", [])
    mem_last.append(text)
    mem_last = mem_last[-8:]
    state.setdefault("agent_memory", {})[agent_name] = {"summary": mem.get("summary", ""), "last_args": mem_last}

    logger.info(f"[Round {round_index+1}] {agent_name}: {text}")
    save_state_snapshot(state)

# MEMORY NODE (per-agent summary)
def MemoryNode(state, agent_name):
    msgs = [t["text"] for t in state.get("transcript", []) if t.get("agent") == agent_name]
    if not msgs:
        return
    # simple structured summary: take last 2 contributions and deduplicate phrases
    last_two = msgs[-2:]
    # compact uniqueness
    unique_clauses = []
    for s in last_two:
        if s not in unique_clauses:
            unique_clauses.append(s)
    summary = " ".join(unique_clauses)
    state.setdefault("agent_memory", {}).setdefault(agent_name, {})["summary"] = summary
    logger.debug(f"[MemoryNode] {agent_name} summary updated.")
    save_state_snapshot(state)

# VALIDATION NODE (pre-turn)
def ValidationNode(state, expected):
    errors = []
    last = state.get("last_speaker", "")
    if last == expected:
        msg = f"Turn violation: {expected} attempted to speak twice."
        errors.append(msg)
        logger.warning(msg)

    if errors:
        state.setdefault("validation_errors", []).extend(errors)
    save_state_snapshot(state)

# POST-AGENT VALIDATION (repetition, fuzzy-similarity, coherence)
def PostAgentValidation(state, agent_name):
    mem = state.get("agent_memory", {}).get(agent_name, {"last_args": []})
    last_args = mem.get("last_args", [])
    if len(last_args) < 2:
        return

    latest = last_args[-1]
    prev = last_args[-2]

    # exact repeat
    if latest.strip().lower() == prev.strip().lower():
        msg = f"{agent_name} repeated an argument verbatim."
        state.setdefault("validation_errors", []).append(msg)
        logger.warning(msg)

    # fuzzy similarity
    sim = similarity(latest, prev)
    if sim > 0.92:
        msg = f"{agent_name} repeated highly similar content (sim={sim:.2f})."
        state.setdefault("validation_errors", []).append(msg)
        logger.warning(msg)

    # coherence: latest must include at least one topic keyword
    kws = topic_keywords(state.get("topic", ""))
    tokens_latest = tokenize(latest)
    if kws and not any(k in tokens_latest for k in kws):
        msg = f"{agent_name}'s argument may not reference topic keywords."
        state.setdefault("validation_errors", []).append(msg)
        logger.warning(msg)

    save_state_snapshot(state)

# JUDGE NODE
def JudgeNode(state):
    sci_args = state.get("agent_memory", {}).get("Scientist", {}).get("last_args", [])
    phi_args = state.get("agent_memory", {}).get("Philosopher", {}).get("last_args", [])

    # scoring heuristics
    def score_agent(agent_name, args):
        score = 0
        for a in args:
            a_l = a.lower()
            # award more for persona keywords
            if agent_name == "Scientist":
                for k in ["safety","evidence","risk","regulated","data","research","experiment"]:
                    if k in a_l:
                        score += 2
                # minor award for specificity (presence of parentheses or examples)
                if "(" in a or "for example" in a_l or "studies" in a_l:
                    score += 1
            else:
                for k in ["freedom","autonomy","creativity","values","ethics","dignity","rights"]:
                    if k in a_l:
                        score += 2
                if "in conclusion" in a_l or "history" in a_l or "tradition" in a_l:
                    score += 1
            # base point for any contribution
            score += 1
        # penalties for repeats
        repeats = len(args) - len(set(args))
        score -= repeats * 2
        # penalties if validation errors mention this agent
        for v in state.get("validation_errors", []):
            if agent_name.lower() in v.lower():
                score -= 3
        return score

    sci_score = score_agent("Scientist", sci_args)
    phi_score = score_agent("Philosopher", phi_args)

    # Decide winner with tie-breaker using fewer validation hits and then Scientist preference
    if sci_score > phi_score:
        winner = "Scientist"
        reason = "Presented more grounded, risk-based arguments aligned with public safety principles."
    elif phi_score > sci_score:
        winner = "Philosopher"
        reason = "Presented stronger ethical reasoning emphasizing freedom and creativity."
    else:
        # tie-breaker: fewer validation mentions
        sci_issues = sum(1 for v in state.get("validation_errors", []) if "scientist" in v.lower())
        phi_issues = sum(1 for v in state.get("validation_errors", []) if "philosopher" in v.lower())
        if sci_issues < phi_issues:
            winner = "Scientist"
            reason = "Tie on score; Scientist had fewer validation issues."
        elif phi_issues < sci_issues:
            winner = "Philosopher"
            reason = "Tie on score; Philosopher had fewer validation issues."
        else:
            winner = "Scientist"
            reason = "Scores tied and validation equal; preferring Scientist for practical grounding."

    # Build a readable summary
    summary_lines = []
    summary_lines.append("Summary of debate:")
    summary_lines.append("Scientist: " + " ".join(sci_args))
    summary_lines.append("Philosopher: " + " ".join(phi_args))

    summary = "\n".join(summary_lines)

    logger.info("[Judge] Summary of debate:\n%s", summary)
    logger.info("[Judge] Winner: %s", winner)
    logger.info("Reason: %s", reason)

    state["judge_summary"] = summary
    state["judge_winner"] = winner
    state["judge_reason"] = reason
    save_state_snapshot(state)
