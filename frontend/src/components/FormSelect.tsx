import React from "react";
import { useState } from "react";
import Select from "react-select";
import CreatableSelect from "react-select/creatable";

interface Props {
	name: string;
	id: string;
	className?: string;
	defaultvalue?: [string];
	defaultlabel?: [string];
	label: string;
	choices: any[];
	isSearchable?: boolean;
	isLoading?: boolean;
	multiple?: boolean;
	creatable?: boolean;
	isClearable?: boolean;
	handleChange?: () => void;
	handleCreate?: (string) => void;
}

const FormSelect = ({
	name,
	id,
	className,
	defaultvalue = undefined,
	defaultlabel = null,
	label,
	choices,
	isSearchable = true,
	isLoading = false,
	multiple = false,
	creatable = false,
	isClearable = true,
	handleChange = () => {},
	handleCreate = () => {},
}: Props) => {
	const chosenDefault = function (_choices) {
		console.log(name, _choices, defaultvalue);
		if (_choices) {
			if (defaultvalue) {
				let chosenDefault = _choices.find(function (item) {
					return defaultvalue == item.value;
				});
				console.log(name, _choices, defaultvalue, chosenDefault);
				return chosenDefault;
			} else if (defaultlabel) {
				let chosenDefault = _choices.find(function (item) {
					return defaultlabel === item.label;
				});
				return chosenDefault;
			} else {
				return null;
			}
		}
	};
	const [selectedValue, setSelectedValue] = useState();

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

	const handleOptionCreate = async (newInput) => {
		console.log(newInput);
		let newOption = await handleCreate(newInput);
		console.log(newOption);
		setSelectedValue(newOption);
	};

	const handleSelectionChange = function (newValue) {
		console.log(newValue);
		setSelectedValue(newValue);
		if (newValue) {
			handleChange(newValue["value"]);
		}
	};

	if (defaultvalue && selectedValue == undefined && choices.length > 0) {
		handleSelectionChange(chosenDefault(choices));
	}

	const getSelect = function () {
		console.log(name, selectedValue);
		if (creatable) {
			return (
				<div className={`form-floating ${className}`}>
					<CreatableSelect
						name={name}
						className="form-control no-border "
						id={id}
						options={choices}
						isClearable={isClearable}
						isSearchable={isSearchable}
						styles={style}
						isLoading={isLoading}
						value={selectedValue}
						placeholder={label}
						isMulti={multiple}
						onChange={handleSelectionChange}
						onCreateOption={handleOptionCreate}
					/>
				</div>
			);
		} else {
			return (
				<div className={`form-floating ${className}`}>
					<Select
						name={name}
						className="form-control no-border "
						id={id}
						options={choices}
						isClearable={isClearable}
						isSearchable={isSearchable}
						styles={style}
						isLoading={isLoading}
						placeholder={label}
						isMulti={multiple}
						onChange={handleSelectionChange}
						value={selectedValue}
					/>
				</div>
			);
		}
	};

	return getSelect();
};

export default FormSelect;
