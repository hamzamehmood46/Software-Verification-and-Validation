from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_ollama import ChatOllama


class State(TypedDict):
    spec: str
    route: str
    precise_spec: str
    test_case: str



llm = ChatOllama(model="llama3.2:3b", temperature=0)



def check_vagueness(state: State):
    prompt = f"""
    Decide if the following requirement is vague or not.

    Requirement: "{state['spec']}"

    If it contains unclear words like fast, secure, high-quality,
    timely, as appropriate, etc., then it is vague.

    Answer only: vague OR not_vague
    """

    result = llm.invoke(prompt).content.lower()

    if "not" in result:
        return {"route": "not_vague"}
    else:
        return {"route": "vague"}



def fix_vagueness(state: State):
    prompt = f"""
    Rewrite the following vague requirement
    to make it precise and measurable.

    Requirement: "{state['spec']}"

    Make it specific, testable and measurable.
    """

    result = llm.invoke(prompt).content

    return {"precise_spec": result}



def create_test_case(state: State):
    final_requirement = state.get("precise_spec") or state["spec"]

    prompt = f"""
    Create a software test case specification
    for the following requirement:

    "{final_requirement}"

    Use this format:

    Title:
    Preconditions:
    Test Data:
    Steps:
    Expected Result:
    """

    result = llm.invoke(prompt).content

    return {"test_case": result}



def build_graph():
    graph = StateGraph(State)

    graph.add_node("check_vagueness", check_vagueness)
    graph.add_node("fix_vagueness", fix_vagueness)
    graph.add_node("create_test_case", create_test_case)

    graph.add_edge(START, "check_vagueness")

    graph.add_conditional_edges(
        "check_vagueness",
        lambda state: state["route"],
        {
            "vague": "fix_vagueness",
            "not_vague": "create_test_case",
        },
    )

    graph.add_edge("fix_vagueness", "create_test_case")
    graph.add_edge("create_test_case", END)

    return graph.compile()



if __name__ == "__main__":
    app = build_graph()

    inputs = [
        "The system shall allow for fast, easy data entry",
        "Install high-quality flooring",
        "The application must be secure",
        "The report will include, as appropriate, investigation findings",
        "The project will be completed in a timely manner",
    ]

    for i, text in enumerate(inputs, start=1):
        print("\n========================")
        print(f"INPUT {i}: {text}")

        result = app.invoke({"spec": text})

        print("Route:", result["route"])

        if result["route"] == "vague":
            print("\nPrecise Specification:\n")
            print(result["precise_spec"])

        print("\nTest Case Specification:\n")
        print(result["test_case"])