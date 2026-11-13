"""Generator model and product catalog for Red Hat offerings."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Generator:
    """Represents a tiered Red Hat product offering that generates Red Hats passively."""

    id: str
    name: str
    base_cost: int
    base_hps: float
    description: str = ""
    unlock_requirement: float = 0.0
    count: int = 0
    multiplier: float = 1.0

    @property
    def total_hps(self) -> float:
        """Calculate total passive HPS output produced by this generator."""
        return self.count * self.base_hps * self.multiplier

    def is_unlocked(self, lifetime_hats: float) -> bool:
        """Check if this generator is unlocked based on lifetime Red Hats produced."""
        return lifetime_hats >= self.unlock_requirement


# 8 Tiered Red Hat Offerings Catalog Specification
GENERATOR_DEFINITIONS: list[dict] = [
    {
        "id": "rhel",
        "name": "Red Hat Enterprise Linux (RHEL)",
        "base_cost": 15,
        "base_hps": 0.1,
        "unlock_requirement": 0.0,
        "description": (
            "The world's leading enterprise Linux platform. Reliable workstation "
            "instances cranking out hats."
        ),
    },
    {
        "id": "ansible",
        "name": "Ansible Automation Platform",
        "base_cost": 100,
        "base_hps": 1.0,
        "unlock_requirement": 50.0,
        "description": (
            "Automation playbooks automating repetitive hat provisioning tasks across systems."
        ),
    },
    {
        "id": "satellite",
        "name": "Red Hat Satellite",
        "base_cost": 1100,
        "base_hps": 8.0,
        "unlock_requirement": 500.0,
        "description": (
            "Scalable infrastructure management patching, provisioning, and auditing hat nodes."
        ),
    },
    {
        "id": "openshift",
        "name": "Red Hat OpenShift",
        "base_cost": 12000,
        "base_hps": 47.0,
        "unlock_requirement": 5000.0,
        "description": (
            "Enterprise Kubernetes container platform scaling hat microservices across pods."
        ),
    },
    {
        "id": "openstack",
        "name": "Red Hat OpenStack Platform",
        "base_cost": 130000,
        "base_hps": 260.0,
        "unlock_requirement": 50000.0,
        "description": (
            "Private cloud infrastructure orchestrating virtualized hat compute instances."
        ),
    },
    {
        "id": "ceph",
        "name": "Red Hat Ceph Storage",
        "base_cost": 1400000,
        "base_hps": 1400.0,
        "unlock_requirement": 500000.0,
        "description": (
            "Massively scalable, software-defined storage holding exabytes of Red Hats."
        ),
    },
    {
        "id": "rhacm",
        "name": "Advanced Cluster Management (RHACM)",
        "base_cost": 20000000,
        "base_hps": 7800.0,
        "unlock_requirement": 8000000.0,
        "description": (
            "Fleet-wide governance, security, and multi-cluster orchestration for distributed hats."
        ),
    },
    {
        "id": "openshift_ai",
        "name": "Red Hat OpenShift AI",
        "base_cost": 330000000,
        "base_hps": 44000.0,
        "unlock_requirement": 100000000.0,
        "description": (
            "Train and deploy generative foundation models designed to invent new Red Hats."
        ),
    },
]


def get_default_generators() -> dict[str, Generator]:
    """Instantiate a fresh dictionary mapping generator IDs to Generator models."""
    return {
        item["id"]: Generator(
            id=item["id"],
            name=item["name"],
            base_cost=item["base_cost"],
            base_hps=item["base_hps"],
            description=item["description"],
            unlock_requirement=item["unlock_requirement"],
            count=0,
            multiplier=1.0,
        )
        for item in GENERATOR_DEFINITIONS
    }


GENERATOR_CATALOG: dict[str, Generator] = get_default_generators()
