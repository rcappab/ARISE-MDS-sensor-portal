import React from "react";
import { useEffect, useRef, useState } from "react";
import { Form, useSubmit } from "react-router-dom";
import FormSelect from "./FormSelect.tsx";
import FormSelectAPI from "./FormSelectAPI.tsx";
import FormDateSelector from "./FormDateSelector.tsx";
import { useSearchParams } from "react-router-dom";

function GalleryForm(props) {
	let [searchParams, setSearchParams] = useSearchParams();
	let [isActive, setIsActive] = useState(searchParams.get("is_active"));
	let [orderBy, setOrderBy] = useState(
		searchParams.get("ordering")
			? searchParams.get("ordering")
			: "deploymentdeviceID"
	);
	let [site, setSite] = useState(searchParams.get("site"));
	let [deviceType, setDeviceType] = useState(searchParams.get("device_type"));
	//let submit = useSubmit();
	const formRef = useRef(null);
	const defaultPageSize = 1;
	const onSubmit = function (e) {
		props.onSubmit();
	};

	const resetForm = function (e) {
		e.preventDefault();
		formRef.current.reset();
		let formData = new FormData(formRef.current);
		console.log(formData);
		let searchParams = new URLSearchParams(formData);
		for (let key of searchParams.keys()) {
			if (key == "page") {
				searchParams.set(key, 1);
			} else if (key == "page_size") {
				searchParams.set(key, defaultPageSize);
			} else {
				searchParams.set(key, "");
			}
		}
		console.log(searchParams);
		setSearchParams(searchParams);
		setIsActive(null);
		setSite(null);
		setDeviceType(null);
		setOrderBy("deploymentdeviceID");
	};

	const addNew = function (e) {
		e.preventDefault();
		props.addNew();
	};

	useEffect(() => {
		if (searchParams.size == 0) {
			let formData = new FormData(formRef.current);
			console.log(formData);
			setSearchParams(new URLSearchParams(formData));
		}
	}, [searchParams]);

	useEffect(() => {
		let formData = new FormData(formRef.current);
		props.setFormKeys(Array.from(formData.keys()));
		console.log(Array.from(formData.keys()));
	}, [formRef]);

	// useEffect(() => {
	//   let searchKeys = searchParams.keys()
	//   for (const x of searchKeys){
	//     let formField = document.getElementsByName(x)
	//     if(formField.length>0){
	//       let fieldValue = searchParams.get(x)
	//       if (fieldValue != ''){
	//         formField[0].setAttribute('value',fieldValue)
	//       }
	//     }
	//   }
	//   onSubmit()
	// },[])

	return (
		<div id="search-form-div">
			<Form
				className="row gy-2 gx-3 mb-3 align-items-center"
				onSubmit={onSubmit}
				id="search-form"
				ref={formRef}
			>
				<div className="col-lg-5">
					<div className="form-floating">
						<input
							name="search"
							id="search"
							className="form-control"
							defaultValue={searchParams.get("search")}
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

				<div className="col-lg-5 col-sm-6 row">
					<FormDateSelector
						id="start_date"
						name="deploymentStart__gte"
						label="Deployment started after"
						defaultvalue={searchParams.get("deploymentStart__gte")}
						className="col-lg-6"
					/>

					<FormDateSelector
						id="end_date"
						name="deploymentEnd__lte"
						label="Deployment ended before"
						defaultvalue={searchParams.get("deploymentEnd__lte")}
						className="col-lg-6"
					/>
				</div>

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

				<div className="col-lg-5">
					<button
						type="submit"
						className="btn btn-primary btn-lg my-sm-1 col-sm-12 col-lg-3"
					>
						Search
					</button>

					<button
						type="button"
						className="btn btn-danger btn-lg my-sm-1 col-sm-12 col-lg-3"
						onClick={resetForm}
					>
						{" "}
						Reset{" "}
					</button>

					<button
						type="button"
						className="btn btn-success btn-lg my-sm-1 col-sm-12 col-lg-3"
						onClick={addNew}
					>
						{" "}
						Add new{" "}
					</button>
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
					defaultValue={searchParams.get("id")}
				/>

				<input
					name="device"
					className="d-none"
					id="device"
					defaultValue={searchParams.get("device")}
				/>
			</Form>
		</div>
	);
}

export default GalleryForm;
