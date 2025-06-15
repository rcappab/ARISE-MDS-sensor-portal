import React, { useCallback } from "react";
import { useEffect, useRef, useState } from "react";
import { Form } from "react-router-dom";
import FormSelect from "../Forms/FormSelect.tsx";
import FormSelectAPI from "../Forms/FormSelectAPI.tsx";
import FormDateSelector from "../Forms/FormDateSelector.tsx";
import { useSearchParams } from "react-router-dom";

interface Props {
	objectType?: string;
	fromObject?: string;
	fromID?: string;
	onSubmit: () => void;
	addNew: () => void;
	jobID: string | null;
	onJobChange: (number) => void;
	handleStartJob: () => void;
	setFormKeys: (val: string[]) => void;
	orderBy: string;
	pageSize: number;
	pageNum: number;
	onReset: (searchParams: any) => void;
	selectedItemsCount?: number;
	noData?: boolean;
}

function GalleryForm({
	onSubmit,
	addNew,
	jobID,
	onJobChange,
	handleStartJob,
	setFormKeys,
	orderBy,
	pageSize,
	pageNum,
	onReset,
	objectType = "deployment",
	fromObject = undefined,
	fromID = undefined,
	selectedItemsCount = 0,
	noData = true,
}: Props) {
	const [searchParams] = useSearchParams();

	const formRef = useRef<HTMLFormElement>(null);

	const handleSubmit = function (e) {
		onSubmit();
	};
	const handleAddNew = function (e) {
		e.preventDefault();
		addNew();
	};

	const defaults = React.useMemo(() => {
		const baseDefaults = {
			site: null,
			device_type: null,
			file_type: null,
			obs_type: null,
			uncertain: null,
			archived: null,
		};
		if (objectType !== "datafile") {
			baseDefaults["is_active"] = "True";
		} else {
			baseDefaults["is_active"] = null;
		}
		return baseDefaults;
	}, [objectType]);

	const [filterData, setFilterData] = useState({
		search: searchParams.get("search") || "",
		site: searchParams.get("site") || defaults["site"],
		device_type: searchParams.get("device_type") || defaults["device_type"],
		file_type: searchParams.get("file_type") || defaults["file_type"],
		is_active: searchParams.get("is_active") || defaults["is_active"],
		obs_type: searchParams.get("obs_type") || defaults["obs_type"],
		uncertain: searchParams.get("uncertain") || defaults["uncertain"],
		archived: searchParams.get("archived") || defaults["archived"],
		recording_dt__gte: !searchParams.get("recording_dt__gte")
			? ""
			: (searchParams.get("recording_dt__gte") as string),
		recording_dt__lte: !searchParams.get("recording_dt__lte")
			? ""
			: (searchParams.get("recording_dt__lte") as string),
		deployment_start__gte: !searchParams.get("deployment_start__gte")
			? ""
			: (searchParams.get("deployment_start__gte") as string),
		end_date: !searchParams.get("deployment_end__lte")
			? ""
			: (searchParams.get("deployment_end__lte") as string),
	});

	const handleChange = useCallback((e) => {
		setFilterData((prevState) => {
			return { ...prevState, [e.target.name]: e.target.value };
		});
	}, []);

	const setNewDataValue = useCallback((key, value) => {
		setFilterData((prevState) => {
			return { ...prevState, [key]: value };
		});
	}, []);

	const handleResetForm = function (e) {
		e.preventDefault();
		resetForm();
	};

	const handleFilterChange = useCallback(() => {
		if (searchParams.size === 0) {
			if (!formRef.current) return;

			let formData = new FormData(formRef.current);
			formData.delete("job_name");
			setFormKeys(Array.from(formData.keys()));

			let searchParams = new URLSearchParams(
				formData as unknown as Record<string, string>
			);
			onReset(searchParams);
		}
	}, [searchParams.size, setFormKeys, onReset]);

	const resetForm = useCallback(
		function () {
			if (!formRef.current) return;
			//Resetting select boxes
			formRef.current.reset();
			const newFilterData = { ...filterData };
			for (const key in newFilterData) {
				if (defaults.hasOwnProperty(key)) {
					newFilterData[key] = defaults[key];
				} else {
					newFilterData[key] = "";
				}
			}

			setFilterData(newFilterData);
		},
		[defaults, filterData]
	);

	useEffect(() => {
		if (searchParams.size === 0) {
			if (!formRef.current) return;
			resetForm();
		}
	}, [resetForm, searchParams, objectType, defaults]);

	useEffect(() => {
		handleFilterChange();
	}, [filterData, handleFilterChange]);

	const doJobButton = function () {
		return (
			<>
				<span className="me-2 align-content-center">
					{selectedItemsCount > 0
						? `${selectedItemsCount} selected. Esc to clear.
				`
						: `Ctrl or shift to select`}
				</span>
				<div className="formControl">
					<FormSelectAPI
						id="select-job"
						name="job_name"
						apiURL={`genericjob/?data_type=${objectType}`}
						label="Select job..."
						valueKey="id"
						labelKey="name"
						choices={[]}
						isSearchable={true}
						value={jobID}
						handleChange={onJobChange}
					/>
				</div>
				<button
					type="button"
					className="btn btn-secondary ms-lg-2"
					onClick={handleStartJob}
					disabled={jobID === null || noData}
				>
					Start job
				</button>
			</>
		);
	};

	const activeField = function () {
		if (!["deployment", "device", "project", "datafile"].includes(objectType))
			return;

		return (
			<div className="col-lg-2">
				<div className="">
					<label htmlFor="select-is_active">Deployment active now?</label>
					<FormSelect
						id="select-is_active"
						name="is_active"
						label="No filter"
						choices={[
							{ value: "True", label: "True" },
							{ value: "False", label: "False" },
						]}
						isSearchable={false}
						value={filterData.is_active}
						handleChange={(newValue) => setNewDataValue("is_active", newValue)}
					/>
				</div>
			</div>
		);
	};

	const archivedField = function () {
		if (!["datafile"].includes(objectType)) return;

		return (
			<div className="col-lg-2">
				<div className="">
					<label htmlFor="select-archived">File archived</label>
					<FormSelect
						id="select-archived"
						name="archived"
						label="No filter"
						choices={[
							{ value: "True", label: "True" },
							{ value: "False", label: "False" },
						]}
						isSearchable={false}
						value={filterData.archived}
						handleChange={(newValue) => setNewDataValue("archived", newValue)}
					/>
				</div>
			</div>
		);
	};

	const observationField = function () {
		if (!["datafile"].includes(objectType)) return;

		return (
			<div className="col-lg-2">
				<div className="">
					<label htmlFor="select-obs_type">Has observations</label>
					<FormSelect
						id="select-obs_type"
						name="obs_type"
						label="No filter"
						choices={[
							{ value: "no_obs", label: "No observations" },
							{ value: "no_human_obs", label: "No human observations" },
							{ value: "all_obs", label: "All observations" },
							{ value: "has_human", label: "Human observations" },
							{ value: "has_ai", label: "AI observations" },
							{ value: "human_only", label: "Human observations only" },
							{ value: "ai_only", label: "AI observations only" },
						]}
						isSearchable={false}
						value={filterData.obs_type}
						handleChange={(newValue) => setNewDataValue("obs_type", newValue)}
					/>
				</div>
			</div>
		);
	};

	const uncertainField = function () {
		if (!["datafile"].includes(objectType)) return;
		return (
			<div className="col-lg-2">
				<div className="">
					<label htmlFor="select-uncertain">Uncertain observations</label>
					<FormSelect
						id="select-uncertain"
						name="uncertain"
						label="No filter"
						choices={[
							{ value: "no_uncertain", label: "No uncertain observations" },
							{ value: "uncertain", label: "Uncertain observations" },
							{
								value: "other_uncertain",
								label: "Other's uncertain observations",
							},
							{ value: "my_uncertain", label: "My uncertain observations" },
						]}
						isSearchable={false}
						value={filterData.uncertain}
						handleChange={(newValue) => setNewDataValue("uncertain", newValue)}
					/>
				</div>
			</div>
		);
	};

	const dateField = function (id, name, label, validtypes) {
		if (!validtypes.includes(objectType)) return;

		return (
			<div className="col-lg-2">
				<label htmlFor="id">{label}</label>
				<FormDateSelector
					id={id}
					name={name}
					label={label}
					value={filterData[name]}
					onChange={handleChange}
					className="col-lg-2"
					float={false}
				/>
			</div>
		);
	};

	const siteField = function () {
		if (!["deployment", "device", "datafile"].includes(objectType)) return;

		return (
			<div className="col-lg-2">
				<label htmlFor="select-site">Site</label>
				<div className="">
					<FormSelectAPI
						id="select-site"
						name="site"
						label="All"
						choices={[]}
						value={filterData.site}
						apiURL="site/?page_size=20"
						valueKey="id"
						labelKey="short_name"
						handleChange={(newValue) => setNewDataValue("site", newValue)}
					/>
				</div>
			</div>
		);
	};

	const deviceTypeField = function () {
		if (!["deployment", "device", "datafile"].includes(objectType)) return;

		return (
			<div className="col-lg-2">
				<div className="">
					<label htmlFor="select-datatype">Device type</label>
					<FormSelectAPI
						key="select-datatype"
						id="select-datatype"
						name="device_type"
						label="All"
						choices={[]}
						value={filterData.device_type}
						apiURL="datatype/?page_size=20"
						valueKey="id"
						labelKey="name"
						handleChange={(newValue) =>
							setNewDataValue("device_type", newValue)
						}
					/>
				</div>
			</div>
		);
	};

	const dataFileTypeField = function () {
		if (objectType !== "datafile") return;

		return (
			<div className="col-lg-2">
				<div className="">
					<label htmlFor="select-filetype">File type</label>
					<FormSelectAPI
						key="select-filetype"
						id="select-fileType"
						name="file_type"
						label="All"
						choices={[]}
						value={filterData.file_type}
						apiURL="datatype/?file_type=true&page_size=20"
						valueKey="id"
						labelKey="name"
						handleChange={(newValue) => setNewDataValue("file_type", newValue)}
					/>
				</div>
			</div>
		);
	};

	const addNewButton = function () {
		if (objectType !== "datafile") {
			return (
				<button
					type="button"
					className="btn btn-success ms-lg-2 me-lg-2"
					onClick={handleAddNew}
				>
					Add new {objectType}
				</button>
			);
		}
	};

	return (
		<div id="search-form-div">
			<Form
				className="mb-3"
				onSubmit={handleSubmit}
				id="search-form"
				ref={formRef}
			>
				<div className="row gx-3 gy-2">
					<div className="col-lg-4">
						<div className="">
							<label htmlFor="search">Search</label>
							<input
								name="search"
								id="search"
								className="form-control"
								value={filterData.search}
								onChange={handleChange}
							/>
						</div>
					</div>
					{activeField()}
					{siteField()}
					{deviceTypeField()}
					{dataFileTypeField()}
					{dateField(
						"start_date",
						"deployment_start__gte",
						"Deployment started after",
						["deployment"]
					)}
					{dateField(
						"start_date_2",
						"deployment_start__lte",
						"Deployment started before",
						["deployment"]
					)}
					{dateField(
						"end_date",
						"deployment_end__lte",
						"Deployment ended before",
						["deployment"]
					)}
					{dateField(
						"end_date2",
						"deployment_end__gte",
						"Deployment ended after",
						["deployment"]
					)}
					{dateField("start_date", "recording_dt__gte", "File recorded after", [
						"datafile",
					])}
					{dateField("end_date", "recording_dt__lte", "File recorded before", [
						"datafile",
					])}
					{observationField()}
					{uncertainField()}
					{archivedField()}
				</div>
				<div className="row gap-2 mt-2 pt-1">
					<div className="col">
						<button
							type="submit"
							className="btn btn-primary me-lg-2"
						>
							Search
						</button>

						<button
							type="button"
							className="btn btn-danger ms-lg-2 me-lg-2"
							onClick={handleResetForm}
						>
							Reset
						</button>
					</div>
					<div className="col d-flex justify-content-end">
						{doJobButton()}
						{addNewButton()}
					</div>
				</div>

				<input
					name="page"
					className="d-none"
					type="number"
					value={pageNum}
					readOnly={true}
				/>
				<input
					name="ordering"
					className="d-none"
					value={orderBy}
					readOnly={true}
				/>
				<input
					name="page_size"
					className="d-none"
					type="number"
					value={pageSize}
					readOnly={true}
				/>
			</Form>
		</div>
	);
}

export default GalleryForm;
