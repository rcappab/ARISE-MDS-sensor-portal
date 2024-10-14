import React from "react";
import { useEffect, useRef, useState } from "react";
import { Form } from "react-router-dom";
import FormSelect from "../FormSelect.tsx";
import FormSelectAPI from "../FormSelectAPI.tsx";
import FormDateSelector from "../FormDateSelector.tsx";
import { useSearchParams } from "react-router-dom";

interface Props {
	onSubmit: () => void;
	addNew: () => void;
	setFormKeys: (val: string[]) => void;
	nameKey: string;
}

function GalleryForm({
	onSubmit,
	addNew,
	setFormKeys,
	nameKey = "deployment_deviceID",
}: Props) {
	let [searchParams, setSearchParams] = useSearchParams();
	let [isActive, setIsActive] = useState(searchParams.get("is_active"));
	let [orderBy, setOrderBy] = useState(
		searchParams.get("ordering") ? searchParams.get("ordering") : nameKey
	);
	let [site, setSite] = useState(searchParams.get("site"));
	let [deviceType, setDeviceType] = useState(searchParams.get("device_type"));
	//let submit = useSubmit();
	const formRef = useRef<HTMLFormElement>(null);
	const defaultPageSize = 1;
	const handleSubmit = function (e) {
		onSubmit();
	};

	const resetForm = function (e) {
		e.preventDefault();
		if (!formRef.current) return;
		formRef.current.reset();
		let formData = new FormData(formRef.current);
		console.log(formData);
		let searchParams = new URLSearchParams(
			formData as unknown as Record<string, string>
		);
		for (let key of searchParams.keys()) {
			if (key === "page") {
				searchParams.set(key, (1).toString());
			} else if (key === "page_size") {
				searchParams.set(key, defaultPageSize.toString());
			} else {
				searchParams.set(key, "");
			}
		}
		console.log(searchParams);
		setSearchParams(searchParams);
		setIsActive(null);
		setSite(null);
		setDeviceType(null);
		setOrderBy(nameKey);
	};

	const handleAddNew = function (e) {
		e.preventDefault();
		addNew();
	};

	useEffect(() => {
		if (searchParams.size === 0) {
			if (!formRef.current) return;
			let formData = new FormData(formRef.current);
			console.log(formData);
			setSearchParams(
				new URLSearchParams(formData as unknown as Record<string, string>)
			);
		}
	}, [searchParams, setSearchParams]);

	useEffect(() => {
		if (!formRef.current) return;
		let formData = new FormData(formRef.current);
		setFormKeys(Array.from(formData.keys()));
		console.log(Array.from(formData.keys()));
	}, [formRef, setFormKeys]);

	return (
		<div id="search-form-div">
			<Form
				className="mb-3"
				onSubmit={handleSubmit}
				id="search-form"
				ref={formRef}
			>
				<div className="row gx-3 gy-2">
					<div className="col-lg-5">
						<div className="form-floating">
							<input
								name="search"
								id="search"
								className="form-control"
								defaultValue={
									!searchParams.get("search")
										? undefined
										: (searchParams.get("search") as string)
								}
							/>
							<label htmlFor="search">Search</label>
						</div>
					</div>

					<div className="col-lg-2">
						<div className="form-floating">
							<FormSelect
								id="select-is_active"
								name="is_active"
								label="Deployment active?"
								choices={[
									{ value: "True", label: "True" },
									{ value: "False", label: "False" },
								]}
								isSearchable={false}
								//defaultvalue={searchParams.get("is_active") || null}
								value={isActive}
								handleChange={setIsActive}
							/>
						</div>
					</div>

					<div className="col-lg-2">
						<div className="form-floating">
							<FormSelectAPI
								id="select-site"
								name="site"
								label="Site"
								choices={[]}
								value={site}
								apiURL="site/"
								valueKey="id"
								labelKey="short_name"
								handleChange={setSite}
							/>
						</div>
					</div>

					<div className="col-lg-2">
						<div className="form-floating">
							<FormSelectAPI
								key="select-datatype"
								id="select-datatype"
								name="device_type"
								label="Device type"
								choices={[]}
								value={deviceType}
								apiURL="datatype/"
								valueKey="id"
								labelKey="name"
								handleChange={setDeviceType}
							/>
						</div>
					</div>

					<FormDateSelector
						id="start_date"
						name="deploymentStart__gte"
						label="Deployment started after"
						defaultvalue={
							!searchParams.get("deploymentStart__gte")
								? undefined
								: (searchParams.get("deploymentStart__gte") as string)
						}
						className="col-lg-2"
					/>

					<FormDateSelector
						id="end_date"
						name="deploymentEnd__lte"
						label="Deployment ended before"
						defaultvalue={
							!searchParams.get("deploymentEnd__lte")
								? undefined
								: (searchParams.get("deploymentStart__gte") as string)
						}
						className="col-lg-2"
					/>

					<div className="col-lg-2">
						<div className="form-floating">
							<input
								className="form-control"
								name="page_size"
								type="number"
								min="1"
								max="100"
								step="5"
								defaultValue={searchParams.get("page_size") || defaultPageSize}
							/>
							<label htmlFor="page_size">Results per page</label>
						</div>
					</div>

					<div className="col-lg-2">
						<div className="form-floating">
							<FormSelect
								id="select-ordering"
								name="ordering"
								label="Order by"
								choices={[
									{ value: "deploymentdeviceID", label: "Alphabetical" },
									{ value: "created_on", label: "Registration time" },
									{
										value: "-created_on",
										label: "Registration time (descending)",
									},
								]}
								isSearchable={false}
								isClearable={false}
								//defaultvalue={searchParams.get("is_active") || null}
								value={orderBy}
								handleChange={setOrderBy}
							/>
						</div>
					</div>

					<div className="d-grid gap-2 d-md-block mt-2 pt-1 col-lg-4">
						<button
							type="submit"
							className="btn btn-primary btn-lg me-lg-2"
						>
							Search
						</button>

						<button
							type="button"
							className="btn btn-danger btn-lg ms-lg-2 me-lg-2"
							onClick={resetForm}
						>
							Reset
						</button>

						<button
							type="button"
							className="btn btn-success btn-lg ms-lg-2"
							onClick={handleAddNew}
						>
							Add new
						</button>
					</div>
				</div>

				<input
					name="page"
					className="d-none"
					type="number"
					value={1}
				/>
				<input
					name="id"
					className="d-none"
					id="deployment"
					defaultValue={
						!searchParams.get("id")
							? undefined
							: (searchParams.get("id") as string)
					}
				/>

				<input
					name="device"
					className="d-none"
					id="device"
					defaultValue={
						!searchParams.get("device")
							? undefined
							: (searchParams.get("device") as string)
					}
				/>
			</Form>
		</div>
	);
}

export default GalleryForm;
