import React from "react";
import { useEffect, useRef, useState } from "react";
import { Form, useSubmit } from "react-router-dom";
import FormSelect from "./FormSelect.tsx";
import FormSelectAPI from "./FormSelectAPI.tsx";
import FormDateSelector from "./FormDateSelector.tsx";
import { useSearchParams } from "react-router-dom";

function GalleryForm(props) {
	let [searchParams, setSearchParams] = useSearchParams();
	//let submit = useSubmit();
	const formRef = useRef(null);

	const onSubmit = function (e) {
		props.onSubmit();
	};

	useEffect(() => {
		if (searchParams.size == 0) {
			let formData = new FormData(formRef.current);
			setSearchParams(new URLSearchParams(formData));
		}
	}, [searchParams]);

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
					<FormSelect
						id="select-is_active"
						name="is_active"
						label="Deployment active?"
						choices={[
							{ value: "True", label: "True" },
							{ value: "False", label: "False" },
						]}
						isSearchable={false}
						defaultvalue={searchParams.get("is_active") || null}
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
						id="select-datatype"
						name="data_type"
						label="Device type"
						choices={[]}
						defaultvalue={searchParams.get("data_type") || null}
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
							defaultValue={searchParams.get("page_size") || 1}
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
