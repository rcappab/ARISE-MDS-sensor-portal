import React from "react";
import "../styles/base.css";

interface Props {
	id: string;
	name: string;
	label: string;
	defaultvalue?: string;
	className?: string;
	handleChange?: () => void;
}

const FormDateSelector = (props: Props) => {
	return (
		<div className={`form-floating ${props.className}`}>
			<input
				className="form-control"
				type="datetime-local"
				id={props.id}
				name={props.name}
				defaultValue={props.defaultvalue}
				onChange={props.handleChange}
			/>
			<label htmlFor={props.id}>{props.label}</label>
		</div>
	);
};

export default FormDateSelector;
