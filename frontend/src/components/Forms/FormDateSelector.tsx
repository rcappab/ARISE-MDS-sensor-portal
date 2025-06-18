import React, { ChangeEvent } from "react";
import "../../styles/base.css";

interface Props {
	id: string;
	name: string;
	label: string;
	value?: string;
	defaultvalue?: string;
	className?: string;
	onChange?: (e: ChangeEvent<HTMLInputElement>) => void;
	valid?: boolean;
	validated?: boolean;
	float?: boolean;
}

const FormDateSelector = ({
	id,
	name,
	label,
	value = undefined,
	className = "",
	onChange = (e) => {},
	valid = true,
	validated = false,
}: Props) => {
	return (
		<input
			className={`form-control px-1 ${
				validated ? (valid ? "is-valid" : "is-invalid") : ""
			}`}
			type="datetime-local"
			id={id}
			name={name}
			value={value}
			onChange={onChange}
		/>
	);
};

export default FormDateSelector;
