import React from "react";
import FormSelect from "./FormSelect.tsx";
import {
	timezonesWithoffsets,
	itemFromTimeZone,
} from "../utils/timezoneFunctions.js";

interface Props {
	name: string;
	id: string;
	label: string;
	className?: string;
	defaultvalue?: string;
	handleChange?: () => void;
}

const FormSelectTZ = ({
	name,
	id,
	label,
	className,
	defaultvalue,
	handleChange = () => {},
}: Props) => {
	return (
		<FormSelect
			defaultvalue={defaultvalue}
			name={name}
			id={id}
			label={label}
			choices={timezonesWithoffsets}
			isClearable={false}
			multiple={false}
			handleChange={handleChange}
			className={className}
		/>
	);
};

export default FormSelectTZ;
