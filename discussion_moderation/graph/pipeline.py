"""Facilitation pipeline: graph definition and entry point.

Assembles the graph nodes into a pydantic_graph Graph and
provides the run_pipeline() function as the main entry point.
"""

import sys

from pydantic_graph import Graph

from discussion_moderation.common.types import (
    DiscussionThread,
    PipelineDeps,
    PipelineResult,
    PipelineState,
)
from discussion_moderation.graph.nodes import (
    ClassifierEvalNode,
    ClassifierNode,
    OrchestratorNode,
    ResponseEvalNode,
    RoleNode,
    WriterNode,
)

facilitation_graph: Graph[PipelineState, PipelineDeps, PipelineResult] = Graph(
    nodes=(
        ClassifierNode,
        ClassifierEvalNode,
        OrchestratorNode,
        RoleNode,
        ResponseEvalNode,
        WriterNode,
    ),
    name="facilitation-pipeline",
)


async def run_pipeline(
    thread: DiscussionThread,
    deps: PipelineDeps,
) -> PipelineResult:
    """Run the facilitation pipeline on a discussion thread.

    Description:
        Entry point for the graph-based pipeline. Creates the
        initial state from the thread and executes the graph
        from the ClassifierNode.

    Args:
        thread: The discussion thread to analyze.
        deps: Pipeline dependencies (settings, toggles, LMS).

    Returns:
        PipelineResult with all intermediate results.
    """
    state = PipelineState(thread=thread)
    result = await facilitation_graph.run(
        start_node=ClassifierNode(),
        state=state,
        deps=deps,
    )
    return result.output


def _print_diagram() -> None:
    """Print the Mermaid diagram for the pipeline graph."""
    diagram = facilitation_graph.mermaid_code(
        start_node=(ClassifierNode,),
        title="Facilitation Pipeline",
    )
    print(diagram)


if __name__ == "__main__":
    if "--diagram" in sys.argv:
        _print_diagram()
    else:
        print("Usage: python -m discussion_moderation.graph.pipeline --diagram")
