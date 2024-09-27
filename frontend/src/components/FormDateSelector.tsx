import React from "react";
import "../styles/base.css";

interface Props {
	id: string;
	name: string;
	label: string;
	defaultvalue?: string;
	className?: string;
	handleChange?: () => void;
	valid?: boolean;
	validated?: boolean;
}

const FormDateSelector = ({
	id,
	name,
	label,
	defaultvalue,
	className = "",
	handleChange = () => {},
	valid = true,
	validated = false,
}: Props) => {
	return (
		<div className={`form-floating ${className}`}>
			<input
				className={`form-control ${
					validated ? (valid ? "is-valid" : "is-invalid") : ""
				}`}
				type="datetime-local"
				id={id}
				name={name}
				defaultValue={defaultvalue}
				onChange={handleChange}
			/>
			<label htmlFor={id}>{label}</label>
		</div>
	);
};

export default FormDateSelector;
