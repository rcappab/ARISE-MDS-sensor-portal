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

	const handleSetIsActive = function (newvalue) {
		console.log(newvalue);
		setIsActive(newvalue);
	};

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
						handleChange={handleSetIsActive}
					/>
				</div>

				<div className="col-lg-2">
					<FormSelectAPI
						id="select-site"
						name="site"
						label="Site"
						choices={[]}
						defaultvalue={searchParams.get("site") || null}
						apiURL="site/"
						valueKey="id"
						labelKey="short_name"
					/>
				</div>

				<div className="col-lg-2">
					<FormSelectAPI
						key="select-datatype"
						id="select-datatype"
						name="device_type"
						label="Device type"
						choices={[]}
						defaultvalue={searchParams.get("device_type") || null}
						apiURL="datatype/"
						valueKey="id"
						labelKey="name"
					/>
				</div>

				<div className="col-lg-2 col-sm-6">
					<FormDateSelector
						id="start_date"
						name="deploymentStart__gte"
						label="Deployment started after"
						defaultvalue={searchParams.get("deploymentStart__gte")}
					/>
				</div>

				<div className="col-lg-2 col-sm-6">
					<FormDateSelector
						id="end_date"
						name="deploymentEnd__lte"
						label="Deployment ended before"
						defaultvalue={searchParams.get("deploymentEnd__lte")}
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

				<button
					type="submit"
					className="btn btn-primary btn-lg my-sm-1 col-sm-12 col-lg-2"
				>
					Search
				</button>

				<input
					type="button"
					className="btn btn-danger btn-lg my-sm-1 col-sm-12 col-lg-2"
					onClick={resetForm}
				/>

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
