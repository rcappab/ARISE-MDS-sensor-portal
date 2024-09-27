import React, { useState } from "react";
import FormSelectTZ from "./FormSelectTZ.tsx";
import FormDateSelector from "./FormDateSelector.tsx";
import { itemFromTimeZone } from "../utils/timezoneFunctions.js";
import { fromZonedTime, formatInTimeZone } from "date-fns-tz";

interface Props {
	id: string;
	name: string;
	label: string;
	text: string;
	defaultvalue?: string;
	handleChange?: (any) => {};
	validated?: boolean;
	valid?: boolean;
	required?: boolean;
}

const FormDateTZSelect = ({
	id,
	name,
	label,
	text,
	defaultvalue,
	handleChange,
	validated = false,
	valid = true,
	required = false,
}: Props) => {
	const [timeZone, setTimeZone] = useState(
		itemFromTimeZone(Intl.DateTimeFormat().resolvedOptions().timeZone).value
	);
	const [dateTime, setDateTime] = useState(
		defaultvalue
			? formatInTimeZone(defaultvalue, timeZone, "yyyy-MM-dd'T'HH:mm:ss")
			: null
	);

	const [dateTimeString, setDateTimeString] = useState(
		defaultvalue ? defaultvalue : null
	);

	const setTimeZoneFromField = function (newValue) {
		setTimeZone(newValue);

		setDateTimeString(fromZonedTime(dateTime, newValue).toJSON());
	};

	const setDateTimeFromField = function (e) {
		let newValue = e.target.value;

		setDateTime(newValue);

		setDateTimeString(fromZonedTime(newValue, timeZone).toJSON());
	};

	return (
		<div
			id={id}
			className="form-floating"
		>
			<FormDateSelector
				id={`${id}_dt`}
				name={`${name}_dt`}
				label={label}
				handleChange={setDateTimeFromField}
				defaultvalue={dateTime}
				valid={valid}
				validated={validated}
			/>

			<FormSelectTZ
				id={`${id}_TZ`}
				name={`${name}_TZ`}
				label="Timezone"
				handleChange={setTimeZoneFromField}
				value={timeZone}
				valid={valid}
			/>

			{required ? (
				<input
					id={`${id}_UTC`}
					name={name}
					value={dateTimeString}
					className="d-none"
					onChange={handleChange}
					required
				/>
			) : (
				<input
					id={`${id}_UTC`}
					name={name}
					value={dateTimeString}
					className="d-none"
					onChange={handleChange}
				/>
			)}
		</div>
	);
};

export default FormDateTZSelect;
