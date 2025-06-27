# Deployment

A deployment refers to the placement and configuration of a monitoring device in a specific location for a defined period of time. It includes metadata about the device, spatial coordinates, project links, and scheduling. Deployments represent the connection between hardware in the field and data collection efforts.

Each deployment is linked to a project and device, and is defined by when, where, and how data is collected. Below is a breakdown of the metadata fields associated with deployments.

Deployment ID: A short identifier to group related deployments

Device n: Numeric suffix of deployment, allowing for multiple deployments to share the same 'deployment_ID' and 'device_type'.

Deployment Device ID: Unique identifier combining 'deployment_ID', 'device_type' and 'device_n'.

Device: Specific device assigned to the deployment

Device Type: The type of sensor or equipment used

Deployment Start: Date and time the deployment begins

Deployment End: Date and time the deployment ends (can be empty if ongoing)

Is Active: Boolean flag checked hourly to determine whether the deployment is currently active

Site: Reference to the defined site where the deployment is located

Latitude / Longitude: GPS coordinates of the deployment

Point: GIS spatial point used in mapping the deployment

Time Zone: Local time zone of the deployment

Project: One or more projects associated with this deployment

Combo Project: String concatenation of all associated projects

Extra Data: Optional JSON-like field to store additional metadata

Thumb URL: Optional thumbnail image for deployment

Created On / Modified On: Timestamps for creation and latest update

Owner: The system user who created the deployment

Managers: Users with permission to manage the deployment

Annotators: Users assigned to annotate data collected in this deployment

Viewers: Users with view-only access to the deployment and its data
