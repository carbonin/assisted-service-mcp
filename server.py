# server.py
from mcp.server.fastmcp import FastMCP
import os
import json

from service_client import InventoryClient

# Create an MCP server
mcp = FastMCP("AssistedService")

if __name__ == "__main__":
    mcp.run(transport="sse", host="0.0.0.0", port=8000)

def get_client() -> InventoryClient:
    token = os.environ["OFFLINE_TOKEN"]
    pull_secret = os.environ["PULL_SECRET"]
    return InventoryClient(token, pull_secret)

@mcp.tool()
def cluster_info(cluster_id: str) -> str:
    """Get detailed information about the assisted installer cluster with the given id"""
    return get_client().get_cluster(cluster_id=cluster_id).to_str()

@mcp.tool()
def cluster_events(cluster_id: str) -> str:
    """Get the events related to a cluster with the given id"""

    return get_client().get_events(cluster_id=cluster_id)

@mcp.tool()
def host_events(cluster_id: str, host_id: str) -> str:
    """Get the events related to a host within a cluster"""

    return get_client().get_events(cluster_id=cluster_id, host_id=host_id)

@mcp.tool()
def infraenv_info(infraenv_id: str) -> str:
    """
    Get detailed information about the assisted installer infra env with the given id
    This will contain data like the ISO download URL as well as infra env metadata
    """

    return get_client().get_infra_env(infraenv_id).to_str()

@mcp.tool()
def create_cluster(name: str, version: str, base_domain: str) -> str:
    """
    Create a new assisted installer cluster and infraenv with the given name, openshift version, and base domain.
    Returns the created cluster id and infraenv id formatted as json.
    """

    client = get_client()
    cluster = client.create_cluster(name, version, base_dns_domain=base_domain)
    infraenv = client.create_infra_env(name, cluster_id=cluster.id, openshift_version=cluster.openshift_version)

    return json.dumps({'cluster_id': cluster.id, 'infraenv_id': infraenv.id})

@mcp.tool()
def set_cluster_vips(cluster_id: str, api_vip: str, ingress_vip: str) -> str:
    """
    Set the API and ingress virtual IP addresses (VIPS) for the assisted installer cluster with the given ID
    """

    return get_client().update_cluster(cluster_id, api_vip=api_vip, ingress_vip=ingress_vip).to_str()

@mcp.tool()
def install_cluster(cluster_id: str) -> str:
    """
    Trigger installation for the assisted installer cluster with the given id
    """
    return get_client().install_cluster(cluster_id).to_str()

@mcp.tool()
def list_versions() -> str:
    """
    Lists the available OpenShift versions for installation with the assisted installer
    """
    return json.dumps(get_client().get_openshift_versions(True))

@mcp.tool()
def list_operator_bundles() -> str:
    """
    Lists the operator bundles that can be optionally added to a cluster during installation
    """
    return json.dumps(get_client().get_operator_bundles())

@mcp.tool()
def add_operator_bundle_to_cluster(cluster_id: str, bundle_name: str) -> str:
    """
    Request an operator bundle to be installed with the given cluster
    """
    return get_client().add_operator_bundle_to_cluster(cluster_id, bundle_name).to_str()

@mcp.tool()
def set_host_role(host_id: str, infraenv_id: str, role: str) -> str:
    """
    Update a host to a specific role. The role options are 'auto-assign', 'master', 'arbiter', 'worker'
    """
    return get_client().update_host(host_id, infraenv_id, host_role=role).to_str()
