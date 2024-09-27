import React from "react";
import { Form } from "react-router-dom";
import FormSelectAPI from "./FormSelectAPI.tsx";
import { useState, useRef, useEffect, useContext } from "react";
import FormDateTZSelect from "./FormDateTZSelect.tsx";
import { useMutation } from "@tanstack/react-query";
import AuthContext from "../context/AuthContext";
import { patchData, postData } from "../utils/FetchFunctions";
import { isValid } from "date-fns";
import FormMap from "./FormMap.tsx";

interface Props {
	selectedData?: object | null;
	onSubmit?: () => void;
	onCancel?: () => void;
}

const DetailEdit = ({
	selectedData = null,
	onSubmit = () => {},
	onCancel = () => {},
}: Props) => {
	const { authTokens } = useContext(AuthContext);

	const formRef = useRef(null);
	const [stopEdit, setStopEdit] = useState(false);

	const [deploymentID, setdeploymentID] = useState(
		selectedData ? selectedData["deploymentID"] : ""
	);
	const [device_type_id, setdevice_type_id] = useState(
		selectedData ? selectedData["device_type_id"] : null
	);
	const [device_n, setdevice_n] = useState(
		selectedData ? selectedData["device_n"] : 1
	);

	const [project_id, setproject_id] = useState(
		selectedData ? selectedData["project_id"] : []
	);

	const [site_id, setsite_id] = useState(
		selectedData ? selectedData["site_id"] : null
	);

	const [device_id, setdevice_id] = useState(
		selectedData ? selectedData["device_id"] : null
	);

	const [deploymentStart, setDeploymentStart] = useState(
		selectedData ? selectedData["deploymentStart"] : new Date().toJSON()
	);

	const [deploymentEnd, setDeploymentEnd] = useState(
		selectedData ? selectedData["deploymentEnd"] : null
	);

	const resetData = function () {
		setWasValidated(false);
		setErrorDict({});
		setdeploymentID("");
		setdevice_type_id(null);
		setdevice_n(null);
		setproject_id([]);
		setsite_id(null);
		setdevice_id(null);
		setDeploymentStart(new Date().toJSON());
		setDeploymentEnd(null);
	};

	useEffect(() => {
		handleFormChange();
	}, [
		device_type_id,
		project_id,
		site_id,
		device_id,
		deploymentStart,
		deploymentEnd,
	]);

	const [wasValidated, setWasValidated] = useState(false);
	const [errorDict, setErrorDict] = useState({});

	const doValidation = function (responseData = null) {
		let form = formRef.current;

		let newErrorDict = {};
		let valid = true;
		for (const input of form.getElementsByTagName("input")) {
			if (!responseData) {
				newErrorDict[input.name] = input.validationMessage;
			} else {
				let responseError = responseData[input.name];
				if (responseError) {
					newErrorDict[input.name] = responseData[input.name];
				} else {
					newErrorDict[input.name] = "";
				}
			}
			if (newErrorDict[input.name] != "") {
				valid = false;
			}
		}

		setErrorDict(newErrorDict);
		console.log(newErrorDict);
		console.log(errorDict);
		return valid;
	};

	const handleFormChange = function (e = null) {
		console.log("Form change " + wasValidated);
		if (wasValidated) {
			doValidation();
		}
	};

	const handleSubmission = async function (e) {
		e.preventDefault();
		let form = e.target;
		let formData = new FormData(form);

		console.log(formData);
		console.log(project_id);

		let addNew = formData.get("id") == "";
		//let allFormKeys = Array.from(formData.keys());
		//console.log(allFormKeys);
		setWasValidated(true);
		let formValid = doValidation();
		if (!formValid) {
			//addNotice("Error in submission", "error");
			return;
		}

		for (let [key, value] of formData.entries()) {
			if (value === "" && key != "project_id") {
				formData.delete(key);
			}
		}

		console.log("Add new :" + addNew);
		console.log(formData);

		let objData = Object.fromEntries(formData);
		objData["project_id"] = JSON.parse(objData["project_id"]);
		console.log(objData);
		let response;
		if (!addNew) {
			response = await doPatch.mutateAsync({
				apiURL: `deployment/${formData.get("id")}/`,
				newData: objData,
			});
		} else {
			response = await doPost.mutateAsync({
				apiURL: `deployment/`,
				newData: objData,
			});
		}

		console.log(response);

		if (!response["ok"]) {
			formValid = doValidation(response);
			if (!formValid) {
				return;
			}
		}
		if (stopEdit) {
			onSubmit(e, addNew, response);
		} else if (addNew) {
			resetData();
		}
	};

	const newPATCH = async function (x) {
		let response_json = await patchData(x.apiURL, authTokens.access, x.newData);
		//console.log(response_json);
		return response_json;
	};

	const doPatch = useMutation({
		mutationFn: (inputValue) => newPATCH(inputValue),
	});

	const newPOST = async function (x) {
		let response_json = await postData(x.apiURL, authTokens.access, x.newData);
		//console.log(response_json);
		return response_json;
	};

	const doPost = useMutation({
		mutationFn: (inputValue) => newPOST(inputValue),
	});

	return (
		<div>
			<Form
				id="detailForm"
				noValidate
				className={`row gy-2 gx-3 mb-3 align-items-center ${
					wasValidated ? "form-validated" : ""
				}`}
				onChange={handleFormChange}
				onSubmit={handleSubmission}
				ref={formRef}
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
						className={`form-control ${
							wasValidated
								? errorDict["deploymentID"]
									? "is-invalid"
									: "is-valid"
								: ""
						}`}
						id="post-deployment"
						value={deploymentID}
						onChange={(e) => {
							setdeploymentID(e.target.value);
						}}
						required
					/>
					<label htmlFor="post-deployment">deployment ID</label>
					<div className="form-text">
						ID for your deployment.
						<div className="invalid-feedback">{errorDict["deploymentID"]}</div>
					</div>
				</div>
				<div className="form-floating">
					<FormSelectAPI
						id="post-devicetype"
						name="device_type_id"
						label="Device type"
						choices={[]}
						value={device_type_id}
						apiURL="datatype/"
						valueKey="id"
						labelKey="name"
						handleChange={setdevice_type_id}
						isClearable={false}
						valid={errorDict["device_type_id"] == ""}
					/>
					<input
						hidden
						name="device_type_id"
						value={device_type_id ? device_type_id : ""}
						required
					></input>

					<div className="form-text">
						Device type of your deployment
						<div className="invalid-feedback">
							{errorDict["device_type_id"]}
						</div>
					</div>
				</div>
				<div className="form-floating">
					<input
						name="device_n"
						className={`form-control ${
							wasValidated
								? errorDict["deploymentID"]
									? "is-invalid"
									: "is-valid"
								: ""
						}`}
						id="post-device_n"
						value={device_n}
						type="number"
						onChange={setdevice_n}
						min={1}
						max={100}
						required
					/>
					<label htmlFor="post-device_n">Device number</label>
					<div className="form-text">
						Deployment ID number
						<div className="invalid-feedback">{errorDict["device_n"]}</div>
					</div>
				</div>
				<div className="form-floating">
					<FormSelectAPI
						id="post-project"
						name="project_id"
						label="Projects"
						choices={[]}
						value={project_id}
						apiURL="project/"
						valueKey="id"
						labelKey="projectID"
						multiple={true}
						handleChange={setproject_id}
						valid={errorDict["project_id"] == ""}
					/>
					<input
						hidden
						name="project_id"
						value={project_id ? JSON.stringify(project_id) : ""}
					></input>
					<div className="form-text">
						Deployment project.
						<div className="invalid-feedback">{errorDict["project_id"]}</div>
					</div>
				</div>
				<div className="form-floating">
					<FormSelectAPI
						id="post-site"
						name="site_id"
						label="Site"
						choices={[]}
						value={site_id}
						apiURL="site/"
						valueKey="id"
						labelKey="name"
						creatable={true}
						handleChange={setsite_id}
						valid={errorDict["site_id"] == ""}
					/>
					<input
						hidden
						name="site_id"
						value={site_id ? site_id : ""}
						required
					></input>
					<div className="form-text">
						Deployment site. New sites can be added.
						<div className="invalid-feedback">{errorDict["site_id"]}</div>
					</div>
				</div>
				<div className="form-floating">
					<FormSelectAPI
						id="post-device"
						name="device_id"
						label="Device"
						choices={[]}
						value={device_id}
						apiURL={device_type_id ? `device/?type=${device_type_id}` : ""}
						valueKey="id"
						labelKey="deviceID"
						creatable={false}
						isClearable={true}
						handleChange={setdevice_id}
						valid={errorDict["device_id"] == ""}
					/>
					<input
						hidden
						name="device_id"
						value={device_id ? device_id : ""}
						required
					></input>
					<div className="form-text">
						Deployment device.
						<div className="invalid-feedback">{errorDict["device_id"]}</div>
					</div>
				</div>
				<div className="form-floating">
					<FormDateTZSelect
						id="post-start_date"
						name="deploymentStart"
						label="Deployment started"
						text="Date and time deployment starts."
						defaultvalue={deploymentStart}
						handleChange={setDeploymentStart}
						required={true}
						valid={
							errorDict["deploymentStart"] == "" &&
							errorDict["deploymentStart_TZ"] == "" &&
							errorDict["deploymentStart_dt"] == ""
						}
						validated={wasValidated}
					/>
					<div className="form-text">
						Deployment start date time.
						<div className="invalid-feedback">
							{`${errorDict["deploymentStart"]} ${errorDict["deploymentStart_TZ"]} ${errorDict["deploymentStart_dt"]}`}
						</div>
					</div>
				</div>
				<div className="form-floating">
					<FormDateTZSelect
						id="post-end_date"
						name="deploymentEnd"
						label="Deployment ended"
						text="Date and time deployment ends."
						defaultvalue={deploymentEnd}
						handleChange={setDeploymentEnd}
						valid={
							errorDict["deploymentEnd"] == "" &&
							errorDict["deploymentEnd_TZ"] == "" &&
							errorDict["deploymentEnd_dt"] == ""
						}
						validated={wasValidated}
					/>
					<div className="form-text">
						Deployment end date time.
						<div className="invalid-feedback">{`${errorDict["deploymentEnd"]} ${errorDict["deploymentEnd_TZ"]} ${errorDict["deploymentEnd_dt"]}`}</div>
					</div>
				</div>
				MAP GOES here EXTRA INFO GOES HERE
				<FormMap />
				<div className="d-grid gap-2 d-md-block mx-auto">
					<button
						className="btn btn-primary btn-lg"
						type="submit"
						onClick={(e) => {
							setStopEdit(true);
						}}
					>
						Save
					</button>
					<button
						className="btn btn-primary btn-lg"
						type="submit"
						onClick={(e) => {
							setStopEdit(false);
						}}
					>
						Save and keep editing
					</button>
					<button
						className="btn btn-danger btn-lg"
						onClick={onCancel}
					>
						Cancel
					</button>
				</div>
			</Form>
		</div>
	);
};

export default DetailEdit;
