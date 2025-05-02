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
		selectedData ? selectedData["project_ID"] : null
	);
	const [projectName, setProjectName] = useState(
		selectedData ? selectedData["name"] : null
	);
	const [objectives, setObjectives] = useState(
		selectedData ? selectedData["objectives"] : ""
	);
	const [principalInvestigator, setPrincipalInvestigator] = useState(
		selectedData ? selectedData["principal_investigator"] : ""
	);
	const [principalInvestigatorEmail, setPrincipalInvestigatorEmail] = useState(
		selectedData ? selectedData["principal_investigator_email"] : ""
	);
	const [contact, setContact] = useState(
		selectedData ? selectedData["contact"] : ""
	);
	const [contactEmail, setContactEmail] = useState(
		selectedData ? selectedData["contact_email"] : ""
	);
	const [organisation, setOrganisation] = useState(
		selectedData ? selectedData["organisation"] : ""
	);

	const resetDetailData = function () {
		onReset();
		setProjectName("");
		setProjectID("");
		setObjectives("");
		setPrincipalInvestigator("");
		setPrincipalInvestigatorEmail("");
		setContact("");
		setContactEmail("");
		setOrganisation("");
	};

	return (
		<DetailEditForm
			objectType="project"
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
						<label htmlFor="post-project_ID">Project ID</label>
						<input
							name="project_ID"
							className={`form-control ${
								wasValidated
									? errorDict["project_ID"]
										? "is-invalid"
										: "is-valid"
									: ""
							}`}
							id="post-project_ID"
							value={projectID}
							onChange={(e) => {
								setProjectID(e.target.value);
							}}
							required
						/>
						<div className="form-text">
							Short identifier for this project.
							<div className="invalid-feedback">{errorDict["project_ID"]}</div>
						</div>
					</div>
					<div className="col-md-4">
						<label htmlFor="post-name">Project name</label>
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
							value={projectName}
							onChange={(e) => {
								setProjectName(e.target.value);
							}}
							required
						/>
						<div className="form-text">
							Full name for project.
							<div className="invalid-feedback">{errorDict["name"]}</div>
						</div>
					</div>
				</div>
				<div className="row px-1 py-1 mb-3 border rounded">
					<div className="col-md-4">
						<label htmlFor="post-organisation">Organisation</label>
						<input
							name="organisation"
							className={`form-control ${
								wasValidated
									? errorDict["organisation"]
										? "is-invalid"
										: "is-valid"
									: ""
							}`}
							id="post-organisation"
							value={organisation}
							onChange={(e) => {
								setOrganisation(e.target.value);
							}}
							required
						/>
						<div className="form-text">
							Organization managing the project.
							<div className="invalid-feedback">
								{errorDict["organisation"]}
							</div>
						</div>
					</div>
					<div className="col-md-12">
						<label htmlFor="post-objectives">Objectives</label>
						<textarea
							name="objectives"
							className={`form-control ${
								wasValidated
									? errorDict["objectives"]
										? "is-invalid"
										: "is-valid"
									: ""
							}`}
							id="post-objectives"
							value={objectives}
							onChange={(e) => {
								setObjectives(e.target.value);
							}}
							required
						/>
						<div className="form-text">
							Project objectives.
							<div className="invalid-feedback">{errorDict["objectives"]}</div>
						</div>
					</div>
				</div>
				<div className="row px-1 py-1 mb-3 border rounded">
					<div className="col-md-6">
						<label htmlFor="post-principal_investigator">
							Principal Investigator
						</label>
						<input
							name="principal_investigator"
							className={`form-control ${
								wasValidated
									? errorDict["principal_investigator"]
										? "is-invalid"
										: "is-valid"
									: ""
							}`}
							id="post-principal_investigator"
							value={principalInvestigator}
							onChange={(e) => {
								setPrincipalInvestigator(e.target.value);
							}}
							required
						/>
						<div className="form-text">
							Name of the principal investigator.
							<div className="invalid-feedback">
								{errorDict["principal_investigator"]}
							</div>
						</div>
					</div>
					<div className="col-md-6">
						<label htmlFor="post-principal_investigator_email">
							Principal Investigator Email
						</label>
						<input
							type="email"
							name="principal_investigator_email"
							className={`form-control ${
								wasValidated
									? errorDict["principal_investigator_email"]
										? "is-invalid"
										: "is-valid"
									: ""
							}`}
							id="post-principal_investigator_email"
							value={principalInvestigatorEmail}
							onChange={(e) => {
								setPrincipalInvestigatorEmail(e.target.value);
							}}
							required
						/>
						<div className="form-text">
							Email of the principal investigator.
							<div className="invalid-feedback">
								{errorDict["principal_investigator_email"]}
							</div>
						</div>
					</div>
				</div>
				<div className="row px-1 py-1 mb-3 border rounded">
					<div className="col-md-6">
						<label htmlFor="post-contact">Contact</label>
						<input
							name="contact"
							className={`form-control ${
								wasValidated
									? errorDict["contact"]
										? "is-invalid"
										: "is-valid"
									: ""
							}`}
							id="post-contact"
							value={contact}
							onChange={(e) => {
								setContact(e.target.value);
							}}
							required
						/>
						<div className="form-text">
							Contact person for the project.
							<div className="invalid-feedback">{errorDict["contact"]}</div>
						</div>
					</div>
					<div className="col-md-6">
						<label htmlFor="post-contact_email">Contact Email</label>
						<input
							type="email"
							name="contact_email"
							className={`form-control ${
								wasValidated
									? errorDict["contact_email"]
										? "is-invalid"
										: "is-valid"
									: ""
							}`}
							id="post-contact_email"
							value={contactEmail}
							onChange={(e) => {
								setContactEmail(e.target.value);
							}}
							required
						/>
						<div className="form-text">
							Email of the contact person.
							<div className="invalid-feedback">
								{errorDict["contact_email"]}
							</div>
						</div>
					</div>
				</div>
			</>
		</DetailEditForm>
	);
};
export default DetailEditProject;
