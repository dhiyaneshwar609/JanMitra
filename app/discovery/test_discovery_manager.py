from discovery_manager import DiscoveryManager

manager = DiscoveryManager()

manager.run(
    "../data/government_sources.json",
    "../data/government_websites.json"
)