from dataclasses import dataclass


@dataclass(frozen=True)
class RelationshipDefinition:
    source: str
    relation: str
    target: str
    description: str


CORE_OPERATIONAL_RELATIONSHIPS = (
    RelationshipDefinition(
        source="Project",
        relation="contains",
        target="WbsTemplate",
        description=(
            "Projects hold the construction taxonomy used for "
            "instantiation."
        ),
    ),
    RelationshipDefinition(
        source="Project",
        relation="contains",
        target="LocationNode",
        description=(
            "Projects own the hierarchical location tree used for "
            "location-aware execution."
        ),
    ),
    RelationshipDefinition(
        source="Project",
        relation="contains",
        target="WorkflowNode",
        description=(
            "Projects define the reusable operational nodes that shape "
            "possible execution paths."
        ),
    ),
    RelationshipDefinition(
        source="WorkflowNode",
        relation="connects_via",
        target="WorkflowEdge",
        description=(
            "Workflow edges define valid next-step paths, branches, and "
            "optional routes."
        ),
    ),
    RelationshipDefinition(
        source="WbsTemplate + LocationNode + WorkflowNode",
        relation="instantiate",
        target="ActivityInstance",
        description=(
            "Executable work emerges from taxonomy, place, and workflow "
            "context."
        ),
    ),
    RelationshipDefinition(
        source="ActivityInstance",
        relation="has_many",
        target="Dependency",
        description=(
            "Dependencies define lightweight activity-to-activity "
            "coordination."
        ),
    ),
    RelationshipDefinition(
        source="ActivityInstance",
        relation="has_many",
        target="Assignment",
        description=(
            "Assignments connect executable work to lightweight "
            "operational resources."
        ),
    ),
    RelationshipDefinition(
        source="Assignment",
        relation="connects",
        target="Resource",
        description=(
            "Assignments link manpower, materials, and equipment to "
            "activity instances."
        ),
    ),
    RelationshipDefinition(
        source="ActivityInstance",
        relation="generates",
        target="ProgressLog",
        description=(
            "Progress logs capture execution reality and become the "
            "operational truth layer."
        ),
    ),
)


def get_relationships_for(entity_name: str) -> list[RelationshipDefinition]:
    return [
        relation
        for relation in CORE_OPERATIONAL_RELATIONSHIPS
        if entity_name in {relation.source, relation.target}
    ]
