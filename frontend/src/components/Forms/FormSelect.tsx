import React from "react";
import { useState, useEffect } from "react";
import Select from "react-select";
import CreatableSelect from "react-select/creatable";

interface Props {
	name: string;
	id: string;
	value?: string | string[] | null;
	label: string;
	choices: any[] | undefined;
	isSearchable?: boolean;
	isLoading?: boolean;
	multiple?: boolean;
	creatable?: boolean;
	isClearable?: boolean;
	handleChange?: (string) => void;
	handleCreate?: (string) => void;
	handleInput?: (input) => void;
	valid?: boolean;
	required?: boolean;
}

const FormSelect = ({
	name,
	id,
	value = undefined,
	label,
	choices = [],
	isSearchable = true,
	isLoading = false,
	multiple = false,
	creatable = false,
	isClearable = true,
	handleChange = (x) => {},
	handleCreate = (x) => {},
	handleInput = (x) => {},
	valid = true,
	required = false,
}: Props) => {
	useEffect(
		function verifyValueExistsInNewOptions() {
			if (value && choices.length === 0) {
				handleChange(null);
			}
		},
		[choices, handleChange, value]
	);

	const objFromValue = function (_choices, value: any | [any] = null) {
		if (!value) return null;

		if (_choices && _choices.length > 0) {
			if (value) {
				let chosenDefault = null;
				if (multiple) {
					chosenDefault = _choices.filter(function (item) {
						return value.includes(item.value);
					});
				} else {
					chosenDefault = _choices.find(function (item) {
						return String(value) === String(item.value);
					});
				}

				return chosenDefault;
			} else {
				return null;
			}
		} else {
			return null;
		}
	};

	const [setSelectedValue] = useState(objFromValue(choices, value) as any);

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
		let newOption = await handleCreate(newInput);

		handleChange(newOption["value"]);
	};

	const handleSelectionChange = function (newValue) {
		if (choices.length === 0) {
			newValue = null;
		}
		if (newValue === undefined) {
			newValue = null;
		}
		setSelectedValue(newValue);

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

	const getSelect = function () {
		if (creatable) {
			return (
				<CreatableSelect
					name={name}
					className={`form-control no-border ${
						valid ? "is-valid" : "is-invalid"
					}`}
					id={id}
					options={choices}
					isClearable={isClearable}
					isSearchable={isSearchable}
					styles={style}
					isLoading={isLoading}
					value={objFromValue(choices, value)}
					placeholder={label}
					isMulti={multiple}
					onChange={handleSelectionChange}
					onCreateOption={handleOptionCreate}
					onInputChange={handleInput}
				/>
			);
		} else {
			return (
				<Select
					key={id}
					name={name}
					className={`form-control no-border ${
						valid ? "is-valid" : "is-invalid"
					}`}
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
					onInputChange={handleInput}
				/>
			);
		}
	};

	return getSelect();
};

export default FormSelect;
