# Device

A device represents a physical data collection unit (e.g., wildlife camera, acoustic sensor) that is used in the field to record observations. Each device has a unique identifier and is associated with storage credentials, data input schedules, and user permissions. Devices can be reused across multiple deployments.
Device metadata is essential for identifying equipment, ensuring data traceability, and managing updates and file transfers.

Device ID: Unique identifier for the device, usually based on serial number

Name: Optional human-readable alias for the device (e.g. last 4 digits of the serial number)

Model: Hardware model

Type: The general type of the device (e.g. wildlifecamera, insectcamera)

Managers: Users with management permissions over this device

Viewers: Users with view-only access to device information

Annotators: Users allowed to annotate data collected from the device

Autoupdate: Boolean field indicating if the device is expected to push updates automatically

Update Time: Expected file delivery interval, in hours (e.g, 48 = send alert if no files arrive after 48 hours)

Username / Password: Credentials for accessing external storage, such as an FTP server

Input Storage: Name of external storage service where data is expected to be uploaded (e.g. uva-FTP)

Extra Data: JSON-like field for storing any additional information not covered by standard fields

Owner: Person or system user responsible for the device record
