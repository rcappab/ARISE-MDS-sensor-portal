import React, { useState } from "react";
import DetailEditForm from "./DetailEditForm.tsx";
import JSONInput from "../General/JSONInput.tsx";
import FormSelectAPI from "../Forms/FormSelectAPI.tsx";
import DetailDisplayStorage from "./DetailDisplayStorage.tsx";

interface Props {
	selectedData?: object | null;
	onSubmit?: (e: Event, addNew: boolean, response: object) => void;
	onCancel?: (e: any) => void;
	setErrorDict: (newVal: object) => void;
	setWasValidated: (newVal: boolean) => void;
	onReset: () => void;
	errorDict: object;
	wasValidated: boolean;
}

const DetailEditDevice = ({
	selectedData,
	onSubmit,
	onCancel,
	setErrorDict,
	setWasValidated,
	onReset = () => {},
	errorDict = {},
	wasValidated = false,
}: Props) => {
	const [typeID, setTypeID] = useState(
		selectedData ? selectedData["type_ID"] : null
	);

	const [storageID, setStorageID] = useState(
		selectedData ? selectedData["input_storage"] : null
	);

	const [modelID, setModelID] = useState(
		selectedData ? selectedData["model_ID"] : null
	);

	const [deviceID, setDeviceID] = useState(
		selectedData ? selectedData["device_ID"] : null
	);
	const [deviceName, setDeviceName] = useState(
		selectedData ? selectedData["name"] : null
	);
	const [extraData, setExtraData] = useState(
		selectedData ? selectedData["extra_data"] : {}
	);

	const [autoUpdate, setAutoUpdate] = useState(
		selectedData ? selectedData["autoupdate"] : false
	);

	const [updateTime, setUpdateTime] = useState(
		selectedData ? selectedData["update_time"] : 48
	);

	const [username, setUsername] = useState(
		selectedData ? selectedData["username"] : null
	);

	const [password, setPassword] = useState(
		selectedData ? selectedData["password"] : null
	);

	const onStorageChange = (value) => {
		setStorageID(value);
		setUsername("");
		setPassword("");
	};

	const resetDetailData = function () {
		onReset();
		setDeviceID("");
		setDeviceName("");
		setTypeID(null);
		setModelID(null);
		setExtraData({});
		setAutoUpdate(true);
		setUpdateTime(48);
		setStorageID(null);
		setUsername("");
		setPassword("");
	};

	return (
		<DetailEditForm
			objectType="device"
			setErrorDict={setErrorDict}
			wasValidated={wasValidated}
			setWasValidated={setWasValidated}
			selectedData={selectedData}
			onSubmit={onSubmit}
			onCancel={onCancel}
			onReset={resetDetailData}
			JSONFields={["extra_data"]}
		>
			<>
				<div className="row px-1 py-1 mb-3 border rounded">
					<div className="col-md-4">
						<label htmlFor="post-device_ID">Device ID</label>
						<input
							name="device_ID"
							className={`form-control ${
								wasValidated
									? errorDict["device_ID"]
										? "is-invalid"
										: "is-valid"
									: ""
							}`}
							id="post-device_ID"
							value={deviceID}
							onChange={(e) => {
								setDeviceID(e.target.value);
							}}
							required
						/>

						<div className="form-text">
							Unique identifier for this device.
							<div className="invalid-feedback">{errorDict["device_ID"]}</div>
						</div>
					</div>
					<div className="col-md-4">
						<label htmlFor="post-name">Device name</label>
						<input
							name="name"
							className={`form-control ${
								wasValidated
									? errorDict["name"]
										? "is-invalid"
										: "is-valid"
									: ""
							}`}
							id="post-name"
							value={deviceName}
							onChange={(e) => {
								setDeviceName(e.target.value);
							}}
							required
						/>

						<div className="form-text">
							Alternative name for device.
							<div className="invalid-feedback">{errorDict["name"]}</div>
						</div>
					</div>
				</div>
				<div className="row px-1 py-1 mb-3 border rounded">
					<div className="col-md-4">
						<label htmlFor="post-type_ID">Device type</label>
						<FormSelectAPI
							id="post-type_ID"
							name="type_ID"
							label="Device type"
							choices={[]}
							value={typeID}
							apiURL="datatype/"
							valueKey="id"
							labelKey="name"
							handleChange={setTypeID}
							isClearable={false}
							valid={errorDict["type_ID"] === ""}
						/>
						<input
							hidden
							id="hidden-post-type_ID"
							name="type_ID"
							value={typeID ? typeID : ""}
							required
						></input>

						<div className="form-text">
							Device type.
							<div className="invalid-feedback">{errorDict["type_ID"]}</div>
						</div>
					</div>
					<div className="col-md-4">
						<label htmlFor="post-model_ID">Device model</label>
						<FormSelectAPI
							id="post-model_ID"
							name="model_ID"
							label="Device model"
							choices={[]}
							value={modelID}
							apiURL={typeID !== null ? `devicemodel/?type=${typeID}` : ""}
							valueKey="id"
							labelKey="name"
							handleChange={setModelID}
							isClearable={false}
							valid={errorDict["model_ID"] === ""}
						/>
						<input
							hidden
							id="hidden-post-model_ID"
							name="model_ID"
							value={modelID ? modelID : ""}
							required
						></input>

						<div className="form-text">
							Device model.
							<div className="invalid-feedback">{errorDict["model_ID"]}</div>
						</div>
					</div>
				</div>

				<div className="row px-1 py-1 mb-3 border rounded">
					<div className="row">
						<div className="col-md-4">
							<label htmlFor="post-input_storage">Import storage</label>
							<FormSelectAPI
								id="post-input_storage"
								name="input_storage"
								label="Input storage"
								choices={[]}
								value={storageID}
								apiURL="datastorageinput/"
								valueKey="id"
								labelKey="name"
								apiSearchKey={"name"}
								handleChange={onStorageChange}
								isClearable={true}
								valid={errorDict["input_storage"] === ""}
							/>
							<input
								hidden
								id="hidden-post-input_storage"
								name="input_storage"
								value={modelID ? modelID : ""}
								required
							></input>

							<div className="form-text">
								Storage to which device will transmit files.
								<div className="invalid-feedback">
									{errorDict["input_storage"]}
								</div>
							</div>
						</div>
						{storageID !== null &&
						(!selectedData || selectedData["input_storage"] !== storageID) ? (
							<>
								<div className="col-md-4">
									<label htmlFor="post-username">Username</label>
									<input
										name="username"
										className={`form-control ${
											wasValidated
												? errorDict["username"]
													? "is-invalid"
													: "is-valid"
												: ""
										}`}
										id="post-username"
										value={username}
										onChange={(e) => {
											setUsername(e.target.value);
										}}
									/>

									<div className="form-text">
										Device username for storage.
										<div className="invalid-feedback">
											{errorDict["username"]}
										</div>
									</div>
								</div>
								<div className="col-md-4">
									<label htmlFor="post-password">Password</label>
									<input
										name="password"
										type="password"
										className={`form-control ${
											wasValidated
												? errorDict["password"]
													? "is-invalid"
													: "is-valid"
												: ""
										}`}
										id="post-password"
										value={password}
										onChange={(e) => {
											setPassword(e.target.value);
										}}
									/>
									<div className="form-text">
										Device password for storage.
										<div className="invalid-feedback">
											{errorDict["password"]}
										</div>
									</div>
								</div>
							</>
						) : null}
					</div>

					{storageID !== null ? (
						<>
							<br />
							<DetailDisplayStorage selectedDataID={storageID} />
							<div className="row">
								<div className="form-text">
									A username and password are required for the device to
									transmit files to the storage. These will be used for the
									device to log on to the storage. On initial setup, a user
									account will be created for the device. Username and password
									cannot be updated if the device is already set up with that
									storage. If you need to change a device's username or
									password, please contact your system administrator.
								</div>
							</div>
						</>
					) : null}
				</div>
				<div className="row px-1 py-1 mb-3 border rounded">
					<div className="col-md-4">
						<label htmlFor="post-autoupdate">Email alerts</label>
						<div
							className={`form-check form-switch form-control  ${
								wasValidated
									? errorDict["autoupdate"]
										? "is-invalid"
										: "is-valid"
									: ""
							}`}
						>
							<label htmlFor="post-autoupdate">Enable</label>
							<input
								name="autoupdate"
								className="form-check-input form-control"
								id="post-autoupdate"
								value={autoUpdate ? "true" : "false"}
								type="checkbox"
								onChange={(e) => {
									setAutoUpdate(e.target.checked);
								}}
							/>
						</div>
						<div className="form-text">
							Alert managers if device does not transmit files in alloted time.
							<div className="invalid-feedback">{errorDict["autoupdate"]}</div>
						</div>
					</div>
					{autoUpdate ? (
						<div className="col-md-4">
							<label htmlFor="post-update_time">Update time</label>
							<input
								name="update_time"
								className={`form-control ${
									wasValidated
										? errorDict["update_time"]
											? "is-invalid"
											: "is-valid"
										: ""
								}`}
								id="post-update_time"
								value={updateTime}
								type="number"
								onChange={setUpdateTime}
								min={1}
							/>
							<div className="form-text">
								Expected update time before alerting managers(hours)
								<div className="invalid-feedback">
									{errorDict["update_time"]}
								</div>
							</div>
						</div>
					) : null}
				</div>
				<div className="row px-1 py-1 mb-3 border rounded">
					<label htmlFor="post-extra_data">Extra fields</label>
					<JSONInput
						id="post-extra_data"
						name="extra_data"
						value={extraData}
						onJSONchange={setExtraData}
						wasValidated={wasValidated}
						errorDict={errorDict["extra_data"] ? errorDict["extra_data"] : {}}
					/>
				</div>
			</>
		</DetailEditForm>
	);
};

export default DetailEditDevice;
