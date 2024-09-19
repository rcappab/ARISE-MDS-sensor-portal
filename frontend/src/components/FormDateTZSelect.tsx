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
}

const FormDateTZSelect = ({ id, name, label, text, defaultvalue }: Props) => {
	const [timeZone, setTimeZone] = useState(String);
	const [dateTime, setDateTime] = useState(String);
	const [dateTimeString, setDateTimeString] = useState(
		defaultvalue ? defaultvalue : null
	);

	const setTimeZoneFromField = function (newValue) {
		console.log(newValue);
		setTimeZone(newValue);

		setDateTimeString(fromZonedTime(dateTime, newValue).toJSON());
	};

	const setDateTimeFromField = function (e) {
		console.log(e.target.value);

		let newValue = e.target.value;

		setDateTime(newValue);

		setDateTimeString(fromZonedTime(newValue, timeZone).toJSON());
	};

	const defaulttimezone = itemFromTimeZone(
		Intl.DateTimeFormat().resolvedOptions().timeZone
	).value;

	const localiseddefaultvalue = defaultvalue
		? formatInTimeZone(defaultvalue, defaulttimezone, "yyyy-MM-dd'T'HH:mm:ss")
		: null;

	return (
		<div className="form-floating">
			<input
				id={id}
				name={name}
				defaultValue={dateTimeString}
				value={dateTimeString}
				className="d-none"
			/>
			<div className="row">
				<FormDateSelector
					id={`${id}_dt`}
					name={`${name}_dt`}
					label={label}
					handleChange={setDateTimeFromField}
					className="col"
					defaultvalue={localiseddefaultvalue}
				/>

				<FormSelectTZ
					id={`${id}_TZ`}
					name={`${name}_TZ`}
					label="Timezone"
					handleChange={setTimeZoneFromField}
					className="col"
					defaultvalue={defaulttimezone}
				/>
			</div>

			<div className="form-text">
				{text}
				<div className="invalid-feedback"></div>
			</div>
		</div>
	);
};

export default FormDateTZSelect;
