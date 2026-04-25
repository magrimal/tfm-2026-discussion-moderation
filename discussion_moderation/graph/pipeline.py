"""Facilitation pipeline: graph definition and entry point.

Assembles the graph nodes into a pydantic_graph Graph and
provides the run_pipeline() function as the main entry point.
"""

from pydantic_graph import Graph

from discussion_moderation.graph.nodes import (
    ClassificationNode,
    InterventionNode,
    OrchestratorNode,
    RoleNode,
)
from discussion_moderation.models import (
    DiscussionThread,
    PipelineDeps,
    PipelineResult,
    PipelineState,
)

facilitation_graph: Graph[PipelineState, PipelineDeps, PipelineResult] = Graph(
    nodes=(
        ClassificationNode,
        InterventionNode,
        OrchestratorNode,
        RoleNode,
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
        from the ClassificationNode.

    Args:
        thread: The discussion thread to analyze.
        deps: Pipeline dependencies (settings, toggles, LMS).

    Returns:
        PipelineResult with all intermediate results.
    """
    state = PipelineState(thread=thread)
    result = await facilitation_graph.run(
        start_node=ClassificationNode(),
        state=state,
        deps=deps,
    )
    return result.output


def print_diagram() -> None:
    """Print the Mermaid diagram for the pipeline graph."""
    diagram = facilitation_graph.mermaid_code(
        start_node=(ClassificationNode,),
        title="Facilitation Pipeline",
    )
    print(diagram)
