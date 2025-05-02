import React, { useCallback, useContext, useEffect, useState } from "react";
import FormSelectAPI from "./FormSelectAPI.tsx";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import AuthContext from "../context/AuthContext";
import {
	deleteData,
	getData,
	patchData,
	postData,
} from "../utils/FetchFunctions.js";
import AsyncCreatableSelect from "react-select/async-creatable";
import { debounce } from "lodash";
import { formatInTimeZone } from "date-fns-tz";
import toast from "react-hot-toast";
import "../styles/observationform.css";

interface speciesSelectorProps {
	obsData?: object;
	handleSelection?: (newValue) => void;
}

const SpeciesSelector = ({
	obsData,
	handleSelection = (newValue) => {},
}: speciesSelectorProps) => {
	const { authTokens } = useContext(AuthContext);
	const queryClient = useQueryClient();
	const [inputValue, setInputValue] = useState("");

	const fetchOptions = async (inputValue, apiURL) => {
		let fullAPIURL = `${apiURL}${inputValue}`;
		let response_json = await getData(fullAPIURL, authTokens.access);
		if ("results" in response_json) {
			response_json = response_json["results"];
		}

		return response_json;
	};

	const loadOptions = debounce(async (inputValue, callback) => {
		const newData = await queryClient.fetchQuery({
			queryKey: ["taxon", inputValue],
			queryFn: () => fetchOptions(inputValue, "taxon?search="),
		});
		callback(newData);
	}, 500);

	const [speciesName, setSpeciesName] = useState(
		obsData !== undefined
			? {
					species_name: obsData["species_name"],
					species_common_name: obsData["species_common_name"],
			  }
			: { species_name: "", species_common_name: "" }
	);

	const style = {
		container: (baseStyles, state) => ({
			...baseStyles,
			padding: "0rem !important",
		}),
		control: (baseStyles, state) => ({
			...baseStyles,
			height: "100% !important",
			boxShadow: state.isFocused ? "0 0 0 .25rem rgba(13,110,253,.25)" : "none",
			borderColor: state.isFocused ? "#86b7fe" : "var(--bs-border-color)",
			"&:hover": {
				borderColor: state.isFocused ? "#86b7fe" : "var(--bs-border-color)",
			},
		}),
		menu: (base) => ({
			...base,
			width: "max-content",
			minWidth: "100%",
		}),
	};

	return (
		<AsyncCreatableSelect
			className={"form-control-sm"}
			//placeholder={""}
			cacheOptions={true}
			name={"species_name"}
			loadOptions={loadOptions}
			value={speciesName}
			noOptionsMessage={({ inputValue }) =>
				!inputValue || inputValue === "" ? "Type to search" : "No options found"
			}
			onChange={(selected) => {
				setSpeciesName(selected);
				handleSelection(selected);
			}}
			loadingMessage={() => "Loading..."}
			isSearchable={true}
			createOptionPosition={"first"}
			getOptionLabel={(e) => {
				let new_label = e["species_name"];
				if (e["species_common_name"] && e["species_common_name"] !== "") {
					new_label += ` - ${e["species_common_name"]}`;
				}
				return new_label;
			}}
			getOptionValue={(e) => {
				return e["species_name"];
			}}
			inputValue={inputValue}
			onInputChange={setInputValue}
			styles={style}
			required={true}
			getNewOptionData={(inputValue) => {
				return { species_name: inputValue, species_common_name: "" };
			}}
		/>
	);
};

interface obsFormRowProps {
	index: number;
	fileData: object;
	obsData?: object;
	onEdit?: (newObjData) => void;
	onAdd?: (copiedData) => void;
	onEditBoundingBox?: (index) => void;
	onHover?: (index) => void;
}

const ObservationFormRow = ({
	index,
	fileData,
	obsData,
	onEdit = (newObjdata) => {},
	onAdd = (copiedData) => {},
	onEditBoundingBox = (index) => {},
	onHover = (index) => {},
}: obsFormRowProps) => {
	const [hover, setHover] = useState(false);

	const handleHover = useCallback(
		(hover) => {
			setHover(hover);
			onHover(hover ? index : -1);
		},
		[index, onHover]
	);

	const handleChange = useCallback(
		(e) => {
			const editedData = {
				...obsData,
				[e.target.name]: e.target.value,
				edited: true,
			};
			onEdit(editedData);
		},
		[obsData, onEdit]
	);

	const setNewDataValue = useCallback(
		(key, value) => {
			const editedData = {
				...obsData,
				[key]: value,
				edited: true,
			};
			onEdit(editedData);
		},
		[obsData, onEdit]
	);

	const handleDelete = useCallback(
		function () {
			const editedData = {
				...obsData,
				data_files: obsData.data_files.filter((x) => x !== fileData["id"]),
				edited: true,
			};
			onEdit(editedData);
		},
		[fileData, obsData, onEdit]
	);

	const handleCopy = useCallback(
		function () {
			onAdd({ ...obsData });
		},
		[obsData, onAdd]
	);

	const handleValidationRequest = useCallback(
		function () {
			setNewDataValue("validation_requested", !obsData["validation_requested"]);
		},
		[obsData, setNewDataValue]
	);

	const handleStartEditBoundingBox = useCallback(
		function () {
			onEditBoundingBox(index);
		},
		[index, onEditBoundingBox]
	);

	const handleSpeciesSelection = useCallback(
		(selected) => {
			setNewDataValue("species_name", selected["species_name"]);
		},
		[setNewDataValue]
	);

	if (obsData.data_files.length === 0) {
		return null;
	}

	return (
		<tr
			className={
				hover ? "highlight" : obsData.validation_requested ? "uncertain" : ""
			}
			onMouseEnter={() => handleHover(true)}
			onMouseLeave={() => handleHover(false)}
		>
			<td className={"date-time-input"}>
				{obsData.user_is_owner ? (
					<input
						className={"form-control-sm"}
						name={"obs_dt"}
						type="datetime-local"
						value={obsData.obs_dt}
						onChange={handleChange}
					/>
				) : (
					obsData.obs_dt
				)}
			</td>
			<td className={"species-selector"}>
				{obsData.user_is_owner ? (
					<SpeciesSelector
						obsData={obsData}
						handleSelection={handleSpeciesSelection}
					/>
				) : (
					obsData.species_name
				)}
			</td>
			<td className={"number-input"}>
				{obsData.user_is_owner ? (
					<input
						className={"form-control-sm"}
						name={"number"}
						type={"number"}
						value={obsData.number}
						onChange={handleChange}
					/>
				) : (
					obsData.number
				)}
			</td>
			<td className={"text-input"}>
				{obsData.user_is_owner ? (
					<input
						className={"form-control-sm"}
						name={"sex"}
						value={obsData.sex}
						onChange={handleChange}
					/>
				) : (
					obsData.sex
				)}
			</td>
			<td className={"text-input"}>
				{obsData.user_is_owner ? (
					<input
						className={"form-control-sm"}
						name={"lifestage"}
						value={obsData.lifestage}
						onChange={handleChange}
					/>
				) : (
					obsData.lifestage
				)}
			</td>
			<td className={"text-input"}>
				{obsData.user_is_owner ? (
					<input
						className={"form-control-sm"}
						name={"behavior"}
						value={obsData.behavior}
						onChange={handleChange}
					/>
				) : (
					obsData.behavior
				)}
			</td>
			<td className={"button-column"}>
				{obsData.user_is_owner ? (
					<button
						onClick={handleValidationRequest}
						className="btn btn-sm btn-secondary uncertain"
					>
						{obsData.validation_requested ? "Certain" : "Uncertain"}
					</button>
				) : obsData.validation_requested ? (
					"Uncertain"
				) : (
					""
				)}
			</td>
			<td className={"button-column"}>
				<button
					onClick={handleCopy}
					className="btn btn-secondary btn-sm"
				>
					{obsData.validation_requested ? "Validate" : "Copy"}
				</button>
			</td>
			<td className={"button-column"}>
				{obsData.user_is_owner ? (
					<button
						onClick={handleStartEditBoundingBox}
						className="btn btn-secondary btn-sm"
					>
						Draw box
					</button>
				) : (
					""
				)}
			</td>
			<td className={"button-column"}>
				{obsData.user_is_owner ? (
					<button
						onClick={handleDelete}
						className="btn btn-sm btn-danger"
					>
						Delete
					</button>
				) : (
					""
				)}
			</td>
		</tr>
	);
};

interface obsFormProps {
	fileData: object;
	allObsData: object[] | [];
	onSubmit: () => void;
	onEdit: (newObservation: object, newRow?: boolean) => void;
	onEditBoundingBox: (index: number) => void;
	onHover: (index: number) => void;
	onStopEdit?: () => void;
}

const ObservationForm = ({
	fileData,
	allObsData = [],
	onSubmit = () => {},
	onEdit = (newObservation, newRow) => {},
	onEditBoundingBox = (index) => {},
	onHover = (index) => {},
	onStopEdit = () => {},
}: obsFormProps) => {
	const { authTokens } = useContext(AuthContext);

	//for each observation
	const getObsRowForm = function (index, obsData) {
		if (!("index" in obsData)) {
			obsData = getNewRow(obsData);
			obsData = { ...obsData, index: index };
			onEdit(obsData);
		}

		return (
			<ObservationFormRow
				key={index}
				index={index}
				obsData={{ ...obsData, index: index }}
				fileData={fileData}
				onEdit={onEdit}
				onAdd={addForm}
				onEditBoundingBox={onEditBoundingBox}
				onHover={onHover}
			/>
		);
	};

	const getNewRow = useCallback(
		function (newRow: object | undefined = undefined) {
			newRow = {
				id: newRow === undefined ? "" : newRow["id"],
				obs_dt:
					newRow === undefined
						? formatInTimeZone(
								fileData["recording_dt"],
								"UTC",
								"yyyy-MM-dd'T'HH:mm:ss"
						  )
						: formatInTimeZone(
								newRow["obs_dt"],
								"UTC",
								"yyyy-MM-dd'T'HH:mm:ss"
						  ),
				species_name: newRow === undefined ? "" : newRow["species_name"],
				source: newRow === undefined ? "human" : newRow["source"],
				sex: newRow === undefined ? "" : newRow["sex"],
				lifestage: newRow === undefined ? "" : newRow["lifestage"],
				behavior: newRow === undefined ? "" : newRow["behaviour"],
				bounding_box: newRow === undefined ? {} : newRow["bounding_box"],
				extra_data: newRow === undefined ? {} : newRow["extra_data"],
				validation_requested:
					newRow === undefined ? false : newRow["validation_requested"],
				data_files:
					newRow === undefined ? [fileData["id"]] : newRow["data_files"],
				number: newRow === undefined ? "1" : newRow["number"],
				user_is_owner: newRow === undefined ? true : newRow["user_is_owner"],
				edited: false,
			};
			return newRow;
		},
		[fileData]
	);

	const addForm = useCallback(
		function (newRow: object | undefined = undefined) {
			if (newRow !== undefined) {
				if (newRow["validation_requested"]) {
					newRow["validation_of"] = newRow["id"];
					newRow["validation_requested"] = false;
				}
				newRow["id"] = "";
				newRow["source"] = "human";
				newRow["edited"] = false;
			}

			newRow = getNewRow(newRow);

			onEdit(newRow, true);
		},
		[allObsData, getNewRow, onEdit]
	);

	const startLoadingToast = () => {
		const toastId = toast.loading("Loading...");
		return toastId;
	};

	const newPATCH = async function (x: { apiURL: string; newData: object }) {
		let response_json = await patchData(x.apiURL, authTokens.access, x.newData);

		return response_json;
	};

	const doPatch = useMutation({
		mutationFn: (inputValue: { apiURL: string; newData: object }) =>
			newPATCH(inputValue),
	});

	const newPOST = async function (x: { apiURL: string; newData: object }) {
		let response_json = await postData(x.apiURL, authTokens.access, x.newData);

		return response_json;
	};

	const doPost = useMutation({
		mutationFn: (inputValue: { apiURL: string; newData: object }) =>
			newPOST(inputValue),
	});

	const handleResponse = function (
		response,
		toastId,
		action,
		index = undefined
	) {
		if (!response["ok"]) {
			toast.error(
				`Error in submission ${
					response["detail"] ? ":" + response["detail"] : ""
				}`,
				{
					id: toastId,
				}
			);

			return false;
		} else {
			toast.success(`Observation succesfully ${action}`, {
				id: toastId,
			});
			if (
				index !== undefined &&
				(action === "created" || action === "modified")
			) {
				// make sure succesfully created rows get an ID so they don't get duplicated in the case of partial success
				// make sure succesfully edited rows are no longer flagged as edited
				let obsData = getNewRow(response);
				obsData = { ...obsData, index: index };

				onEdit(obsData);
			} else if (index !== undefined && action === "deleted") {
				//make sure succesfully deleted rows don't get submitted for deletion again
				let obsData = { ...allObsData[index], edited: false, index: index };

				onEdit(obsData);
			}
			return true;
		}
	};

	const submitForms = async function (stopEdit = false) {
		let toDelete = [] as object[];
		let toCreate = [] as object[];
		let toEdit = [] as object[];
		let successArray = [] as boolean[];

		for (const rowData of allObsData) {
			if (rowData !== undefined) {
				if (rowData["id"] === "") {
					if (rowData["data_files"].length > 0) {
						toCreate.push(rowData);
					}
				} else {
					if (rowData["data_files"].length > 0 && rowData["edited"]) {
						toEdit.push(rowData);
					} else if (rowData["data_files"].length === 0 && rowData["edited"]) {
						toDelete.push(rowData);
					}
				}
			}
		}

		if (toDelete.length === 0 && toCreate.length === 0 && toEdit.length === 0) {
			const toastId = startLoadingToast();
			toast.success("No change", {
				id: toastId,
			});
			return;
		}

		//edit
		for (const formData of toEdit) {
			const toastId = startLoadingToast();
			const response = await doPatch.mutateAsync({
				apiURL: `observation/${formData["id"]}/`,
				newData: formData,
			});
			let success = handleResponse(
				response,
				toastId,
				"modified",
				formData.index
			);
			successArray.push(success);
		}

		//create
		for (const formData of toCreate) {
			const toastId = startLoadingToast();

			const response = await doPost.mutateAsync({
				apiURL: "observation/",
				newData: formData,
			});
			let success = handleResponse(
				response,
				toastId,
				"created",
				formData.index
			);
			successArray.push(success);
		}

		//delete

		for (const formData of toDelete) {
			const toastId = startLoadingToast();
			const response = await deleteData(
				`observation/${formData["id"]}/`,
				authTokens.access
			);
			let success = handleResponse(
				response,
				toastId,
				"deleted",
				formData.index
			);
			successArray.push(success);
		}

		if (
			successArray.every((x, i) => {
				return x;
			})
		) {
			//only get data again if everything was succesful
			if (stopEdit) {
				onStopEdit();
			} else {
				onSubmit();
			}
		}
	};

	return (
		<>
			<table className={"observation-form table table-sm"}>
				<thead>
					<tr>
						<td>DateTime UTC</td>
						<td>Species name</td>
						<td>n</td>
						<td>Sex</td>
						<td>Lifestage</td>
						<td>Behaviour</td>
						<td></td>
						<td></td>
						<td></td>
					</tr>
				</thead>
				<tbody>
					{allObsData.map((obsData, index) => {
						return getObsRowForm(index, obsData);
					})}
				</tbody>
			</table>
			<button
				className="btn btn-outline-primary"
				onClick={() => addForm()}
			>
				Add new annotation
			</button>
			<button
				className="btn btn-outline-primary"
				onClick={submitForms}
			>
				Save and keep annotating
			</button>
			<button
				className="btn btn-outline-primary"
				onClick={() => submitForms(true)}
			>
				Save and finish annotating
			</button>
		</>
	);
};

export default ObservationForm;
