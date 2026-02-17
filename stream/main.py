"""
Entry point for the multi-provider press release pipeline.

Registers all five press release providers with the orchestrator
and starts concurrent polling.

Usage:
    python -m stream.main
"""
from dotenv import load_dotenv
load_dotenv()

from stream.orchestrator import Orchestrator
from stream.config import PipelineConfig
from stream.providers import (
    PRNewswireProvider,
    GlobeNewswireProvider,
    BusinessWireProvider,
    NewsfileProvider,
    AccessNewswireProvider,
)


def main():
    config = PipelineConfig()
    orchestrator = Orchestrator(config)

    # Register all five press release providers
    orchestrator.register_provider(PRNewswireProvider())
    orchestrator.register_provider(GlobeNewswireProvider())
    orchestrator.register_provider(BusinessWireProvider())
    orchestrator.register_provider(NewsfileProvider())
    orchestrator.register_provider(AccessNewswireProvider())

    # Blocks forever — each provider polls in its own thread
    orchestrator.run()


if __name__ == "__main__":
    main()
