import React from "react";
import { useEffect } from "react";
import Select from "react-select";

interface Props {
	name: string;
	id: string;
	defaultvalue: string;
	label: string;
	choices: [];
	isSearchable: boolean;
	isLoading: boolean;
}

const FormSelect = ({
	name,
	id,
	defaultvalue,
	label,
	choices,
	isSearchable,
	isLoading = false,
}: Props) => {
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
		menu: (baseStyles, state) => ({
			...baseStyles,
			marginTop: "0",
			zIndex: "999",
		}),
	};

	const chosenDefault = function () {
		if (choices) {
			return choices.find(function (item) {
				return item.value === defaultvalue;
			});
		} else {
			return null;
		}
	};

	return (
		<div className="form-floating">
			{/* <select className="form-control form-select" name={name} id={id}>
        {options.map((x) => {
          return <option value={x.value}> {x.label} </option>;
        })}
      </select> */}
			<Select
				name={name}
				className="form-control no-border"
				id={id}
				options={choices}
				isClearable={true}
				isSearchable={isSearchable}
				styles={style}
				isLoading={isLoading}
				defaultValue={chosenDefault}
				placeholder={label}
			/>
		</div>
	);
};

export default FormSelect;
