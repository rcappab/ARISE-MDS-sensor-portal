import React, { useState } from "react";
import DetailEditForm from "./DetailEditForm.tsx";

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

const DetailEditProject = ({
	selectedData,
	onSubmit,
	onCancel,
	setErrorDict,
	setWasValidated,
	onReset = () => {},
	errorDict = {},
	wasValidated = false,
}: Props) => {
	const [projectID, setProjectID] = useState(
		selectedData ? selectedData["projectID"] : null
	);
	const [projectName, setProjectName] = useState(
		selectedData ? selectedData["projectName"] : null
	);

	const resetDetailData = function () {
		onReset();
		setProjectName("");
		setProjectID("");
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
		>
			<>
				<div className="row px-1 py-1 mb-3 border rounded">
					<div className="col-md-4">
						<label htmlFor="post-projectID">Project ID</label>
						<input
							name="projectID"
							className={`form-control ${
								wasValidated
									? errorDict["projectID"]
										? "is-invalid"
										: "is-valid"
									: ""
							}`}
							id="post-projectID"
							value={projectID}
							onChange={(e) => {
								setProjectID(e.target.value);
							}}
							required
						/>

						<div className="form-text">
							Short identifier for this project.
							<div className="invalid-feedback">{errorDict["projectID"]}</div>
						</div>
					</div>
					<div className="col-md-4">
						<label htmlFor="post-projectName">Oroject name</label>
						<input
							name="name"
							className={`form-control ${
								wasValidated
									? errorDict["projectName"]
										? "is-invalid"
										: "is-valid"
									: ""
							}`}
							id="post-device"
							value={projectName}
							onChange={(e) => {
								setProjectName(e.target.value);
							}}
							required
						/>

						<div className="form-text">
							Alternative name for device.
							<div className="invalid-feedback">{errorDict["projectName"]}</div>
						</div>
					</div>
				</div>
			</>
		</DetailEditForm>
	);
};
export default DetailEditProject;
