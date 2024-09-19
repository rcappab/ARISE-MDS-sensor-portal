import React from "react";
import { useState, useEffect } from "react";
import Select from "react-select";
import CreatableSelect from "react-select/creatable";

interface Props {
	name: string;
	id: string;
	className?: string;
	value?: string | [string] | null;
	defaultvalue?: string | [string] | null;
	defaultlabel?: string | [string] | null;
	label: string;
	choices: any[];
	isSearchable?: boolean;
	isLoading?: boolean;
	multiple?: boolean;
	creatable?: boolean;
	isClearable?: boolean;
	handleChange?: (string) => void;
	handleCreate?: (string) => void;
}

const FormSelect = ({
	name,
	id,
	className,
	value = undefined,
	defaultvalue = null,
	defaultlabel = null,
	label,
	choices = [],
	isSearchable = true,
	isLoading = false,
	multiple = false,
	creatable = false,
	isClearable = true,
	handleChange = (x) => {},
	handleCreate = (x) => {},
}: Props) => {
	useEffect(
		function verifyValueExistsInNewOptions() {
			if (selectedValue && choices.length == 0) {
				setSelectedValue(null);
			}
		},
		[choices]
	);

	// useEffect(
	// 	function tryToReset() {
	// 		console.log("defaukt changed");
	// 		setSelectedValue(undefined);
	// 	},
	// 	[defaultvalue]
	// );

	const objFromValue = function (_choices, value = null, label = null) {
		console.log(name, _choices, value);
		if (_choices) {
			if (value) {
				let chosenDefault;
				if (multiple) {
					chosenDefault = _choices.filter(function (item) {
						return value.includes(item.value);
					});
				} else {
					console.log("Not multiple " + defaultvalue);
					chosenDefault = _choices.find(function (item) {
						return value == item.value;
					});
				}
				console.log(name, _choices, value, chosenDefault);
				return chosenDefault;
			} else if (label) {
				let chosenDefault;
				if (multiple) {
					chosenDefault = _choices.filter(function (item) {
						return defaultlabel.includes(item.label);
					});
				} else {
					chosenDefault = _choices.find(function (item) {
						return defaultlabel == item.label;
					});
				}
				return chosenDefault;
			} else {
				console.log("NULL");
				return null;
			}
		}
	};

	const [selectedValue, setSelectedValue] = useState(
		objFromValue(choices, value)
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
		if (choices.length == 0) {
			newValue = null;
		}
		if (newValue == undefined) {
			newValue = null;
		}
		console.log("SELECTION CHANGE " + newValue);
		setSelectedValue(newValue);

		console.log(Array.isArray(newValue));
		if (newValue === null) {
			handleChange(newValue);
		} else if (multiple) {
			handleChange(
				newValue.map((x) => {
					return x["value"];
				})
			);
		} else {
			handleChange(newValue["value"]);
		}
	};

	// console.log(defaultvalue, selectedValue);
	// if (selectedValue === undefined && choices && choices.length > 0) {
	// 	if (multiple && !Array.isArray(defaultvalue)) {
	// 		defaultvalue = [defaultvalue];
	// 	}
	// 	console.log(
	// 		"set default " +
	// 			name +
	// 			" value " +
	// 			" " +
	// 			defaultvalue +
	// 			" " +
	// 			selectedValue
	// 	);
	// 	handleSelectionChange(objFromValue(choices));
	// }

	const getSelect = function () {
		console.log(name + " " + selectedValue);
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
						key={id}
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
						value={objFromValue(choices, value)}
					/>
				</div>
			);
		}
	};

	return getSelect();
};

export default FormSelect;
