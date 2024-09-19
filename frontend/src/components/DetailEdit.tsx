import React from "react";
import { Form, useSubmit } from "react-router-dom";
import FormSelect from "./FormSelect.tsx";
import FormSelectAPI from "./FormSelectAPI.tsx";
import FormDateSelector from "./FormDateSelector.tsx";
import { useState } from "react";
import FormSelectTZ from "./FormSelectTZ.tsx";
import FormDateTZSelect from "./FormDateTZSelect.tsx";

interface Props {
	selectedData?: object | null;
	onSubmit?: () => void;
	onCancel?: () => void;
}

const DetailEdit = ({ selectedData = null }: Props) => {
	const [deviceType, setDeviceType] = useState(
		selectedData ? selectedData["device_type_id"] : ""
	);

	const handleSetDeviceType = function (newval) {
		console.log("SET DEVICE TYPE " + newval);
		setDeviceType(newval);
	};

	return (
		<div>
			<Form
				id="detailForm"
				noValidate={true}
				className="row gy-2 gx-3 mb-3 align-items-center"
			>
				<input
					name="id"
					className="d-none"
					id="post-id"
					value={selectedData ? selectedData["id"] : ""}
					readOnly={true}
				/>
				<div className="form-floating">
					<input
						name="deploymentID"
						className="form-control"
						id="post-deployment"
						value={selectedData ? selectedData["deploymentID"] : ""}
						required
					/>
					<label htmlFor="post-deployment">deployment ID</label>
					<div className="form-text">
						ID for your deployment.
						<div className="invalid-feedback"></div>
					</div>
				</div>
				<div className="form-floating">
					<FormSelectAPI
						id="post-devicetype"
						name="device_type"
						label="Device type"
						choices={[]}
						defaultvalue={deviceType}
						apiURL="datatype/"
						valueKey="id"
						labelKey="name"
						handleChange={handleSetDeviceType}
						isClearable={false}
					/>

					<div className="form-text">
						Device type of your deployment
						<div className="invalid-feedback"></div>
					</div>
				</div>
				<div className="form-floating">
					<input
						name="device_n"
						className="form-control"
						id="post-device_n"
						defaultValue={selectedData ? selectedData["device_n"] : 1}
						type="number"
					/>
					<label htmlFor="post-device_n">Device number</label>
				</div>
				<div className="form-floating">
					<FormSelectAPI
						id="post-project"
						name="project"
						label="Projects"
						choices={[]}
						defaultvalue={selectedData ? selectedData["project_id"] : ""}
						apiURL="project/"
						valueKey="id"
						labelKey="projectID"
						multiple={true}
					/>
					<div className="form-text">
						Deployment project.
						<div className="invalid-feedback"></div>
					</div>
				</div>
				<div className="form-floating">
					<FormSelectAPI
						id="post-site"
						name="site"
						label="Site"
						choices={[]}
						defaultvalue={selectedData ? selectedData["site_id"] : ""}
						apiURL="site/"
						valueKey="id"
						labelKey="name"
						creatable={true}
					/>
					<div className="form-text">
						Deployment site. New sites can be added.
						<div className="invalid-feedback"></div>
					</div>
				</div>
				<div className="form-floating">
					<FormSelectAPI
						id="post-device"
						name="device"
						label="Device"
						choices={[]}
						defaultvalue={selectedData ? selectedData["device_id"] : null}
						apiURL={`device/?type=${deviceType}`}
						valueKey="id"
						labelKey="deviceID"
						creatable={false}
						isClearable={true}
					/>
					<div className="form-text">
						Deployment device.
						<div className="invalid-feedback"></div>
					</div>
				</div>
				<div className="form-floating">
					<FormDateTZSelect
						id="post-start_date"
						name="deploymentStart"
						label="Deployment started"
						text="Date and time deployment starts."
						defaultvalue={selectedData ? selectedData["deploymentStart"] : null}
					/>
				</div>
				<div className="form-floating">
					<FormDateTZSelect
						id="post-end_date"
						name="deploymentEnd"
						label="Deployment ended"
						text="Date and time deployment ends."
						defaultvalue={selectedData ? selectedData["deploymentEnd"] : null}
					/>
				</div>
				MAP GOES here EXTRA INFO GOES HERE
				<div className="d-grid gap-2 d-md-block mx-auto">
					<button className="btn btn-primary btn-lg">Save</button>
					<button className="btn btn-primary btn-lg">
						Save and keep editing
					</button>
					<button className="btn btn-danger btn-lg">Cancel</button>
				</div>
			</Form>
		</div>
	);
};

export default DetailEdit;
